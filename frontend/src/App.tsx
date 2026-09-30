import React from 'react';
import { RouteProvider, useRoute } from './app/AppRouter';
import { LocaleProvider } from './app/LocaleProvider';
import { ThemeProvider } from './app/ThemeProvider';
import { RootLayout } from './app/layouts/RootLayout';
import { HomePage } from './pages/HomePage';
import { ScreeningPage } from './pages/ScreeningPage';
import { AboutPage } from './pages/AboutPage';

const AppContent: React.FC = () => {
  const { currentRoute } = useRoute();

  const renderPage = () => {
    switch (currentRoute) {
      case '/screening':
        return <ScreeningPage />;
      case '/about':
        return <AboutPage />;
      case '/':
      default:
        return <HomePage />;
    }
  };

  return <RootLayout>{renderPage()}</RootLayout>;
};

export default function App() {
  return (
    <ThemeProvider>
      <LocaleProvider>
        <RouteProvider>
          <AppContent />
        </RouteProvider>
      </LocaleProvider>
    </ThemeProvider>
  );
}
