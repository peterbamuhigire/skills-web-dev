# Implementation Checklist

## Frontend

- [ ] Install Squoosh library
- [ ] Implement `imageCompressor.ts`
- [ ] Implement `useImageUpload.ts`
- [ ] Add file input with `accept="image/*"`
- [ ] Log compression stats
- [ ] Test Canvas fallback

## Backend

- [ ] Install Sharp
- [ ] Configure multer limits
- [ ] Add compression middleware
- [ ] Add validation middleware
- [ ] Add storage service
- [ ] Add routes
- [ ] Add error handling + logging

## Testing

- [ ] JPEG/PNG/WebP inputs
- [ ] Large images (>1MB)
- [ ] Edge aspect ratios
- [ ] Mobile devices
- [ ] Slow networks
