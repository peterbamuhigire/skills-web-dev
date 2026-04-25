# React Usage Example

```tsx
import React, { useRef } from 'react';
import { useImageUpload } from './useImageUpload';

export function ImageUploadComponent() {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const { handleImageSelect, isCompressing, compressionStats } = useImageUpload();
  const [previewUrl, setPreviewUrl] = React.useState<string>('');

  const handleFileChange = async (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    const compressed = await handleImageSelect(event);

    if (compressed) {
      const url = URL.createObjectURL(compressed);
      setPreviewUrl(url);

      await uploadImageToServer(compressed);
    }

    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const uploadImageToServer = async (blob: Blob) => {
    const formData = new FormData();
    formData.append('image', blob, 'image.jpg');

    const response = await fetch('/api/upload/image', {
      method: 'POST',
      body: formData
    });

    if (!response.ok) {
      throw new Error('Upload failed');
    }
  };

  return (
    <div className="image-upload-container">
      <input
        ref={fileInputRef}
        type="file"
        accept="image/*"
        onChange={handleFileChange}
        disabled={isCompressing}
        style={{ display: 'none' }}
      />

      <button
        onClick={() => fileInputRef.current?.click()}
        disabled={isCompressing}
      >
        {isCompressing ? 'Compressing...' : 'Upload Image'}
      </button>

      {previewUrl && (
        <div className="preview-section">
          <img src={previewUrl} alt="Preview" style={{ maxWidth: '100%' }} />
          {compressionStats && (
            <p className="compression-info">
              Compressed from {compressionStats.originalSize} to{' '}
              {compressionStats.compressedSize} ({compressionStats.ratio})
            </p>
          )}
        </div>
      )}
    </div>
  );
}
```
