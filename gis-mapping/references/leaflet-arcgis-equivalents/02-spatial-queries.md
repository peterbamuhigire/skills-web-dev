# 2) Spatial Queries (Server + Client)

### Server-Side (PHP)

```php
// /app/Services/SpatialQueryService.php
namespace App\Services;

use Illuminate\Support\Facades\DB;

class SpatialQueryService {
    public function findWithinRadius($lat, $lng, $radiusKm, $table = 'farmers') {
        $query = DB::table($table)
            ->select('*')
            ->selectRaw(
                "ST_Distance_Sphere(
                    point(longitude, latitude),
                    point(?, ?)
                ) as distance_meters",
                [$lng, $lat]
            )
            ->whereRaw(
                "ST_Distance_Sphere(
                    point(longitude, latitude),
                    point(?, ?)
                ) <= ?",
                [$lng, $lat, $radiusKm * 1000]
            )
            ->orderBy('distance_meters')
            ->get();

        return $query;
    }

    public function findWithinPolygon($polygonWKT, $table = 'farmers') {
        return DB::table($table)
            ->select('*')
            ->whereRaw(
                "ST_Within(
                    point(longitude, latitude),
                    ST_GeomFromText(?, 4326)
                )",
                [$polygonWKT]
            )
            ->get();
    }

    public function findInBuffer($lat, $lng, $bufferMeters) {
        $bufferWKT = "ST_Buffer(
            ST_GeomFromText('POINT($lng $lat)', 4326),
            $bufferMeters / 111000
        )";

        return DB::table('farmers as f')
            ->join('fields as fd', function ($join) use ($bufferWKT) {
                $join->whereRaw(
                    "ST_Intersects(
                        fd.boundary,
                        $bufferWKT
                    )"
                );
            })
            ->select('f.*', 'fd.field_name')
            ->get();
    }
}
```

### Client-Side (JavaScript + Turf)

```javascript
class SpatialQuery {
  static findNearest(point, features) {
    const pointFeature = turf.point([point.lng, point.lat]);
    const featureCollection = turf.featureCollection(
      features.map((f) =>
        turf.point(
          [f.geometry.coordinates[0], f.geometry.coordinates[1]],
          f.properties,
        ),
      ),
    );
    return turf.nearestPoint(pointFeature, featureCollection);
  }

  static spatialJoin(points, polygons) {
    const results = [];
    polygons.forEach((poly) => {
      const pointsInPoly = points.filter((point) =>
        turf.booleanPointInPolygon(
          turf.point([point.lng, point.lat]),
          poly.geometry,
        ),
      );
      if (pointsInPoly.length > 0) {
        results.push({
          polygon: poly,
          pointCount: pointsInPoly.length,
          points: pointsInPoly,
          center: turf.center(
            turf.featureCollection(
              pointsInPoly.map((p) => turf.point([p.lng, p.lat])),
            ),
          ),
        });
      }
    });
    return results;
  }

  static queryByAttribute(features, filters) {
    return features.filter((feature) =>
      Object.entries(filters).every(([key, value]) => {
        const featureValue = feature.properties[key];
        if (Array.isArray(value)) {
          return featureValue >= value[0] && featureValue <= value[1];
        }
        if (typeof value === "object" && value.operator) {
          switch (value.operator) {
            case ">":
              return featureValue > value.value;
            case "<":
              return featureValue < value.value;
            case "contains":
              return featureValue.includes(value.value);
            default:
              return featureValue == value.value;
          }
        }
        return featureValue == value;
      }),
    );
  }
}
```
