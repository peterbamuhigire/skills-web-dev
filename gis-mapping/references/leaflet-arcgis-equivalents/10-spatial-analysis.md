# 10) Spatial Analysis

```javascript
// /public/js/spatial-analysis.js
class SpatialAnalysis {
  constructor(map) {
    this.map = map;
    this.analysisLayer = L.layerGroup().addTo(map);
    this.results = [];
    this.init();
  }

  init() {
    this.addControls();
  }

  addControls() {
    this.panel = L.control({ position: "topright" });

    this.panel.onAdd = () => {
      const container = L.DomUtil.create("div", "spatial-analysis-panel");
      container.innerHTML = `
                <h4>Spatial Analysis</h4>
                <div class="analysis-tools">
                    <select id="analysisType">
                        <option value="nearest">Nearest Neighbor</option>
                        <option value="convexhull">Convex Hull</option>
                        <option value="centroid">Centroid</option>
                        <option value="voronoi">Voronoi Diagram</option>
                        <option value="delaunay">Delaunay Triangulation</option>
                        <option value="envelope">Bounding Envelope</option>
                        <option value="density">Point Density</option>
                        <option value="hotspot">Hotspot Analysis</option>
                    </select>
                    <button id="runAnalysis">Run Analysis</button>
                    <button id="clearAnalysis">Clear</button>
                </div>
                <div class="analysis-options" id="analysisOptions"></div>
                <div class="analysis-results"></div>
            `;

      setTimeout(() => {
        document
          .getElementById("analysisType")
          .addEventListener("change", (e) => {
            this.showOptions(e.target.value);
          });

        document.getElementById("runAnalysis").addEventListener("click", () => {
          this.runAnalysis();
        });

        document
          .getElementById("clearAnalysis")
          .addEventListener("click", () => {
            this.clearAnalysis();
          });

        this.showOptions("nearest");
      }, 100);

      return container;
    };

    this.panel.addTo(this.map);
  }
}
```
