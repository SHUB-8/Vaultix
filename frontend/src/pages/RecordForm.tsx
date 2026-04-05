import React, { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import api from '../services/api';
import { useToast } from '../context/ToastContext';
import { ArrowLeft, Save, Plus } from 'lucide-react';

const INCOME_CATEGORIES = [
  'college_grant', 'sponsorship_title', 'sponsorship_associate',
  'registration_fees', 'workshop_fees', 'merchandise_sales',
  'alumni_donation', 'other_income',
];
const EXPENSE_CATEGORIES = [
  'venue_logistics', 'guest_honorarium', 'marketing_printing',
  'food_hospitality', 'equipment_av', 'prizes_certificates',
  'digital_tools', 'travel', 'miscellaneous',
];

export default function RecordForm() {
  const { id } = useParams();
  const isEdit = Boolean(id);
  const navigate = useNavigate();
  const { toast } = useToast();

  const [form, setForm] = useState({
    amount: '',
    type: 'expense',
    category: '',
    event_id: '',
    date: new Date().toISOString().split('T')[0],
    notes: '',
  });
  const [events, setEvents] = useState<{ id: string; name: string }[]>([]);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    api.get('/events').then(res => setEvents(res.data.events || [])).catch(() => {});
    if (isEdit) {
      setLoading(true);
      api.get(`/records/${id}`).then(res => {
        const r = res.data;
        setForm({
          amount: String(r.amount),
          type: r.type,
          category: r.category,
          event_id: r.event_id || '',
          date: r.date,
          notes: r.notes || '',
        });
      }).catch(() => toast('error', 'Failed to load record.')).finally(() => setLoading(false));
    }
  }, [id]);

  const categories = form.type === 'income' ? INCOME_CATEGORIES : EXPENSE_CATEGORIES;

  const handleSubmit = async (e: React.FormEvent, addAnother = false) => {
    e.preventDefault();
    if (!form.amount || !form.category || !form.date) {
      toast('warning', 'Please fill all required fields.');
      return;
    }
    setSaving(true);
    try {
      const payload: any = {
        amount: parseFloat(form.amount),
        type: form.type,
        category: form.category,
        date: form.date,
        notes: form.notes || null,
        event_id: form.event_id || null,
      };
      if (isEdit) {
        await api.patch(`/records/${id}`, payload);
        toast('success', 'Record updated successfully.');
        navigate('/records');
      } else {
        await api.post('/records', payload);
        toast('success', 'Record created successfully.');
        if (addAnother) {
          setForm({ ...form, amount: '', category: '', notes: '' });
        } else {
          navigate('/records');
        }
      }
    } catch (err: any) {
      toast('error', err.response?.data?.error?.message || err.response?.data?.detail?.[0]?.msg || 'Save failed.');
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <div className="animate-pulse text-text-secondary">Loading record…</div>;

  return (
    <div className="max-w-2xl mx-auto">
      <button onClick={() => navigate('/records')} className="flex items-center gap-1 text-text-secondary hover:text-text-primary text-sm mb-6 transition-colors">
        <ArrowLeft size={16} /> Back to Records
      </button>

      <h1 className="text-3xl font-bold tracking-tight mb-6">{isEdit ? 'Edit Record' : 'New Financial Record'}</h1>

      <form onSubmit={(e) => handleSubmit(e)} className="glass-card p-6 space-y-5">
        {/* Type Toggle */}
        <div>
          <label className="block text-xs uppercase tracking-widest text-text-secondary font-semibold mb-2">Type</label>
          <div className="flex gap-2">
            {['income', 'expense'].map(t => (
              <button
                key={t}
                type="button"
                onClick={() => setForm({ ...form, type: t, category: '' })}
                className={`px-4 py-2 rounded-lg text-sm font-bold uppercase tracking-wider transition-all ${
                  form.type === t
                    ? t === 'income'
                      ? 'bg-accent-green/20 text-accent-green border border-accent-green/30'
                      : 'bg-accent-red/20 text-accent-red border border-accent-red/30'
                    : 'bg-bg-card-hover text-text-secondary border border-border-layer'
                }`}
              >
                {t}
              </button>
            ))}
          </div>
        </div>

        {/* Amount */}
        <div>
          <label className="block text-xs uppercase tracking-widest text-text-secondary font-semibold mb-2">Amount (₹) *</label>
          <input
            type="number"
            step="0.01"
            min="0.01"
            className="input-field font-mono text-lg"
            value={form.amount}
            onChange={(e) => setForm({ ...form, amount: e.target.value })}
            placeholder="0.00"
            required
          />
        </div>

        {/* Category */}
        <div>
          <label className="block text-xs uppercase tracking-widest text-text-secondary font-semibold mb-2">Category *</label>
          <select className="input-field" value={form.category} onChange={(e) => setForm({ ...form, category: e.target.value })} required>
            <option value="">Select category</option>
            {categories.map(c => <option key={c} value={c}>{c.replace(/_/g, ' ')}</option>)}
          </select>
        </div>

        {/* Event */}
        <div>
          <label className="block text-xs uppercase tracking-widest text-text-secondary font-semibold mb-2">Event (optional)</label>
          <select className="input-field" value={form.event_id} onChange={(e) => setForm({ ...form, event_id: e.target.value })}>
            <option value="">No Event</option>
            {events.map(ev => <option key={ev.id} value={ev.id}>{ev.name}</option>)}
          </select>
        </div>

        {/* Date */}
        <div>
          <label className="block text-xs uppercase tracking-widest text-text-secondary font-semibold mb-2">Date *</label>
          <input
            type="date"
            className="input-field"
            value={form.date}
            max={new Date().toISOString().split('T')[0]}
            onChange={(e) => setForm({ ...form, date: e.target.value })}
            required
          />
        </div>

        {/* Notes */}
        <div>
          <label className="block text-xs uppercase tracking-widest text-text-secondary font-semibold mb-2">Notes</label>
          <textarea
            className="input-field min-h-[80px] resize-y"
            maxLength={1000}
            value={form.notes}
            onChange={(e) => setForm({ ...form, notes: e.target.value })}
            placeholder="Description of this transaction…"
          />
          <div className="text-right text-[10px] text-text-secondary mt-1">{form.notes.length}/1000</div>
        </div>

        {/* Actions */}
        <div className="flex gap-3 pt-2">
          <button type="submit" disabled={saving} className="btn-primary">
            <Save size={16} /> {saving ? 'Saving…' : isEdit ? 'Update Record' : 'Create Record'}
          </button>
          {!isEdit && (
            <button type="button" disabled={saving} onClick={(e) => handleSubmit(e, true)} className="px-4 py-2 rounded-lg text-sm font-semibold text-text-secondary bg-bg-card-hover border border-border-layer hover:border-accent-blue/30 transition-colors flex items-center gap-2">
              <Plus size={16} /> Save & Add Another
            </button>
          )}
        </div>
      </form>
    </div>
  );
}
