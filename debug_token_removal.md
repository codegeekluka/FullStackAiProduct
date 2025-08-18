# Debugging Token Removal Issue

## Problem
Token is being removed when pressing the back button from a recipe page.

## Debugging Steps

### Step 1: Check Console Logs
With the debugging code added, you should see these logs when you:
1. **Navigate to recipe page** - should see origin being set
2. **Press back button** - should see what origin is being used
3. **Token removal** - should see which component is removing the token

### Step 2: Check Network Tab
1. Open browser dev tools
2. Go to Network tab
3. Press the back button
4. Look for any failed API calls that might trigger token removal

### Step 3: Check Application Tab
1. Go to Application tab in dev tools
2. Look at Local Storage
3. Watch the `token` value when you press back button
4. See exactly when it gets removed

## Potential Causes

### 1. Navigation to Login Page
- Back button navigates to '/' (login page)
- Login page might be clearing tokens
- AuthContext re-initializes and clears token

### 2. Failed API Calls
- Navigation triggers API calls
- API calls fail with 401/403
- Error handlers clear token

### 3. Route Change Effects
- Route change triggers useEffect
- useEffect re-validates token
- Token validation fails

### 4. Origin Not Set
- Origin is null when navigating to recipe
- Back button defaults to '/' (login page)
- Login page clears token

## Expected Console Output

### When Scraping Recipe:
```
ScrapeWebsiteBtn - redirecting to recipe: recipe-slug
ScrapeWebsiteBtn - setting origin to /home
```

### When Pressing Back Button:
```
RecipeHero - ReturnBtn clicked, origin: /home
RecipeHero - navigating to /home
RecipeHero - clearing nav origin
RecipeHero - token after navigation: true
```

### If Token Gets Removed:
```
AuthContext - useEffect triggered, token exists: false
AuthContext - no token found
```

## Quick Fixes to Try

### Fix 1: Set Origin Properly
The ScrapeWebsiteBtn now sets the origin to '/home' when navigating to a recipe page.

### Fix 2: Check Login Page
Make sure the login page ('/') doesn't clear tokens unnecessarily.

### Fix 3: Add Error Boundaries
Add error boundaries to prevent unexpected token clearing.

### Fix 4: Improve Navigation Logic
Make the back button more robust by checking current location.

## Next Steps

1. **Test the fix** - Try scraping a recipe and pressing back
2. **Check console logs** - See if origin is being set correctly
3. **Monitor token** - Watch if token gets removed
4. **Identify root cause** - Based on logs, find what's clearing the token

## Common Issues Found

1. **Origin not set** - Back button defaults to login page
2. **Login page clears tokens** - Unnecessary token clearing
3. **API call failures** - Failed requests trigger token removal
4. **Route change effects** - Navigation triggers unwanted effects
