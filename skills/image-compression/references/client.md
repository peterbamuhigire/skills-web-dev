# Client-Side Compression (Squoosh + Canvas)

## Dependencies

- `@squoosh/lib` (primary)
- Canvas API (fallback)

## Service: imageCompressor.ts

```typescript
import { ImageQuant, MozJPEG, WebP, Avif } from '@squoosh/lib';

export interface CompressionOptions {
  maxWidth: number;
  maxHeight: number;
  maxSize: number; // bytes
  quality: number; // 0-100
}

const DEFAULT_OPTIONS: CompressionOptions = {
  maxWidth: 1920,
  maxHeight: 1920,
  maxSize: 512 * 1024,
  quality: 75
};

export class ImageCompressor {
  static async compressImage(
    file: File,
    options: Partial<CompressionOptions> = {}
  ): Promise<Blob> {
    const settings = { ...DEFAULT_OPTIONS, ...options };

    try {
      return await this.compressWithSquoosh(file, settings);
    } catch (error) {
      console.warn('Squoosh failed, using Canvas fallback', error);
      return this.compressWithCanvas(file, settings);
    }
  }

  private static async compressWithSquoosh(
    file: File,
    options: CompressionOptions
  ): Promise<Blob> {
    const buffer = await file.arrayBuffer();
    const image = new ImageQuant();

    await image.decode(buffer);
    const { width, height } = image.decoded;

    const { newWidth, newHeight } = this.calculateDimensions(
      width,
      height,
      options.maxWidth,
      options.maxHeight
    );

    await image.resize({ width: newWidth, height: newHeight });

    let quality = options.quality;
    let compressedBuffer: ArrayBuffer;
    let compressed: any;

    while (quality > 30) {
      compressed = await image.encode({
        mozjpeg: {
          quality,
          progressive: true,
          optimize_coding: true
        }
      });

      compressedBuffer = compressed.mozjpeg;

      if (compressedBuffer.byteLength <= options.maxSize) {
        return new Blob([compressedBuffer], { type: 'image/jpeg' });
      }

      quality -= 5;
    }

    compressed = await image.encode({
      webp: {
        quality,
        method: 6
      }
    });

    compressedBuffer = compressed.webp;
    return new Blob([compressedBuffer], { type: 'image/webp' });
  }

  private static async compressWithCanvas(
    file: File,
    options: CompressionOptions
  ): Promise<Blob> {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();

      reader.onload = (event) => {
        const img = new Image();

        img.onload = () => {
          const { newWidth, newHeight } = this.calculateDimensions(
            img.width,
            img.height,
            options.maxWidth,
            options.maxHeight
          );

          const canvas = document.createElement('canvas');
          canvas.width = newWidth;
          canvas.height = newHeight;

          const ctx = canvas.getContext('2d');
          if (!ctx) reject(new Error('Canvas context unavailable'));

          ctx!.drawImage(img, 0, 0, newWidth, newHeight);

          let quality = options.quality / 100;

          canvas.toBlob(
            (blob) => {
              if (!blob) {
                reject(new Error('Canvas compression failed'));
                return;
              }

              if (blob.size > options.maxSize && quality > 0.3) {
                const lowerQuality = quality - 0.1;
                canvas.toBlob(
                  (retryBlob) => {
                    resolve(retryBlob || blob);
                  },
                  'image/jpeg',
                  lowerQuality
                );
              } else {
                resolve(blob);
              }
            },
            'image/jpeg',
            quality
          );
        };

        img.onerror = () => reject(new Error('Failed to load image'));
        img.src = event.target?.result as string;
      };

      reader.onerror = () => reject(new Error('Failed to read file'));
      reader.readAsDataURL(file);
    });
  }

  private static calculateDimensions(
    origWidth: number,
    origHeight: number,
    maxWidth: number,
    maxHeight: number
  ): { newWidth: number; newHeight: number } {
    if (origWidth <= maxWidth && origHeight <= maxHeight) {
      return { newWidth: origWidth, newHeight: origHeight };
    }

    let newWidth = origWidth;
    let newHeight = origHeight;

    if (origWidth > maxWidth) {
      newHeight = Math.round((origHeight * maxWidth) / origWidth);
      newWidth = maxWidth;
    }

    if (newHeight > maxHeight) {
      newWidth = Math.round((newWidth * maxHeight) / newHeight);
      newHeight = maxHeight;
    }

    return { newWidth, newHeight };
  }

  static getCompressionStats(original: File, compressed: Blob) {
    const originalKB = (original.size / 1024).toFixed(2);
    const compressedKB = (compressed.size / 1024).toFixed(2);
    const ratio = ((compressed.size / original.size) * 100).toFixed(1);
    const savedKB = ((original.size - compressed.size) / 1024).toFixed(2);

    return {
      originalSize: `${originalKB} KB`,
      compressedSize: `${compressedKB} KB`,
      ratio: `${ratio}%`,
      saved: `${savedKB} KB`
    };
  }
}
```

## React Hook: useImageUpload.ts

```typescript
import { useState } from 'react';
import { ImageCompressor } from './imageCompressor';

export function useImageUpload() {
  const [isCompressing, setIsCompressing] = useState(false);
  const [compressionStats, setCompressionStats] = useState<any>(null);

  const handleImageSelect = async (
    event: React.ChangeEvent<HTMLInputElement>
  ): Promise<Blob | null> => {
    const file = event.target.files?.[0];
    if (!file) return null;

    if (!file.type.startsWith('image/')) {
      console.error('Selected file is not an image');
      return null;
    }

    setIsCompressing(true);

    try {
      const compressed = await ImageCompressor.compressImage(file, {
        maxWidth: 1920,
        maxSize: 512 * 1024
      });

      const stats = ImageCompressor.getCompressionStats(file, compressed);
      setCompressionStats(stats);

      return compressed;
    } catch (error) {
      console.error('Image compression failed:', error);
      return file;
    } finally {
      setIsCompressing(false);
    }
  };

  return {
    handleImageSelect,
    isCompressing,
    compressionStats
  };
}
```
