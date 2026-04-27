import React, { useState } from 'react';
import { motion } from 'motion/react';
import { Bell, Brain, Grid2X2, Map, Pill, History, Stethoscope, Info, User, ShoppingCart } from 'lucide-react';
import logo from '../assets/logo.png';


type TabId = 'dashboard' | 'care-maze' | 'medications' | 'marketplace' | 'hitl' | 'history' | 'about';

interface LayoutProps {
  children: React.ReactNode;
  activeTab: TabId;
  onTabChange: (tab: TabId) => void;
  patientName: string;
  onRefresh: () => void;
  loading: boolean;
  onRoleChange?: () => void;
}

export const Layout: React.FC<LayoutProps> = ({
  children,
  activeTab,
  onTabChange,
  patientName,
  onRefresh,
  loading,
  onRoleChange,
}) => {
  const [profileOpen, setProfileOpen] = useState(false);
  const tabs: Array<{ id: TabId; icon: React.ComponentType<{ className?: string }>; label: string }> = [
    { id: 'dashboard', icon: Grid2X2, label: 'Dashboard' },
    { id: 'care-maze', icon: Map, label: 'Care Maze' },
    { id: 'medications', icon: Pill, label: 'Meds' },
    { id: 'marketplace', icon: ShoppingCart, label: 'Market' },
    { id: 'hitl', icon: Stethoscope, label: 'Doctors' },
    { id: 'history', icon: History, label: 'History' },
    { id: 'about', icon: Info, label: 'About' },
  ];

  const isDashboard = activeTab === 'dashboard';
  const isMarketplace = activeTab === 'marketplace';

  return (
    <div className="cq-app-frame flex min-h-screen w-full flex-col app-background-image relative overflow-x-hidden">
      {/* Background Overlay */}
      <div className={`absolute inset-0 transition-colors duration-500 z-0 ${(isDashboard || isMarketplace) ? 'overlay-bright' : 'overlay-dim'}`} />

      <div className="cq-app-inner relative z-10 grid min-h-screen w-full grid-rows-[auto_minmax(0,1fr)] px-6 pb-28 pt-6 md:px-8 md:pb-10 lg:px-10 2xl:px-12">
        <header className="glass relative z-50 mb-6 flex min-w-0 items-center justify-between rounded-[2rem] p-6 shadow-[0_12px_32px_-4px_rgba(27,28,21,0.06)]">
          {/* Left: Logo */}
          <div className="flex flex-[1.5] items-center gap-4 min-w-0">
            <div className="flex h-13 w-13 items-center justify-center shrink-0 rounded-[1.45rem] bg-surface-container-lowest shadow-[0_10px_22px_-6px_rgba(83,100,49,0.45)] overflow-hidden">
              <img src={logo} alt="Cure-Quest" className="h-9 w-9 object-contain" />
            </div>
            <div className="hidden md:block truncate">
              <p className="font-serif text-[1.7rem] font-semibold tracking-[-0.02em] text-primary truncate">Cure-Quest</p>
              <p className="text-[0.92rem] leading-6 text-on-surface/50 truncate">Digital sanctuary for {patientName}</p>
            </div>
          </div>

          {/* Center: Navigation tabs */}
          <div className="flex flex-1 justify-center shrink-0 px-4">
            <nav className="hidden items-center justify-center gap-1.5 rounded-[1.75rem] bg-surface-container-low/50 p-1.5 lg:flex">
              {tabs.map((tab) => {
                const isActive = tab.id === activeTab;
                return (
                  <button
                    key={tab.id}
                    onClick={() => onTabChange(tab.id)}
                    className={`relative flex items-center justify-center gap-2 rounded-[1.25rem] px-5 py-3 text-[0.92rem] font-medium transition-all duration-200 whitespace-nowrap ${
                      isActive
                        ? 'bg-primary-fixed/45 text-primary shadow-[0_6px_16px_-8px_rgba(83,100,49,0.5)]'
                        : 'text-on-surface/55 hover:bg-surface-container-lowest hover:text-primary'
                    }`}
                  >
                    <tab.icon className="h-4 w-4 shrink-0" />
                    <span>{tab.label}</span>
                  </button>
                );
              })}
            </nav>
          </div>

          {/* Right: Actions */}
          <div className="relative flex flex-[0.5] items-center justify-end gap-3 min-w-0">
            <button className="relative flex h-12 w-12 items-center justify-center rounded-full bg-surface-container-low text-on-surface/70 transition-colors hover:bg-surface-container-high">
              <ShoppingCart className="h-5 w-5" />
              <span className="absolute -top-1 -right-1 flex h-4 w-4 items-center justify-center rounded-full bg-terracotta text-[10px] font-bold text-white">3</span>
            </button>
            <button
              onClick={() => setProfileOpen(!profileOpen)}
              className="flex h-12 w-12 items-center justify-center rounded-full bg-surface-container-low text-on-surface/70 transition-colors hover:bg-surface-container-high"
            >
              <User className="h-5 w-5" />
            </button>

            {profileOpen && (
              <div className="absolute right-0 top-[3.5rem] w-64 rounded-2xl bg-surface-container-low p-4 shadow-xl border border-outline-variant/30 z-50">
                <div className="flex flex-col items-center">
                  <div className="h-14 w-14 rounded-full bg-primary-container text-on-primary-container flex items-center justify-center text-xl font-medium mb-3">
                    {patientName.charAt(0)}
                  </div>
                  <h3 className="font-serif font-medium text-lg text-on-surface">{patientName}</h3>
                  <p className="text-sm text-on-surface/60 mb-4">Patient Profile</p>
                  
                  <div className="w-full h-px bg-outline-variant/30 mb-2"></div>
                  
                  <button className="w-full py-2 text-sm text-left text-on-surface/70 hover:text-primary transition-colors">
                    Account Settings
                  </button>
                  {onRoleChange && (
                    <button 
                      onClick={onRoleChange}
                      className="w-full py-2 text-sm text-left text-primary hover:text-primary/80 transition-colors font-medium"
                    >
                      Switch to Provider Portal
                    </button>
                  )}
                  <button className="w-full py-2 text-sm text-left text-terracotta hover:text-terracotta/80 transition-colors">
                    Sign Out
                  </button>
                </div>
              </div>
            )}
          </div>
        </header>

        <main className="min-h-0 min-w-0 w-full">{children}</main>
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
