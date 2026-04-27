import React from 'react';
import { motion } from 'motion/react';
import { Settings, Shield, Bell, CreditCard, LogOut, ChevronRight, User, Heart } from 'lucide-react';
import { patient2Image } from '../lib/api';

export const Profile: React.FC = () => {
  const settings = [
    { id: 'account', icon: User, label: 'Account Details', desc: 'Personal info, health profile' },
    { id: 'privacy', icon: Shield, label: 'Privacy & Security', desc: 'Data sharing, encryption' },
    { id: 'notifications', icon: Bell, label: 'Notifications', desc: 'Alerts, health reminders' },
    { id: 'billing', icon: CreditCard, label: 'Subscription', desc: 'Premium features, billing' },
  ];

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="space-y-12"
    >
      <section className="flex flex-col items-center text-center">
        <div className="relative mb-6 group">
          <div className="w-32 h-32 rounded-[3rem] overflow-hidden border-8 border-surface shadow-xl group-hover:scale-105 transition-transform duration-500">
            <img src={patient2Image} alt="Me" className="w-full h-full object-cover" />
          </div>
          <button className="absolute bottom-0 right-0 w-10 h-10 bg-primary rounded-full flex items-center justify-center text-surface border-4 border-surface shadow-md hover:bg-primary-container transition-colors">
            <Settings className="w-5 h-5" />
          </button>
        </div>
        <h1 className="text-3xl font-serif mb-1">Shreesh Bhat</h1>
        <p className="text-on-surface/40 text-sm font-sans uppercase tracking-widest">Primary Caregiver • Since 2024</p>
      </section>

      <section className="grid gap-4">
        {settings.map((item, i) => (
          <motion.div
            key={item.id}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: i * 0.1 }}
            className="nurture-card group cursor-pointer hover:shadow-xl transition-all p-6"
          >
            <div className="flex gap-6 items-center">
              <div className="w-12 h-12 rounded-2xl bg-surface-container-low flex items-center justify-center text-primary group-hover:bg-primary group-hover:text-surface transition-all">
                <item.icon className="w-6 h-6" />
              </div>
              <div className="flex-1">
                <h3 className="text-lg font-serif group-hover:text-primary transition-colors">{item.label}</h3>
                <p className="text-on-surface/40 text-xs font-sans">{item.desc}</p>
              </div>
              <ChevronRight className="w-5 h-5 text-on-surface/20 group-hover:text-primary transition-colors" />
            </div>
          </motion.div>
        ))}
      </section>

      <section className="bg-secondary-container/10 rounded-[2.5rem] p-8 flex flex-col items-center text-center gap-4">
        <div className="w-12 h-12 rounded-full bg-secondary-container/30 flex items-center justify-center text-secondary">
          <Heart className="w-6 h-6" />
        </div>
        <div>
          <h3 className="text-lg font-serif mb-1">Support the Hearth</h3>
          <p className="text-on-surface/60 text-sm leading-relaxed">Help us keep the sanctuary growing for families everywhere.</p>
        </div>
        <button className="text-secondary font-medium hover:underline">Learn more</button>
      </section>

      <button className="w-full py-6 rounded-[3rem] border-2 border-outline-variant text-on-surface/40 font-medium flex items-center justify-center gap-2 hover:text-secondary hover:border-secondary transition-all">
        <LogOut className="w-5 h-5" />
        <span>Sign Out</span>
      </button>
    </motion.div>
  );
};
