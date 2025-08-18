# Debugging Authentication Issue

## Problem
Users are being redirected to the login page after scraping recipes, even though the scraping itself is working.

## Potential Causes

### 1. Token Expiration
- Tokens expire after 30 minutes (`ACCESS_TOKEN_EXPIRE_MINUTES = 30`)
- Timezone issues between frontend and backend
- Token validation timing issues

### 2. JWT Configuration
- JWT_PASSWORD environment variable might not be set correctly
- Secret key mismatch between token creation and validation

### 3. Frontend State Management
- User state being cleared unexpectedly
- Race conditions in AuthContext
- PrivateRoute redirecting before user state is loaded

### 4. Backend Authentication
- Database connection issues
- User not found in database
- Token validation errors

## Debugging Steps

### Step 1: Check Browser Console
1. Open browser developer tools
2. Go to Console tab
3. Try scraping a recipe
4. Look for these debug messages:
   - `AuthContext - checking token: true/false`
   - `AuthContext - token decoded, expired: true/false`
   - `ScrapeWebsiteBtn - token exists: true/false`
   - `PrivateRoute - user: null/object, loading: true/false`

### Step 2: Check Token in Browser
1. Open browser developer tools
2. Go to Application tab
3. Look for Local Storage
4. Check if `token` exists and its value
5. Copy the token and decode it at jwt.io to see:
   - Expiration time
   - Payload content
   - Whether it's properly formatted

### Step 3: Check Backend Logs
1. Look at the backend console output
2. Check for any authentication errors
3. Look for database connection issues
4. Check if the JWT_PASSWORD is being loaded correctly

### Step 4: Test Token Manually
1. Get a fresh token by logging in
2. Use curl or Postman to test the `/recipes/{slug}` endpoint
3. Check if the token works for other authenticated endpoints

## Quick Fixes to Try

### Fix 1: Increase Token Expiration
```python
# In backend/Apis/auth.py
ACCESS_TOKEN_EXPIRE_MINUTES = 60  # Increase to 1 hour
```

### Fix 2: Check JWT_PASSWORD
Make sure the `.env` file in `backend/database/` contains:
```
JWT_PASSWORD=your_secret_key_here
```

### Fix 3: Add More Debugging
The debugging code has been added to:
- `PrivateRoute.jsx`
- `AuthContext.jsx`
- `ScrapeWebsiteBtn.jsx`

### Fix 4: Check Timezone
Make sure both frontend and backend are using the same timezone for token validation.

## Expected Behavior After Debugging

1. **Token should be valid** for at least 30 minutes after login
2. **User state should persist** across page refreshes
3. **PrivateRoute should not redirect** unless token is actually expired
4. **Scraping should work** without causing login redirects

## Common Issues Found

1. **Token expires too quickly** - Increase expiration time
2. **JWT_PASSWORD not set** - Add to environment file
3. **Timezone mismatch** - Ensure consistent timezone handling
4. **Database connection issues** - Check database connectivity
5. **Race conditions** - User state cleared before component loads

## Next Steps

1. Run the app with debugging enabled
2. Check browser console for debug messages
3. Identify the specific cause of the redirect
4. Apply the appropriate fix
5. Test the scraping functionality again
