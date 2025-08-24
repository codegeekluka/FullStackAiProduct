import React from 'react';
import '../../styles/onboarding/shared.css';
import '../../styles/onboarding/ReviewStep.css';

const ReviewStep = ({ formData, updateFormData, onComplete, onBack, loading }) => {
  const handleInputChange = (field, value) => {
    updateFormData({ [field]: value });
  };

  const handleRadioChange = (field, value) => {
    // If the same value is clicked again, deselect it
    if (formData[field] === value) {
      updateFormData({ [field]: null });
    } else {
      updateFormData({ [field]: value });
    }
  };

  const formatLabel = (label) => {
    return label.split('_').map(word => 
      word.charAt(0).toUpperCase() + word.slice(1)
    ).join(' ');
  };

  const commonOptions = [
    'Social Media',
    'Friend Recommendation',
    'Search Engine',
    'App Store',
    'Advertisement',
    'Blog or Article',
    'Other'
  ];

  const isValid = formData.how_heard_about && (formData.how_heard_about !== 'Other' || formData.how_heard_about_other?.trim());

  return (
            <div className="modal onboarding-modal">
      <div className="modal__content">
        <div className="modal__header">
          <h2 className="modal__title">How did you discover Cheffy?</h2>
          <p className="modal__subtitle">Help us understand how users find our app</p>
        </div>

        <div className="modal__body">
          <div className="form-group">
            <label className="form-group__label">How did you hear about us?</label>
            <div className="radio-group">
              {commonOptions.map((option) => (
                <div
                  key={option}
                  className={`radio-item ${formData.how_heard_about === option ? 'radio-item--selected' : ''}`}
                  onClick={() => handleRadioChange('how_heard_about', option)}
                >
                  <input
                    type="radio"
                    name="how_heard_about"
                    value={option}
                    checked={formData.how_heard_about === option}
                    onChange={() => handleRadioChange('how_heard_about', option)}
                    className="radio-item__input"
                  />
                  <span className="radio-item__label">{option}</span>
                </div>
              ))}
            </div>
          </div>

          {formData.how_heard_about === 'Other' && (
            <div className="custom-input">
              <label className="form-group__label">Please specify:</label>
              <input
                type="text"
                value={formData.how_heard_about_other || ''}
                onChange={(e) => updateFormData({ how_heard_about_other: e.target.value })}
                placeholder="Tell us how you found us..."
                className="form-group__input"
              />
            </div>
          )}

          <div className="thank-you">
            <h3 className="thank-you__title">Thank you! 🎉</h3>
            <p className="thank-you__message">Your feedback helps us improve and reach more food lovers like you!</p>
          </div>
        </div>

        <div className="modal__footer modal__footer--two-buttons">
          <button className="btn btn--secondary" onClick={onBack} disabled={loading}>
            Back
          </button>
          <button className="btn btn--primary" onClick={onComplete} disabled={loading || !isValid}>
            Complete Setup
          </button>
        </div>
      </div>
    </div>
  );
};

export default ReviewStep;
