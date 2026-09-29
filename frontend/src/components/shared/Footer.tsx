import React from 'react';
import { useRoute } from '../../app/AppRouter';
import { navigationContent } from '../../content/navigation.content';

/** Same text size as the hero lede for every line; column titles carry the weight. */
const footerText = 'text-lg sm:text-xl short:text-[17px] leading-relaxed';

export const Footer: React.FC = () => {
  const { navigate } = useRoute();
  const { footer, menuItems, brand } = navigationContent;

  return (
    <footer className={`no-print mt-auto bg-ground border-t border-line text-body ${footerText}`}>
      <div className="max-w-[1240px] mx-auto px-5 sm:px-8 lg:px-12 pt-16 short:pt-12 pb-10 grid grid-cols-12 gap-x-6 gap-y-10">
        <div className="col-span-12 md:col-span-5 lg:col-span-4">
          <p className="font-semibold text-ink">{brand.title}</p>
          <p className="mt-3 max-w-[46ch]">{footer.brandDescription}</p>
        </div>

        <div className="col-span-12 sm:col-span-4 md:col-span-2 md:col-start-7 lg:col-start-6">
          <p className="font-semibold text-ink">{footer.navigationTitle}</p>
          <ul className="mt-3">
            {menuItems.map((item) => (
              <li key={item.id}>
                <button
                  type="button"
                  onClick={() => navigate(item.path)}
                  className="py-1 text-body hover:text-iris transition-colors cursor-pointer text-left"
                >
                  {item.label}
                </button>
              </li>
            ))}
          </ul>
        </div>

        <div className="col-span-12 sm:col-span-8 md:col-span-4 lg:col-span-5 lg:col-start-8">
          <p className="font-semibold text-ink">{footer.disclaimerTitle}</p>
          <p className="mt-3 max-w-[52ch]">{footer.disclaimerText}</p>
        </div>
      </div>

      <div className="max-w-[1240px] mx-auto px-5 sm:px-8 lg:px-12">
        <div className="border-t border-line py-6">
          <p>{footer.copyrightText}</p>
        </div>
      </div>
    </footer>
  );
};
