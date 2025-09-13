# Onboarding System Documentation

## Overview

The onboarding system provides a multi-step wizard for new users to set up their profile and preferences after account creation. It follows Apple premium liquid glass aesthetic design principles and integrates seamlessly with the existing authentication system.

## Architecture

### Backend Components

#### Database Schema
- **User Model Extensions**:
  - `onboarding_complete` (Boolean) - Tracks if user has completed onboarding
  - `age` (Integer) - User's age (0-116)
  - `profile_picture_url` (String) - URL to user's profile picture
  - `hero_image_url` (String) - URL to user's hero section image
  - `how_heard_about` (String) - How user discovered the app

#### Preference Tables
- **UserDietaryRestriction** - One-to-many relationship with User
- **UserCuisinePreference** - One-to-many relationship with User  
- **UserHealthGoal** - One-to-many relationship with User
- **UserBudgetPreference** - One-to-many relationship with User
- **UserSkillLevel** - One-to-one relationship with User

#### API Endpoints
- `GET /users/me` - Get current user profile with preferences
- `POST /users/me/onboarding` - Complete onboarding with profile and preferences
- `PATCH /users/me/onboarding-complete` - Mark onboarding as complete
- `POST /users/me/upload-profile-picture` - Upload profile picture
- `POST /users/me/upload-hero-image` - Upload hero section image
- `GET /users/me/preferences/options` - Get available preference options
- `PUT /users/me/profile` - Update profile information

### Frontend Components

#### Core Components
- **Onboarding** - Main wizard container with step management
- **ProfileStep** - Step 1: Basic profile information and image uploads
- **PreferencesStep** - Step 2: Cooking preferences and dietary restrictions
- **ReviewStep** - Step 3: Review information and how they heard about the app
- **AuthGate** - Route guard that checks onboarding completion
- **Settings** - Post-onboarding profile and preference management

#### Styling
- **Onboarding.css** - Apple premium liquid glass aesthetic
- Responsive design with mobile-first approach
- Smooth animations and transitions
- Glassmorphism effects with backdrop blur

## User Flow

### New User Journey
1. User signs up/logs in
2. AuthGate checks onboarding status
3. If incomplete → redirect to `/onboarding`
4. User completes 3-step wizard:
   - **Step 1**: Profile info (name, age, profile picture, hero image)
   - **Step 2**: Preferences (skill level, dietary restrictions, cuisines, health goals, budget)
   - **Step 3**: Review and "how heard about us"
5. On completion → redirect to `/home`
6. Future visits → AuthGate allows access to protected routes

### Skip Functionality
- Users can skip onboarding at any step
- Skipping immediately marks onboarding as complete
- Redirects to `/home` with wizard popup suggesting settings update

### Settings Page
- Accessible via navbar profile picture dropdown
- Allows users to update all onboarding information
- Uses same styling and components as onboarding

## File Upload System

### Current Implementation
- Files stored locally in `uploads/` directory
- Organized by type: `profile_pictures/` and `hero_images/`
- Unique filenames generated using UUID
- URLs stored as relative paths in database

### Production Considerations
**⚠️ IMPORTANT**: For production deployment, switch to AWS S3 or similar cloud storage:

1. **Why**: Local file storage doesn't scale and files are lost on server restart
2. **Implementation**: 
   - Use AWS SDK for Python (boto3)
   - Configure S3 bucket with proper CORS
   - Update `save_uploaded_file()` function
   - Store full S3 URLs in database
3. **Benefits**: Scalability, reliability, CDN integration

### Image Handling
- Profile pictures: 200x200px recommended, circular crop
- Hero images: Maintains aspect ratio, fits existing hero section dimensions
- File validation: Only image files accepted
- Fallback: Default icons when no image uploaded

## Preference Options

### Default Values
```javascript
DIETARY_RESTRICTIONS = [
  "vegetarian", "vegan", "gluten-free", "dairy-free", "nut-free", 
  "pescatarian", "keto", "paleo", "low-carb", "halal", "kosher"
]

CUISINES = [
  "italian", "mexican", "chinese", "japanese", "indian", "thai", 
  "french", "mediterranean", "american", "greek", "spanish", "korean"
]

HEALTH_GOALS = [
  "lose_weight", "gain_weight", "maintain_weight", "build_muscle", 
  "improve_energy", "better_digestion", "heart_health"
]

BUDGET_OPTIONS = [
  "cheap", "expensive", "something_in_between"
]

SKILL_LEVELS = [
  "beginner", "intermediate", "advanced"
]
```

