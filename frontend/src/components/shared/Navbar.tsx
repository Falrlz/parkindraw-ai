import React, { useState } from 'react';
import { Brain, Menu, X } from 'lucide-react';
import { useRoute } from '../../app/AppRouter';
import { navigationContent } from '../../content/navigation.content';

export const Navbar: React.FC = () => {
  const { currentRoute, navigate } = useRoute();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const { brand, menuItems } = navigationContent;

  return (
    <header className="sticky top-0 z-40 bg-white/95 border-b border-slate-200">
      <div className="max-w-5xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between">
        {/* Brand */}
        <button
          type="button"
          onClick={() => {
            navigate('/');
            setMobileMenuOpen(false);
          }}
          className="flex items-center gap-2.5 text-left cursor-pointer group"
        >
          <div className="w-8 h-8 rounded-lg bg-teal-700 flex items-center justify-center text-white" aria-hidden="true">
            <Brain className="w-5 h-5" />
          </div>
          <div>
            <span className="font-bold text-base text-slate-900 tracking-tight group-hover:text-teal-800 transition-colors">
              {brand.title}
            </span>
          </div>
        </button>

        {/* Desktop Navigation */}
        <nav className="hidden md:flex items-center gap-1" aria-label="Navigasi Utama">
          {menuItems.map((item) => {
            const isActive = currentRoute === item.path;
            return (
              <button
                key={item.id}
                type="button"
                aria-current={isActive ? 'page' : undefined}
                onClick={() => navigate(item.path)}
                className="px-3 py-1.5 rounded-md text-sm font-medium text-slate-600 hover:text-slate-900 hover:bg-slate-100 transition-colors cursor-pointer"
              >
                {item.label}
              </button>
            );
          })}
        </nav>

        {/* Mobile Toggle */}
        <div className="md:hidden flex items-center">
          <button
            type="button"
            aria-expanded={mobileMenuOpen}
            aria-label="Buka menu navigasi"
            onClick={() => setMobileMenuOpen((prev) => !prev)}
            className="p-1.5 text-slate-600 hover:text-slate-900 rounded-md hover:bg-slate-100 cursor-pointer"
          >
            {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
        </div>
      </div>

      {/* Mobile Menu Dropdown */}
      {mobileMenuOpen && (
        <nav
          className="md:hidden border-t border-slate-200 bg-white px-4 py-3 flex flex-col gap-1.5 shadow-xs"
          aria-label="Menu Navigasi Mobile"
        >
          {menuItems.map((item) => {
            const isActive = currentRoute === item.path;
            return (
              <button
                key={item.id}
                type="button"
                aria-current={isActive ? 'page' : undefined}
                onClick={() => {
                  navigate(item.path);
                  setMobileMenuOpen(false);
                }}
                className="text-left px-3 py-2 rounded-md text-sm font-medium text-slate-600 hover:text-slate-900 hover:bg-slate-50 transition-colors cursor-pointer"
              >
                {item.label}
              </button>
            );
          })}
        </nav>
      )}
    </header>
  );
};
