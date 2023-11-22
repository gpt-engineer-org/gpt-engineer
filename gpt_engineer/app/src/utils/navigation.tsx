import { IRoute } from '@/types/navigation';
// NextJS Requirement
export const isWindowAvailable = () => typeof window !== 'undefined';

export const findCurrentRoute = (
  routes: IRoute[],
  pathname: string,
): IRoute | undefined => {
  for (let route of routes) {
    if (route.items) {
      const found = findCurrentRoute(route.items, pathname);
      if (found) return found;
    }
    if (pathname?.match(route.path) && route) {
      return route;
    }
  }
};

export const getActiveRoute = (routes: IRoute[], pathname: string): string => {
  const route = findCurrentRoute(routes, pathname);
  return route?.name || 'Default Brand Text';
};

export const getActiveNavbar = (
  routes: IRoute[],
  pathname: string,
): boolean => {
  const route = findCurrentRoute(routes, pathname);
  if (route?.secondary) return route?.secondary;
  else return false;
};

export const getActiveNavbarText = (
  routes: IRoute[],
  pathname: string,
): string | boolean => {
  return getActiveRoute(routes, pathname) || false;
};
