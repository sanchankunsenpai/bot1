import React, { useEffect, useState } from 'react';
import dayjs from 'dayjs';
import { fetchAlliances } from '../api/alliances';
import { createMinister, deleteMinister, fetchMinisters, updateMinister } from '../api/ministers';

const emptyForm = {
  alliance_id: '',
  role: 'Construction',
  player_name: '',
  start_time: dayjs().format('YYYY-MM-DDTHH:mm'),
  end_time: dayjs().add(8, 'hour').format('YYYY-MM-DDTHH:mm'),
  notes: ''
};

const Ministers = () => {
  const [alliances, setAlliances] = useState([]);
  const [ministers, setMinisters] = useState([]);
  const [form, setForm] = useState(emptyForm);
  const [editingId, setEditingId] = useState(null);
  const [selectedAlliance, setSelectedAlliance] = useState('');

  const loadMinisters = async (allianceId) => {
    setMinisters(await fetchMinisters(allianceId || undefined));
  };

  useEffect(() => {
    const load = async () => {
      const allianceData = await fetchAlliances();
      setAlliances(allianceData);
      if (allianceData.length) {
        const firstId = String(allianceData[0].id);
        setSelectedAlliance(firstId);
        setForm((prev) => ({ ...prev, alliance_id: firstId }));
        loadMinisters(firstId);
      }
    };
    load();
  }, []);

  const handleSubmit = async (event) => {
    event.preventDefault();
    const payload = {
      alliance_id: form.alliance_id ? Number(form.alliance_id) : null,
      role: form.role,
      player_name: form.player_name,
      start_time: dayjs(form.start_time).toISOString(),
      end_time: dayjs(form.end_time).toISOString(),
      notes: form.notes || null
    };
    if (editingId) {
      await updateMinister(editingId, payload);
    } else {
      await createMinister(payload);
    }
    setEditingId(null);
    setForm((prev) => ({ ...emptyForm, alliance_id: form.alliance_id }));
    loadMinisters(form.alliance_id);
  };

  return (
    <div className="space-y-6">
      <section className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
        <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <div>
            <h2 className="text-lg font-semibold text-white">Minister schedule</h2>
            <p className="text-sm text-slate-400">Coordinate construction, research, and training slots.</p>
          </div>
          <select
            value={selectedAlliance}
            onChange={(event) => {
              const value = event.target.value;
              setSelectedAlliance(value);
              setForm((prev) => ({ ...prev, alliance_id: value }));
              loadMinisters(value);
            }}
            className="rounded-md border border-slate-700 bg-slate-900 px-3 py-2 text-sm text-white focus:border-brand-400 focus:outline-none"
          >
            {alliances.map((alliance) => (
              <option key={alliance.id} value={alliance.id}>
                {alliance.name}
              </option>
            ))}
          </select>
        </div>
        <div className="mt-6 overflow-x-auto">
          <table className="min-w-full divide-y divide-slate-800 text-sm">
            <thead>
              <tr className="text-left text-xs uppercase text-slate-400">
                <th className="px-4 py-2">Role</th>
                <th className="px-4 py-2">Player</th>
                <th className="px-4 py-2">Start</th>
                <th className="px-4 py-2">End</th>
                <th className="px-4 py-2">Notes</th>
                <th className="px-4 py-2"></th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800 text-slate-200">
              {ministers.map((minister) => (
                <tr key={minister.id}>
                  <td className="px-4 py-2 font-medium text-white">{minister.role}</td>
                  <td className="px-4 py-2">{minister.player_name}</td>
                  <td className="px-4 py-2">{dayjs(minister.start_time).format('MMM D HH:mm')}</td>
                  <td className="px-4 py-2">{dayjs(minister.end_time).format('MMM D HH:mm')}</td>
                  <td className="px-4 py-2">{minister.notes ?? '—'}</td>
                  <td className="px-4 py-2 text-right">
                    <div className="flex justify-end gap-2">
                      <button
                        type="button"
                        className="rounded-md border border-slate-700 px-3 py-1 text-xs text-slate-200 hover:bg-slate-800"
                        onClick={() => {
                          setEditingId(minister.id);
                          setForm({
                            alliance_id: minister.alliance_id ? String(minister.alliance_id) : '',
                            role: minister.role,
                            player_name: minister.player_name,
                            start_time: dayjs(minister.start_time).format('YYYY-MM-DDTHH:mm'),
                            end_time: dayjs(minister.end_time).format('YYYY-MM-DDTHH:mm'),
                            notes: minister.notes ?? ''
                          });
                        }}
                      >
                        Edit
                      </button>
                      <button
                        type="button"
                        className="rounded-md border border-red-500 px-3 py-1 text-xs text-red-300 hover:bg-red-500/20"
                        onClick={async () => {
                          await deleteMinister(minister.id);
                          loadMinisters(selectedAlliance);
                        }}
                      >
                        Remove
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
        <h2 className="text-lg font-semibold text-white">{editingId ? 'Update booking' : 'Book slot'}</h2>
        <form className="mt-4 grid gap-4 md:grid-cols-3" onSubmit={handleSubmit}>
          <div>
            <label className="block text-sm text-slate-400" htmlFor="alliance">
              Alliance
            </label>
            <select
              id="alliance"
              value={form.alliance_id}
              onChange={(event) => setForm((prev) => ({ ...prev, alliance_id: event.target.value }))}
              className="mt-1 w-full rounded-md border border-slate-700 bg-slate-900 px-3 py-2 text-white focus:border-brand-400 focus:outline-none"
            >
              <option value="">Global</option>
              {alliances.map((alliance) => (
                <option key={alliance.id} value={alliance.id}>
                  {alliance.name}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm text-slate-400" htmlFor="role">
              Role
            </label>
            <input
              id="role"
              value={form.role}
              onChange={(event) => setForm((prev) => ({ ...prev, role: event.target.value }))}
              className="mt-1 w-full rounded-md border border-slate-700 bg-slate-900 px-3 py-2 text-white focus:border-brand-400 focus:outline-none"
            />
          </div>
          <div>
            <label className="block text-sm text-slate-400" htmlFor="player_name">
              Player
            </label>
            <input
              id="player_name"
              value={form.player_name}
              required
              onChange={(event) => setForm((prev) => ({ ...prev, player_name: event.target.value }))}
              className="mt-1 w-full rounded-md border border-slate-700 bg-slate-900 px-3 py-2 text-white focus:border-brand-400 focus:outline-none"
            />
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
              End time
            </label>
            <input
              id="end_time"
              type="datetime-local"
              value={form.end_time}
              onChange={(event) => setForm((prev) => ({ ...prev, end_time: event.target.value }))}
              className="mt-1 w-full rounded-md border border-slate-700 bg-slate-900 px-3 py-2 text-white focus:border-brand-400 focus:outline-none"
            />
          </div>
          <div className="md:col-span-3">
            <label className="block text-sm text-slate-400" htmlFor="notes">
              Notes
            </label>
            <textarea
              id="notes"
              value={form.notes}
              onChange={(event) => setForm((prev) => ({ ...prev, notes: event.target.value }))}
              className="mt-1 w-full rounded-md border border-slate-700 bg-slate-900 px-3 py-2 text-white focus:border-brand-400 focus:outline-none"
            />
          </div>
          <div className="md:col-span-3 flex justify-end gap-2">
            {editingId ? (
              <button
                type="button"
                className="rounded-md border border-slate-700 px-4 py-2 text-sm text-slate-300 hover:bg-slate-800"
                onClick={() => {
                  setEditingId(null);
                  setForm((prev) => ({ ...emptyForm, alliance_id: selectedAlliance }));
                }}
              >
                Cancel
              </button>
            ) : null}
            <button
              type="submit"
              className="rounded-md bg-brand-500 px-4 py-2 text-sm font-medium text-white hover:bg-brand-400"
            >
              {editingId ? 'Update booking' : 'Book slot'}
            </button>
          </div>
        </form>
      </section>
    </div>
  );
};

export default Ministers;
