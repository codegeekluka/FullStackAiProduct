import React, { useState, useRef, useEffect } from "react";
import "../../styles/ui/TagDropdown.css";

export default function TagDropdown({ options, selected, onChange }) {
  const [isOpen, setIsOpen] = useState(false);
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

  return (
    <div className="tag-dropdown" ref={dropdownRef}>
      <button
        className="tag-dropdown-toggle"
        onClick={() => setIsOpen((prev) => !prev)}
      >
        <span>{selected || "All tags"}</span>
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
          <li onClick={() => { onChange(""); setIsOpen(false); }}>All tags</li>
          {options.map((tag) => (
            <li
              key={tag}
              onClick={() => {
                onChange(tag);
                setIsOpen(false);
              }}
            >
              {tag}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
