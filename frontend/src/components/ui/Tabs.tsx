import React from 'react';

export interface TabItem {
  id: string;
  label: string;
  icon?: React.ReactNode;
}

export interface TabsProps {
  tabs: TabItem[];
  activeTab: string;
  onChange: (tabId: string) => void;
  className?: string;
}

export const Tabs: React.FC<TabsProps> = ({
  tabs,
  activeTab,
  onChange,
  className = '',
}) => {
  const handleKeyDown = (e: React.KeyboardEvent<HTMLDivElement>) => {
    if (e.key !== 'ArrowRight' && e.key !== 'ArrowLeft') return;
    const index = tabs.findIndex((t) => t.id === activeTab);
    const delta = e.key === 'ArrowRight' ? 1 : -1;
    const next = tabs[(index + delta + tabs.length) % tabs.length];
    onChange(next.id);
    const el = e.currentTarget.querySelector<HTMLButtonElement>(`[data-tab="${next.id}"]`);
    el?.focus();
  };

  return (
    <div
      role="tablist"
      onKeyDown={handleKeyDown}
      className={`inline-flex p-1 bg-paper border border-line rounded-lg gap-1 ${className}`}
    >
      {tabs.map((tab) => {
        const isActive = tab.id === activeTab;
        return (
          <button
            key={tab.id}
            role="tab"
            type="button"
            data-tab={tab.id}
            aria-selected={isActive}
            tabIndex={isActive ? 0 : -1}
            onClick={() => onChange(tab.id)}
            className={`inline-flex items-center justify-center gap-2 min-h-11 px-4 text-sm sm:text-[15px] font-medium rounded-md transition-colors duration-200 cursor-pointer ${
              isActive ? 'bg-ink-fill text-white' : 'text-body hover:text-ink hover:bg-ground'
            }`}
          >
            {tab.icon}
            <span>{tab.label}</span>
          </button>
        );
      })}
    </div>
  );
};
