# 4) Buffering & Zone Analysis

```javascript
class BufferAnalysis {
  static createBuffer(geometry, distance, units = "kilometers") {
    if (!geometry) return null;

    let geojson;

    if (geometry.type) {
      geojson = geometry;
    } else if (geometry.getLatLng) {
      const latlng = geometry.getLatLng();
      geojson = turf.point([latlng.lng, latlng.lat]);
    } else if (geometry.getLatLngs) {
      const coordinates = this.leafletToGeoJSON(geometry);
      if (geometry instanceof L.Polygon) {
        geojson = turf.polygon(coordinates);
      } else {
        geojson = turf.lineString(coordinates[0]);
      }
    }

    if (!geojson) return null;

    const buffer = turf.buffer(geojson, distance, { units: units });
    const area = turf.area(buffer);
    const areaKm2 = area / 1000000;

    return {
      geometry: buffer,
      area: {
        squareMeters: Math.round(area),
        squareKilometers: Math.round(areaKm2 * 100) / 100,
        acres: Math.round((area / 4046.86) * 100) / 100,
      },
      radius: distance,
      units: units,
    };
  }

  static findIntersections(buffer, features) {
    const intersections = [];

    features.forEach((feature) => {
      if (feature.geometry && buffer.geometry) {
        const intersection = turf.intersect(feature.geometry, buffer.geometry);

        if (intersection) {
          const area = turf.area(intersection);
          const percentage = (area / turf.area(feature.geometry)) * 100;

          intersections.push({
            feature: feature,
            intersection: intersection,
            area: area,
            percentage: Math.round(percentage * 100) / 100,
            centroid: turf.centroid(intersection),
          });
        }
      }
    });

    return intersections;
  }

  static createServiceAreas(facilities, distances) {
    const serviceAreas = [];

    facilities.forEach((facility) => {
      distances.forEach((distance) => {
        const buffer = this.createBuffer(facility, distance);

        if (buffer) {
          serviceAreas.push({
            facility: facility,
            distance: distance,
            buffer: buffer,
            color: this.getColorForDistance(distance),
          });
        }
      });
    });

    const merged = this.mergeBuffers(
      serviceAreas.map((sa) => sa.buffer.geometry),
    );

    return {
      individualAreas: serviceAreas,
      mergedArea: merged,
      totalCoverage: this.calculateCoverage(merged),
    };
  }

  static calculateCoverage(geometry, studyArea) {
    if (!studyArea) {
      const bounds = map.getBounds();
      const sw = bounds.getSouthWest();
      const ne = bounds.getNorthEast();
      studyArea = turf.bboxPolygon([sw.lng, sw.lat, ne.lng, ne.lat]);
    }

    const intersection = turf.intersect(geometry, studyArea);
    if (!intersection) return 0;

    const coverageArea = turf.area(intersection);
    const totalArea = turf.area(studyArea);

    return (coverageArea / totalArea) * 100;
  }

  static leafletToGeoJSON(layer) {
    if (layer.toGeoJSON) {
      return layer.toGeoJSON();
    }

    if (layer.getLatLngs) {
      const latlngs = layer.getLatLngs();
      return latlngs.map((ll) => [ll.lng, ll.lat]);
    }

    return null;
  }

  static mergeBuffers(geometries) {
    if (geometries.length === 0) return null;

    let merged = geometries[0];

    for (let i = 1; i < geometries.length; i++) {
      merged = turf.union(merged, geometries[i]);
    }

    return merged;
  }

  static getColorForDistance(distance) {
    const colors = [
      { dist: 1, color: "#00ff00" },
      { dist: 5, color: "#ffff00" },
      { dist: 10, color: "#ff9900" },
      { dist: 20, color: "#ff0000" },
    ];

    for (let i = 0; i < colors.length; i++) {
      if (distance <= colors[i].dist) {
        return colors[i].color;
      }
    }

    return "#ff0000";
  }
}
```
