import React from 'react';
import { ShieldAlert } from 'lucide-react';
import { useRoute } from '../../app/AppRouter';
import { navigationContent } from '../../content/navigation.content';

export const Footer: React.FC = () => {
  const { navigate } = useRoute();
  const { footer, menuItems } = navigationContent;

  return (
    <footer className="border-t border-slate-200 bg-slate-100/70 text-slate-700 text-xs sm:text-sm mt-auto">
      <div className="max-w-5xl mx-auto px-4 sm:px-6 py-10 sm:py-12 grid grid-cols-1 md:grid-cols-12 gap-8">
        {/* Kolom 1: Visi ParkinDraw */}
        <div className="md:col-span-5">
          <p className="font-bold text-base text-slate-900 tracking-tight mb-2">
            ParkinDraw <span className="text-teal-700">AI</span>
          </p>
          <p className="text-slate-600 leading-relaxed text-xs sm:text-sm">
            {footer.brandDescription}
          </p>
        </div>

        {/* Kolom 2: Navigasi */}
        <div className="md:col-span-3">
          <p className="font-semibold text-slate-900 uppercase tracking-wider text-xs mb-3">
            {footer.navigationTitle}
          </p>
          <ul className="space-y-2">
            {menuItems.map((item) => (
              <li key={item.id}>
                <button
                  type="button"
                  onClick={() => navigate(item.path)}
                  className="text-slate-600 hover:text-teal-800 transition-colors cursor-pointer text-left"
                >
                  {item.label}
                </button>
              </li>
            ))}
          </ul>
        </div>

        {/* Kolom 3: Peringatan Medis Resmi */}
        <div className="md:col-span-4">
          <div className="flex items-center gap-1.5 text-amber-900 font-semibold mb-2">
            <ShieldAlert className="w-4 h-4 shrink-0 text-amber-700" aria-hidden="true" />
            <p className="text-xs uppercase tracking-wider">{footer.disclaimerTitle}</p>
          </div>
          <p className="text-slate-600 leading-relaxed text-xs">
            {footer.disclaimerText}
          </p>
        </div>
      </div>

      {/* Copyright */}
      <div className="border-t border-slate-200 py-4 text-center text-xs text-slate-500">
        <p>{footer.copyrightText}</p>
      </div>
    </footer>
  );
};
