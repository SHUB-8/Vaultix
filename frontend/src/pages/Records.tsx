import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import api from '../services/api';
import { useAuth } from '../context/AuthContext';
import { Search, ChevronLeft, ChevronRight, Trash2, Plus, Pencil } from 'lucide-react';

interface Record {
  id: string;
  amount: number;
  type: string;
  category: string;
  event_id: string | null;
  date: string;
  notes: string | null;
  is_deleted: boolean;
  created_at: string;
}

export default function Records() {
  const { user } = useAuth();
  const [records, setRecords] = useState<Record[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [total, setTotal] = useState(0);
  const [search, setSearch] = useState('');
  const [typeFilter, setTypeFilter] = useState('');
  const [events, setEvents] = useState<{ id: string; name: string }[]>([]);
  const [eventFilter, setEventFilter] = useState('');
  const [deleting, setDeleting] = useState<string | null>(null);
  const limit = 20;

  useEffect(() => {
    api.get('/events').then(res => {
      setEvents(res.data.events || []);
    }).catch(() => {});
  }, []);

  useEffect(() => {
    fetchRecords();
  }, [page, typeFilter, eventFilter]);

  const fetchRecords = async () => {
    setLoading(true);
    try {
      const params: any = { page, limit };
      if (typeFilter) params.type = typeFilter;
      if (eventFilter) params.event_id = eventFilter;
      if (search) params.search = search;
      const res = await api.get('/records', { params });
      setRecords(res.data.records);
      setTotal(res.data.total);
      setTotalPages(res.data.pages);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    fetchRecords();
  };

  const handleDelete = async (id: string) => {
    if (!confirm('This record will be soft-deleted. It will no longer appear in reports. Continue?')) return;
    setDeleting(id);
    try {
      await api.delete(`/records/${id}`);
      fetchRecords();
    } catch (err: any) {
      alert(err.response?.data?.error?.message || 'Delete failed.');
    } finally {
      setDeleting(null);
    }
  };

  const formatCurrency = (val: number) =>
    `₹${Number(val).toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;

  const formatDate = (d: string) => {
    const dt = new Date(d);
    return dt.toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' });
  };

  const eventName = (eventId: string | null) => {
    if (!eventId) return '—';
    const ev = events.find(e => e.id === eventId);
    return ev?.name || eventId.slice(0, 8);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-end gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Ledger & Records</h1>
          <p className="text-text-secondary text-sm mt-1">{total} total records</p>
        </div>
        {user?.role === 'admin' && (
          <Link to="/records/new" className="btn-primary text-sm px-4 py-2">
            <Plus size={16} /> Add Record
          </Link>
        )}
      </div>

      {/* Filters */}
      <div className="glass-card p-4 flex flex-wrap gap-3 items-center">
        <form onSubmit={handleSearch} className="flex-1 min-w-[200px] relative">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-text-secondary" />
          <input
            className="input-field pl-9 text-sm"
            placeholder="Search notes…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </form>
        <select
          className="input-field w-auto text-sm"
          value={typeFilter}
          onChange={(e) => { setTypeFilter(e.target.value); setPage(1); }}
        >
          <option value="">All Types</option>
          <option value="income">Income</option>
          <option value="expense">Expense</option>
        </select>
        <select
          className="input-field w-auto text-sm"
          value={eventFilter}
          onChange={(e) => { setEventFilter(e.target.value); setPage(1); }}
        >
          <option value="">All Events</option>
          {events.map(ev => <option key={ev.id} value={ev.id}>{ev.name}</option>)}
        </select>
      </div>

      {/* Table */}
      <div className="glass-card overflow-x-auto">
        <table className="w-full text-left text-sm">
          <thead className="bg-[#13131b] text-text-secondary uppercase tracking-wider text-[10px] border-b border-border-layer">
            <tr>
              <th className="p-4 font-semibold">Date</th>
              <th className="p-4 font-semibold">Type</th>
              <th className="p-4 font-semibold">Category</th>
              <th className="p-4 font-semibold">Event</th>
              <th className="p-4 font-semibold text-right">Amount</th>
              <th className="p-4 font-semibold">Notes</th>
              {user?.role === 'admin' && <th className="p-4 font-semibold text-center">Actions</th>}
            </tr>
          </thead>
          <tbody className="divide-y divide-border-layer">
            {loading ? (
              Array.from({ length: 5 }).map((_, i) => (
                <tr key={i}><td colSpan={7} className="p-4"><div className="h-4 bg-bg-card-hover rounded animate-pulse" /></td></tr>
              ))
            ) : records.length === 0 ? (
              <tr><td colSpan={7} className="p-8 text-center text-text-secondary">No records found matching your filters.</td></tr>
            ) : (
              records.map((r) => (
                <tr key={r.id} className={`hover:bg-bg-card-hover transition-colors ${r.is_deleted ? 'opacity-40 line-through' : ''}`}>
                  <td className="p-4 font-mono text-xs text-text-secondary whitespace-nowrap">{formatDate(r.date)}</td>
                  <td className="p-4">
                    <span className={`px-2 py-0.5 text-[10px] font-bold tracking-wider rounded uppercase ${
                      r.type === 'income'
                        ? 'text-accent-green bg-accent-green/10 border border-accent-green/20'
                        : 'text-accent-red bg-accent-red/10 border border-accent-red/20'
                    }`}>
                      {r.type}
                    </span>
                  </td>
                  <td className="p-4 text-text-primary capitalize text-xs">{r.category.replace(/_/g, ' ')}</td>
                  <td className="p-4 text-text-secondary text-xs">{eventName(r.event_id)}</td>
                  <td className={`p-4 text-right font-mono font-semibold whitespace-nowrap ${
                    r.type === 'income' ? 'text-accent-green' : 'text-accent-red'
                  }`}>
                    {r.type === 'income' ? '+' : '-'}{formatCurrency(r.amount)}
                  </td>
                  <td className="p-4 text-text-secondary text-xs max-w-[200px] truncate">{r.notes || '—'}</td>
                  {user?.role === 'admin' && (
                    <td className="p-4 text-center flex items-center justify-center gap-2">
                      {!r.is_deleted && (
                        <>
                          <Link to={`/records/${r.id}/edit`} className="text-text-secondary hover:text-accent-blue transition-colors" title="Edit"><Pencil size={14} /></Link>
                          <button onClick={() => handleDelete(r.id)} disabled={deleting === r.id} className="text-text-secondary hover:text-accent-red transition-colors" title="Soft Delete"><Trash2 size={14} /></button>
                        </>
                      )}
                    </td>
                  )}
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex justify-between items-center text-sm text-text-secondary">
          <span>Page {page} of {totalPages} &bull; {total} records</span>
          <div className="flex gap-2">
            <button
              onClick={() => setPage(p => Math.max(1, p - 1))}
              disabled={page <= 1}
              className="glass-card px-3 py-1.5 disabled:opacity-30 hover:bg-bg-card-hover transition-colors"
            >
              <ChevronLeft size={14} />
            </button>
            <button
              onClick={() => setPage(p => Math.min(totalPages, p + 1))}
              disabled={page >= totalPages}
              className="glass-card px-3 py-1.5 disabled:opacity-30 hover:bg-bg-card-hover transition-colors"
            >
              <ChevronRight size={14} />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
