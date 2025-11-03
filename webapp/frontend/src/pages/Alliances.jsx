import React, { useEffect, useState } from 'react';
import { fetchAlliances, createAlliance, updateAlliance, deleteAlliance } from '../api/alliances';

const emptyForm = { name: '', discord_server_id: '', interval_minutes: 0 };

const Alliances = () => {
  const [alliances, setAlliances] = useState([]);
  const [form, setForm] = useState(emptyForm);
  const [editingId, setEditingId] = useState(null);

  const load = async () => {
    setAlliances(await fetchAlliances());
  };

  useEffect(() => {
    load();
  }, []);

  const handleChange = (event) => {
    const { name, value } = event.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    const payload = {
      name: form.name,
      discord_server_id: form.discord_server_id ? Number(form.discord_server_id) : null,
      interval_minutes: Number(form.interval_minutes)
    };
    if (editingId) {
      await updateAlliance(editingId, payload);
    } else {
      await createAlliance(payload);
    }
    setForm(emptyForm);
    setEditingId(null);
    load();
  };

  const startEdit = (alliance) => {
    setEditingId(alliance.id);
    setForm({
      name: alliance.name,
      discord_server_id: alliance.discord_server_id ?? '',
      interval_minutes: alliance.interval_minutes ?? 0
    });
  };

  return (
    <div className="space-y-6">
      <section className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
        <h2 className="text-lg font-semibold text-white">Alliance Directory</h2>
        <p className="text-sm text-slate-400">Manage alliances synced from the original Discord bot.</p>
        <div className="mt-6 overflow-x-auto">
          <table className="min-w-full divide-y divide-slate-800">
            <thead>
              <tr className="text-left text-xs uppercase text-slate-400">
                <th className="px-4 py-2">Alliance</th>
                <th className="px-4 py-2">Discord Server ID</th>
                <th className="px-4 py-2">Control Interval (min)</th>
                <th className="px-4 py-2"></th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800 text-sm text-slate-200">
              {alliances.map((alliance) => (
                <tr key={alliance.id}>
                  <td className="px-4 py-2 font-medium text-white">{alliance.name}</td>
                  <td className="px-4 py-2">{alliance.discord_server_id ?? '—'}</td>
                  <td className="px-4 py-2">{alliance.interval_minutes}</td>
                  <td className="px-4 py-2 text-right">
                    <div className="flex justify-end gap-2">
                      <button
                        type="button"
                        className="rounded-md border border-slate-700 px-3 py-1 text-xs text-slate-200 hover:bg-slate-800"
                        onClick={() => startEdit(alliance)}
                      >
                        Edit
                      </button>
                      <button
                        type="button"
                        className="rounded-md border border-red-500 px-3 py-1 text-xs text-red-300 hover:bg-red-500/20"
                        onClick={async () => {
                          await deleteAlliance(alliance.id);
                          load();
                        }}
                      >
                        Delete
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
        <h2 className="text-lg font-semibold text-white">{editingId ? 'Edit alliance' : 'Create alliance'}</h2>
        <form className="mt-4 grid gap-4 md:grid-cols-3" onSubmit={handleSubmit}>
          <div className="md:col-span-1">
            <label className="block text-sm text-slate-400" htmlFor="name">
              Name
            </label>
            <input
              id="name"
              name="name"
              required
              value={form.name}
              onChange={handleChange}
              className="mt-1 w-full rounded-md border border-slate-700 bg-slate-900 px-3 py-2 text-white focus:border-brand-400 focus:outline-none"
            />
          </div>
          <div className="md:col-span-1">
            <label className="block text-sm text-slate-400" htmlFor="discord_server_id">
              Discord server ID
            </label>
            <input
              id="discord_server_id"
              name="discord_server_id"
              value={form.discord_server_id}
              onChange={handleChange}
              className="mt-1 w-full rounded-md border border-slate-700 bg-slate-900 px-3 py-2 text-white focus:border-brand-400 focus:outline-none"
            />
          </div>
          <div className="md:col-span-1">
            <label className="block text-sm text-slate-400" htmlFor="interval_minutes">
              Control interval (minutes)
            </label>
            <input
              id="interval_minutes"
              name="interval_minutes"
              type="number"
              min="0"
              value={form.interval_minutes}
              onChange={handleChange}
              className="mt-1 w-full rounded-md border border-slate-700 bg-slate-900 px-3 py-2 text-white focus:border-brand-400 focus:outline-none"
            />
          </div>
          <div className="md:col-span-3 flex justify-end gap-2">
            {editingId ? (
              <button
                type="button"
                className="rounded-md border border-slate-700 px-4 py-2 text-sm text-slate-300 hover:bg-slate-800"
                onClick={() => {
                  setForm(emptyForm);
                  setEditingId(null);
                }}
              >
                Cancel
              </button>
            ) : null}
            <button
              type="submit"
              className="rounded-md bg-brand-500 px-4 py-2 text-sm font-medium text-white hover:bg-brand-400"
            >
              {editingId ? 'Update alliance' : 'Create alliance'}
            </button>
          </div>
        </form>
      </section>
    </div>
  );
};

export default Alliances;
