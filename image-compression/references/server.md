# Server-Side Compression (Sharp)

## Middleware: imageUploadMiddleware.ts

```typescript
import sharp from 'sharp';
import { Request, Response, NextFunction } from 'express';
import multer from 'multer';

export const upload = multer({
  storage: multer.memoryStorage(),
  fileFilter: (req, file, cb) => {
    if (file.mimetype.startsWith('image/')) cb(null, true);
    else cb(new Error('Only image files allowed'));
  },
  limits: { fileSize: 10 * 1024 * 1024 }
});

export const compressImageMiddleware = async (
  req: Request,
  res: Response,
  next: NextFunction
) => {
  if (!req.file) return res.status(400).json({ error: 'No image file provided' });

  try {
    const startTime = Date.now();
    const originalSize = req.file.size;

    const compressedBuffer = await sharp(req.file.buffer)
      .resize(1920, 1920, {
        fit: 'inside',
        withoutEnlargement: true
      })
      .jpeg({
        quality: 75,
        progressive: true,
        mozjpeg: true,
        optimizeScans: true
      })
      .toBuffer();

    let finalBuffer = compressedBuffer;

    if (finalBuffer.length > 512 * 1024) {
      finalBuffer = await sharp(req.file.buffer)
        .resize(1920, 1920, {
          fit: 'inside',
          withoutEnlargement: true
        })
        .jpeg({
          quality: 60,
          progressive: true,
          mozjpeg: true,
          optimizeScans: true
        })
        .toBuffer();

      if (finalBuffer.length > 512 * 1024) {
        return res.status(413).json({
          error: 'Image too large even after compression',
          details: {
            original: originalSize,
            compressed: finalBuffer.length,
            maxAllowed: 512 * 1024
          }
        });
      }
    }

    req.file.buffer = finalBuffer;
    req.file.size = finalBuffer.length;

    (req as any).compressionStats = {
      original: originalSize,
      compressed: finalBuffer.length,
      ratio: ((finalBuffer.length / originalSize) * 100).toFixed(1),
      saved: originalSize - finalBuffer.length,
      processingTime: Date.now() - startTime
    };

    next();
  } catch (error) {
    console.error('Image compression error:', error);
    res.status(500).json({ error: 'Image processing failed' });
  }
};

export const validateImageDimensions = async (
  req: Request,
  res: Response,
  next: NextFunction
) => {
  if (!req.file) return res.status(400).json({ error: 'No image file provided' });

  try {
    const metadata = await sharp(req.file.buffer).metadata();

    if ((metadata.width || 0) < 200 || (metadata.height || 0) < 200) {
      return res.status(400).json({
        error: 'Image too small',
        minDimensions: '200x200'
      });
    }

    next();
  } catch (error) {
    console.error('Dimension validation error:', error);
    res.status(400).json({ error: 'Invalid image format' });
  }
};
```

## Routes: imageRoutes.ts

```typescript
import express from 'express';
import { upload, compressImageMiddleware, validateImageDimensions } from '../middleware/imageUploadMiddleware';
import { saveImageToStorage } from '../services/storageService';

const router = express.Router();

router.post(
  '/api/upload/image',
  upload.single('image'),
  compressImageMiddleware,
  validateImageDimensions,
  async (req, res) => {
    try {
      if (!req.file) return res.status(400).json({ error: 'No image file provided' });

      const savedImageUrl = await saveImageToStorage(
        req.file.buffer,
        req.file.originalname,
        req.file.mimetype
      );

      const stats = (req as any).compressionStats;
      res.json({ success: true, url: savedImageUrl, compression: stats });
    } catch (error) {
      console.error('Image upload error:', error);
      res.status(500).json({ error: 'Failed to save image' });
    }
  }
);

export default router;
```
