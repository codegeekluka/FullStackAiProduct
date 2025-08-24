import React from 'react';
import { useTheme } from '../../hooks/useTheme';
import { SunIcon, MoonIcon, ComputerIcon } from './Icons';

const ThemeToggle = ({ className = '' }) => {
  const { theme, toggleTheme, isDark, isLight, isSystem } = useTheme();

  const getThemeIcon = () => {
    if (isSystem) return <ComputerIcon />;
    if (isDark) return <MoonIcon />;
    return <SunIcon />;
  };

  const getThemeLabel = () => {
    if (isSystem) return 'System';
    if (isDark) return 'Dark';
    return 'Light';
  };

  return (
    <button
      onClick={toggleTheme}
      className={`theme-toggle ${className}`}
      title={`Current theme: ${getThemeLabel()}. Click to cycle themes.`}
      aria-label={`Switch theme. Current: ${getThemeLabel()}`}
    >
      <span className="theme-toggle-icon">
        {getThemeIcon()}
      </span>
      <span className="theme-toggle-label">
        {getThemeLabel()}
      </span>
    </button>
  );
};

export default ThemeToggle;
