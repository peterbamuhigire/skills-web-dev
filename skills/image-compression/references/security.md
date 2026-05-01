# Security Checks

```typescript
export function validateImageFile(file: File): {
  valid: boolean;
  error?: string;
} {
  const allowedMimes = ['image/jpeg', 'image/png', 'image/webp', 'image/gif'];
  if (!allowedMimes.includes(file.type)) {
    return {
      valid: false,
      error: 'Invalid image format. Allowed: JPEG, PNG, WebP, GIF'
    };
  }

  const maxPreCompressionSize = 20 * 1024 * 1024;
  if (file.size > maxPreCompressionSize) {
    return {
      valid: false,
      error: `File too large. Max: ${maxPreCompressionSize / 1024 / 1024}MB`
    };
  }

  return { valid: true };
}
```
