export type AppRoute = '/' | '/screening' | '/about' | '/faq';

export const ROUTES: Record<string, AppRoute> = {
  HOME: '/',
  SCREENING: '/screening',
  ABOUT: '/about',
  FAQ: '/faq',
};
