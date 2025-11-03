import React, { useEffect, useState } from 'react';
import { fetchAlliances } from '../api/alliances';
import { createMember, deleteMember, fetchMembers, updateMember } from '../api/members';

const emptyForm = { alliance_id: '', name: '', fl_level: '', title: '', joined_at: '', notes: '' };

const Members = () => {
  const [alliances, setAlliances] = useState([]);
  const [selectedAlliance, setSelectedAlliance] = useState('');
  const [members, setMembers] = useState([]);
  const [form, setForm] = useState(emptyForm);
  const [editingId, setEditingId] = useState(null);

  const loadMembers = async (allianceId) => {
    if (!allianceId) {
      setMembers([]);
      return;
    }
    setMembers(await fetchMembers(allianceId));
  };

  useEffect(() => {
    const load = async () => {
      const allianceData = await fetchAlliances();
      setAlliances(allianceData);
      if (allianceData.length) {
        const firstId = allianceData[0].id;
        setSelectedAlliance(String(firstId));
        setForm((prev) => ({ ...prev, alliance_id: String(firstId) }));
        loadMembers(firstId);
      }
    };
    load();
  }, []);

  const handleAllianceChange = (event) => {
    const { value } = event.target;
    setSelectedAlliance(value);
    setForm((prev) => ({ ...prev, alliance_id: value }));
    loadMembers(value);
  };

  const handleChange = (event) => {
    const { name, value } = event.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    const payload = {
      alliance_id: Number(form.alliance_id),
      name: form.name,
      fl_level: form.fl_level ? Number(form.fl_level) : null,
      title: form.title || null,
      joined_at: form.joined_at || null,
      notes: form.notes || null
    };
    if (editingId) {
      await updateMember(editingId, payload);
    } else {
      await createMember(payload);
    }
    setForm((prev) => ({ ...emptyForm, alliance_id: form.alliance_id }));
    setEditingId(null);
    loadMembers(form.alliance_id);
  };

  return (
    <div className="space-y-6">
      <section className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
        <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <div>
            <h2 className="text-lg font-semibold text-white">Alliance members</h2>
            <p className="text-sm text-slate-400">Synchronised roster for gift code and attendance automation.</p>
          </div>
          <select
            value={selectedAlliance}
            onChange={handleAllianceChange}
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
                <th className="px-4 py-2">Name</th>
                <th className="px-4 py-2">FL level</th>
                <th className="px-4 py-2">Title</th>
                <th className="px-4 py-2">Joined</th>
                <th className="px-4 py-2"></th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800 text-slate-200">
              {members.map((member) => (
                <tr key={member.id}>
                  <td className="px-4 py-2 font-medium text-white">{member.name}</td>
                  <td className="px-4 py-2">{member.fl_level ?? '—'}</td>
                  <td className="px-4 py-2">{member.title ?? '—'}</td>
                  <td className="px-4 py-2">{member.joined_at ?? '—'}</td>
                  <td className="px-4 py-2 text-right">
                    <div className="flex justify-end gap-2">
                      <button
                        type="button"
                        className="rounded-md border border-slate-700 px-3 py-1 text-xs text-slate-200 hover:bg-slate-800"
                        onClick={() => {
                          setEditingId(member.id);
                          setForm({
                            alliance_id: String(member.alliance_id),
                            name: member.name,
                            fl_level: member.fl_level ?? '',
                            title: member.title ?? '',
                            joined_at: member.joined_at ?? '',
                            notes: member.notes ?? ''
                          });
                        }}
                      >
                        Edit
                      </button>
                      <button
                        type="button"
                        className="rounded-md border border-red-500 px-3 py-1 text-xs text-red-300 hover:bg-red-500/20"
                        onClick={async () => {
                          await deleteMember(member.id);
                          loadMembers(selectedAlliance);
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
        <h2 className="text-lg font-semibold text-white">{editingId ? 'Update member' : 'Add member'}</h2>
        <form className="mt-4 grid gap-4 md:grid-cols-3" onSubmit={handleSubmit}>
          <div>
            <label className="block text-sm text-slate-400" htmlFor="form-alliance">
              Alliance
            </label>
            <select
              id="form-alliance"
              name="alliance_id"
              value={form.alliance_id}
              required
              onChange={handleChange}
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
            <label className="block text-sm text-slate-400" htmlFor="name">
              Player name
            </label>
            <input
              id="name"
              name="name"
              value={form.name}
              required
              onChange={handleChange}
              className="mt-1 w-full rounded-md border border-slate-700 bg-slate-900 px-3 py-2 text-white focus:border-brand-400 focus:outline-none"
            />
          </div>
          <div>
            <label className="block text-sm text-slate-400" htmlFor="fl_level">
              FL level
            </label>
            <input
              id="fl_level"
              name="fl_level"
              type="number"
              value={form.fl_level}
              onChange={handleChange}
              className="mt-1 w-full rounded-md border border-slate-700 bg-slate-900 px-3 py-2 text-white focus:border-brand-400 focus:outline-none"
            />
          </div>
          <div>
            <label className="block text-sm text-slate-400" htmlFor="title">
              Title
            </label>
            <input
              id="title"
              name="title"
              value={form.title}
              onChange={handleChange}
              className="mt-1 w-full rounded-md border border-slate-700 bg-slate-900 px-3 py-2 text-white focus:border-brand-400 focus:outline-none"
            />
          </div>
          <div>
            <label className="block text-sm text-slate-400" htmlFor="joined_at">
              Join date
            </label>
            <input
              id="joined_at"
              name="joined_at"
              type="date"
              value={form.joined_at}
              onChange={handleChange}
              className="mt-1 w-full rounded-md border border-slate-700 bg-slate-900 px-3 py-2 text-white focus:border-brand-400 focus:outline-none"
            />
          </div>
          <div>
            <label className="block text-sm text-slate-400" htmlFor="notes">
              Notes
            </label>
            <textarea
              id="notes"
              name="notes"
              value={form.notes}
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
              {editingId ? 'Update member' : 'Add member'}
            </button>
          </div>
        </form>
      </section>
    </div>
  );
};

export default Members;
