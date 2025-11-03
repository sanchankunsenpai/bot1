import React, { useEffect, useMemo, useState } from 'react';
import dayjs from 'dayjs';
import { fetchAlliances } from '../api/alliances';
import { createEvent, deleteEvent, fetchAttendance, fetchEvents, updateAttendance } from '../api/events';
import { fetchMembers } from '../api/members';

const emptyForm = {
  name: '',
  description: '',
  start_time: dayjs().format('YYYY-MM-DDTHH:mm'),
  end_time: '',
  reminder_minutes: 60,
  alliance_id: ''
};

const statusOptions = [
  { value: 'present', label: 'Present' },
  { value: 'late', label: 'Late' },
  { value: 'absent', label: 'Absent' }
];

const Events = () => {
  const [alliances, setAlliances] = useState([]);
  const [events, setEvents] = useState([]);
  const [form, setForm] = useState(emptyForm);
  const [selectedEvent, setSelectedEvent] = useState(null);
  const [attendance, setAttendance] = useState([]);
  const [members, setMembers] = useState([]);

  const loadEvents = async () => {
    const data = await fetchEvents();
    setEvents(data);
    return data;
  };

  useEffect(() => {
    const load = async () => {
      const allianceData = await fetchAlliances();
      setAlliances(allianceData);
      if (allianceData.length && !form.alliance_id) {
        setForm((prev) => ({ ...prev, alliance_id: String(allianceData[0].id) }));
      }
      const eventData = await loadEvents();
      if (eventData.length) {
        await selectEvent(eventData[0]);
      }
    };
    load();
  }, []);

  const selectEvent = async (event) => {
    setSelectedEvent(event);
    if (event?.alliance_id) {
      const roster = await fetchMembers(event.alliance_id);
      setMembers(roster);
    } else {
      setMembers([]);
    }
    if (event) {
      const data = await fetchAttendance(event.id);
      setAttendance(data);
    } else {
      setAttendance([]);
    }
  };

  const attendanceMap = useMemo(() => {
    const map = new Map();
    attendance.forEach((entry) => {
      map.set(entry.member_id, entry.status);
    });
    return map;
  }, [attendance]);

  const handleSubmit = async (event) => {
    event.preventDefault();
    const payload = {
      name: form.name,
      description: form.description || null,
      start_time: dayjs(form.start_time).toISOString(),
      end_time: form.end_time ? dayjs(form.end_time).toISOString() : null,
      reminder_minutes: Number(form.reminder_minutes),
      alliance_id: form.alliance_id ? Number(form.alliance_id) : null
    };
    await createEvent(payload);
    setForm(emptyForm);
    const data = await loadEvents();
    if (data.length) {
      await selectEvent(data[0]);
    }
  };

  const handleAttendanceChange = (memberId, status) => {
    setAttendance((prev) => {
      const other = prev.filter((entry) => entry.member_id !== memberId);
      return [...other, { member_id: memberId, status }];
    });
  };

  const handleAttendanceSave = async () => {
    if (!selectedEvent) return;
    await updateAttendance(
      selectedEvent.id,
      members.map((member) => ({
        member_id: member.id,
        status: attendanceMap.get(member.id) || 'absent'
      }))
    );
    const data = await fetchAttendance(selectedEvent.id);
    setAttendance(data);
  };

  return (
    <div className="space-y-6">
      <section className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
        <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <div>
            <h2 className="text-lg font-semibold text-white">Events</h2>
            <p className="text-sm text-slate-400">Schedule reminders and track attendance directly from the web app.</p>
          </div>
          <div className="flex gap-2">
            {events.map((event) => (
              <button
                key={event.id}
                type="button"
                className={`rounded-md px-3 py-2 text-sm ${
                  selectedEvent?.id === event.id
                    ? 'bg-brand-500 text-white'
                    : 'border border-slate-700 text-slate-300 hover:bg-slate-800'
                }`}
                onClick={() => selectEvent(event)}
              >
                {event.name}
              </button>
            ))}
          </div>
        </div>

        {selectedEvent ? (
          <div className="mt-6 rounded-xl border border-slate-800 bg-slate-900/60 p-4">
            <div className="flex flex-col gap-2 text-sm text-slate-300 md:flex-row md:items-center md:justify-between">
              <div>
                <p className="text-lg font-semibold text-white">{selectedEvent.name}</p>
                <p>{selectedEvent.description}</p>
                <p className="text-xs text-slate-400">
                  {dayjs(selectedEvent.start_time).format('MMM D, YYYY HH:mm')} →{' '}
                  {selectedEvent.end_time ? dayjs(selectedEvent.end_time).format('MMM D, YYYY HH:mm') : 'TBD'}
                </p>
              </div>
              <button
                type="button"
                className="rounded-md border border-red-500 px-3 py-2 text-xs text-red-300 hover:bg-red-500/20"
                onClick={async () => {
                  await deleteEvent(selectedEvent.id);
                  const data = await loadEvents();
                  await selectEvent(data[0] ?? null);
                }}
              >
                Delete event
              </button>
            </div>

            <div className="mt-4 overflow-x-auto">
              <table className="min-w-full divide-y divide-slate-800 text-sm">
                <thead>
                  <tr className="text-left text-xs uppercase text-slate-400">
                    <th className="px-4 py-2">Member</th>
                    <th className="px-4 py-2">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800 text-slate-200">
                  {members.map((member) => (
                    <tr key={member.id}>
                      <td className="px-4 py-2">{member.name}</td>
                      <td className="px-4 py-2">
                        <select
                          className="rounded-md border border-slate-700 bg-slate-900 px-3 py-1 text-sm text-white focus:border-brand-400 focus:outline-none"
                          value={attendanceMap.get(member.id) || 'absent'}
                          onChange={(event) => handleAttendanceChange(member.id, event.target.value)}
                        >
                          {statusOptions.map((option) => (
                            <option key={option.value} value={option.value}>
                              {option.label}
                            </option>
                          ))}
                        </select>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <div className="mt-4 flex justify-end">
              <button
                type="button"
                className="rounded-md bg-brand-500 px-4 py-2 text-sm font-medium text-white hover:bg-brand-400"
                onClick={handleAttendanceSave}
              >
                Save attendance
              </button>
            </div>
          </div>
        ) : (
          <p className="mt-6 text-sm text-slate-400">Create an event to begin tracking attendance.</p>
        )}
      </section>

      <section className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
        <h2 className="text-lg font-semibold text-white">Schedule new event</h2>
        <form className="mt-4 grid gap-4 md:grid-cols-2" onSubmit={handleSubmit}>
          <div>
            <label className="block text-sm text-slate-400" htmlFor="name">
              Event name
            </label>
            <input
              id="name"
              name="name"
              value={form.name}
              required
              onChange={(event) => setForm((prev) => ({ ...prev, name: event.target.value }))}
              className="mt-1 w-full rounded-md border border-slate-700 bg-slate-900 px-3 py-2 text-white focus:border-brand-400 focus:outline-none"
            />
          </div>
          <div>
            <label className="block text-sm text-slate-400" htmlFor="alliance_id">
              Alliance
            </label>
            <select
              id="alliance_id"
              value={form.alliance_id}
              required
              onChange={(event) => setForm((prev) => ({ ...prev, alliance_id: event.target.value }))}
              className="mt-1 w-full rounded-md border border-slate-700 bg-slate-900 px-3 py-2 text-white focus:border-brand-400 focus:outline-none"
            >
              <option value="">Select alliance</option>
              {alliances.map((alliance) => (
                <option key={alliance.id} value={alliance.id}>
                  {alliance.name}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm text-slate-400" htmlFor="start_time">
              Start time
            </label>
            <input
              id="start_time"
              type="datetime-local"
              value={form.start_time}
              onChange={(event) => setForm((prev) => ({ ...prev, start_time: event.target.value }))}
              className="mt-1 w-full rounded-md border border-slate-700 bg-slate-900 px-3 py-2 text-white focus:border-brand-400 focus:outline-none"
            />
          </div>
          <div>
            <label className="block text-sm text-slate-400" htmlFor="end_time">
              End time (optional)
            </label>
            <input
              id="end_time"
              type="datetime-local"
              value={form.end_time}
              onChange={(event) => setForm((prev) => ({ ...prev, end_time: event.target.value }))}
              className="mt-1 w-full rounded-md border border-slate-700 bg-slate-900 px-3 py-2 text-white focus:border-brand-400 focus:outline-none"
            />
          </div>
          <div>
            <label className="block text-sm text-slate-400" htmlFor="reminder_minutes">
              Reminder lead (minutes)
            </label>
            <input
              id="reminder_minutes"
              type="number"
              min="0"
              value={form.reminder_minutes}
              onChange={(event) => setForm((prev) => ({ ...prev, reminder_minutes: event.target.value }))}
              className="mt-1 w-full rounded-md border border-slate-700 bg-slate-900 px-3 py-2 text-white focus:border-brand-400 focus:outline-none"
            />
          </div>
          <div className="md:col-span-2">
            <label className="block text-sm text-slate-400" htmlFor="description">
              Description
            </label>
            <textarea
              id="description"
              value={form.description}
              onChange={(event) => setForm((prev) => ({ ...prev, description: event.target.value }))}
              className="mt-1 w-full rounded-md border border-slate-700 bg-slate-900 px-3 py-2 text-white focus:border-brand-400 focus:outline-none"
            />
          </div>
          <div className="md:col-span-2 flex justify-end">
            <button
              type="submit"
              className="rounded-md bg-brand-500 px-4 py-2 text-sm font-medium text-white hover:bg-brand-400"
            >
              Schedule event
            </button>
          </div>
        </form>
      </section>
    </div>
  );
};

export default Events;
