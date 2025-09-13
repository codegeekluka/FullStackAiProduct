# Onboarding CSS Architecture

This document outlines the CSS architecture for the onboarding flow, following BEM naming conventions, ITCSS structure, and responsive design best practices.

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [File Structure](#file-structure)
- [BEM Naming Conventions](#bem-naming-conventions)
- [ITCSS Layers](#itcss-layers)
- [Responsive Design](#responsive-design)
- [Component Documentation](#component-documentation)
- [Best Practices](#best-practices)
- [Migration Guide](#migration-guide)

## Architecture Overview

The onboarding CSS follows a modular, scalable architecture designed for maintainability and consistency:

- **BEM Methodology**: Block__Element--Modifier naming convention
- **ITCSS Structure**: Inverted Triangle CSS for organized specificity
- **Mobile-First**: Responsive design starting from mobile breakpoints
- **Rem Units**: Scalable typography and spacing using rem units
- **CSS Custom Properties**: Future-ready for design system integration

## File Structure

```
onboarding/
├── Onboarding.css          # Base layer - main container styles
├── shared.css              # Components layer - reusable components
├── ProfileStep.css         # Components layer - profile-specific components
├── PreferencesStep.css     # Components layer - preferences-specific components
├── ReviewStep.css          # Components layer - review-specific components
└── README.md              # This documentation file
```

## BEM Naming Conventions

### Block__Element--Modifier

- **Block**: Standalone entity (e.g., `.modal`, `.btn`, `.form-group`)
- **Element**: Parts of a block (e.g., `.modal__header`, `.btn__icon`)
- **Modifier**: Variations of blocks/elements (e.g., `.btn--primary`, `.modal--large`)

### Examples

```css
/* Block */
.modal { }

/* Element */
.modal__header { }
.modal__body { }
.modal__footer { }

/* Modifier */
.modal--large { }
.modal__footer--two-buttons { }

/* Element with modifier */
.btn__icon--small { }
```

### Naming Rules

1. **Use lowercase with hyphens** for multi-word names
2. **Use double underscores** for elements (`__`)
3. **Use double hyphens** for modifiers (`--`)
4. **Keep names semantic and descriptive**
5. **Avoid nesting more than 2 levels deep**

## ITCSS Layers

The CSS follows the Inverted Triangle CSS methodology:

### 1. Base Layer (`Onboarding.css`)
- **Purpose**: Foundation styles, resets, and base elements
- **Specificity**: Lowest
- **Scope**: Global within onboarding context

```css
.onboarding {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 1000;
  background-color: var(--color-white, #ffffff);
  overflow-y: auto;
}
```

### 2. Components Layer (`shared.css`, `*Step.css`)
- **Purpose**: Reusable UI components
- **Specificity**: Medium
- **Scope**: Component-specific

```css
.modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 1000;
  background-color: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(10px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
}
```

## Responsive Design

### Mobile-First Approach

All styles start with mobile as the base, then scale up:

```css
/* Base styles (mobile) */
.modal__content {
  max-width: 31.25rem;
  width: 100%;
  border-radius: 1.5rem;
}

/* Tablet and up */
@media (min-width: 48rem) {
  .modal__content {
    border-radius: 1.25rem;
  }
}

/* Desktop and up */
@media (min-width: 64rem) {
  .modal__content {
    border-radius: 1rem;
  }
}
```

### Breakpoint Strategy

- **Mobile**: `0px - 479px` (base styles)
- **Tablet**: `480px - 767px` (`@media (min-width: 30rem)`)
- **Desktop**: `768px - 1023px` (`@media (min-width: 48rem)`)
- **Large Desktop**: `1024px+` (`@media (min-width: 64rem)`)

### Rem Units

All measurements use rem units for scalability:

```css
/* Convert px to rem: divide by 16 */
.modal__header {
  padding: 2rem 2rem 1rem; /* 32px 32px 16px */
  margin-bottom: 1.5rem;   /* 24px */
}

.btn {
  padding: 1rem 2rem;      /* 16px 32px */
  border-radius: 1rem;     /* 16px */
  font-size: 1rem;         /* 16px */
}
```

## Component Documentation

### Modal Component

**File**: `shared.css`

**Usage**:
```html
<div class="modal">
  <div class="modal__content">
    <div class="modal__header">
      <h2 class="modal__title">Title</h2>
      <p class="modal__subtitle">Subtitle</p>
    </div>
    <div class="modal__body">
      <!-- Content -->
    </div>
    <div class="modal__footer modal__footer--two-buttons">
      <button class="btn btn--skip">Skip</button>
      <button class="btn btn--primary">Continue</button>
    </div>
  </div>
</div>
```

**Modifiers**:
- `.modal__footer--two-buttons`: Two-button layout
- `.modal__footer--three-buttons`: Three-button layout

### Button Component

**File**: `shared.css`

**Usage**:
```html
<button class="btn btn--primary">Primary Button</button>
<button class="btn btn--secondary">Secondary Button</button>
<button class="btn btn--skip">Skip</button>
```

**Variants**:
- `.btn--primary`: Primary action button
- `.btn--secondary`: Secondary action button
- `.btn--skip`: Skip/back button

### Form Components

**File**: `shared.css`

**Usage**:
```html
<div class="form-group">
  <label class="form-group__label">Label</label>
  <input class="form-group__input" type="text" placeholder="Enter text" />
</div>
```

### Upload Area Component

**File**: `ProfileStep.css`

**Usage**:
```html
<div class="upload-area upload-area--profile upload-area--has-image">
  <img class="upload-area__image" src="..." alt="Profile" />
  <div class="upload-area__placeholder">
    <div class="upload-area__icon">📷</div>
    <div class="upload-area__text">Upload Photo</div>
    <div class="upload-area__hint">Click to upload</div>
  </div>
</div>
```

**Modifiers**:
- `.upload-area--profile`: Circular profile image upload
- `.upload-area--hero`: Rectangular hero image upload
- `.upload-area--has-image`: Applied when image is uploaded

### Progress Indicator

**File**: `PreferencesStep.css`

**Usage**:
```html
<div class="progress">
  <div class="progress__pills">
    <div class="progress__pill progress__pill--completed"></div>
    <div class="progress__pill progress__pill--active"></div>
    <div class="progress__pill"></div>
  </div>
</div>
```

**Modifiers**:
- `.progress__pill--active`: Current step
- `.progress__pill--completed`: Completed step

### Checkbox/Radio Items

**File**: `PreferencesStep.css`

**Usage**:
```html
<div class="checkbox-group">
  <label class="checkbox-item checkbox-item--selected">
    <input class="checkbox-item__input" type="checkbox" />
    <span class="checkbox-item__label">Option 1</span>
  </label>
</div>

<div class="radio-group">
  <label class="radio-item radio-item--selected">
    <input class="radio-item__input" type="radio" name="option" />
    <span class="radio-item__label">Option 1</span>
  </label>
</div>
```

**Modifiers**:
- `.checkbox-item--selected`: Selected state
- `.radio-item--selected`: Selected state

### Option Cards

**File**: `ReviewStep.css`

**Usage**:
```html
<div class="option-grid">
  <div class="option-card option-card--selected">
    <div class="option-card__icon">🍕</div>
    <div class="option-card__text">Pizza</div>
  </div>
</div>
```

**Modifiers**:
- `.option-card--selected`: Selected state

## Best Practices

### 1. CSS Organization

```css
/* ==========================================================================
   SECTION NAME
   ========================================================================== */

/**
 * Component Description
 * Brief explanation of the component's purpose
 * 
 * @example
 * <div class="component">
 *   <div class="component__element">...</div>
 * </div>
 */

.component {
  /* Layout */
  display: flex;
  position: relative;
  
  /* Typography */
  font-size: 1rem;
  font-weight: 600;
  
  /* Visual */
  background-color: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  
  /* Spacing */
  padding: 1rem;
  margin-bottom: 1rem;
  
  /* Transitions */
  transition: all 0.3s ease;
  
  /* Interactive */
  cursor: pointer;
  
  /* Hover states */
  &:hover {
    background-color: #f9fafb;
  }
  
  /* Focus states */
  &:focus {
    outline: none;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
  }
}
```

### 2. Responsive Design

```css
/* Mobile-first approach */
.component {
  padding: 1rem;
  font-size: 0.875rem;
}

/* Tablet and up */
@media (min-width: 48rem) {
  .component {
    padding: 1.5rem;
    font-size: 1rem;
  }
}

/* Desktop and up */
@media (min-width: 64rem) {
  .component {
    padding: 2rem;
    font-size: 1.125rem;
  }
}
```

### 3. Accessibility

```css
/* High DPI displays */
@media (-webkit-min-device-pixel-ratio: 2), (min-resolution: 192dpi) {
  .component {
    border-width: 0.5px;
  }
}

/* Reduced motion */
@media (prefers-reduced-motion: reduce) {
  .component {
    transition: none;
  }
  
  .component:hover {
    transform: none;
  }
}

/* High contrast */
@media (prefers-contrast: high) {
  .component {
    border: 2px solid #000000;
  }
}
```

### 4. Performance

- Use `transform` and `opacity` for animations
- Avoid layout-triggering properties in animations
- Use `will-change` sparingly
- Minimize repaints and reflows

## Migration Guide

### From Old Class Names

| Old Class | New Class | Notes |
|-----------|-----------|-------|
| `.onboarding-container` | `.onboarding` | Simplified naming |
| `.ob-review-modal` | `.modal` | Removed prefix |
| `.ob-modal-content` | `.modal__content` | BEM structure |
| `.ob-modal-header` | `.modal__header` | BEM structure |
| `.ob-modal-title` | `.modal__title` | BEM structure |
| `.ob-modal-subtitle` | `.modal__subtitle` | BEM structure |
| `.ob-modal-body` | `.modal__body` | BEM structure |
| `.ob-modal-footer` | `.modal__footer` | BEM structure |
| `.ob-btn` | `.btn` | Simplified naming |
| `.ob-btn-primary` | `.btn--primary` | BEM modifier |
| `.ob-btn-secondary` | `.btn--secondary` | BEM modifier |
| `.ob-btn-skip` | `.btn--skip` | BEM modifier |
| `.ob-form-group` | `.form-group` | Simplified naming |
| `.ob-form-label` | `.form-group__label` | BEM structure |
| `.ob-form-input` | `.form-group__input` | BEM structure |
| `.profile-upload-area` | `.upload-area--profile` | BEM modifier |
| `.hero-upload-area` | `.upload-area--hero` | BEM modifier |
| `.uploaded-profile-image` | `.upload-area__image` | BEM structure |
| `.upload-placeholder` | `.upload-area__placeholder` | BEM structure |
| `.upload-icon` | `.upload-area__icon` | BEM structure |
| `.upload-text` | `.upload-area__text` | BEM structure |
| `.upload-hint` | `.upload-area__hint` | BEM structure |
| `.ob-progress-container` | `.progress` | Simplified naming |
| `.ob-progress-pills` | `.progress__pills` | BEM structure |
| `.ob-progress-pill` | `.progress__pill` | BEM structure |
| `.ob-progress-pill.active` | `.progress__pill--active` | BEM modifier |
| `.ob-progress-pill.completed` | `.progress__pill--completed` | BEM modifier |
| `.ob-step-header` | `.step-header` | Simplified naming |
| `.ob-step-title` | `.step-header__title` | BEM structure |
| `.ob-step-description` | `.step-header__description` | BEM structure |
| `.ob-checkbox-group` | `.checkbox-group` | Simplified naming |
| `.ob-checkbox-item` | `.checkbox-item` | Simplified naming |
| `.ob-checkbox-item.selected` | `.checkbox-item--selected` | BEM modifier |
| `.ob-checkbox-input` | `.checkbox-item__input` | BEM structure |
| `.ob-checkbox-label` | `.checkbox-item__label` | BEM structure |
| `.ob-radio-group` | `.radio-group` | Simplified naming |
| `.ob-radio-item` | `.radio-item` | Simplified naming |
| `.ob-radio-item.selected` | `.radio-item--selected` | BEM modifier |
| `.ob-radio-input` | `.radio-item__input` | BEM structure |
| `.ob-radio-label` | `.radio-item__label` | BEM structure |
| `.ob-option-grid` | `.option-grid` | Simplified naming |
| `.ob-option-card` | `.option-card` | Simplified naming |
| `.ob-option-card.selected` | `.option-card--selected` | BEM modifier |
| `.ob-option-icon` | `.option-card__icon` | BEM structure |
| `.ob-option-text` | `.option-card__text` | BEM structure |
| `.ob-custom-input-section` | `.custom-input` | Simplified naming |
| `.ob-footer-actions` | `.custom-input__actions` | BEM structure |
| `.thank-you-message` | `.thank-you` | Simplified naming |
| `.thank-you-message h3` | `.thank-you__title` | BEM structure |
| `.thank-you-message p` | `.thank-you__message` | BEM structure |

### Migration Steps

1. **Update HTML**: Replace old class names with new BEM structure
2. **Update JavaScript**: Update any class selectors in JavaScript
3. **Test Responsive**: Verify all breakpoints work correctly
4. **Test Accessibility**: Ensure screen readers and keyboard navigation work
5. **Performance Test**: Verify no performance regressions

### Example Migration

**Before**:
```html
<div class="ob-review-modal">
  <div class="ob-modal-content">
    <div class="ob-modal-header">
      <h2 class="ob-modal-title">Welcome</h2>
    </div>
    <div class="ob-modal-body">
      <div class="ob-form-group">
        <label class="ob-form-label">Name</label>
        <input class="ob-form-input" type="text" />
      </div>
    </div>
    <div class="ob-modal-footer ob-two-button-layout">
      <button class="ob-btn ob-btn-skip">Skip</button>
      <button class="ob-btn ob-btn-primary">Continue</button>
    </div>
  </div>
</div>
```

**After**:
```html
<div class="modal">
  <div class="modal__content">
    <div class="modal__header">
      <h2 class="modal__title">Welcome</h2>
    </div>
    <div class="modal__body">
      <div class="form-group">
        <label class="form-group__label">Name</label>
        <input class="form-group__input" type="text" />
      </div>
    </div>
    <div class="modal__footer modal__footer--two-buttons">
      <button class="btn btn--skip">Skip</button>
      <button class="btn btn--primary">Continue</button>
    </div>
  </div>
</div>
```

## Future Considerations

1. **CSS Custom Properties**: Consider migrating to CSS custom properties for theming
2. **Design System**: Integrate with a broader design system
3. **CSS Modules**: Consider CSS Modules for better encapsulation
4. **PostCSS**: Use PostCSS plugins for advanced features
5. **CSS Grid**: Leverage CSS Grid for more complex layouts
6. **Container Queries**: Use container queries when browser support improves

## Support

For questions or issues with the CSS architecture:

1. Check this documentation first
2. Review the component examples
3. Test in different browsers and devices
4. Validate accessibility requirements
5. Consider performance implications

---

**Last Updated**: December 2024  
**Version**: 2.0.0  
**Maintainer**: Development Team
