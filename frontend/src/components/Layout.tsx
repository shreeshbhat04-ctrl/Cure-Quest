import React from 'react';
import { motion } from 'motion/react';
import { Bell, Brain, Grid2X2, Map, Pill, History, Sparkles } from 'lucide-react';

type TabId = 'dashboard' | 'care-maze' | 'medications' | 'hitl' | 'history';

interface LayoutProps {
  children: React.ReactNode;
  activeTab: TabId;
  onTabChange: (tab: TabId) => void;
  patientName: string;
  onRefresh: () => void;
  loading: boolean;
}

export const Layout: React.FC<LayoutProps> = ({
  children,
  activeTab,
  onTabChange,
  patientName,
  onRefresh,
  loading,
}) => {
  const tabs: Array<{ id: TabId; icon: React.ComponentType<{ className?: string }>; label: string }> = [
    { id: 'dashboard', icon: Grid2X2, label: 'Dashboard' },
    { id: 'care-maze', icon: Map, label: 'Care Maze' },
    { id: 'medications', icon: Pill, label: 'Meds' },
    { id: 'hitl', icon: Brain, label: 'HITL' },
    { id: 'history', icon: History, label: 'History' },
  ];

  return (
    <div className="min-h-screen bg-surface text-on-surface relative overflow-hidden">
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_top_right,rgba(213,235,170,0.32),transparent_32%),radial-gradient(circle_at_15%_55%,rgba(253,179,143,0.15),transparent_24%)]" />
      <div className="pointer-events-none absolute right-[-7rem] top-[-4rem] h-80 w-80 rounded-full bg-primary-fixed/25 blur-3xl" />
      <div className="pointer-events-none absolute left-[-6rem] top-[38%] h-72 w-72 rounded-full bg-tertiary-container/12 blur-3xl" />

      <div className="relative z-10 mx-auto flex min-h-screen w-full max-w-[1440px] flex-col px-6 pb-28 pt-6 md:px-8 md:pb-10 xl:px-10 2xl:px-12">
        <header className="glass mb-8 flex items-center justify-between rounded-[2rem] px-6 py-4 shadow-[0_12px_32px_-4px_rgba(27,28,21,0.06)] md:px-8">
          <div className="flex items-center gap-4">
            <div className="flex h-13 w-13 items-center justify-center rounded-[1.45rem] bg-gradient-to-br from-primary to-primary-container text-surface shadow-[0_10px_22px_-6px_rgba(83,100,49,0.45)]">
              <Sparkles className="h-5 w-5" />
            </div>
            <div>
              <p className="font-serif text-[1.7rem] font-semibold tracking-[-0.02em] text-primary">Cure-Quest</p>
              <p className="text-[0.92rem] leading-6 text-on-surface/50">Digital sanctuary for {patientName}</p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={onRefresh}
              className="river-stone-btn bg-surface-container-low px-5 py-3 text-[0.92rem] text-on-surface/72 hover:bg-surface-container-high"
            >
              {loading ? 'Refreshing...' : 'Refresh'}
            </button>
            <button className="flex h-12 w-12 items-center justify-center rounded-full bg-surface-container-low text-on-surface/70 transition-colors hover:bg-surface-container-high">
              <Bell className="h-5 w-5" />
            </button>
          </div>
        </header>

        <div className="grid flex-1 gap-8 xl:grid-cols-[260px_minmax(0,1fr)] 2xl:grid-cols-[280px_minmax(0,1fr)]">
          <aside className="hidden lg:flex lg:flex-col">
            <div className="glass flex h-full flex-col rounded-[2rem] px-5 py-6 shadow-[0_12px_32px_-4px_rgba(27,28,21,0.06)]">
              <div className="mb-9 px-2">
                <h2 className="font-serif text-[1.2rem] text-primary">Nurturing Navigation</h2>
                <p className="mt-1 text-[0.9rem] leading-6 text-on-surface/50">The Digital Sanctuary</p>
              </div>

              <nav className="space-y-2.5">
                {tabs.map((tab) => {
                  const isActive = tab.id === activeTab;
                  return (
                    <button
                      key={tab.id}
                      onClick={() => onTabChange(tab.id)}
                      className={`flex w-full items-center gap-3 rounded-[1.35rem] px-4 py-3.5 text-left transition-all duration-200 ${
                        isActive
                          ? 'bg-primary-fixed/45 text-primary shadow-[0_10px_24px_-14px_rgba(83,100,49,0.5)]'
                          : 'text-on-surface/55 hover:bg-surface-container-low hover:text-primary'
                      }`}
                    >
                      <tab.icon className="h-5 w-5" />
                      <span className="text-[0.95rem] font-medium">{tab.label}</span>
                    </button>
                  );
                })}
              </nav>

              <div className="mt-auto rounded-[2rem] bg-tertiary-container/18 px-5 py-6">
                <p className="mb-2 font-serif text-[1.15rem] text-tertiary">Quietly coordinated</p>
                <p className="text-[0.95rem] leading-7 text-on-surface/60">
                  Your reminders, documents, escalations, and doctor touchpoints are gathered in one place.
                </p>
              </div>
            </div>
          </aside>

          <main className="min-w-0 w-full">{children}</main>
        </div>
      </div>

      <nav className="glass fixed bottom-5 left-1/2 z-50 flex w-[92%] max-w-lg -translate-x-1/2 items-center justify-between rounded-[3rem] p-2 shadow-[0_18px_40px_-18px_rgba(27,28,21,0.25)] lg:hidden">
        {tabs.map((tab) => {
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => onTabChange(tab.id)}
              className={`relative flex flex-1 items-center justify-center rounded-full px-2 py-3 transition-colors ${
                isActive ? 'text-primary' : 'text-on-surface/45'
              }`}
            >
              {isActive && (
                <motion.div
                  layoutId="mobile-tab"
                  className="absolute inset-0 rounded-full bg-primary-fixed/35"
                  transition={{ type: 'spring', duration: 0.5, bounce: 0.18 }}
                />
              )}
              <tab.icon className="relative z-10 h-5 w-5" />
            </button>
          );
        })}
      </nav>
    </div>
  );
};

export type { TabId };
