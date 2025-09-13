import React from "react";
import "../../styles/ui/TagPills.css";

export default function TagPills({ tags, onRemoveTag }) {
  if (tags.length === 0) return null;

  return (
    <div className="tag-pills-container">
      {tags.map((tag) => (
        <div key={tag} className="tag-pill">
          <span className="tag-pill-text">{tag}</span>
          <button
            className="tag-pill-remove"
            onClick={() => onRemoveTag(tag)}
            title={`Remove ${tag}`}
          >
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>
        </div>
      ))}
    </div>
  );
}
