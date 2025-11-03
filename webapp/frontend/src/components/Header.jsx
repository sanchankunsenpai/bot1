import React from 'react';
import { Bars3Icon } from '@heroicons/react/24/outline';
import { useAuth } from '../context/AuthContext.jsx';

const Header = ({ onToggleSidebar }) => {
  const { user, logout } = useAuth();

  return (
    <header className="flex items-center justify-between border-b border-slate-800 bg-slate-950/70 px-4 py-3 backdrop-blur">
      <div className="flex items-center gap-2">
        <button
          type="button"
          className="lg:hidden inline-flex items-center justify-center rounded-md border border-slate-700 bg-slate-900 p-2 text-slate-200"
          onClick={onToggleSidebar}
        >
          <Bars3Icon className="h-6 w-6" />
        </button>
        <div>
          <p className="text-sm text-slate-400">Signed in as</p>
          <p className="text-base font-semibold text-white">{user?.username ?? 'Loading'}</p>
        </div>
      </div>
      <button
        type="button"
        onClick={logout}
        className="rounded-md bg-brand-500 px-4 py-2 text-sm font-medium text-white shadow hover:bg-brand-400"
      >
        Sign out
      </button>
    </header>
  );
};

export default Header;
