import React, { useEffect, useState } from 'react';
import api from '../services/api';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';
import { UserPlus, Search } from 'lucide-react';

interface UserItem {
  id: string;
  name: string;
  email: string;
  role: string;
  is_active: boolean;
  assigned_event_id: string | null;
  created_at: string;
}

interface EventItem { id: string; name: string; }

export default function Users() {
  const { user: me } = useAuth();
  const { toast } = useToast();
  const [users, setUsers] = useState<UserItem[]>([]);
  const [events, setEvents] = useState<EventItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ name: '', email: '', password: '', role: 'viewer', assigned_event_id: '' });
  const [saving, setSaving] = useState(false);

  const fetchUsers = async () => {
    try {
      const res = await api.get('/users');
      setUsers(res.data.users || []);
    } catch (err) { console.error(err); }
    finally { setLoading(false); }
  };

  useEffect(() => {
    fetchUsers();
    api.get('/events').then(res => setEvents(res.data.events || [])).catch(() => {});
  }, []);

  const handleCreateUser = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.name || !form.email || !form.password) { toast('warning', 'Fill all required fields.'); return; }
    setSaving(true);
    try {
      await api.post('/users', {
        name: form.name, email: form.email, password: form.password,
        role: form.role, assigned_event_id: form.assigned_event_id || null,
      });
      toast('success', `Member "${form.name}" created as ${form.role}.`);
      setForm({ name: '', email: '', password: '', role: 'viewer', assigned_event_id: '' });
      setShowForm(false);
      fetchUsers();
    } catch (err: any) {
      toast('error', err.response?.data?.detail?.error?.message || err.response?.data?.error?.message || 'Failed to create user.');
    } finally { setSaving(false); }
  };

  const handleRoleChange = async (userId: string, newRole: string) => {
    try {
      await api.patch(`/users/${userId}/role`, { role: newRole });
      toast('success', 'Role updated.');
      fetchUsers();
    } catch (err: any) {
      toast('error', err.response?.data?.detail?.error?.message || err.response?.data?.error?.message || 'Role change failed.');
    }
  };

  const handleStatusToggle = async (userId: string, currentStatus: boolean) => {
    try {
      await api.patch(`/users/${userId}/status`, { is_active: !currentStatus });
      toast('success', !currentStatus ? 'User activated.' : 'User deactivated.');
      fetchUsers();
    } catch (err: any) {
      toast('error', err.response?.data?.detail?.error?.message || err.response?.data?.error?.message || 'Status change failed.');
    }
  };

  const eventName = (eid: string | null) => {
    if (!eid) return '—';
    return events.find(e => e.id === eid)?.name || eid.slice(0, 8);
  };

  const filtered = users.filter(u =>
    u.name.toLowerCase().includes(search.toLowerCase()) ||
    u.email.toLowerCase().includes(search.toLowerCase())
  );

  const roleBadge: Record<string, string> = {
    admin: 'bg-accent-purple/15 text-accent-purple border-accent-purple/20',
    analyst: 'bg-accent-blue/15 text-accent-blue border-accent-blue/20',
    viewer: 'bg-bg-card-hover text-text-secondary border-border-layer',
  };

  if (loading) return <div className="animate-pulse text-text-secondary">Loading users…</div>;

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-end gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Club Members</h1>
          <p className="text-text-secondary text-sm mt-1">{users.length} registered members</p>
        </div>
        <button onClick={() => setShowForm(!showForm)} className="btn-primary text-sm px-4 py-2">
          <UserPlus size={16} /> Add Member
        </button>
      </div>

      {/* Add Member Form */}
      {showForm && (
        <form onSubmit={handleCreateUser} className="glass-card p-6 space-y-4">
          <h3 className="text-sm font-semibold uppercase tracking-widest text-text-secondary">New Member</h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <input className="input-field" placeholder="Full Name *" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required />
            <input className="input-field" type="email" placeholder="Email *" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} required />
            <input className="input-field" type="password" placeholder="Password (min 8 chars) *" minLength={8} value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} required />
            <select className="input-field" value={form.role} onChange={(e) => setForm({ ...form, role: e.target.value })}>
              <option value="viewer">Viewer</option>
              <option value="analyst">Analyst</option>
              <option value="admin">Admin</option>
            </select>
            {form.role === 'analyst' && (
              <select className="input-field" value={form.assigned_event_id} onChange={(e) => setForm({ ...form, assigned_event_id: e.target.value })}>
                <option value="">No Event Restriction (full access)</option>
                {events.map(ev => <option key={ev.id} value={ev.id}>{ev.name}</option>)}
              </select>
            )}
          </div>
          <div className="flex gap-3">
            <button type="submit" disabled={saving} className="btn-primary text-sm">{saving ? 'Creating…' : 'Create Member'}</button>
            <button type="button" onClick={() => setShowForm(false)} className="text-sm text-text-secondary hover:text-text-primary transition-colors">Cancel</button>
          </div>
        </form>
      )}

      {/* Search */}
      <div className="relative max-w-sm">
        <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-text-secondary" />
        <input className="input-field pl-9 text-sm" placeholder="Search by name or email…" value={search} onChange={(e) => setSearch(e.target.value)} />
      </div>

      {/* Users Table */}
      <div className="glass-card overflow-x-auto">
        <table className="w-full text-left text-sm">
          <thead className="bg-[#13131b] text-text-secondary uppercase tracking-wider text-[10px] border-b border-border-layer">
            <tr>
              <th className="p-4 font-semibold">Name</th>
              <th className="p-4 font-semibold">Email</th>
              <th className="p-4 font-semibold">Role</th>
              <th className="p-4 font-semibold">Assigned Event</th>
              <th className="p-4 font-semibold">Status</th>
              <th className="p-4 font-semibold text-center">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border-layer">
            {filtered.map((u) => (
              <tr key={u.id} className="hover:bg-bg-card-hover transition-colors">
                <td className="p-4 font-semibold">{u.name}</td>
                <td className="p-4 text-text-secondary text-xs font-mono">{u.email}</td>
                <td className="p-4">
                  {u.id === me?.id ? (
                    <span className={`text-[10px] px-2 py-0.5 rounded font-bold uppercase tracking-wider border ${roleBadge[u.role]}`}>{u.role}</span>
                  ) : (
                    <select
                      value={u.role}
                      onChange={(e) => handleRoleChange(u.id, e.target.value)}
                      className="bg-transparent text-[11px] font-bold uppercase tracking-wider border border-border-layer rounded px-2 py-1 text-text-primary focus:outline-none focus:border-accent-blue cursor-pointer"
                    >
                      <option value="viewer">Viewer</option>
                      <option value="analyst">Analyst</option>
                      <option value="admin">Admin</option>
                    </select>
                  )}
                </td>
                <td className="p-4 text-text-secondary text-xs">{eventName(u.assigned_event_id)}</td>
                <td className="p-4">
                  <span className={`flex items-center gap-1.5 text-xs ${u.is_active ? 'text-accent-green' : 'text-accent-red'}`}>
                    <span className={`w-2 h-2 rounded-full ${u.is_active ? 'bg-accent-green' : 'bg-accent-red'}`} />
                    {u.is_active ? 'Active' : 'Inactive'}
                  </span>
                </td>
                <td className="p-4 text-center">
                  {u.id !== me?.id && (
                    <button
                      onClick={() => handleStatusToggle(u.id, u.is_active)}
                      className={`text-xs px-3 py-1 rounded border transition-colors ${
                        u.is_active
                          ? 'text-accent-red border-accent-red/20 hover:bg-accent-red/10'
                          : 'text-accent-green border-accent-green/20 hover:bg-accent-green/10'
                      }`}
                    >
                      {u.is_active ? 'Deactivate' : 'Activate'}
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {filtered.length === 0 && <div className="p-8 text-center text-text-secondary text-sm">No users found.</div>}
      </div>
    </div>
  );
}
