import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import api from '../services/api';
import { useAuth } from '../context/AuthContext';
import { Calendar, Pencil, Layers, Plus } from 'lucide-react';

interface EventItem {
  id: string;
  name: string;
  type: string;
  parent_event_id: string | null;
  description: string | null;
  is_active: boolean;
  created_at: string;
}

export default function Events() {
  const { user } = useAuth();
  const [events, setEvents] = useState<EventItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');

  useEffect(() => {
    const fetchEvents = async () => {
      try {
        const res = await api.get('/events');
        setEvents(res.data.events || []);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchEvents();
  }, []);

  const parentName = (pid: string | null) => {
    if (!pid) return null;
    const p = events.find(e => e.id === pid);
    return p?.name || pid.slice(0, 8);
  };

  const filtered = events.filter(e =>
    e.name.toLowerCase().includes(search.toLowerCase())
  );

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="h-8 w-48 bg-bg-card rounded animate-pulse" />
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {[1,2,3,4].map(i => <div key={i} className="glass-card h-40 animate-pulse" />)}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-end gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Event Ledgers</h1>
          <p className="text-text-secondary text-sm mt-1">{events.length} events registered</p>
        </div>
        {user?.role === 'admin' && (
          <Link to="/events/new" className="btn-primary text-sm px-4 py-2">
            <Plus size={16} /> New Event
          </Link>
        )}
      </div>

      <input
        className="input-field text-sm max-w-sm"
        placeholder="Search events…"
        value={search}
        onChange={(e) => setSearch(e.target.value)}
      />

      {filtered.length === 0 ? (
        <div className="glass-card p-10 text-center">
          <Layers className="mx-auto mb-4 text-text-secondary" size={40} />
          <p className="text-text-secondary text-sm">No events found.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {filtered.map((ev) => (
            <div key={ev.id} className="glass-card p-5 relative overflow-hidden group hover:border-accent-blue/40 transition-colors">
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="text-lg font-semibold group-hover:text-accent-blue transition-colors">{ev.name}</h3>
                  <div className="flex items-center gap-2 mt-1">
                    <span className={`text-[10px] px-2 py-0.5 rounded font-bold uppercase tracking-wider ${
                      ev.type === 'major_fest'
                        ? 'text-accent-purple bg-accent-purple/10 border border-accent-purple/20'
                        : 'text-accent-blue bg-accent-blue/10 border border-accent-blue/20'
                    }`}>
                      {ev.type === 'major_fest' ? 'Major Fest' : 'Sub-Event'}
                    </span>
                    <span className={`text-[10px] flex items-center gap-1 ${ev.is_active ? 'text-accent-green' : 'text-text-secondary'}`}>
                      <span className={`w-1.5 h-1.5 rounded-full ${ev.is_active ? 'bg-accent-green' : 'bg-text-secondary'}`} />
                      {ev.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </div>
                </div>
                {user?.role === 'admin' && (
                  <Link to={`/events/${ev.id}/edit`} className="text-text-secondary hover:text-accent-blue transition-colors" title="Edit"><Pencil size={16} /></Link>
                )}
              </div>

              {ev.parent_event_id && (
                <div className="mt-3 text-xs text-text-secondary flex items-center gap-1">
                  <Layers size={12} /> Part of: <span className="text-text-primary font-semibold">{parentName(ev.parent_event_id)}</span>
                </div>
              )}

              {ev.description && (
                <p className="mt-3 text-xs text-text-secondary line-clamp-2">{ev.description}</p>
              )}

              <div className="mt-4 flex items-center gap-2 text-[10px] text-text-secondary">
                <Calendar size={10} />
                Created {new Date(ev.created_at).toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' })}
              </div>

              {/* Ambient glow */}
              <div className={`absolute -bottom-6 -right-6 w-24 h-24 rounded-full blur-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-500 ${
                ev.type === 'major_fest' ? 'bg-accent-purple/15' : 'bg-accent-blue/15'
              }`} />
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
