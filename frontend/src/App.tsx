import React from 'react';
import { RouteProvider, useRoute } from './app/AppRouter';
import { RootLayout } from './app/layouts/RootLayout';
import { HomePage } from './pages/HomePage';
import { ScreeningPage } from './pages/ScreeningPage';
import { AboutPage } from './pages/AboutPage';
import { FaqPage } from './pages/FaqPage';

const AppContent: React.FC = () => {
  const { currentRoute } = useRoute();

  const renderPage = () => {
    switch (currentRoute) {
      case '/screening':
        return <ScreeningPage />;
      case '/about':
        return <AboutPage />;
      case '/faq':
        return <FaqPage />;
      case '/':
      default:
        return <HomePage />;
    }
  };

  return <RootLayout>{renderPage()}</RootLayout>;
};

export default function App() {
  return (
    <RouteProvider>
      <AppContent />
    </RouteProvider>
  );
}
