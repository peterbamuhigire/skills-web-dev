# 8) Measurement Tools

```javascript
// /public/js/measurement-tools.js
class MeasurementTools {
  constructor(map) {
    this.map = map;
    this.measurements = [];
    this.currentMeasurement = null;
    this.measurementLayer = L.layerGroup().addTo(map);
    this.isMeasuring = false;

    this.init();
  }

  init() {
    this.addControls();
    this.bindEvents();
  }

  addControls() {
    this.toolbar = L.control({ position: "topleft" });

    this.toolbar.onAdd = () => {
      const container = L.DomUtil.create("div", "measurement-toolbar");
      container.innerHTML = `
                <h4>Measurement Tools</h4>
                <div class="tool-buttons">
                    <button class="tool-btn" data-tool="distance">📏 Distance</button>
                    <button class="tool-btn" data-tool="area">📐 Area</button>
                    <button class="tool-btn" data-tool="radius">⭕ Radius</button>
                    <button class="tool-btn" data-tool="clear">🗑️ Clear</button>
                </div>
                <div class="measurement-results"></div>
                <div class="unit-selector">
                    <label><input type="radio" name="units" value="metric" checked> Metric</label>
                    <label><input type="radio" name="units" value="imperial"> Imperial</label>
                </div>
            `;

      L.DomEvent.disableClickPropagation(container);
      return container;
    };

    this.toolbar.addTo(this.map);

    document.querySelectorAll(".tool-btn").forEach((btn) => {
      btn.addEventListener("click", (e) => {
        const tool = e.target.dataset.tool;
        this.selectTool(tool);
      });
    });
  }

  selectTool(tool) {
    this.isMeasuring = true;
    this.currentTool = tool;

    if (this.tempLayer) {
      this.map.removeLayer(this.tempLayer);
    }

    document.querySelectorAll(".tool-btn").forEach((btn) => {
      btn.classList.toggle("active", btn.dataset.tool === tool);
    });

    switch (tool) {
      case "distance":
        this.startDistanceMeasurement();
        break;
      case "area":
        this.startAreaMeasurement();
        break;
      case "radius":
        this.startRadiusMeasurement();
        break;
      case "clear":
        this.clearMeasurements();
        break;
    }
  }

  startDistanceMeasurement() {
    this.currentMeasurement = {
      type: "distance",
      points: [],
      line: null,
      markers: [],
    };

    this.map.on("click", this.addDistancePoint.bind(this));
    this.showMessage(
      "Click to add points for distance measurement. Double-click to finish.",
    );
  }

  addDistancePoint(e) {
    const point = e.latlng;
    this.currentMeasurement.points.push(point);

    const marker = L.marker(point, {
      icon: L.divIcon({
        className: "measurement-point",
        html: `<div class="point-number">${this.currentMeasurement.points.length}</div>`,
        iconSize: [24, 24],
      }),
    }).addTo(this.measurementLayer);

    this.currentMeasurement.markers.push(marker);

    if (this.currentMeasurement.points.length > 1) {
      if (this.currentMeasurement.line) {
        this.map.removeLayer(this.currentMeasurement.line);
      }

      this.currentMeasurement.line = L.polyline(
        this.currentMeasurement.points,
        {
          color: "#3388ff",
          weight: 3,
          dashArray: "5, 10",
        },
      ).addTo(this.measurementLayer);

      this.updateDistanceDisplay();
    }

    let clickTimer;
    marker.on("click", () => {
      if (clickTimer) {
        clearTimeout(clickTimer);
        clickTimer = null;
        this.finishDistanceMeasurement();
      } else {
        clickTimer = setTimeout(() => {
          clickTimer = null;
        }, 300);
      }
    });
  }

  updateDistanceDisplay() {
    if (this.currentMeasurement.points.length < 2) return;

    let totalDistance = 0;
    for (let i = 1; i < this.currentMeasurement.points.length; i++) {
      const p1 = this.currentMeasurement.points[i - 1];
      const p2 = this.currentMeasurement.points[i];
      totalDistance += this.map.distance(p1, p2);
    }

    const units = document.querySelector('input[name="units"]:checked').value;
    const display = this.formatDistance(totalDistance, units);

    document.querySelector(".measurement-results").innerHTML = `
            <div class="distance-result">
                <strong>Distance:</strong> ${display.total}<br>
                <small>Segments: ${this.currentMeasurement.points.length - 1}</small>
            </div>
        `;

    if (this.currentMeasurement.line) {
      this.currentMeasurement.line.bindPopup(`
                <strong>Distance Measurement</strong><br>
                Total: ${display.total}<br>
                Segments: ${this.currentMeasurement.points.length - 1}<br>
                ${display.details ? `Details:<br>${display.details}` : ""}
            `);
    }
  }

  finishDistanceMeasurement() {
    if (this.currentMeasurement.points.length >= 2) {
      this.measurements.push({ ...this.currentMeasurement });

      if (this.currentMeasurement.line) {
        this.currentMeasurement.line.setStyle({
          dashArray: null,
          color: "#ff0000",
          weight: 2,
        });
        this.addDistanceLabel(this.currentMeasurement.line);
      }

      this.showMessage("Distance measurement saved.");
    }

    this.resetCurrentMeasurement();
    this.map.off("click", this.addDistancePoint);
  }

  startAreaMeasurement() {
    this.currentMeasurement = {
      type: "area",
      points: [],
      polygon: null,
      markers: [],
    };

    this.map.on("click", this.addAreaPoint.bind(this));
    this.showMessage("Click to add polygon vertices. Double-click to finish.");
  }

  addAreaPoint(e) {
    const point = e.latlng;
    this.currentMeasurement.points.push(point);

    const marker = L.marker(point, {
      icon: L.divIcon({
        className: "measurement-point",
        html: `<div class="point-number">${this.currentMeasurement.points.length}</div>`,
        iconSize: [24, 24],
      }),
    }).addTo(this.measurementLayer);

    this.currentMeasurement.markers.push(marker);

    if (this.currentMeasurement.points.length >= 3) {
      if (this.currentMeasurement.polygon) {
        this.map.removeLayer(this.currentMeasurement.polygon);
      }

      this.currentMeasurement.polygon = L.polygon(
        this.currentMeasurement.points,
        {
          color: "#3388ff",
          weight: 2,
          fillColor: "#3388ff",
          fillOpacity: 0.2,
          dashArray: "5, 10",
        },
      ).addTo(this.measurementLayer);

      this.updateAreaDisplay();
    }

    let clickTimer;
    marker.on("click", () => {
      if (clickTimer) {
        clearTimeout(clickTimer);
        clickTimer = null;
        this.finishAreaMeasurement();
      } else {
        clickTimer = setTimeout(() => {
          clickTimer = null;
        }, 300);
      }
    });
  }

  updateAreaDisplay() {
    if (this.currentMeasurement.points.length < 3) return;

    const area = L.GeometryUtil.geodesicArea(this.currentMeasurement.points);
    const units = document.querySelector('input[name="units"]:checked').value;
    const display = this.formatArea(area, units);

    document.querySelector(".measurement-results").innerHTML = `
            <div class="area-result">
                <strong>Area:</strong> ${display.total}<br>
                <small>Vertices: ${this.currentMeasurement.points.length}</small>
            </div>
        `;

    if (this.currentMeasurement.polygon) {
      this.currentMeasurement.polygon.bindPopup(`
                <strong>Area Measurement</strong><br>
                ${display.total}<br>
                ${display.details ? `Also: ${display.details}` : ""}
            `);
    }
  }

  finishAreaMeasurement() {
    if (this.currentMeasurement.points.length >= 3) {
      this.currentMeasurement.points.push(this.currentMeasurement.points[0]);

      if (this.currentMeasurement.polygon) {
        this.currentMeasurement.polygon.setLatLngs(
          this.currentMeasurement.points,
        );
        this.currentMeasurement.polygon.setStyle({
          dashArray: null,
          color: "#00aa00",
          fillColor: "#00aa00",
        });
        this.addAreaLabel(this.currentMeasurement.polygon);
      }

      this.measurements.push({ ...this.currentMeasurement });
      this.showMessage("Area measurement saved.");
    }

    this.resetCurrentMeasurement();
    this.map.off("click", this.addAreaPoint);
  }

  startRadiusMeasurement() {
    this.currentMeasurement = {
      type: "radius",
      center: null,
      radius: 0,
      circle: null,
      marker: null,
    };

    this.map.on("click", this.setRadiusCenter.bind(this));
    this.showMessage("Click to set center point, then drag to set radius.");
  }

  setRadiusCenter(e) {
    this.currentMeasurement.center = e.latlng;

    this.currentMeasurement.marker = L.marker(e.latlng, {
      icon: L.divIcon({
        className: "radius-center",
        html: '<div class="center-dot">•</div>',
        iconSize: [20, 20],
      }),
    }).addTo(this.measurementLayer);

    this.map.off("click", this.setRadiusCenter);
    this.map.on("mousemove", this.updateRadius.bind(this));
    this.map.on("click", this.finishRadiusMeasurement.bind(this));
  }

  updateRadius(e) {
    if (!this.currentMeasurement.center) return;

    const radius = this.map.distance(this.currentMeasurement.center, e.latlng);
    this.currentMeasurement.radius = radius;

    if (this.currentMeasurement.circle) {
      this.currentMeasurement.circle.setRadius(radius);
    } else {
      this.currentMeasurement.circle = L.circle(
        this.currentMeasurement.center,
        {
          radius: radius,
          color: "#3388ff",
          weight: 2,
          fillColor: "#3388ff",
          fillOpacity: 0.2,
          dashArray: "5, 10",
        },
      ).addTo(this.measurementLayer);
    }

    this.updateRadiusDisplay();
  }

  updateRadiusDisplay() {
    const radius = this.currentMeasurement.radius;
    const area = Math.PI * radius * radius;
    const units = document.querySelector('input[name="units"]:checked').value;

    const radiusDisplay = this.formatDistance(radius, units);
    const areaDisplay = this.formatArea(area, units);

    document.querySelector(".measurement-results").innerHTML = `
            <div class="radius-result">
                <strong>Radius:</strong> ${radiusDisplay.total}<br>
                <strong>Area:</strong> ${areaDisplay.total}
            </div>
        `;

    if (this.currentMeasurement.circle) {
      this.currentMeasurement.circle.bindPopup(`
                <strong>Circle Measurement</strong><br>
                Radius: ${radiusDisplay.total}<br>
                Area: ${areaDisplay.total}
            `);
    }
  }

  finishRadiusMeasurement() {
    if (this.currentMeasurement.circle) {
      this.currentMeasurement.circle.setStyle({
        dashArray: null,
        color: "#aa00aa",
        fillColor: "#aa00aa",
      });

      this.measurements.push({ ...this.currentMeasurement });
      this.showMessage("Radius measurement saved.");
    }

    this.resetCurrentMeasurement();
    this.map.off("mousemove", this.updateRadius);
    this.map.off("click", this.finishRadiusMeasurement);
  }

  formatDistance(meters, unitSystem) {
    if (unitSystem === "imperial") {
      const miles = meters / 1609.34;
      const feet = meters * 3.28084;

      if (miles >= 0.1) {
        return {
          total: `${miles.toFixed(2)} miles`,
          details: `${feet.toFixed(0)} feet`,
        };
      }
      return {
        total: `${feet.toFixed(0)} feet`,
        details: `${miles.toFixed(3)} miles`,
      };
    }

    const km = meters / 1000;
    if (km >= 1) {
      return {
        total: `${km.toFixed(2)} km`,
        details: `${meters.toFixed(0)} meters`,
      };
    }
    return {
      total: `${meters.toFixed(0)} meters`,
      details: `${km.toFixed(3)} km`,
    };
  }

  formatArea(squareMeters, unitSystem) {
    if (unitSystem === "imperial") {
      const acres = squareMeters / 4046.86;
      const squareFeet = squareMeters * 10.7639;

      if (acres >= 0.1) {
        return {
          total: `${acres.toFixed(2)} acres`,
          details: `${squareFeet.toFixed(0)} ft²`,
        };
      }
      return {
        total: `${squareFeet.toFixed(0)} ft²`,
        details: `${acres.toFixed(3)} acres`,
      };
    }

    const hectares = squareMeters / 10000;
    const squareKm = squareMeters / 1000000;

    if (hectares >= 1) {
      return {
        total: `${hectares.toFixed(2)} hectares`,
        details: `${squareMeters.toFixed(0)} m²`,
      };
    }
    if (squareKm >= 1) {
      return {
        total: `${squareKm.toFixed(2)} km²`,
        details: `${hectares.toFixed(1)} hectares`,
      };
    }
    return {
      total: `${squareMeters.toFixed(0)} m²`,
      details: `${hectares.toFixed(3)} hectares`,
    };
  }

  addDistanceLabel(line) {
    const latlngs = line.getLatLngs();
    const midIndex = Math.floor(latlngs.length / 2);
    const midpoint = latlngs[midIndex];

    const totalDistance = this.measurements[
      this.measurements.length - 1
    ].points.reduce(
      (sum, point, i, arr) =>
        i === 0 ? 0 : sum + this.map.distance(arr[i - 1], point),
      0,
    );

    const units = document.querySelector('input[name="units"]:checked').value;
    const display = this.formatDistance(totalDistance, units);

    L.marker(midpoint, {
      icon: L.divIcon({
        className: "distance-label",
        html: `<div class="label">${display.total}</div>`,
        iconSize: [100, 30],
      }),
      interactive: false,
    }).addTo(this.measurementLayer);
  }

  addAreaLabel(polygon) {
    const bounds = polygon.getBounds();
    const center = bounds.getCenter();

    const area = L.GeometryUtil.geodesicArea(polygon.getLatLngs()[0]);
    const units = document.querySelector('input[name="units"]:checked').value;
    const display = this.formatArea(area, units);

    L.marker(center, {
      icon: L.divIcon({
        className: "area-label",
        html: `<div class="label">${display.total}</div>`,
        iconSize: [120, 40],
      }),
      interactive: false,
    }).addTo(this.measurementLayer);
  }

  clearMeasurements() {
    if (confirm("Clear all measurements?")) {
      this.measurementLayer.clearLayers();
      this.measurements = [];
      this.currentMeasurement = null;
      this.isMeasuring = false;
      document.querySelector(".measurement-results").innerHTML = "";

      document.querySelectorAll(".tool-btn").forEach((btn) => {
        btn.classList.remove("active");
      });

      this.map.off("click");
      this.map.off("mousemove");

      this.showMessage("All measurements cleared.");
    }
  }

  resetCurrentMeasurement() {
    this.currentMeasurement = null;
    this.isMeasuring = false;
    this.currentTool = null;

    document.querySelectorAll(".tool-btn").forEach((btn) => {
      btn.classList.remove("active");
    });
  }

  showMessage(message) {
    let messageDiv = document.querySelector(".measurement-message");
    if (!messageDiv) {
      messageDiv = document.createElement("div");
      messageDiv.className = "measurement-message";
      document.querySelector(".measurement-toolbar").appendChild(messageDiv);
    }

    messageDiv.textContent = message;
    messageDiv.style.display = "block";

    setTimeout(() => {
      messageDiv.style.display = "none";
    }, 3000);
  }

  exportMeasurements() {
    const exportData = this.measurements.map((measurement, index) => {
      const data = {
        id: index + 1,
        type: measurement.type,
        created: new Date().toISOString(),
      };

      if (measurement.type === "distance") {
        data.points = measurement.points.map((p) => ({
          lat: p.lat,
          lng: p.lng,
        }));
        data.totalDistance = measurement.points.reduce(
          (sum, point, i, arr) =>
            i === 0 ? 0 : sum + this.map.distance(arr[i - 1], point),
          0,
        );
      } else if (measurement.type === "area") {
        data.points = measurement.points.map((p) => ({
          lat: p.lat,
          lng: p.lng,
        }));
        data.area = L.GeometryUtil.geodesicArea(measurement.points);
      } else if (measurement.type === "radius") {
        data.center = {
          lat: measurement.center.lat,
          lng: measurement.center.lng,
        };
        data.radius = measurement.radius;
        data.area = Math.PI * measurement.radius * measurement.radius;
      }

      return data;
    });

    this.downloadFile(
      JSON.stringify(exportData, null, 2),
      "measurements.json",
      "application/json",
    );
  }

  downloadFile(content, filename, mimeType) {
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);

    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    a.click();

    URL.revokeObjectURL(url);
  }
}
```
