import React from 'react';

export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
}

export const Card: React.FC<CardProps> = ({ children, className = '', ...props }) => {
  return (
    <div
      {...props}
      className={`bg-paper border border-line rounded-[10px] overflow-hidden ${className}`}
    >
      {children}
    </div>
  );
};

export const CardHeader: React.FC<CardProps> = ({ children, className = '', ...props }) => {
  return (
    <header {...props} className={`px-5 pt-5 pb-4 sm:px-6 border-b border-line ${className}`}>
      {children}
    </header>
  );
};

export const CardBody: React.FC<CardProps> = ({ children, className = '', ...props }) => {
  return (
    <div {...props} className={`p-5 sm:p-6 ${className}`}>
      {children}
    </div>
  );
};

export const CardFooter: React.FC<CardProps> = ({ children, className = '', ...props }) => {
  return (
    <footer {...props} className={`px-5 py-4 sm:px-6 border-t border-line bg-ground ${className}`}>
      {children}
    </footer>
  );
};
