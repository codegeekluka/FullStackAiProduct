import React, { useState, useRef, useEffect } from "react";
import "../../styles/ui/TagDropdown.css";

export default function MultiTagDropdown({ options, selected, onChange }) {
  const [isOpen, setIsOpen] = useState(false);
  const [isMobile, setIsMobile] = useState(false);
  const dropdownRef = useRef(null);

  // Close dropdown if clicking outside
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
        setIsOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  // Check screen size for mobile responsiveness
  useEffect(() => {
    const checkScreenSize = () => {
      setIsMobile(window.innerWidth <= 600);
    };
    
    checkScreenSize();
    window.addEventListener('resize', checkScreenSize);
    return () => window.removeEventListener('resize', checkScreenSize);
  }, []);

  const handleTagToggle = (tag) => {
    const newSelected = selected.includes(tag)
      ? selected.filter(t => t !== tag)
      : [...selected, tag];
    onChange(newSelected);
  };

  const removeTag = (tagToRemove) => {
    onChange(selected.filter(tag => tag !== tagToRemove));
  };

  const getSelectedLabel = () => {
    if (selected.length === 0) {
      return "Select Tags";
    } else if (selected.length === 1) {
      return selected[0];
    } else {
      // On mobile, just show "Select Tags" instead of "X tags"
      return isMobile ? "Select Tags" : `${selected.length} tags`;
    }
  };

  return (
    <div className="tag-dropdown" ref={dropdownRef}>
      <button
        className="tag-dropdown-toggle"
        onClick={() => setIsOpen((prev) => !prev)}
      >
        <span>{getSelectedLabel()}</span>
        <svg 
          className="arrow" 
          width="12" 
          height="12" 
          viewBox="0 0 24 24" 
          fill="none" 
          stroke="currentColor" 
          strokeWidth="2"
          style={{ 
            transform: isOpen ? 'rotate(180deg)' : 'rotate(0deg)',
            transition: 'transform 0.2s ease'
          }}
        >
          <path d="M6 9l6 6 6-6"/>
        </svg>
      </button>

      {isOpen && (
        <ul className="tag-dropdown-menu">
          {options.map((tag) => (
            <li
              key={tag}
              onClick={() => handleTagToggle(tag)}
              className="tag-dropdown-item"
            >
              <span className="tag-name">{tag}</span>
              {selected.includes(tag) && (
                <svg 
                  className="checkmark" 
                  width="16" 
                  height="16" 
                  viewBox="0 0 24 24" 
                  fill="none" 
                  stroke="currentColor" 
                  strokeWidth="2"
                >
                  <polyline points="20,6 9,17 4,12"/>
                </svg>
              )}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
