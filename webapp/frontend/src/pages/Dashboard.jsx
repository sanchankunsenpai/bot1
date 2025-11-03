import React, { useEffect, useState } from 'react';
import { ArrowTrendingUpIcon, GiftIcon, UsersIcon } from '@heroicons/react/24/outline';
import StatsCard from '../components/StatsCard.jsx';
import AttendanceChart from '../components/AttendanceChart.jsx';
import { fetchAlliances } from '../api/alliances';
import { fetchEvents, fetchAttendanceSummary } from '../api/events';
import { fetchGiftCodes } from '../api/giftCodes';

const Dashboard = () => {
  const [alliances, setAlliances] = useState([]);
  const [events, setEvents] = useState([]);
  const [giftCodes, setGiftCodes] = useState([]);
  const [summary, setSummary] = useState([]);

  useEffect(() => {
    const load = async () => {
      const allianceData = await fetchAlliances();
      setAlliances(allianceData);
      setGiftCodes(await fetchGiftCodes());
      const eventsData = await fetchEvents();
      setEvents(eventsData);
      if (allianceData.length) {
        setSummary(await fetchAttendanceSummary(allianceData[0].id));
      }
    };
    load();
  }, []);

  return (
    <div className="space-y-6">
      <div className="grid gap-4 md:grid-cols-3">
        <StatsCard
          title="Active Alliances"
          value={alliances.length}
          description="Total alliances configured in the control center."
          icon={UsersIcon}
        />
        <StatsCard
          title="Scheduled Events"
          value={events.length}
          description="Events across all alliances in the next cycle."
          icon={ArrowTrendingUpIcon}
        />
        <StatsCard
          title="Tracked Gift Codes"
          value={giftCodes.length}
          description="Gift codes awaiting redemption review."
          icon={GiftIcon}
        />
      </div>

      <section className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold text-white">Attendance Overview</h2>
            <p className="text-sm text-slate-400">Summary for the most active alliance.</p>
          </div>
        </div>
        {summary.length ? (
          <AttendanceChart data={summary} />
        ) : (
          <p className="mt-6 text-sm text-slate-400">Attendance data will appear once events are recorded.</p>
        )}
      </section>
    </div>
  );
};

export default Dashboard;
