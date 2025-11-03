import React, { useEffect, useRef, useState } from 'react';
import { trackGiftCode, fetchGiftCodes, solveCaptcha, updateGiftCode, deleteGiftCode } from '../api/giftCodes';
import { fetchAlliances } from '../api/alliances';

const GiftCodes = () => {
  const [codes, setCodes] = useState([]);
  const [alliances, setAlliances] = useState([]);
  const [form, setForm] = useState({ code: '', alliance_id: '' });
  const [captchaResult, setCaptchaResult] = useState(null);
  const fileInputRef = useRef(null);

  const load = async () => {
    setCodes(await fetchGiftCodes());
  };

  useEffect(() => {
    load();
    const loadAlliances = async () => setAlliances(await fetchAlliances());
    loadAlliances();
  }, []);

  const handleSubmit = async (event) => {
    event.preventDefault();
    await trackGiftCode({
      code: form.code,
      alliance_id: form.alliance_id ? Number(form.alliance_id) : null
    });
    setForm({ code: '', alliance_id: '' });
    load();
  };

  const handleCaptchaUpload = async (event) => {
    const file = event.target.files?.[0];
    if (!file) return;
    const result = await solveCaptcha(file);
    setCaptchaResult(result);
    if (result.code) {
      setForm((prev) => ({ ...prev, code: result.code }));
    }
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div className="space-y-6">
      <section className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
        <h2 className="text-lg font-semibold text-white">Gift code pipeline</h2>
        <p className="text-sm text-slate-400">Redeem codes without the Discord bot using the ONNX OCR solver.</p>
        <div className="mt-6 overflow-x-auto">
          <table className="min-w-full divide-y divide-slate-800 text-sm">
            <thead>
              <tr className="text-left text-xs uppercase text-slate-400">
                <th className="px-4 py-2">Code</th>
                <th className="px-4 py-2">Alliance</th>
                <th className="px-4 py-2">Status</th>
                <th className="px-4 py-2">Confidence</th>
                <th className="px-4 py-2">Updated</th>
                <th className="px-4 py-2"></th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800 text-slate-200">
              {codes.map((code) => (
                <tr key={code.id}>
                  <td className="px-4 py-2 font-mono text-sm text-brand-100">{code.code}</td>
                  <td className="px-4 py-2">{code.alliance_id ?? '—'}</td>
                  <td className="px-4 py-2">{code.status}</td>
                  <td className="px-4 py-2">{code.confidence ? `${(code.confidence * 100).toFixed(1)}%` : '—'}</td>
                  <td className="px-4 py-2">{code.last_checked_at ?? '—'}</td>
                  <td className="px-4 py-2 text-right">
                    <div className="flex justify-end gap-2">
                      <button
                        type="button"
                        className="rounded-md border border-slate-700 px-3 py-1 text-xs text-slate-200 hover:bg-slate-800"
                        onClick={() => updateGiftCode(code.id, { status: 'redeemed', redeemed_by: 'manual' }).then(load)}
                      >
                        Mark redeemed
                      </button>
                      <button
                        type="button"
                        className="rounded-md border border-red-500 px-3 py-1 text-xs text-red-300 hover:bg-red-500/20"
                        onClick={() => deleteGiftCode(code.id).then(load)}
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
        <h2 className="text-lg font-semibold text-white">Track or validate a gift code</h2>
        <form className="mt-4 grid gap-4 md:grid-cols-3" onSubmit={handleSubmit}>
          <div className="md:col-span-2">
            <label className="block text-sm text-slate-400" htmlFor="code">
              Gift code
            </label>
            <input
              id="code"
              name="code"
              value={form.code}
              required
              onChange={(event) => setForm((prev) => ({ ...prev, code: event.target.value }))}
              className="mt-1 w-full rounded-md border border-slate-700 bg-slate-900 px-3 py-2 font-mono text-white focus:border-brand-400 focus:outline-none"
            />
          </div>
          <div>
            <label className="block text-sm text-slate-400" htmlFor="alliance_id">
              Alliance (optional)
            </label>
            <select
              id="alliance_id"
              value={form.alliance_id}
              onChange={(event) => setForm((prev) => ({ ...prev, alliance_id: event.target.value }))}
              className="mt-1 w-full rounded-md border border-slate-700 bg-slate-900 px-3 py-2 text-white focus:border-brand-400 focus:outline-none"
            >
              <option value="">Unassigned</option>
              {alliances.map((alliance) => (
                <option key={alliance.id} value={alliance.id}>
                  {alliance.name}
                </option>
              ))}
            </select>
          </div>
          <div className="md:col-span-3 flex items-center gap-3">
            <button
              type="submit"
              className="rounded-md bg-brand-500 px-4 py-2 text-sm font-medium text-white hover:bg-brand-400"
            >
              Save code
            </button>
            <label className="inline-flex cursor-pointer items-center gap-2 text-sm text-slate-300">
              <input ref={fileInputRef} type="file" accept="image/*" className="hidden" onChange={handleCaptchaUpload} />
              <span className="rounded-md border border-slate-700 px-3 py-2 text-xs uppercase tracking-wide text-slate-200">
                Upload captcha image
              </span>
            </label>
            {captchaResult ? (
              <span className="text-xs text-slate-400">
                {captchaResult.success ? `OCR success (${(captchaResult.confidence * 100).toFixed(1)}%)` : 'OCR failed'}
              </span>
            ) : null}
          </div>
        </form>
      </section>
    </div>
  );
};

export default GiftCodes;
