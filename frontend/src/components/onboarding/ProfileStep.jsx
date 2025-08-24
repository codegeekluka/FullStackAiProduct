import React, { useState, useRef } from 'react';
import axios from 'axios';
import '../../styles/onboarding/shared.css';
import '../../styles/onboarding/ProfileStep.css';

const ProfileStep = ({ formData, updateFormData, onNext, onSkip, loading }) => {
  const [profileImage, setProfileImage] = useState(formData.profile_picture_url);
  const [heroImage, setHeroImage] = useState(formData.hero_image_url);
  const [uploadingProfile, setUploadingProfile] = useState(false);
  const [uploadingHero, setUploadingHero] = useState(false);
  
  const profileInputRef = useRef();
  const heroInputRef = useRef();
  const token = localStorage.getItem('token');

  const handleInputChange = (field, value) => {
    updateFormData({ [field]: value });
  };

  const handleProfileImageUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setUploadingProfile(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post('http://localhost:8000/users/me/upload-profile-picture', formData, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'multipart/form-data'
        }
      });
      
      setProfileImage(response.data.profile_picture_url);
      updateFormData({ profile_picture_url: response.data.profile_picture_url });
    } catch (error) {
      console.error('Error uploading profile picture:', error);
    } finally {
      setUploadingProfile(false);
    }
  };

  const handleHeroImageUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setUploadingHero(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post('http://localhost:8000/users/me/upload-hero-image', formData, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'multipart/form-data'
        }
      });
      
      setHeroImage(response.data.hero_image_url);
      updateFormData({ hero_image_url: response.data.hero_image_url });
    } catch (error) {
      console.error('Error uploading hero image:', error);
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

  return (
            <div className="modal onboarding-modal">
      <div className="modal__content">
        <div className="modal__body">
          {/* Profile Picture Upload */}
          <div className="form-group">
            <label className="form-group__label">Profile Picture</label>
            <div className="profile-step__upload">
              <div 
                className={`upload-area upload-area--profile ${profileImage ? 'upload-area--has-image' : ''}`}
                onClick={triggerProfileUpload}
              >
                {profileImage ? (
                  <img src={profileImage} alt="Profile" className="upload-area__image" />
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
              onChange={handleProfileImageUpload}
              style={{ display: 'none' }}
            />
          </div>

          {/* Hero Image Upload */}
          <div className="form-group">
            <label className="form-group__label">Cover Photo</label>
            <div className="profile-step__upload">
              <div 
                className={`upload-area upload-area--hero ${heroImage ? 'upload-area--has-image' : ''}`}
                onClick={triggerHeroUpload}
              >
                {heroImage ? (
                  <img src={heroImage} alt="Hero" className="upload-area__image" />
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
              onChange={handleHeroImageUpload}
              style={{ display: 'none' }}
            />
          </div>

          {/* Name Fields */}
          <div className="form-row">
            <div className="form-group">
              <label className="form-group__label">First Name</label>
              <input
                type="text"
                value={formData.firstname || ''}
                onChange={(e) => handleInputChange('firstname', e.target.value)}
                placeholder="Enter your first name"
                className="form-group__input"
              />
            </div>
            <div className="form-group">
              <label className="form-group__label">Last Name</label>
              <input
                type="text"
                value={formData.lastname || ''}
                onChange={(e) => handleInputChange('lastname', e.target.value)}
                placeholder="Enter your last name"
                className="form-group__input"
              />
            </div>
          </div>

          {/* Age Field */}
          <div className="form-group">
            <label className="form-group__label">Age</label>
            <input
              type="number"
              value={formData.age || ''}
              onChange={(e) => handleInputChange('age', e.target.value)}
              placeholder="Enter age"
              min="0"
              max="116"
              className="form-group__input"
            />
          </div>
        </div>

        <div className="modal__footer modal__footer--two-buttons">
          <button className="btn btn--skip" onClick={onSkip} disabled={loading}>
            Skip for now
          </button>
          <button className="btn btn--primary" onClick={onNext} disabled={loading}>
            Next
          </button>
        </div>
      </div>
    </div>
  );
};

export default ProfileStep;

