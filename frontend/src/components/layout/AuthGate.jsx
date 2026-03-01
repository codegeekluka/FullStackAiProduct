import React, { useState, useEffect, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import { AuthContext } from '../../contexts/AuthContext';
import axios from 'axios';
import { API_BASE_URL } from '../../config/api';

const AuthGate = ({ children }) => {
  const { user, loading } = useContext(AuthContext);
  const [onboardingComplete, setOnboardingComplete] = useState(null);
  const [checkingOnboarding, setCheckingOnboarding] = useState(true);
  const navigate = useNavigate();
  const token = localStorage.getItem('token');

  useEffect(() => {
    if (!loading && user && token) {
      checkOnboardingStatus();
    } else if (!loading && !user) {
      setCheckingOnboarding(false);
    }
  }, [user, loading, token]);

  // Handle navigation after checking onboarding status
  useEffect(() => {
    if (!loading && !checkingOnboarding) {
      if (!user) {
        navigate('/');
      } else if (onboardingComplete === false) {
        navigate('/onboarding');
      }
    }
  }, [loading, checkingOnboarding, user, onboardingComplete, navigate]);

  const checkOnboardingStatus = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/users/me`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      setOnboardingComplete(response.data.onboarding_complete);
    } catch (error) {
      console.error('Error checking onboarding status:', error);
      // If there's an error, assume onboarding is not complete
      setOnboardingComplete(false);
    } finally {
      setCheckingOnboarding(false);
    }
  };

  // Show loading while checking auth and onboarding status
  if (loading || checkingOnboarding) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100vh',
        background: 'linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, rgba(255, 255, 255, 0.05) 100%)',
        backdropFilter: 'blur(20px)'
      }}>
        <div style={{
          background: 'rgba(255, 255, 255, 0.1)',
          backdropFilter: 'blur(20px)',
          borderRadius: '16px',
          padding: '40px',
          border: '1px solid rgba(255, 255, 255, 0.2)',
          boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)'
        }}>
          <div style={{
            width: '40px',
            height: '40px',
            border: '3px solid rgba(147, 51, 234, 0.3)',
            borderTop: '3px solid #9333ea',
            borderRadius: '50%',
            animation: 'spin 1s linear infinite',
            margin: '0 auto'
          }}></div>
          <p style={{ 
            marginTop: '16px', 
            textAlign: 'center', 
            color: 'rgba(0, 0, 0, 0.7)',
            fontSize: '1rem'
          }}>
            Loading...
          </p>
        </div>
      </div>
    );
  }

  // If not authenticated or onboarding not complete, show loading or nothing
  if (!user || onboardingComplete === false) {
    return null;
  }

  // If onboarding is complete, render the children
  return children;
};

export default AuthGate;
