# 1) Basic Mapping & Visualization

### Map Manager (PHP Example)

```php
// /app/Services/MapManager.php
namespace App\Services;

class MapManager {
    private $config;

    public function __construct() {
        $this->config = config('gis');
    }

    public function renderMap($elementId, $options = []) {
        $defaults = [
            'center' => [40.7128, -74.0060],
            'zoom' => 10,
            'layers' => [],
            'controls' => true,
            'attribution' => true
        ];

        $options = array_merge($defaults, $options);

        return view('components.map', [
            'elementId' => $elementId,
            'options' => $options,
            'config' => $this->config
        ])->render();
    }

    public function getMapScript($elementId, $options = []) {
        return <<<EOT
        <script>
        window.addEventListener('DOMContentLoaded', function() {
            window.map_{$elementId} = L.map('{$elementId}').setView(
                [{$options['center'][0]}, {$options['center'][1]}],
                {$options['zoom']}
            );

            var baseLayers = {
                "Street Map": L.tileLayer(
                    '{$this->config['providers']['osm']['url']}', {
                        attribution: '{$this->config['providers']['osm']['attribution']}',
                        maxZoom: {$this->config['providers']['osm']['maxZoom']}
                    }
                ),
                "Satellite": L.tileLayer(
                    'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
                        attribution: 'Tiles © Esri',
                        maxZoom: 19
                    }
                )
            };

            baseLayers["Street Map"].addTo(window.map_{$elementId});

            if (Object.keys(baseLayers).length > 1) {
                L.control.layers(baseLayers).addTo(window.map_{$elementId});
            }

            if ({$options['controls']}) {
                L.control.scale().addTo(window.map_{$elementId});
            }

            if ({$options['attribution']}) {
                L.control.attribution({prefix: false})
                    .addAttribution('{$this->config['providers']['osm']['attribution']}')
                    .addTo(window.map_{$elementId});
            }
        });
        </script>
EOT;
    }
}
```

### Usage Example

```php
use App\Services\MapManager;

$mapManager = new MapManager();

echo $mapManager->renderMap('farmerMap', [
    'center' => [$farmer->lat, $farmer->lng],
    'zoom' => 14
]);
```
