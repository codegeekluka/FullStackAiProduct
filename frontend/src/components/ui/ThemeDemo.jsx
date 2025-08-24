import React from 'react';
import { useTheme } from '../../hooks/useTheme';
import ThemeToggle from './ThemeToggle';
import '../../styles/ui/ThemeDemo.css';

const ThemeDemo = () => {
  const { theme, isDark, isLight, isSystem, effectiveTheme } = useTheme();

  return (
    <div className="theme-demo">
      <div className="theme-demo-header">
        <h2>Theme System Demo</h2>
        <ThemeToggle />
      </div>
      
      <div className="theme-demo-info">
        <p><strong>Current Theme:</strong> {theme}</p>
        <p><strong>Effective Theme:</strong> {effectiveTheme}</p>
        <p><strong>Is Dark:</strong> {isDark ? 'Yes' : 'No'}</p>
        <p><strong>Is Light:</strong> {isLight ? 'Yes' : 'No'}</p>
        <p><strong>Is System:</strong> {isSystem ? 'Yes' : 'No'}</p>
      </div>

      <div className="theme-demo-sections">
        <section className="demo-section">
          <h3>Colors</h3>
          <div className="color-grid">
            <div className="color-swatch bg-primary">Primary Background</div>
            <div className="color-swatch bg-secondary">Secondary Background</div>
            <div className="color-swatch bg-surface">Surface</div>
            <div className="color-swatch bg-surface-secondary">Surface Secondary</div>
          </div>
        </section>

        <section className="demo-section">
          <h3>Text Colors</h3>
          <div className="text-demo">
            <p className="text-primary">Primary Text</p>
            <p className="text-secondary">Secondary Text</p>
            <p className="text-muted">Muted Text</p>
            <p className="text-inverse bg-primary">Inverse Text</p>
          </div>
        </section>

        <section className="demo-section">
          <h3>Buttons</h3>
          <div className="button-demo">
            <button className="btn-primary">Primary Button</button>
            <button className="btn-secondary">Secondary Button</button>
          </div>
        </section>

        <section className="demo-section">
          <h3>Glass Effects</h3>
          <div className="glass-demo">
            <div className="glass">Glass Card</div>
            <div className="glass-secondary">Secondary Glass</div>
          </div>
        </section>

        <section className="demo-section">
          <h3>Shadows</h3>
          <div className="shadow-demo">
            <div className="shadow-card shadow-sm">Small Shadow</div>
            <div className="shadow-card shadow-md">Medium Shadow</div>
            <div className="shadow-card shadow-lg">Large Shadow</div>
            <div className="shadow-card shadow-primary">Primary Shadow</div>
          </div>
        </section>

        <section className="demo-section">
          <h3>Borders</h3>
          <div className="border-demo">
            <div className="border-card border-primary">Primary Border</div>
            <div className="border-card border-secondary">Secondary Border</div>
          </div>
        </section>
      </div>
    </div>
  );
};

export default ThemeDemo;
