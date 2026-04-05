import React, { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import api from '../services/api';
import { useToast } from '../context/ToastContext';
import { ArrowLeft, Save } from 'lucide-react';

export default function EventForm() {
  const { id } = useParams();
  const isEdit = Boolean(id);
  const navigate = useNavigate();
  const { toast } = useToast();

  const [form, setForm] = useState({
    name: '',
    type: 'sub_event',
    parent_event_id: '',
    description: '',
    is_active: true,
  });
  const [majorEvents, setMajorEvents] = useState<{ id: string; name: string }[]>([]);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    api.get('/events').then(res => {
      const evts = res.data.events || [];
      setMajorEvents(evts.filter((e: any) => e.type === 'major_fest'));
    }).catch(() => {});

    if (isEdit) {
      setLoading(true);
      api.get(`/events/${id}`).then(res => {
        const e = res.data;
        setForm({
          name: e.name,
          type: e.type,
          parent_event_id: e.parent_event_id || '',
          description: e.description || '',
          is_active: e.is_active,
        });
      }).catch(() => toast('error', 'Failed to load event.')).finally(() => setLoading(false));
    }
  }, [id]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.name) { toast('warning', 'Name is required.'); return; }
    setSaving(true);
    try {
      const payload: any = {
        name: form.name,
        type: form.type,
        description: form.description || null,
        parent_event_id: form.type === 'sub_event' && form.parent_event_id ? form.parent_event_id : null,
      };
      if (isEdit) {
        const updatePayload: any = { name: form.name, description: form.description || null, is_active: form.is_active };
        await api.patch(`/events/${id}`, updatePayload);
        toast('success', 'Event updated successfully.');
      } else {
        await api.post('/events', payload);
        toast('success', 'Event created successfully.');
      }
      navigate('/events');
    } catch (err: any) {
      toast('error', err.response?.data?.error?.message || 'Save failed.');
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <div className="animate-pulse text-text-secondary">Loading event…</div>;

  return (
    <div className="max-w-2xl mx-auto">
      <button onClick={() => navigate('/events')} className="flex items-center gap-1 text-text-secondary hover:text-text-primary text-sm mb-6 transition-colors">
        <ArrowLeft size={16} /> Back to Events
      </button>

      <h1 className="text-3xl font-bold tracking-tight mb-6">{isEdit ? 'Edit Event' : 'New Event'}</h1>

      <form onSubmit={handleSubmit} className="glass-card p-6 space-y-5">
        <div>
          <label className="block text-xs uppercase tracking-widest text-text-secondary font-semibold mb-2">Event Name *</label>
          <input className="input-field" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} placeholder="e.g. TechSurge 2025" required />
        </div>

        {!isEdit && (
          <>
            <div>
              <label className="block text-xs uppercase tracking-widest text-text-secondary font-semibold mb-2">Event Type</label>
              <div className="flex gap-2">
                {[{ v: 'major_fest', l: 'Major Fest' }, { v: 'sub_event', l: 'Sub-Event' }].map(t => (
                  <button
                    key={t.v}
                    type="button"
                    onClick={() => setForm({ ...form, type: t.v, parent_event_id: '' })}
                    className={`px-4 py-2 rounded-lg text-sm font-bold uppercase tracking-wider transition-all ${
                      form.type === t.v
                        ? t.v === 'major_fest'
                          ? 'bg-accent-purple/20 text-accent-purple border border-accent-purple/30'
                          : 'bg-accent-blue/20 text-accent-blue border border-accent-blue/30'
                        : 'bg-bg-card-hover text-text-secondary border border-border-layer'
                    }`}
                  >
                    {t.l}
                  </button>
                ))}
              </div>
            </div>

            {form.type === 'sub_event' && (
              <div>
                <label className="block text-xs uppercase tracking-widest text-text-secondary font-semibold mb-2">Parent Event (optional)</label>
                <select className="input-field" value={form.parent_event_id} onChange={(e) => setForm({ ...form, parent_event_id: e.target.value })}>
                  <option value="">Standalone (no parent)</option>
                  {majorEvents.map(ev => <option key={ev.id} value={ev.id}>{ev.name}</option>)}
                </select>
              </div>
            )}
          </>
        )}

        {isEdit && (
          <div>
            <label className="block text-xs uppercase tracking-widest text-text-secondary font-semibold mb-2">Status</label>
            <button
              type="button"
              onClick={() => setForm({ ...form, is_active: !form.is_active })}
              className={`px-4 py-2 rounded-lg text-sm font-bold transition-all ${
                form.is_active
                  ? 'bg-accent-green/20 text-accent-green border border-accent-green/30'
                  : 'bg-accent-red/20 text-accent-red border border-accent-red/30'
              }`}
            >
              {form.is_active ? '● Active' : '○ Inactive'}
            </button>
          </div>
        )}

        <div>
          <label className="block text-xs uppercase tracking-widest text-text-secondary font-semibold mb-2">Description</label>
          <textarea className="input-field min-h-[80px] resize-y" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} placeholder="Brief description of this event…" />
        </div>

        <button type="submit" disabled={saving} className="btn-primary">
          <Save size={16} /> {saving ? 'Saving…' : isEdit ? 'Update Event' : 'Create Event'}
        </button>
      </form>
    </div>
  );
}
