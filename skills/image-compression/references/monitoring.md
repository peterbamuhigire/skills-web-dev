# Monitoring & Analytics

```typescript
export class CompressionAnalytics {
  static track(stats: {
    original: number;
    compressed: number;
    format: string;
    processingTime: number;
    method: 'squoosh' | 'canvas' | 'sharp';
  }) {
    fetch('/api/analytics/compression', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        timestamp: new Date(),
        ...stats,
        ratio: ((stats.compressed / stats.original) * 100).toFixed(1),
        saved: stats.original - stats.compressed
      })
    }).catch(console.error);
  }
}
```
