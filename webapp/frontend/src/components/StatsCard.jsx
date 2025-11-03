import React from 'react';

const StatsCard = ({ title, value, description, icon: Icon }) => (
  <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-5 shadow-sm">
    <div className="flex items-center justify-between">
      <div>
        <p className="text-sm text-slate-400">{title}</p>
        <p className="mt-2 text-3xl font-semibold text-white">{value}</p>
      </div>
      {Icon ? <Icon className="h-12 w-12 text-brand-400" /> : null}
    </div>
    {description ? <p className="mt-3 text-xs text-slate-500">{description}</p> : null}
  </div>
);

export default StatsCard;
