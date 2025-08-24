import { useEffect, useRef } from 'react';
import { useLocation } from 'react-router-dom';

function ScrollToTop() {
  const { pathname } = useLocation();
  const previousPathname = useRef(pathname);

  useEffect(() => {
    // Only scroll to top if the pathname actually changed (real navigation)
    // This prevents scrolling when only state changes occur on the same page
    if (previousPathname.current !== pathname) {
      window.scrollTo(0, 0);
      previousPathname.current = pathname;
    }
  }, [pathname]);

  return null;
}

export default ScrollToTop;
