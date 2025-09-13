import { useContext, useEffect } from 'react';
import { AuthContext } from '../contexts/AuthContext';
import { useTheme } from './useTheme';

export const useAuthAndTheme = () => {
  const auth = useContext(AuthContext);
  const theme = useTheme();

  // Sync theme when user profile is loaded
  useEffect(() => {
    if (auth.userProfile?.theme_preference && auth.userProfile.theme_preference !== theme.theme) {
      theme.switchTheme(auth.userProfile.theme_preference);
    }
  }, [auth.userProfile?.theme_preference, theme]);

  return {
    ...auth,
    ...theme
  };
};
