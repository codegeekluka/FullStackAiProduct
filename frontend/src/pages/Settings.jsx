import React, { useState, useEffect, useRef, useContext } from 'react';
import axios from 'axios';
import ImageCropper from '../components/ui/ImageCropper';
import ReturnBtn from '../components/ui/ReturnBtn';
import { SunIcon, MoonIcon, ComputerIcon } from '../components/ui/Icons';
import { AuthContext } from '../contexts/AuthContext';
import { useTheme } from '../hooks/useTheme';
import { useNavigate } from 'react-router-dom';
import photoPlaceholder from '../assets/photo.png';
import '../styles/settings/Settings.css';
import '../styles/onboarding/shared.css';

const Settings = () => {
  const { refreshUserProfile, origin, clearNavOrigin } = useContext(AuthContext);
  const { theme, switchTheme } = useTheme();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('profile');
  const [userProfile, setUserProfile] = useState(null);
  const [preferenceOptions, setPreferenceOptions] = useState({
    dietary_restrictions: [],
    cuisines: [],
    health_goals: [],
    budget_options: [],
    skill_levels: []
  });
  const [loading, setLoading] = useState(false);
  const [uploadingProfile, setUploadingProfile] = useState(false);
  const [uploadingHero, setUploadingHero] = useState(false);
  const [showProfileCropper, setShowProfileCropper] = useState(false);
  const [showHeroCropper, setShowHeroCropper] = useState(false);
  const [tempImageSrc, setTempImageSrc] = useState(null);
  const [tempImageType, setTempImageType] = useState(null);
  
  const profileInputRef = useRef();
  const heroInputRef = useRef();
  const token = localStorage.getItem('token');

  useEffect(() => {
    fetchUserProfile();
    fetchPreferenceOptions();
  }, []);

  const fetchUserProfile = async () => {
    try {
      const response = await axios.get('http://localhost:8000/users/me', {
        headers: { Authorization: `Bearer ${token}` }
      });
      setUserProfile(response.data);
    } catch (error) {
      console.error('Error fetching user profile:', error);
    }
  };

  const fetchPreferenceOptions = async () => {
    try {
      const response = await axios.get('http://localhost:8000/users/me/preferences/options', {
        headers: { Authorization: `Bearer ${token}` }
      });
      setPreferenceOptions(response.data);
    } catch (error) {
      console.error('Error fetching preference options:', error);
    }
  };

  const handleBackClick = () => {
    console.log('Settings - ReturnBtn clicked, origin:', origin);
    
    if (origin === '/home') {
      console.log('Settings - navigating to /home');
      navigate('/home');
    } else if (origin === '/MyRecipes') {
      console.log('Settings - navigating to /MyRecipes');
      navigate('/MyRecipes');
    } else {
      console.log('Settings - navigating to /home (fallback)');
      navigate('/home'); // Fallback to home
    }
    
    console.log('Settings - clearing nav origin');
    clearNavOrigin(); // Clear origin after navigating
  };

  const handleInputChange = (field, value) => {
    setUserProfile(prev => ({ ...prev, [field]: value }));
  };

  const handleCheckboxChange = (field, value) => {
    const currentValues = userProfile[field] || [];
    const newValues = currentValues.includes(value)
      ? currentValues.filter(item => item !== value)
      : [...currentValues, value];
    
    setUserProfile(prev => ({ ...prev, [field]: newValues }));
  };

  const handleRadioChange = (field, value) => {
    setUserProfile(prev => ({ ...prev, [field]: value }));
  };

  const handleFileSelect = (event, type) => {
    console.log('File select triggered for type:', type);
    console.log('Files:', event.target.files);
    const file = event.target.files[0];
    if (!file) {
      console.log('No file selected');
      return;
    }

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
      const response = await axios.post('http://localhost:8000/users/me/upload-profile-picture', formData, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'multipart/form-data'
        }
      });
      
      setUserProfile(prev => ({ ...prev, profile_picture_url: response.data.profile_picture_url }));
      
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
      const response = await axios.post('http://localhost:8000/users/me/upload-hero-image', formData, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'multipart/form-data'
        }
      });
      
      setUserProfile(prev => ({ ...prev, hero_image_url: response.data.hero_image_url }));
    } catch (error) {
      console.error('Error uploading hero image:', error);
      alert('Failed to upload hero image. Please try again.');
    } finally {
      setUploadingHero(false);
    }
  };

  const triggerProfileUpload = () => {
    console.log('Profile upload triggered');
    if (profileInputRef.current) {
      profileInputRef.current.click();
    } else {
      console.error('Profile input ref is null');
    }
  };

  const triggerHeroUpload = () => {
    console.log('Hero upload triggered');
    if (heroInputRef.current) {
      heroInputRef.current.click();
    } else {
      console.error('Hero input ref is null');
    }
  };

  const handleSave = async () => {
    setLoading(true);
    try {
      await axios.post('http://localhost:8000/users/me/onboarding', userProfile, {
        headers: { Authorization: `Bearer ${token}` }
      });
      alert('Settings saved successfully!');
    } catch (error) {
      console.error('Error saving settings:', error);
      alert('Error saving settings. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const formatLabel = (label) => {
    return label.split('_').map(word => 
      word.charAt(0).toUpperCase() + word.slice(1)
    ).join(' ');
  };

  // Helper function to construct full image URL
  const getImageUrl = (relativeUrl) => {
    if (!relativeUrl) return null;
    // If it's already a full URL, return as is
    if (relativeUrl.startsWith('http')) return relativeUrl;
    // Otherwise, prepend the backend URL
    return `http://localhost:8000${relativeUrl}`;
  };

  const getProfileDisplay = () => {
    if (userProfile?.profile_picture_url) {
      const fullImageUrl = getImageUrl(userProfile.profile_picture_url);
      return <img src={fullImageUrl} alt="Profile" className="profile-image" />;
    }
    return <span className="profile-placeholder" style={{ pointerEvents: 'none' }}>👤</span>;
  };

  const getHeroDisplay = () => {
    if (userProfile?.hero_image_url) {
      const fullImageUrl = getImageUrl(userProfile.hero_image_url);
      return <img src={fullImageUrl} alt="Hero" className="hero-image" />;
    }
    return <img src={photoPlaceholder} alt="Hero placeholder" className="hero-placeholder" />;
  };

  if (!userProfile) {
    return (
      <div className="settings-container">
        <div className="loading-spinner">Loading...</div>
      </div>
    );
  }

  return (
    <div className="settings-container">
      <div className="settings-header">
        <ReturnBtn onClick={handleBackClick} />
        <div className="settings-header-top">
          <h1 className="settings-title">Settings</h1>
        </div>
        <p className="settings-subtitle">Manage your profile and preferences</p>
      </div>

      <div className="settings-content">
        <div className="settings-tabs">
          <button 
            className={`tab-button ${activeTab === 'profile' ? 'active' : ''}`}
            onClick={() => setActiveTab('profile')}
          >
            Profile
          </button>
          <button 
            className={`tab-button ${activeTab === 'preferences' ? 'active' : ''}`}
            onClick={() => setActiveTab('preferences')}
          >
            Preferences
          </button>
          <button 
            className={`tab-button ${activeTab === 'appearance' ? 'active' : ''}`}
            onClick={() => setActiveTab('appearance')}
          >
            Appearance
          </button>
        </div>

        <div className="tab-content">
          {activeTab === 'profile' && (
            <div className="profile-tab">
              <div className="form-group">
                <label className="form-label">First Name</label>
                <input
                  type="text"
                  className="form-input"
                  value={userProfile.firstname || ''}
                  onChange={(e) => handleInputChange('firstname', e.target.value)}
                />
              </div>

              <div className="form-group">
                <label className="form-label">Last Name</label>
                <input
                  type="text"
                  className="form-input"
                  value={userProfile.lastname || ''}
                  onChange={(e) => handleInputChange('lastname', e.target.value)}
                />
              </div>

              <div className="form-group">
                <label className="form-label">Age</label>
                <input
                  type="number"
                  className="form-input"
                  value={userProfile.age || ''}
                  onChange={(e) => handleInputChange('age', e.target.value)}
                  min="0"
                  max="116"
                />
              </div>
            </div>
          )}

          {activeTab === 'preferences' && (
            <div className="preferences-tab">
              <div className="ob-form-group">
                <label className="ob-form-label">Cooking Skill Level</label>
                <div className="ob-radio-group">
                  {preferenceOptions.skill_levels?.map((level) => (
                    <div 
                      key={level}
                      className={`ob-radio-item ${userProfile.skill_level === level ? 'selected' : ''}`}
                      onClick={() => handleRadioChange('skill_level', level)}
                    >
                      <input
                        type="radio"
                        className="ob-radio-input"
                        name="skill_level"
                        value={level}
                        checked={userProfile.skill_level === level}
                        onChange={() => handleRadioChange('skill_level', level)}
                      />
                      <span className="ob-radio-label">{formatLabel(level)}</span>
                    </div>
                  ))}
                </div>
              </div>

              <div className="ob-form-group">
                <label className="ob-form-label">Dietary Restrictions</label>
                <div className="ob-checkbox-group">
                  {preferenceOptions.dietary_restrictions?.map((restriction) => (
                    <div 
                      key={restriction}
                      className={`ob-checkbox-item ${userProfile.dietary_restrictions?.includes(restriction) ? 'selected' : ''}`}
                      onClick={() => handleCheckboxChange('dietary_restrictions', restriction)}
                    >
                      <input
                        type="checkbox"
                        className="ob-checkbox-input"
                        value={restriction}
                        checked={userProfile.dietary_restrictions?.includes(restriction)}
                        onChange={() => handleCheckboxChange('dietary_restrictions', restriction)}
                      />
                      <span className="ob-checkbox-label">{formatLabel(restriction)}</span>
                    </div>
                  ))}
                </div>
              </div>

              <div className="ob-form-group">
                <label className="ob-form-label">Preferred Cuisines</label>
                <div className="ob-checkbox-group">
                  {preferenceOptions.cuisines?.map((cuisine) => (
                    <div 
                      key={cuisine}
                      className={`ob-checkbox-item ${userProfile.cuisine_preferences?.includes(cuisine) ? 'selected' : ''}`}
                      onClick={() => handleCheckboxChange('cuisine_preferences', cuisine)}
                    >
                      <input
                        type="checkbox"
                        className="ob-checkbox-input"
                        value={cuisine}
                        checked={userProfile.cuisine_preferences?.includes(cuisine)}
                        onChange={() => handleCheckboxChange('cuisine_preferences', cuisine)}
                      />
                      <span className="ob-checkbox-label">{formatLabel(cuisine)}</span>
                    </div>
                  ))}
                </div>
              </div>

              <div className="ob-form-group">
                <label className="ob-form-label">Health Goals</label>
                <div className="ob-checkbox-group">
                  {preferenceOptions.health_goals?.map((goal) => (
                    <div 
                      key={goal}
                      className={`ob-checkbox-item ${userProfile.health_goals?.includes(goal) ? 'selected' : ''}`}
                      onClick={() => handleCheckboxChange('health_goals', goal)}
                    >
                      <input
                        type="checkbox"
                        className="ob-checkbox-input"
                        value={goal}
                        checked={userProfile.health_goals?.includes(goal)}
                        onChange={() => handleCheckboxChange('health_goals', goal)}
                      />
                      <span className="ob-checkbox-label">{formatLabel(goal)}</span>
                    </div>
                  ))}
                </div>
              </div>

              <div className="ob-form-group">
                <label className="ob-form-label">Budget Preferences</label>
                <div className="ob-checkbox-group">
                  {preferenceOptions.budget_options?.map((option) => (
                    <div 
                      key={option}
                      className={`ob-checkbox-item ${userProfile.budget_preferences?.includes(option) ? 'selected' : ''}`}
                      onClick={() => handleCheckboxChange('budget_preferences', option)}
                    >
                      <input
                        type="checkbox"
                        className="ob-checkbox-input"
                        value={option}
                        checked={userProfile.budget_preferences?.includes(option)}
                        onChange={() => handleCheckboxChange('budget_preferences', option)}
                      />
                      <span className="ob-checkbox-label">{formatLabel(option)}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}



          {activeTab === 'appearance' && (
            <div className="appearance-tab">
              <div className="form-group">
                <label className="form-label">Theme</label>
                <div className="theme-options-container">
                  <div className="theme-radio-group">
                    <div 
                      className={`theme-radio-item ${theme === 'light' ? 'selected' : ''}`}
                      onClick={() => switchTheme('light')}
                    >
                      <input
                        type="radio"
                        name="theme"
                        value="light"
                        checked={theme === 'light'}
                        onChange={() => switchTheme('light')}
                      />
                      <span className="theme-radio-icon">
                        <SunIcon />
                      </span>
                      <span className="theme-radio-label">Light</span>
                    </div>
                    
                    <div 
                      className={`theme-radio-item ${theme === 'dark' ? 'selected' : ''}`}
                      onClick={() => switchTheme('dark')}
                    >
                      <input
                        type="radio"
                        name="theme"
                        value="dark"
                        checked={theme === 'dark'}
                        onChange={() => switchTheme('dark')}
                      />
                      <span className="theme-radio-icon">
                        <MoonIcon />
                      </span>
                      <span className="theme-radio-label">Dark</span>
                    </div>
                    
                    <div 
                      className={`theme-radio-item ${theme === 'system' ? 'selected' : ''}`}
                      onClick={() => switchTheme('system')}
                    >
                      <input
                        type="radio"
                        name="theme"
                        value="system"
                        checked={theme === 'system'}
                        onChange={() => switchTheme('system')}
                      />
                      <span className="theme-radio-icon">
                        <ComputerIcon />
                      </span>
                      <span className="theme-radio-label">System</span>
                    </div>
                  </div>
                  <p className="theme-description">
                    Choose between light, dark, or system theme preference
                  </p>
                </div>
              </div>

              <div className="form-group">
                <label className="form-label">Profile Picture</label>
                <div className="image-upload-container">
                  <div 
                    className={`image-upload-area ${userProfile.profile_picture_url ? 'has-image' : ''}`}
                    onClick={() => {
                      console.log('Profile image area clicked');
                      triggerProfileUpload();
                    }}
                    onMouseDown={() => console.log('Profile image area mouse down')}
                    onMouseUp={() => console.log('Profile image area mouse up')}
                  >
                    {getProfileDisplay()}
                  </div>
                  <p className="upload-text">Click to upload your profile picture</p>
                  <p className="upload-hint">Recommended: Square image, 200x200px or larger</p>
                  {uploadingProfile && <p className="upload-hint">Uploading...</p>}
                </div>
                <input
                  ref={profileInputRef}
                  type="file"
                  accept="image/*"
                  onChange={(e) => handleFileSelect(e, 'profile')}
                  style={{ display: 'none' }}
                  onClick={(e) => {
                    console.log('File input clicked');
                    e.stopPropagation();
                  }}
                />
              </div>

              <div className="form-group">
                <label className="form-label">Hero Section Image</label>
                <div 
                  className={`hero-image-upload ${userProfile.hero_image_url ? 'has-image' : ''}`}
                  onClick={() => {
                    console.log('Hero image area clicked');
                    triggerHeroUpload();
                  }}
                >
                  {getHeroDisplay()}
                </div>
                <p className="upload-hint" style={{ textAlign: 'center', marginTop: '8px' }}>
                  This will be displayed on every pages hero section
                </p>
                {uploadingHero && <p className="upload-hint" style={{ textAlign: 'center' }}>Uploading...</p>}
                <input
                  ref={heroInputRef}
                  type="file"
                  accept="image/*"
                  onChange={(e) => handleFileSelect(e, 'hero')}
                  style={{ display: 'none' }}
                  onClick={(e) => {
                    console.log('Hero file input clicked');
                    e.stopPropagation();
                  }}
                />
              </div>
            </div>
          )}
        </div>

        <div className="settings-actions">
          <button 
            className="btn btn-primary" 
            onClick={handleSave}
            disabled={loading}
          >
            {loading ? 'Saving...' : 'Save Changes'}
          </button>
        </div>
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
    </div>
  );
};

export default Settings;
