import React, { useEffect, useState } from 'react';
import { ArrowRight, Menu, X } from 'lucide-react';
import { useRoute } from '../../app/AppRouter';
import { useLocalized } from '../../app/localeContext';
import { navigationContent } from '../../content/navigation.content';
import { uiContent } from '../../content/ui.content';
import { BrandMark } from '../brand/BrandMark';
import { LanguageSwitch } from './LanguageSwitch';
import { SettingsMenu } from './SettingsMenu';
import { ThemeSwitch } from './ThemeSwitch';

export const Navbar: React.FC = () => {
  const { currentRoute, navigate } = useRoute();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const { brand, menuItems } = useLocalized(navigationContent);
  const { settings, nav } = useLocalized(uiContent);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 8);
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  const go = (path: (typeof menuItems)[number]['path']) => {
    navigate(path);
    setMobileMenuOpen(false);
  };

  return (
    <header
      className={`no-print sticky top-0 z-40 transition-[background-color,border-color,box-shadow] duration-300 border-b ${
        scrolled || mobileMenuOpen
          ? 'bg-ground/95 border-line shadow-[0_6px_24px_-18px_rgba(27,21,71,0.35)]'
          : 'bg-transparent border-transparent'
      }`}
    >
      <div className="relative max-w-[1240px] mx-auto px-5 sm:px-8 lg:px-12 h-[72px] flex items-center justify-between gap-6">
        <button
          type="button"
          onClick={() => go('/')}
          className="flex items-center gap-3 text-left cursor-pointer group rounded-md"
          aria-label={`${brand.title}, ${brand.tagline}`}
        >
          <BrandMark className="w-9 h-9" />
          <span className="flex flex-col leading-none">
            <span className="text-lg font-semibold tracking-[-0.02em] text-ink">{brand.title}</span>
            <span className="mt-1 text-xs text-muted">{brand.tagline}</span>
          </span>
        </button>

        {/* Centred so the hero ribbon passing behind the right edge never crosses a label */}
        <nav className="hidden md:flex absolute left-1/2 -translate-x-1/2 items-center gap-8" aria-label={nav.mainLabel}>
          {menuItems.map((item) => {
            const isActive = currentRoute === item.path;
            return (
              <button
                key={item.id}
                type="button"
                aria-current={isActive ? 'page' : undefined}
                onClick={() => go(item.path)}
                className={`relative py-2 text-[15px] font-medium transition-colors cursor-pointer after:absolute after:left-0 after:right-0 after:-bottom-0.5 after:h-0.5 after:rounded-full after:transition-transform after:duration-300 after:origin-left ${
                  isActive
                    ? 'text-iris after:bg-iris after:scale-x-100'
                    : 'text-ink hover:text-iris after:bg-iris after:scale-x-0'
                }`}
              >
                {item.label}
              </button>
            );
          })}
        </nav>

        {/* Settings (language, theme) on the right edge (desktop); on phones they live inside the menu */}
        <div className="hidden md:block -mr-2">
          <SettingsMenu />
        </div>

        <button
          type="button"
          aria-expanded={mobileMenuOpen}
          aria-controls="mobile-nav"
          aria-label={mobileMenuOpen ? nav.closeMenu : nav.openMenu}
          onClick={() => setMobileMenuOpen((prev) => !prev)}
          className="md:hidden w-11 h-11 -mr-2 flex items-center justify-center text-ink rounded-md hover:bg-iris-wash cursor-pointer"
        >
          {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
        </button>
      </div>

      {mobileMenuOpen && (
        <nav
          id="mobile-nav"
          className="md:hidden border-t border-line bg-ground px-5 pt-2 pb-6"
          aria-label={nav.mobileLabel}
        >
          <ul>
            {menuItems.map((item) => {
              const isActive = currentRoute === item.path;
              return (
                <li key={item.id} className="border-b border-line">
                  <button
                    type="button"
                    aria-current={isActive ? 'page' : undefined}
                    onClick={() => go(item.path)}
                    className={`w-full flex items-center justify-between py-4 text-2xl font-medium tracking-[-0.02em] cursor-pointer ${
                      isActive ? 'text-iris' : 'text-ink'
                    }`}
                  >
                    {item.label}
                    <ArrowRight className="w-5 h-5" aria-hidden="true" />
                  </button>
                </li>
              );
            })}
          </ul>

          <div className="mt-6">
            <p className="text-base font-semibold text-ink">{settings.title}</p>
            <p className="mt-3 mb-2 text-sm text-muted">{settings.language}</p>
            <LanguageSwitch />
            <p className="mt-5 mb-2 text-sm text-muted">{settings.theme}</p>
            <ThemeSwitch />
          </div>
        </nav>
      )}
    </header>
  );
};
