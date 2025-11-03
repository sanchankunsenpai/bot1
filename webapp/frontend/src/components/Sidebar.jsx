import React from 'react';
import { NavLink } from 'react-router-dom';
import clsx from 'classnames';
import {
  HomeIcon,
  UsersIcon,
  GiftIcon,
  CalendarDaysIcon,
  ClipboardDocumentCheckIcon,
  ChartPieIcon,
  Cog6ToothIcon
} from '@heroicons/react/24/outline';

const navigation = [
  { name: 'Dashboard', to: '/', icon: HomeIcon },
  { name: 'Alliances', to: '/alliances', icon: UsersIcon },
  { name: 'Members', to: '/members', icon: ClipboardDocumentCheckIcon },
  { name: 'Gift Codes', to: '/gift-codes', icon: GiftIcon },
  { name: 'Events', to: '/events', icon: CalendarDaysIcon },
  { name: 'Ministers', to: '/ministers', icon: ChartPieIcon },
  { name: 'Settings & Logs', to: '/settings', icon: Cog6ToothIcon }
];

const Sidebar = ({ variant = 'desktop', className }) => (
  <aside
    className={clsx(
      'flex w-64 flex-col border-r border-slate-800 bg-slate-950',
      variant === 'desktop' ? 'hidden lg:flex' : 'flex lg:hidden',
      className
    )}
  >
    <div className="px-6 py-8">
      <span className="text-2xl font-bold tracking-tight text-white">Whiteout Control</span>
      <p className="text-sm text-slate-400 mt-2">Alliance operations at a glance.</p>
    </div>
    <nav className="flex-1 px-3 pb-6 space-y-1">
      {navigation.map((item) => (
        <NavLink
          key={item.name}
          to={item.to}
          className={({ isActive }) =>
            `flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors ${
              isActive ? 'bg-brand-500/20 text-brand-100' : 'text-slate-300 hover:bg-slate-800 hover:text-white'
            }`
          }
        >
          <item.icon className="h-5 w-5" />
          {item.name}
        </NavLink>
      ))}
    </nav>
  </aside>
);

export default Sidebar;