## Navigation Updates

### Navbar Changes
- Profile picture display (40px circular)
- Fallback to first letter of firstname/username with purple background
- Settings link in dropdown menu
- Removed arrow indicator

### Route Protection
- **PrivateRoute**: Basic authentication check
- **AuthGate**: Authentication + onboarding completion check
- All main app routes now use AuthGate
- Onboarding route uses PrivateRoute only

## Styling System

### Design Principles
- **Apple Premium**: Clean, minimal, premium feel
- **Liquid Glass**: Glassmorphism with backdrop blur
- **Rounded Corners**: 16px-24px border radius
- **Soft Shadows**: Subtle elevation effects
- **Smooth Transitions**: 200-300ms ease-in-out animations

### Color Palette
- **Primary**: Purple gradient (#9333ea to #4f46e5)
- **Background**: Transparent whites with blur effects
- **Text**: Near-black for headings, medium gray for secondary
- **Accents**: Purple for selections and highlights

### Responsive Design
- Mobile-first approach
- Grid layouts adapt to screen size
- Touch-friendly button sizes
- Optimized for kitchen use

## Error Handling

### Backend
- Comprehensive try-catch blocks
- Database rollback on errors
- Meaningful error messages
- Input validation (age limits, file types)

### Frontend
- Loading states for all async operations
- Error boundaries for component failures
- Graceful fallbacks for missing data
- User-friendly error messages

## Testing Considerations

### Backend Testing
- API endpoint testing
- Database migration testing
- File upload testing
- Preference validation testing

### Frontend Testing
- Component rendering tests
- Form validation tests
- Navigation flow tests
- Responsive design tests

## Performance Optimizations

### Backend
- Database indexes on user_id foreign keys
- Efficient preference queries
- File upload size limits
- Image compression (future enhancement)

### Frontend
- Lazy loading of preference options
- Debounced form inputs
- Optimized image rendering
- Minimal re-renders with proper state management

## Security Considerations

### File Uploads
- File type validation
- Size limits
- Secure file naming
- Path traversal prevention

### API Security
- JWT token validation
- User ownership verification
- Input sanitization
- CORS configuration

## Future Enhancements

### Planned Features
1. **Image Cropping**: Client-side image editing
2. **Default Avatars**: Pre-built profile picture options
3. **Preference Analytics**: Track popular choices
4. **Progressive Onboarding**: Spread across multiple sessions
5. **Social Login Integration**: Import profile data

### Technical Improvements
1. **AWS S3 Integration**: Cloud file storage
2. **Image Optimization**: Automatic resizing and compression
3. **Caching**: Redis for preference options
4. **Real-time Updates**: WebSocket for live preference sync
5. **Offline Support**: Local storage for form data

## Deployment Notes

### Database Migration
```bash
# Run migration to add onboarding tables
alembic upgrade head
```

### Environment Variables
```env
# File upload settings
UPLOAD_DIR=uploads
MAX_FILE_SIZE=5242880  # 5MB

# AWS S3 (for production)
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_S3_BUCKET=your_bucket
AWS_REGION=us-east-1
```

### File Permissions
```bash
# Ensure upload directory is writable
chmod 755 uploads/
chmod 755 uploads/profile_pictures/
chmod 755 uploads/hero_images/
```

## Troubleshooting

### Common Issues
1. **Migration Errors**: Check database connection and pgvector extension
2. **File Upload Failures**: Verify directory permissions and disk space
3. **Styling Issues**: Check CSS import paths and browser compatibility
4. **Navigation Problems**: Verify route configuration and AuthGate logic

### Debug Steps
1. Check browser console for JavaScript errors
2. Verify API endpoints with Postman/curl
3. Check database for missing tables/columns
4. Validate JWT token expiration
5. Test file upload permissions

---

**Last Updated**: [Current Date]
**Version**: 1.0.0
**Maintainer**: Development Team

