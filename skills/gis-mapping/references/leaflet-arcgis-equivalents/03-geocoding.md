# 3) Geocoding

```php
// /app/Services/GeocodingService.php
namespace App\Services;

class GeocodingService {
    private $providers = [
        'nominatim' => 'https://nominatim.openstreetmap.org/search',
        'photon' => 'https://photon.komoot.io/api'
    ];

    public function geocode($address, $provider = 'nominatim', $options = []) {
        $defaults = [
            'limit' => 5,
            'countrycodes' => 'us',
            'addressdetails' => 1
        ];

        $options = array_merge($defaults, $options);

        switch ($provider) {
            case 'nominatim':
                return $this->nominatimGeocode($address, $options);
            case 'photon':
                return $this->photonGeocode($address, $options);
            default:
                throw new \Exception('Unknown geocoding provider');
        }
    }

    private function nominatimGeocode($address, $options) {
        $params = [
            'q' => $address,
            'format' => 'json',
            'limit' => $options['limit'],
            'countrycodes' => $options['countrycodes'],
            'addressdetails' => $options['addressdetails']
        ];

        $url = $this->providers['nominatim'] . '?' . http_build_query($params);

        $ch = curl_init();
        curl_setopt($ch, CURLOPT_URL, $url);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_USERAGENT, 'YourSaaSApp/1.0');
        curl_setopt($ch, CURLOPT_HTTPHEADER, ['Accept-Language: en']);

        $response = curl_exec($ch);
        curl_close($ch);

        $results = json_decode($response, true);

        return array_map(function ($result) {
            return [
                'lat' => $result['lat'],
                'lng' => $result['lon'],
                'address' => $result['display_name'],
                'type' => $result['type'],
                'importance' => $result['importance'],
                'details' => $result['address'] ?? []
            ];
        }, $results);
    }

    public function reverseGeocode($lat, $lng) {
        $url = "https://nominatim.openstreetmap.org/reverse?format=json&lat=$lat&lon=$lng";

        $ch = curl_init();
        curl_setopt($ch, CURLOPT_URL, $url);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_USERAGENT, 'YourSaaSApp/1.0');

        $response = curl_exec($ch);
        curl_close($ch);

        $result = json_decode($response, true);

        return [
            'address' => $result['display_name'],
            'details' => $result['address'] ?? [],
            'type' => $result['type'] ?? 'unknown'
        ];
    }

    public function batchGeocode($addresses, $delayMs = 1000) {
        $results = [];

        foreach ($addresses as $address) {
            $results[] = $this->geocode($address);
            usleep($delayMs * 1000);
        }

        return $results;
    }
}
```

```javascript
class Geocoder {
  constructor(map, options = {}) {
    this.map = map;
    this.options = {
      serviceUrl: "/api/geocode",
      reverseUrl: "/api/reverse-geocode",
      placeholder: "Search address...",
      ...options,
    };
    this.init();
  }

  init() {
    this.container = document.createElement("div");
    this.container.className = "geocoder-control";

    this.input = document.createElement("input");
    this.input.type = "text";
    this.input.placeholder = this.options.placeholder;
    this.input.className = "geocoder-input";

    this.results = document.createElement("div");
    this.results.className = "geocoder-results";

    this.container.appendChild(this.input);
    this.container.appendChild(this.results);

    L.DomUtil.addClass(this.container, "leaflet-control");
    L.DomEvent.disableClickPropagation(this.container);

    this.map.getContainer().appendChild(this.container);
    this.bindEvents();
  }

  bindEvents() {
    let timeout;
    this.input.addEventListener("input", (e) => {
      clearTimeout(timeout);
      timeout = setTimeout(() => {
        this.search(e.target.value);
      }, 300);
    });

    this.input.addEventListener("keypress", (e) => {
      if (e.key === "Enter") {
        this.search(e.target.value);
      }
    });

    document.addEventListener("click", (e) => {
      if (!this.container.contains(e.target)) {
        this.clearResults();
      }
    });
  }

  async search(query) {
    if (!query || query.length < 3) {
      this.clearResults();
      return;
    }

    try {
      const response = await fetch(
        `${this.options.serviceUrl}?q=${encodeURIComponent(query)}`,
      );
      const results = await response.json();
      this.displayResults(results);
    } catch (error) {
      console.error("Geocoding error:", error);
    }
  }

  displayResults(results) {
    this.clearResults();

    if (results.length === 0) {
      const noResults = document.createElement("div");
      noResults.className = "geocoder-no-results";
      noResults.textContent = "No results found";
      this.results.appendChild(noResults);
      return;
    }

    results.forEach((result) => {
      const item = document.createElement("div");
      item.className = "geocoder-result-item";
      item.innerHTML = `
                <strong>${result.address}</strong>
                <small>${result.type}</small>
            `;

      item.addEventListener("click", () => {
        this.selectResult(result);
      });

      this.results.appendChild(item);
    });
  }

  selectResult(result) {
    this.map.setView([result.lat, result.lng], 14);

    if (this.marker) {
      this.map.removeLayer(this.marker);
    }

    this.marker = L.marker([result.lat, result.lng])
      .addTo(this.map)
      .bindPopup(result.address)
      .openPopup();

    this.input.value = result.address;
    this.clearResults();

    this.map.fire("geocode:result", { result });
  }

  async reverseGeocode(lat, lng) {
    try {
      const response = await fetch(
        `${this.options.reverseUrl}?lat=${lat}&lng=${lng}`,
      );
      return await response.json();
    } catch (error) {
      console.error("Reverse geocoding error:", error);
      return null;
    }
  }

  clearResults() {
    this.results.innerHTML = "";
  }

  destroy() {
    this.container.remove();
  }
}
```
