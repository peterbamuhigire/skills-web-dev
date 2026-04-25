# 9) Clustering & Aggregation

```javascript
// /public/js/smart-clustering.js
class SmartClustering {
  constructor(map, options = {}) {
    this.map = map;
    this.options = {
      chunkedLoading: true,
      chunkInterval: 100,
      maxClusterRadius: 80,
      spiderfyOnMaxZoom: true,
      showCoverageOnHover: false,
      zoomToBoundsOnClick: true,
      disableClusteringAtZoom: 18,
      ...options,
    };

    this.clusterLayer = null;
    this.data = [];
    this.filters = {};
    this.heatmapLayer = null;

    this.init();
  }

  init() {
    this.createClusterLayer();
    this.addControls();
  }

  createClusterLayer() {
    this.clusterLayer = L.markerClusterGroup({
      chunkedLoading: this.options.chunkedLoading,
      chunkInterval: this.options.chunkInterval,
      maxClusterRadius: this.options.maxClusterRadius,
      spiderfyOnMaxZoom: this.options.spiderfyOnMaxZoom,
      showCoverageOnHover: this.options.showCoverageOnHover,
      zoomToBoundsOnClick: this.options.zoomToBoundsOnClick,
      disableClusteringAtZoom: this.options.disableClusteringAtZoom,
      iconCreateFunction: this.createClusterIcon.bind(this),
      spiderfyDistanceMultiplier: 1.5,
    });

    this.map.addLayer(this.clusterLayer);

    this.clusterLayer.on("clusterclick", this.handleClusterClick.bind(this));
    this.clusterLayer.on(
      "clustermouseover",
      this.handleClusterHover.bind(this),
    );
    this.clusterLayer.on("clustermouseout", this.handleClusterOut.bind(this));
  }

  createClusterIcon(cluster) {
    const count = cluster.getChildCount();
    const size = this.getClusterSize(count);
    const markers = cluster.getAllChildMarkers();
    const avgValue = this.calculateAverage(markers, "value");

    return L.divIcon({
      html: `
                <div class="cluster-icon cluster-${size}">
                    <div class="cluster-count">${count}</div>
                    ${avgValue ? `<div class="cluster-avg">${avgValue.toFixed(1)}</div>` : ""}
                </div>
            `,
      className: `marker-cluster marker-cluster-${size}`,
      iconSize: L.point(40, 40),
    });
  }

  getClusterSize(count) {
    if (count < 10) return "small";
    if (count < 50) return "medium";
    if (count < 100) return "large";
    return "xlarge";
  }

  calculateAverage(markers, property) {
    const values = markers
      .map((m) => m.options[property])
      .filter((v) => v !== undefined);
    if (values.length === 0) return null;
    const sum = values.reduce((a, b) => a + b, 0);
    return sum / values.length;
  }

  handleClusterClick(cluster) {
    const markers = cluster.getAllChildMarkers();
    const bounds = L.latLngBounds(markers.map((m) => m.getLatLng()));

    if (
      markers.length > 20 &&
      this.map.getZoom() >= this.options.disableClusteringAtZoom - 1
    ) {
      cluster.spiderfy();
    } else {
      this.map.fitBounds(bounds, { padding: [50, 50] });
    }
  }

  handleClusterHover(cluster) {
    const markers = cluster.getAllChildMarkers();
    const bounds = L.latLngBounds(markers.map((m) => m.getLatLng()));

    if (!this.highlightLayer) {
      this.highlightLayer = L.rectangle(bounds, {
        color: "#ff0000",
        weight: 2,
        fillOpacity: 0.1,
      }).addTo(this.map);
    } else {
      this.highlightLayer.setBounds(bounds);
    }
  }

  handleClusterOut() {
    if (this.highlightLayer) {
      this.map.removeLayer(this.highlightLayer);
      this.highlightLayer = null;
    }
  }
}
```
