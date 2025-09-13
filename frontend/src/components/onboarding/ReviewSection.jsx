import React from 'react';
import '../../styles/onboarding/shared.css';

const ReviewSection = ({ formData, updateFormData }) => {
  const handleRadioChange = (field, value) => {
    // If the same value is clicked again, deselect it
    if (formData[field] === value) {
      updateFormData({ [field]: null });
    } else {
      updateFormData({ [field]: value });
    }
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

  return (
    <>
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
    </>
  );
};

export default ReviewSection;
