import '../../styles/layout/NavBar.css'
import { Link, useNavigate } from 'react-router-dom'
import { useContext, useState, useEffect, useRef } from 'react'
import { AuthContext } from '../../contexts/AuthContext'
import { API_BASE_URL } from '../../config/api'
import { createPortal } from 'react-dom'


const Navbar = () => {
    const { logout, user, userProfile } = useContext(AuthContext);
    const navigate = useNavigate()
    const [dropdownOpen, setDropdownOpen] = useState(false);
    const dropdownRef = useRef(null);
    const [dropdownPosition, setDropdownPosition] = useState({ top: 0, right: 0 });
    const timeoutRef = useRef(null);

    const handleLogout = () => {
        logout();
        navigate('/');
    }

    // Calculate dropdown position when it opens
    useEffect(() => {
        if (dropdownOpen && dropdownRef.current) {
            const rect = dropdownRef.current.getBoundingClientRect();
            setDropdownPosition({
                top: rect.bottom + 4,
                right: window.innerWidth - rect.right
            });
        }
    }, [dropdownOpen]);

    // Clear timeout on unmount
    useEffect(() => {
        return () => {
            if (timeoutRef.current) {
                clearTimeout(timeoutRef.current);
            }
        };
    }, []);

    // Helper function to construct full image URL
    const getImageUrl = (relativeUrl) => {
        if (!relativeUrl) return null;
        // If it's already a full URL, return as is
        if (relativeUrl.startsWith('http')) return relativeUrl;
        // Otherwise, prepend the backend URL
        return `${API_BASE_URL}${relativeUrl}`;
    };

    const getProfileDisplay = () => {
        if (userProfile?.profile_picture_url) {
            const fullImageUrl = getImageUrl(userProfile.profile_picture_url);
            return (
                <img 
                    src={fullImageUrl} 
                    alt="Profile" 
                    style={{
                        width: '48px',
                        height: '48px',
                        borderRadius: '50%',
                        objectFit: 'cover',
                        objectPosition: 'center',
                        border: '2px solid rgba(255, 255, 255, 0.3)',
                        boxShadow: '0 3px 8px rgba(0, 0, 0, 0.15)',
                        flexShrink: 0,
                        imageRendering: 'high-quality'
                    }}
                />
            );
        }
        
        // Fallback to username from AuthContext if profile fetch failed
        const displayName = userProfile?.firstname || user?.username || 'U';
        const firstLetter = displayName.charAt(0).toUpperCase();
        
        return (
            <div style={{
                width: '48px',
                height: '48px',
                borderRadius: '50%',
                backgroundColor: '#9333ea',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: 'white',
                fontSize: '1.2rem',
                fontWeight: '600',
                border: '2px solid rgba(255, 255, 255, 0.3)',
                boxShadow: '0 3px 8px rgba(0, 0, 0, 0.15)',
                flexShrink: 0
            }}>
                {firstLetter}
            </div>
        );
    };
    return(
        <>
        <nav className="nav">
            <Link to="/home" className="site-title">Cheffy</Link>
            <ul>
                
                <li className="dropdown" 
                    onMouseEnter={() => {
                        if (timeoutRef.current) {
                            clearTimeout(timeoutRef.current);
                        }
                        setDropdownOpen(true);
                    }} 
                    onMouseLeave={() => {
                        timeoutRef.current = setTimeout(() => {
                            setDropdownOpen(false);
                        }, 150);
                    }}
                >
                    <button 
                        ref={dropdownRef}
                        className="user-btn" 
                        style={{ display: 'flex', alignItems: 'center', gap: '8px' }}
                    >
                        {getProfileDisplay()}
                    </button>
                </li>
            </ul>
        </nav>
        {dropdownOpen && createPortal(
            <ul 
                className="dropdown-menu" 
                style={{
                    position: 'fixed',
                    top: dropdownPosition.top,
                    right: dropdownPosition.right,
                    zIndex: 9999
                }}
                onMouseEnter={() => {
                    if (timeoutRef.current) {
                        clearTimeout(timeoutRef.current);
                    }
                }}
                onMouseLeave={() => {
                    timeoutRef.current = setTimeout(() => {
                        setDropdownOpen(false);
                    }, 150);
                }}
            >
                {!user ? (
                    <>
                    <li><Link to="/">Login</Link></li>
                    <li><Link to="/register">Signup</Link></li>
                    </>
                ) : (
                    <>
                    <li><Link to="/settings">Settings</Link></li>
                    <li><button onClick={handleLogout} className="logout-btn">Logout</button></li>
                    </>
                )}
            </ul>,
            document.body
        )}
    </>
    )
}

export default Navbar