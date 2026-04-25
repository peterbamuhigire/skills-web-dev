# Storage Adapters

## S3 Storage

```typescript
import AWS from 'aws-sdk';
import crypto from 'crypto';

const s3 = new AWS.S3();

export async function saveImageToStorage(
  buffer: Buffer,
  originalFilename: string,
  mimeType: string
): Promise<string> {
  const hash = crypto.randomBytes(16).toString('hex');
  const ext = originalFilename.split('.').pop() || 'jpg';
  const filename = `${hash}.${ext}`;

  const params = {
    Bucket: process.env.AWS_BUCKET_NAME!,
    Key: `images/${filename}`,
    Body: buffer,
    ContentType: mimeType,
    CacheControl: 'max-age=31536000',
    Metadata: {
      'original-name': originalFilename,
      'compressed': 'true'
    }
  };

  const result = await s3.upload(params).promise();
  return result.Location;
}
```

## Local Storage

```typescript
import fs from 'fs/promises';
import path from 'path';
import crypto from 'crypto';

const UPLOAD_DIR = process.env.UPLOAD_DIR || '/var/uploads/images';

export async function saveImageToStorage(
  buffer: Buffer,
  originalFilename: string,
  mimeType: string
): Promise<string> {
  await fs.mkdir(UPLOAD_DIR, { recursive: true });

  const hash = crypto.randomBytes(16).toString('hex');
  const ext = originalFilename.split('.').pop() || 'jpg';
  const filename = `${hash}.${ext}`;
  const filepath = path.join(UPLOAD_DIR, filename);

  await fs.writeFile(filepath, buffer);
  return `/images/${filename}`;
}
```
