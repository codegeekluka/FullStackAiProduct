import React, { useState, useRef, useEffect } from "react";
import "../../styles/ui/TagDropdown.css";

export default function TimeDropdown({ selected, onChange }) {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef(null);

  const timeOptions = [
    { value: "", label: "All times", icon: true },
    { value: "quick", label: "Quick (< 30 min)" },
    { value: "medium", label: "Medium (30-60 min)" },
    { value: "long", label: "Long (> 60 min)" }
  ];

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

  const getSelectedLabel = () => {
    const option = timeOptions.find(opt => opt.value === selected);
    if (option && option.icon) {
      return (
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <circle cx="12" cy="12" r="10"/>
          <polyline points="12,6 12,12 16,14"/>
        </svg>
      );
    }
    return option ? option.label : (
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <circle cx="12" cy="12" r="10"/>
        <polyline points="12,6 12,12 16,14"/>
      </svg>
    );
  };

  return (
    <div className="tag-dropdown time-dropdown" ref={dropdownRef}>
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
           {timeOptions.map((option) => (
             <li
               key={option.value}
               onClick={() => {
                 onChange(option.value);
                 setIsOpen(false);
               }}
             >
               {option.icon ? (
                 <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                   <circle cx="12" cy="12" r="10"/>
                   <polyline points="12,6 12,12 16,14"/>
                 </svg>
               ) : (
                 option.label
               )}
             </li>
           ))}
         </ul>
       )}
    </div>
  );
}
