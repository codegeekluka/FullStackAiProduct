import { useState, useRef, useEffect, useContext } from "react";
import { createPortal } from "react-dom";
import { AuthContext } from "../../contexts/AuthContext";
import { getUserTags, addUserTag } from "../../services/userTagsService";
import '../../styles/ui/AddTags.css'

export default function TagsManager({ tags, onAddTag, onRemoveTag }) {
  const [showPopup, setShowPopup] = useState(false);
  const [customTag, setCustomTag] = useState("");
  const [selectedDefaults, setSelectedDefaults] = useState([]);
  const [availableTags, setAvailableTags] = useState([]);
  const [loading, setLoading] = useState(false);
  const popupRef = useRef();
  const { user } = useContext(AuthContext);
  
  // Get token from localStorage
  const token = localStorage.getItem('token');

  // Fetch available tags when popup is shown and set initial selection
  useEffect(() => {
    if (showPopup && token) {
      setLoading(true);
      getUserTags(token)
        .then(data => {
          setAvailableTags(data.tags.map(tag => tag.tag_name));
          // Set initial selection to current recipe tags
          setSelectedDefaults(tags);
        })
        .catch(error => {
          console.error("Error fetching user tags:", error);
        })
        .finally(() => {
          setLoading(false);
        });
    }
  }, [showPopup, token, tags]);

  // Close popup if clicked outside
  useEffect(() => {
    function handleClickOutside(event) {
      if (popupRef.current && !popupRef.current.contains(event.target) && 
          buttonRef.current && !buttonRef.current.contains(event.target)) {
        setShowPopup(false);
        setCustomTag("");
      }
    }
    if (showPopup) {
      document.addEventListener("mousedown", handleClickOutside);
    }
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [showPopup]);



  const toggleDefaultTag = (tag) => {
    const isCurrentlySelected = selectedDefaults.includes(tag);
    
    if (isCurrentlySelected) {
      // Tag is currently selected - remove it immediately from recipe
      const updatedSelection = selectedDefaults.filter(t => t !== tag);
      setSelectedDefaults(updatedSelection);
      onRemoveTag(tag);
    } else {
      // Tag is not selected - add it to selection
      setSelectedDefaults(prev => [...prev, tag]);
    }
  };

  const addSelectedTags = () => {
    // Only add tags that are newly selected (not already on the recipe)
    const newlySelectedTags = selectedDefaults.filter(tag => !tags.includes(tag));
    
    if (newlySelectedTags.length > 0) {
      onAddTag(newlySelectedTags);
    }
    setShowPopup(false);
  };

  // Calculate popup position
  const [popupPosition, setPopupPosition] = useState({ top: 0, right: 0 });
  const buttonRef = useRef(null);

  useEffect(() => {
    if (showPopup && buttonRef.current) {
      const buttonRect = buttonRef.current.getBoundingClientRect();
      // Find the bottom-right-buttons container
      const container = buttonRef.current.closest('.bottom-right-buttons');
      if (container) {
        const containerRect = container.getBoundingClientRect();
        setPopupPosition({
          top: containerRect.top - 240, // Position higher above the container
          right: window.innerWidth - containerRect.right
        });
      } else {
        // Fallback to button position
        setPopupPosition({
          top: buttonRect.top - 240, // Position higher above the button
          right: window.innerWidth - buttonRect.right
        });
      }
    }
  }, [showPopup]);

  const addCustomTag = async () => {
    const trimmed = customTag.trim().toLowerCase();
    if (trimmed && !availableTags.includes(trimmed)) {
      try {
        await addUserTag(trimmed, token);
        // Add the new tag to available tags and select it
        setAvailableTags(prev => [...prev, trimmed]);
        setSelectedDefaults(prev => [...prev, trimmed]);
        setCustomTag("");
      } catch (error) {
        console.error("Error adding custom tag:", error);
        // If the tag already exists, just select it
        if (error.response?.status === 400) {
          setSelectedDefaults(prev => [...prev, trimmed]);
          setCustomTag("");
        }
      }
    } else if (trimmed && availableTags.includes(trimmed)) {
      // Tag already exists, just select it
      setSelectedDefaults(prev => [...prev, trimmed]);
      setCustomTag("");
    }
  };

  return (
    <>
                   <button
        ref={buttonRef}
        className="icon-button add-tags-btn"
        onClick={() => setShowPopup(!showPopup)}
        title="Add Tags"
        aria-haspopup="true"
        aria-expanded={showPopup}
      >
        <svg width="28" height="28" fill="none" stroke="#333" strokeWidth="3" viewBox="0 0 24 24">
          <line x1="12" y1="5" x2="12" y2="19" />
          <line x1="5" y1="12" x2="19" y2="12" />
        </svg>
      </button>

      {showPopup && createPortal(
        <div 
          className="tags-popup" 
          ref={popupRef} 
          role="dialog" 
          aria-modal="true"
          style={{
            position: 'fixed',
            top: popupPosition.top,
            right: popupPosition.right,
            zIndex: 1000
          }}
        >
          <div className="default-tags">
            {loading ? (
              <div>Loading tags...</div>
            ) : (
              availableTags.map(tag => (
                <button
                  key={tag}
                  type="button"
                  className={`default-tag ${selectedDefaults.includes(tag) ? "selected" : ""}`}
                  onClick={() => toggleDefaultTag(tag)}
                >
                  {tag}
                </button>
              ))
            )}
          </div>

          <div className="custom-tag-input">
            <input
              type="text"
              placeholder="Add custom tag"
              value={customTag}
              onChange={e => setCustomTag(e.target.value)}
              onKeyDown={e => e.key === "Enter" && addCustomTag()}
              aria-label="Custom tag input"
            />
            <button type="button" onClick={addCustomTag} disabled={!customTag.trim() || loading}>
              Add
            </button>
          </div>

          <div className="popup-actions">
            <button type="button" onClick={addSelectedTags} disabled={selectedDefaults.length === 0 || loading}>
              Add Selected
            </button>
          </div>
        </div>,
        document.body
      )}

    </>
  );
}
