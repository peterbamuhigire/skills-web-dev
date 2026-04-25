# Mapbox offline — mobile SDKs and web fallback

Native Mapbox SDKs on Android and iOS have a first-class offline region API. Web Mapbox GL JS does **not** have native offline — you implement tile caching with service workers and IndexedDB.

Companion: `mapbox-gl-basics.md`.

## Decision

```text
Target         Strategy
-------------  ---------------------------------------------------
Android app    Mapbox Maps SDK for Android - OfflineManager + OfflineRegion
iOS app        MapboxMaps - OfflineManager + TileStore
Web PWA        Service worker + Cache Storage + IndexedDB for style/sprites
Web (desktop)  Usually unnecessary; cache only for brief reconnects
React Native   @rnmapbox/maps offlineManager (thin wrapper over native)
```

## iOS offline (MapboxMaps v10+)

```swift
import MapboxMaps

final class OfflineService {
    let tileStore = TileStore.default
    let offlineManager = OfflineManager(resourceOptions: .init(accessToken: "..."))

    func downloadRegion(
        styleURI: StyleURI = .streets,
        name: String,
        bounds: CoordinateBounds,
        minZoom: UInt8 = 10,
        maxZoom: UInt8 = 15
    ) async throws {
        let stylePackOptions = StylePackLoadOptions(
            glyphsRasterizationMode: .ideographsRasterizedLocally,
            metadata: ["name": name],
            acceptExpired: true
        )
        let tilesetDescriptor = offlineManager.createTilesetDescriptor(
            for: .init(styleURI: styleURI, minZoom: minZoom, maxZoom: maxZoom)
        )
        let region = TileRegionLoadOptions(
            geometry: .polygon(Polygon(outerRing: .init(coordinates: [
                bounds.southwest,
                .init(latitude: bounds.southwest.latitude, longitude: bounds.northeast.longitude),
                bounds.northeast,
                .init(latitude: bounds.northeast.latitude, longitude: bounds.southwest.longitude),
                bounds.southwest,
            ]))),
            descriptors: [tilesetDescriptor],
            metadata: ["name": name],
            acceptExpired: true
        )!

        try await withCheckedThrowingContinuation { cont in
            tileStore.loadTileRegion(forId: name, loadOptions: region) { progress in
                print("Download \(progress.completedResourceCount)/\(progress.requiredResourceCount)")
            } completion: { result in
                switch result {
                case .success: cont.resume()
                case .failure(let err): cont.resume(throwing: err)
                }
            }
        }
    }

    func deleteRegion(id: String) {
        tileStore.removeTileRegion(forId: id)
    }
}
```

Storage quotas and rules:

- Default limit is **750 MB** for offline data on Mapbox plans.
- Tile regions use ~5-50 MB per small city area.
- Style packs are separate from tile regions — download both for full offline.
- Delete stale regions; `TileStore.allTileRegions` enumerates them.

## Android offline (Maps SDK v10+)

```kotlin
class OfflineService(context: Context, token: String) {
    private val tileStore = TileStore.create()
    private val offlineManager = OfflineManager(MapboxOptions.builder().accessToken(token).build())

    fun downloadRegion(
        name: String,
        bounds: CoordinateBounds,
        styleUri: String = Style.MAPBOX_STREETS,
        minZoom: Byte = 10, maxZoom: Byte = 15,
    ) {
        val tilesetDescriptor = offlineManager.createTilesetDescriptor(
            TilesetDescriptorOptions.Builder()
                .styleURI(styleUri)
                .minZoom(minZoom)
                .maxZoom(maxZoom)
                .build()
        )
        val tileRegionOptions = TileRegionLoadOptions.Builder()
            .geometry(Polygon.fromLngLats(listOf(listOf(
                Point.fromLngLat(bounds.southwest.longitude(), bounds.southwest.latitude()),
                Point.fromLngLat(bounds.northeast.longitude(), bounds.southwest.latitude()),
                Point.fromLngLat(bounds.northeast.longitude(), bounds.northeast.latitude()),
                Point.fromLngLat(bounds.southwest.longitude(), bounds.northeast.latitude()),
                Point.fromLngLat(bounds.southwest.longitude(), bounds.southwest.latitude()),
            ))))
            .descriptors(listOf(tilesetDescriptor))
            .acceptExpired(true)
            .build()

        tileStore.loadTileRegion(name, tileRegionOptions,
            { progress -> Log.d("offline", "${progress.completedResourceCount}/${progress.requiredResourceCount}") },
            { result -> if (result.isValue) Log.d("offline", "done") }
        )
    }
}
```

