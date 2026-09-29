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
      className={`w-full max-w-[1240px] mx-auto px-5 sm:px-8 lg:px-12 py-16 sm:py-24 ${className}`}
    >
      {children}
    </Component>
  );
};
