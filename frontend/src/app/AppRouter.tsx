import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { ROUTES, type AppRoute } from './routes';

interface RouteContextType {
  currentRoute: AppRoute;
  navigate: (route: AppRoute) => void;
}

const RouteContext = createContext<RouteContextType>({
  currentRoute: ROUTES.HOME,
  navigate: () => {},
});

export const useRoute = () => useContext(RouteContext);

function getInitialRoute(): AppRoute {
  const path = window.location.pathname as AppRoute;
  if (path === ROUTES.SCREENING || path === ROUTES.ABOUT || path === ROUTES.FAQ) {
    return path;
  }
  return ROUTES.HOME;
}

export const RouteProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [currentRoute, setCurrentRoute] = useState<AppRoute>(getInitialRoute);

  const navigate = useCallback((route: AppRoute) => {
    setCurrentRoute(route);
    if (window.location.pathname !== route) {
      window.history.pushState(null, '', route);
    }
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }, []);

  useEffect(() => {
    const handlePopState = () => {
      setCurrentRoute(getInitialRoute());
    };
    window.addEventListener('popstate', handlePopState);
    return () => window.removeEventListener('popstate', handlePopState);
  }, []);

  return (
    <RouteContext.Provider value={{ currentRoute, navigate }}>
      {children}
    </RouteContext.Provider>
  );
};
