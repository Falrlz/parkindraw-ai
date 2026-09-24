import React from 'react';

export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
}

export const Card: React.FC<CardProps> = ({ children, className = '', ...props }) => {
  return (
    <div
      {...props}
      className={`bg-white border border-slate-200 rounded-xl overflow-hidden ${className}`}
    >
      {children}
    </div>
  );
};

export const CardHeader: React.FC<CardProps> = ({ children, className = '', ...props }) => {
  return (
    <header {...props} className={`p-4 sm:p-5 border-b border-slate-100 ${className}`}>
      {children}
    </header>
  );
};

export const CardBody: React.FC<CardProps> = ({ children, className = '', ...props }) => {
  return (
    <div {...props} className={`p-4 sm:p-5 ${className}`}>
      {children}
    </div>
  );
};

export const CardFooter: React.FC<CardProps> = ({ children, className = '', ...props }) => {
  return (
    <footer {...props} className={`p-4 sm:p-5 border-t border-slate-100 bg-slate-50/50 ${className}`}>
      {children}
    </footer>
  );
};
