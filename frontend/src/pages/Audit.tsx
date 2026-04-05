import React, { useEffect, useState } from 'react';
import api from '../services/api';
import { ChevronLeft, ChevronRight, Plus, Edit, Trash2, Eye } from 'lucide-react';

interface AuditLog {
  id: string;
  actor_id: string;
  action: string;
  resource_type: string;
  resource_id: string;
  old_data: Record<string, any> | null;
  new_data: Record<string, any> | null;
  timestamp: string;
}

const ACTION_STYLES: Record<string, { color: string; icon: React.ReactNode; label: string }> = {
  create: { color: 'accent-green', icon: <Plus size={14} />, label: 'Created' },
  update: { color: 'accent-blue', icon: <Edit size={14} />, label: 'Updated' },
  delete: { color: 'accent-red', icon: <Trash2 size={14} />, label: 'Deleted' },
  soft_delete: { color: 'accent-yellow', icon: <Trash2 size={14} />, label: 'Soft-Deleted' },
};

export default function Audit() {
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [total, setTotal] = useState(0);
  const [actionFilter, setActionFilter] = useState('');
  const [resourceFilter, setResourceFilter] = useState('');
  const [expanded, setExpanded] = useState<string | null>(null);
  const limit = 20;

  useEffect(() => {
    fetchLogs();
  }, [page, actionFilter, resourceFilter]);

  const fetchLogs = async () => {
    setLoading(true);
    try {
      const params: any = { page, limit };
      if (actionFilter) params.action = actionFilter;
      if (resourceFilter) params.resource_type = resourceFilter;
      const res = await api.get('/audit-logs', { params });
      setLogs(res.data.audit_logs);
      setTotal(res.data.total);
      setTotalPages(res.data.pages);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const formatTimestamp = (ts: string) => {
    const d = new Date(ts);
    return d.toLocaleString('en-IN', {
      day: '2-digit', month: 'short', year: 'numeric',
      hour: '2-digit', minute: '2-digit', hour12: true
    });
  };

  const getActionStyle = (action: string) => ACTION_STYLES[action] || { color: 'text-secondary', icon: <Eye size={14} />, label: action };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Audit Trail</h1>
        <p className="text-text-secondary text-sm mt-1">{total} log entries</p>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-3">
        <select
          className="input-field w-auto text-sm"
          value={actionFilter}
          onChange={(e) => { setActionFilter(e.target.value); setPage(1); }}
        >
          <option value="">All Actions</option>
          <option value="create">Create</option>
          <option value="update">Update</option>
          <option value="delete">Delete</option>
          <option value="soft_delete">Soft Delete</option>
        </select>
        <select
          className="input-field w-auto text-sm"
          value={resourceFilter}
          onChange={(e) => { setResourceFilter(e.target.value); setPage(1); }}
        >
          <option value="">All Resources</option>
          <option value="financial_record">Financial Record</option>
          <option value="event">Event</option>
          <option value="user">User</option>
        </select>
      </div>

      {/* Timeline */}
      <div className="relative">
        {/* Vertical line */}
        <div className="absolute left-5 top-0 bottom-0 w-px bg-border-layer" />

        <div className="space-y-4">
          {loading ? (
            Array.from({ length: 5 }).map((_, i) => (
              <div key={i} className="ml-12 glass-card p-4 h-16 animate-pulse" />
            ))
          ) : logs.length === 0 ? (
            <div className="ml-12 glass-card p-8 text-center text-text-secondary text-sm">
              No audit logs found matching your filters.
            </div>
          ) : (
            logs.map((log) => {
              const style = getActionStyle(log.action);
              const isExpanded = expanded === log.id;

              return (
                <div key={log.id} className="flex items-start gap-4">
                  {/* Timeline node */}
                  <div className={`relative z-10 w-10 h-10 rounded-full flex items-center justify-center border-2 bg-bg-primary shrink-0 border-${style.color} text-${style.color}`}
                    style={{ boxShadow: `0 0 12px color-mix(in srgb, var(--color-${style.color}) 30%, transparent)` }}
                  >
                    {style.icon}
                  </div>

                  {/* Log card */}
                  <div
                    className="glass-card p-4 flex-1 cursor-pointer hover:border-accent-blue/30 transition-colors"
                    onClick={() => setExpanded(isExpanded ? null : log.id)}
                  >
                    <div className="flex flex-wrap items-center gap-2 mb-1">
                      <span className={`text-[10px] px-2 py-0.5 rounded font-bold uppercase tracking-wider bg-${style.color}/10 text-${style.color} border border-${style.color}/20`}>
                        {style.label}
                      </span>
                      <span className="text-[10px] px-2 py-0.5 rounded font-semibold uppercase tracking-wider bg-bg-card-hover text-text-secondary border border-border-layer">
                        {log.resource_type.replace(/_/g, ' ')}
                      </span>
                    </div>

                    <div className="flex flex-wrap justify-between items-end mt-2">
                      <div className="text-xs text-text-secondary">
                        Resource: <span className="font-mono text-text-primary">{log.resource_id.slice(0, 8)}…</span>
                        &ensp;|&ensp;
                        Actor: <span className="font-mono text-text-primary">{log.actor_id.slice(0, 8)}…</span>
                      </div>
                      <div className="text-[10px] text-text-secondary font-mono">{formatTimestamp(log.timestamp)}</div>
                    </div>

                    {/* Expanded diff view */}
                    {isExpanded && (log.old_data || log.new_data) && (
                      <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
                        {log.old_data && (
                          <div className="bg-[#13131b] rounded-lg p-3 border border-border-layer">
                            <div className="text-accent-red text-[10px] uppercase tracking-wider font-bold mb-2">Old Data</div>
                            <pre className="overflow-auto max-h-40 font-mono text-text-secondary whitespace-pre-wrap">{JSON.stringify(log.old_data, null, 2)}</pre>
                          </div>
                        )}
                        {log.new_data && (
                          <div className="bg-[#13131b] rounded-lg p-3 border border-border-layer">
                            <div className="text-accent-green text-[10px] uppercase tracking-wider font-bold mb-2">New Data</div>
                            <pre className="overflow-auto max-h-40 font-mono text-text-secondary whitespace-pre-wrap">{JSON.stringify(log.new_data, null, 2)}</pre>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              );
            })
          )}
        </div>
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex justify-between items-center text-sm text-text-secondary">
          <span>Page {page} of {totalPages} &bull; {total} logs</span>
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
