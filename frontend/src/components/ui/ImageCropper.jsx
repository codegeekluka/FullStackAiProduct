import React, { useState, useCallback, useEffect } from 'react';
import Cropper from 'react-easy-crop';
import '../../styles/ui/ImageCropper.css';

const ImageCropper = ({ 
  imageSrc, 
  onCropComplete, 
  onCancel, 
  aspectRatio = 1, 
  cropShape = 'rect', 
  title = 'Crop Image' 
}) => {
  const [crop, setCrop] = useState({ x: 0, y: 0 });
  const [zoom, setZoom] = useState(1);
  const [croppedAreaPixels, setCroppedAreaPixels] = useState(null);

  // Debug logging
  useEffect(() => {
    console.log('ImageCropper - imageSrc:', imageSrc);
    console.log('ImageCropper - aspectRatio:', aspectRatio);
    console.log('ImageCropper - cropShape:', cropShape);
  }, [imageSrc, aspectRatio, cropShape]);

  const onCropCompleteInternal = useCallback((croppedArea, croppedAreaPixels) => {
    console.log('Crop complete - croppedArea:', croppedArea);
    console.log('Crop complete - croppedAreaPixels:', croppedAreaPixels);
    setCroppedAreaPixels(croppedAreaPixels);
  }, []);

  const getCroppedImg = useCallback(async () => {
    if (!croppedAreaPixels) {
      console.log('No cropped area pixels available');
      return null;
    }

    const image = new Image();
    image.src = imageSrc;

    return new Promise((resolve) => {
      image.onload = () => {
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');

        // For circular crops, we need to create a circular mask
        if (cropShape === 'circle') {
          // Generate higher resolution for better quality on large monitors
          const size = Math.min(croppedAreaPixels.width, croppedAreaPixels.height);
          const scale = 2; // 2x resolution for better quality
          canvas.width = size * scale;
          canvas.height = size * scale;

          // Enable high-quality rendering
          ctx.imageSmoothingEnabled = true;
          ctx.imageSmoothingQuality = 'high';

          // Create circular clipping path
          ctx.beginPath();
          ctx.arc(size * scale / 2, size * scale / 2, size * scale / 2, 0, 2 * Math.PI);
          ctx.clip();

          // Draw the cropped image at higher resolution
          ctx.drawImage(
            image,
            croppedAreaPixels.x,
            croppedAreaPixels.y,
            croppedAreaPixels.width,
            croppedAreaPixels.height,
            0,
            0,
            size * scale,
            size * scale
          );
        } else {
          // For rectangular crops - also generate higher resolution
          const scale = 2; // 2x resolution for better quality
          canvas.width = croppedAreaPixels.width * scale;
          canvas.height = croppedAreaPixels.height * scale;

          // Enable high-quality rendering
          ctx.imageSmoothingEnabled = true;
          ctx.imageSmoothingQuality = 'high';

          ctx.drawImage(
            image,
            croppedAreaPixels.x,
            croppedAreaPixels.y,
            croppedAreaPixels.width,
            croppedAreaPixels.height,
            0,
            0,
            croppedAreaPixels.width * scale,
            croppedAreaPixels.height * scale
          );
        }

        canvas.toBlob((blob) => {
          if (blob) {
            const file = new File([blob], 'cropped-image.jpg', { type: 'image/jpeg' });
            resolve(file);
          }
        }, 'image/jpeg', 0.95);
      };
    });
  }, [croppedAreaPixels, imageSrc, cropShape]);

  const handleCropConfirm = async () => {
    console.log('Apply crop clicked');
    console.log('Current croppedAreaPixels:', croppedAreaPixels);
    
    const croppedFile = await getCroppedImg();
    if (croppedFile) {
      console.log('Cropped file created:', croppedFile);
      onCropComplete(croppedFile);
    } else {
      console.log('Failed to create cropped file');
    }
  };

  // Don't render if no image source
  if (!imageSrc) {
    console.log('No image source provided');
    return null;
  }

  // Check if we can enable the apply button - only need valid crop area
  const canApplyCrop = croppedAreaPixels && 
    croppedAreaPixels.width > 0 && croppedAreaPixels.height > 0;

  console.log('Can apply crop:', canApplyCrop, {
    hasCroppedArea: !!croppedAreaPixels,
    cropWidth: croppedAreaPixels?.width,
    cropHeight: croppedAreaPixels?.height
  });

  return (
    <div className="image-cropper-overlay">
      <div className="image-cropper-modal">
        <div className="image-cropper-header">
          <h3>{title}</h3>
          <p>Drag to adjust the crop area</p>
        </div>
        
        <div className="image-cropper-content">
          <div className="crop-container">
            {imageSrc && (
              <Cropper
                image={imageSrc}
                crop={crop}
                zoom={zoom}
                aspect={aspectRatio}
                onCropChange={setCrop}
                onZoomChange={setZoom}
                onCropComplete={onCropCompleteInternal}
                cropShape={cropShape === 'circle' ? 'round' : 'rect'}
                showGrid={false}
                objectFit="contain"
                minZoom={0.5}
                maxZoom={3}
                style={{
                  containerStyle: {
                    width: '100%',
                    height: '100%',
                    backgroundColor: '#f0f0f0',
                    borderRadius: '12px'
                  }
                }}
              />
            )}
          </div>
        </div>

        <div className="image-cropper-actions">
          <button 
            className="crop-btn crop-btn-secondary" 
            onClick={onCancel}
          >
            Cancel
          </button>
          <button 
            className="crop-btn crop-btn-primary" 
            onClick={handleCropConfirm}
            disabled={!canApplyCrop}
          >
            Apply Crop
          </button>
        </div>
      </div>
    </div>
  );
};

export default ImageCropper;