## Sync strategy

Rules of thumb for sync in background:

1. User requests a download of a named region (city, delivery zone).
2. Download style pack + tile region + any app data (GeoJSON of listings) as a unit.
3. Versioned: store `downloaded_at` and a `min_freshness`. Re-download when older than X days.
4. WiFi-only by default; let users override.
5. Show storage used and provide a delete button.
6. Warn before exceeding 500 MB (app-level cap under Mapbox 750 MB).

## Web offline (service worker + Cache Storage)

```ts
// public/sw.js
const TILE_CACHE = "mapbox-tiles-v1";
const STYLE_CACHE = "mapbox-style-v1";
const TILE_HOSTS = ["api.mapbox.com", "tiles.example.com"];
const MAX_TILES = 2000;

self.addEventListener("fetch", (event) => {
  const url = new URL(event.request.url);
  if (!TILE_HOSTS.includes(url.hostname)) return;

  const isStyle = url.pathname.includes("/styles/") || url.pathname.endsWith(".json")
               || url.pathname.includes("/sprites/") || url.pathname.endsWith(".pbf");

  const cacheName = isStyle ? STYLE_CACHE : TILE_CACHE;
  event.respondWith((async () => {
    const cache = await caches.open(cacheName);
    const cached = await cache.match(event.request);
    if (cached) {
      event.waitUntil(revalidate(event.request, cache));
      return cached;
    }
    try {
      const response = await fetch(event.request);
      if (response.ok) cache.put(event.request, response.clone());
      pruneIfOversized(cache, MAX_TILES);
      return response;
    } catch {
      return cached ?? Response.error();
    }
  })());
});

async function revalidate(req, cache) {
  try {
    const fresh = await fetch(req);
    if (fresh.ok) await cache.put(req, fresh);
  } catch { /* offline — keep cached */ }
}

async function pruneIfOversized(cache, max) {
  const keys = await cache.keys();
  if (keys.length <= max) return;
  // FIFO eviction
  for (const k of keys.slice(0, keys.length - max)) await cache.delete(k);
}
```

Registration:

```ts
if ("serviceWorker" in navigator) {
  navigator.serviceWorker.register("/sw.js", { scope: "/" });
}
```

## Web storage quotas

Browsers give origins an opaque quota (typically ~6% of disk on Chrome, with per-cache-entry size limits). Check usage:

```ts
const { usage, quota } = await navigator.storage.estimate();
console.log(`Used ${usage}/${quota}`);

// Request persistent storage so the browser won't evict when storage is low
if ("storage" in navigator && "persist" in navigator.storage) {
  await navigator.storage.persist();
}
```

Rules:

- Never assume indefinite retention — browsers may evict under pressure.
- `navigator.storage.persist()` asks the browser to treat the origin as important.
- Budget: a realistic city tile pack (z10-15) is 30-80 MB.

## Pre-caching at install

Use a `workbox-precaching` recipe or custom install event to seed the cache:

```ts
self.addEventListener("install", (event) => {
  event.waitUntil((async () => {
    const cache = await caches.open(STYLE_CACHE);
    await cache.addAll([
      "https://api.mapbox.com/styles/v1/mapbox/streets-v12?access_token=...",
      "https://api.mapbox.com/fonts/v1/mapbox/Open%20Sans%20Regular%2CArial%20Unicode%20MS%20Regular/0-255.pbf",
    ]);
  })());
});
```

Note: tile prefetch is expensive; do it only behind a user action ("Download offline map for this region").

## App-data offline

Offline maps without offline data are half a feature. Sync strategy for the business data layer:

- Store a GeoJSON snapshot in IndexedDB.
- Version it with ETag; re-fetch when online.
- Register background sync (`ServiceWorkerRegistration.sync.register`) for queued mutations.

## Testing

- Chrome DevTools > Application > Service Workers > Offline toggle.
- Device: toggle airplane mode; verify last-seen map still renders.
- CI: run Playwright with `context.setOffline(true)` after initial load.

## Anti-patterns

- Caching Google Maps tiles via service worker — violates Google ToS (>30 day cache).
- Downloading tile packs without a style pack — map renders blank.
- Forgetting to delete regions; users run out of disk.
- Shipping a web-offline map without `navigator.storage.persist()` — silent eviction.
- Using the service worker to proxy API keys (exposes them to DevTools anyway).
