import { AppRoute } from '../app/routes';

export type { AppRoute };

export interface NavItem {
  id: string;
  label: string;
  path: AppRoute;
  isAction?: boolean;
}
