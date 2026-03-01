import React, { useState, useRef, useContext } from 'react';
import axios from 'axios';
import ImageCropper from '../ui/ImageCropper';
import { AuthContext } from '../../contexts/AuthContext';
import { API_BASE_URL } from '../../config/api';
import '../../styles/onboarding/ProfileStep.css';

const ProfileSection = ({ formData, updateFormData }) => {
  const { refreshUserProfile } = useContext(AuthContext);
  const [profileImage, setProfileImage] = useState(formData.profile_picture_url);
  const [heroImage, setHeroImage] = useState(formData.hero_image_url);
  const [uploadingProfile, setUploadingProfile] = useState(false);
  const [uploadingHero, setUploadingHero] = useState(false);
  const [showProfileCropper, setShowProfileCropper] = useState(false);
  const [showHeroCropper, setShowHeroCropper] = useState(false);
  const [tempImageSrc, setTempImageSrc] = useState(null);
  const [tempImageType, setTempImageType] = useState(null);
  
  const profileInputRef = useRef();
  const heroInputRef = useRef();
  const token = localStorage.getItem('token');

  // Helper function to construct full image URL
  const getImageUrl = (relativeUrl) => {
    if (!relativeUrl) return null;
    // If it's already a full URL, return as is
    if (relativeUrl.startsWith('http')) return relativeUrl;
    // Otherwise, prepend the backend URL
    return `${API_BASE_URL}${relativeUrl}`;
  };

  const handleFileSelect = (event, type) => {
    const file = event.target.files[0];
    if (!file) return;

    // Validate file type
    if (!file.type.startsWith('image/')) {
      alert('Please select an image file');
      return;
    }

    // Create a temporary URL for the cropper
    const tempUrl = URL.createObjectURL(file);
    setTempImageSrc(tempUrl);
    setTempImageType(type);
    
    // Show the appropriate cropper
    if (type === 'profile') {
      setShowProfileCropper(true);
    } else {
      setShowHeroCropper(true);
    }
  };

  const handleCropComplete = async (croppedFile) => {
    if (tempImageType === 'profile') {
      await uploadProfileImage(croppedFile);
      setShowProfileCropper(false);
    } else {
      await uploadHeroImage(croppedFile);
      setShowHeroCropper(false);
    }
    
    // Clean up
    if (tempImageSrc) {
      URL.revokeObjectURL(tempImageSrc);
      setTempImageSrc(null);
      setTempImageType(null);
    }
  };

  const handleCropCancel = () => {
    setShowProfileCropper(false);
    setShowHeroCropper(false);
    
    // Clean up
    if (tempImageSrc) {
      URL.revokeObjectURL(tempImageSrc);
      setTempImageSrc(null);
      setTempImageType(null);
    }
  };

  const uploadProfileImage = async (file) => {
    setUploadingProfile(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post(`${API_BASE_URL}/users/me/upload-profile-picture`, formData, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'multipart/form-data'
        }
      });
      
      const fullImageUrl = getImageUrl(response.data.profile_picture_url);
      setProfileImage(fullImageUrl);
      updateFormData({ profile_picture_url: response.data.profile_picture_url });
      
      // Refresh user profile in AuthContext to update navbar
      await refreshUserProfile();
    } catch (error) {
      console.error('Error uploading profile picture:', error);
      alert('Failed to upload profile picture. Please try again.');
    } finally {
      setUploadingProfile(false);
    }
  };

  const uploadHeroImage = async (file) => {
    setUploadingHero(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post(`${API_BASE_URL}/users/me/upload-hero-image`, formData, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'multipart/form-data'
        }
      });
      
      const fullImageUrl = getImageUrl(response.data.hero_image_url);
      setHeroImage(fullImageUrl);
      updateFormData({ hero_image_url: response.data.hero_image_url });
    } catch (error) {
      console.error('Error uploading hero image:', error);
      alert('Failed to upload hero image. Please try again.');
    } finally {
      setUploadingHero(false);
    }
  };

  const triggerProfileUpload = () => {
    profileInputRef.current?.click();
  };

  const triggerHeroUpload = () => {
    heroInputRef.current?.click();
  };

  const handleInputChange = (field, value) => {
    updateFormData({ [field]: value });
  };

  // Get the full URLs for display
  const displayProfileImage = getImageUrl(profileImage || formData.profile_picture_url);
  const displayHeroImage = getImageUrl(heroImage || formData.hero_image_url);

  return (
    <>
      {/* Profile Picture Upload */}
      <div className="form-group">
        <label className="form-group__label">Profile Picture</label>
        <div className="profile-step__upload">
          <div 
            className={`upload-area upload-area--profile ${displayProfileImage ? 'upload-area--has-image' : ''}`}
            onClick={triggerProfileUpload}
          >
            {displayProfileImage ? (
              <img src={displayProfileImage} alt="Profile" className="upload-area__image" />
            ) : (
              <div className="upload-area__placeholder">
                <div className="upload-area__icon">👤</div>
                <div className="upload-area__text">Click to upload</div>
              </div>
            )}
          </div>
          {uploadingProfile && <div className="upload-area__hint">Uploading...</div>}
        </div>
        <input
          ref={profileInputRef}
          type="file"
          accept="image/*"
          onChange={(e) => handleFileSelect(e, 'profile')}
          style={{ display: 'none' }}
        />
      </div>

      {/* Hero Image Upload */}
      <div className="form-group">
        <label className="form-group__label">Cover Photo</label>
        <div className="profile-step__upload">
          <div 
            className={`upload-area upload-area--hero ${displayHeroImage ? 'upload-area--has-image' : ''}`}
            onClick={triggerHeroUpload}
          >
            {displayHeroImage ? (
              <img src={displayHeroImage} alt="Hero" className="upload-area__image" />
            ) : (
              <div className="upload-area__placeholder">
                <div className="upload-area__icon">🖼️</div>
                <div className="upload-area__text">Click to upload</div>
              </div>
            )}
          </div>
          {uploadingHero && <div className="upload-area__hint">Uploading...</div>}
        </div>
        <input
          ref={heroInputRef}
          type="file"
          accept="image/*"
          onChange={(e) => handleFileSelect(e, 'hero')}
          style={{ display: 'none' }}
        />
      </div>

      {/* Name and Age Inputs */}
      <div className="form-row">
        <div className="form-group">
          <label className="form-group__label">First Name</label>
          <input
            type="text"
            className="form-group__input"
            value={formData.firstname || ''}
            onChange={(e) => handleInputChange('firstname', e.target.value)}
            placeholder="Enter your first name"
          />
        </div>
        <div className="form-group">
          <label className="form-group__label">Last Name</label>
          <input
            type="text"
            className="form-group__input"
            value={formData.lastname || ''}
            onChange={(e) => handleInputChange('lastname', e.target.value)}
            placeholder="Enter your last name"
          />
        </div>
      </div>

      <div className="form-group">
        <label className="form-group__label">Age</label>
        <input
          type="number"
          className="form-group__input"
          value={formData.age || ''}
          onChange={(e) => handleInputChange('age', e.target.value)}
          placeholder="Enter your age"
          min="0"
          max="116"
        />
      </div>

      {/* Image Croppers */}
      {showProfileCropper && tempImageSrc && (
        <ImageCropper
          imageSrc={tempImageSrc}
          onCropComplete={handleCropComplete}
          onCancel={handleCropCancel}
          aspectRatio={1}
          cropShape="circle"
          title="Crop Profile Picture"
        />
      )}

      {showHeroCropper && tempImageSrc && (
        <ImageCropper
          imageSrc={tempImageSrc}
          onCropComplete={handleCropComplete}
          onCancel={handleCropCancel}
          aspectRatio={16/9}
          cropShape="rect"
          title="Crop Cover Photo"
        />
      )}
    </>
  );
};

export default ProfileSection;
