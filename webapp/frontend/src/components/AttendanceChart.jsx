import React from 'react';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, Legend } from 'recharts';

const AttendanceChart = ({ data }) => (
  <div className="h-80 w-full">
    <ResponsiveContainer width="100%" height="100%">
      <BarChart data={data}>
        <XAxis dataKey="event_name" stroke="#94a3b8" tick={{ fill: '#94a3b8' }} />
        <YAxis stroke="#94a3b8" tick={{ fill: '#94a3b8' }} allowDecimals={false} />
        <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b', color: '#f8fafc' }} />
        <Legend />
        <Bar dataKey="present" stackId="a" fill="#22c55e" name="Present" />
        <Bar dataKey="late" stackId="a" fill="#f59e0b" name="Late" />
        <Bar dataKey="absent" stackId="a" fill="#ef4444" name="Absent" />
      </BarChart>
    </ResponsiveContainer>
  </div>
);

export default AttendanceChart;
