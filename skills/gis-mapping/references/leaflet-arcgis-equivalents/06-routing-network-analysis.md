# 6) Routing & Network Analysis

```javascript
class RoutingService {
  constructor(map, options = {}) {
    this.map = map;
    this.options = {
      serviceUrl: "https://router.project-osrm.org/route/v1",
      profile: "driving",
      alternatives: false,
      steps: true,
      overview: "full",
      geometries: "geojson",
      ...options,
    };

    this.routeLayer = L.layerGroup().addTo(map);
    this.waypoints = [];
    this.currentRoute = null;
  }

  async calculateRoute(waypoints) {
    if (waypoints.length < 2) {
      throw new Error("At least two waypoints required");
    }

    this.waypoints = waypoints;

    const coordinates = waypoints.map((w) => `${w.lng},${w.lat}`).join(";");

    const url =
      `${this.options.serviceUrl}/${this.options.profile}/${coordinates}?` +
      `alternatives=${this.options.alternatives}&` +
      `steps=${this.options.steps}&` +
      `overview=${this.options.overview}&` +
      `geometries=${this.options.geometries}`;

    const response = await fetch(url);
    const data = await response.json();

    if (data.code !== "Ok") {
      throw new Error(data.message || "Routing failed");
    }

    this.currentRoute = data.routes[0];
    this.displayRoute(this.currentRoute);
    return this.currentRoute;
  }

  displayRoute(route) {
    this.routeLayer.clearLayers();

    L.geoJSON(route.geometry, {
      style: { color: "#3388ff", weight: 6, opacity: 0.7 },
    }).addTo(this.routeLayer);
  }
}
```
