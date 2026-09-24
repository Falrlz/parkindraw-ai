import React from 'react';
import { Navbar } from '../../components/shared/Navbar';
import { Footer } from '../../components/shared/Footer';

export const RootLayout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return (
    <div className="min-h-screen flex flex-col bg-slate-50 text-slate-900 font-sans antialiased selection:bg-teal-100 selection:text-teal-900">
      {/* Skip to Content for Accessibility */}
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:fixed focus:top-2 focus:left-2 focus:z-50 focus:px-4 focus:py-2 focus:bg-teal-700 focus:text-white focus:rounded-md focus:shadow-md"
      >
        Lewati ke Konten Utama
      </a>

      <Navbar />

      <main id="main-content" className="flex-1 flex flex-col">
        {children}
      </main>

      <Footer />
    </div>
  );
};
