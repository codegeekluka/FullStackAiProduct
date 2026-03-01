import { createContext, useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { API_BASE_URL } from '../config/api';

const ThemeContext = createContext();

export { ThemeContext };

export const ThemeProvider = ({ children }) => {
  const [theme, setTheme] = useState('system');
  const [isLoading, setIsLoading] = useState(true);

  // Get the actual theme to apply (resolves 'system' to light/dark)
  const getEffectiveTheme = useCallback(() => {
    if (theme === 'system') {
      return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    }
    return theme;
  }, [theme]);

  // Initialize theme from localStorage or system preference
  const initializeTheme = useCallback(() => {
    const storedTheme = localStorage.getItem('theme');
    const initialTheme = storedTheme || 'system';
    setTheme(initialTheme);
    setIsLoading(false);
  }, []);

  // Apply theme to DOM
  const applyTheme = useCallback((newTheme) => {
    const effectiveTheme = newTheme === 'system' 
      ? (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light')
      : newTheme;

    // Remove existing theme classes
    document.documentElement.classList.remove('theme-light', 'theme-dark');
    
    // Add new theme class
    document.documentElement.classList.add(`theme-${effectiveTheme}`);
    document.documentElement.setAttribute('data-theme', effectiveTheme);
    
    // Save to localStorage
    localStorage.setItem('theme', newTheme);
  }, []);

  // Switch theme
  const switchTheme = useCallback(async (newTheme) => {
    if (newTheme === theme) return;

    setTheme(newTheme);
    applyTheme(newTheme);

    // Save to database if user is authenticated
    const token = localStorage.getItem('token');
    if (token) {
      try {
        await axios.put(`${API_BASE_URL}/users/me/profile`, 
          { theme_preference: newTheme },
          { headers: { Authorization: `Bearer ${token}` } }
        );
      } catch (error) {
        console.error('Failed to save theme preference:', error);
        // Don't throw error - theme is still applied locally
      }
    }
  }, [theme, applyTheme]);

  // Toggle between light, dark, and system
  const toggleTheme = useCallback(() => {
    const themes = ['light', 'dark', 'system'];
    const currentIndex = themes.indexOf(theme);
    const nextIndex = (currentIndex + 1) % themes.length;
    switchTheme(themes[nextIndex]);
  }, [theme, switchTheme]);

  // Listen for system theme changes
  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    
    const handleSystemThemeChange = () => {
      // Only update if current theme is 'system'
      if (theme === 'system') {
        applyTheme('system');
      }
    };

    mediaQuery.addEventListener('change', handleSystemThemeChange);
    
    return () => mediaQuery.removeEventListener('change', handleSystemThemeChange);
  }, [theme, applyTheme]);

  // Apply theme when it changes
  useEffect(() => {
    if (!isLoading) {
      applyTheme(theme);
    }
  }, [theme, applyTheme, isLoading]);

  // Initialize on mount
  useEffect(() => {
    initializeTheme();
  }, [initializeTheme]);

  const value = {
    theme,
    isLoading,
    switchTheme,
    toggleTheme,
    isDark: getEffectiveTheme() === 'dark',
    isLight: getEffectiveTheme() === 'light',
    isSystem: theme === 'system',
    effectiveTheme: getEffectiveTheme()
  };

  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  );
};
