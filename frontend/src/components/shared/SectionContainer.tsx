import React from 'react';

export interface SectionContainerProps extends React.HTMLAttributes<HTMLElement> {
  children: React.ReactNode;
  as?: 'section' | 'article' | 'div';
}

export const SectionContainer: React.FC<SectionContainerProps> = ({
  children,
  as: Component = 'section',
  className = '',
  ...props
}) => {
  return (
    <Component
      {...props}
      className={`w-full max-w-5xl mx-auto px-4 sm:px-6 py-8 sm:py-12 ${className}`}
    >
      {children}
    </Component>
  );
};
