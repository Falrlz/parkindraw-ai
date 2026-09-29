import React from 'react';
import { Navbar } from '../../components/shared/Navbar';
import { Footer } from '../../components/shared/Footer';

export const RootLayout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return (
    <div className="min-h-screen flex flex-col bg-ground text-ink font-sans antialiased">
      {/* Skip to Content for Accessibility */}
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:fixed focus:top-3 focus:left-3 focus:z-50 focus:px-4 focus:py-3 focus:bg-ink-fill focus:text-white focus:rounded-md"
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
