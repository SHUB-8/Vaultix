import React, { useEffect, useState } from 'react';
import api from '../services/api';
import { useAuth } from '../context/AuthContext';
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { TrendingUp, TrendingDown, Wallet, FileText, AlertTriangle } from 'lucide-react';

interface Summary {
  total_income: number;
  total_expenses: number;
  net_balance: number;
  total_records: number;
  as_of: string;
}

interface TrendItem {
  month: string;
  income: number;
  expenses: number;
}

interface EventPnLItem {
  event_id: string;
  event_name: string;
  income: number;
  expenses: number;
  profit_loss: number;
}

interface CategoryItem {
  category: string;
  amount: number;
  percentage: number;
}

interface Analytics {
  summary: Summary;
  sponsorship_dependency_ratio: number;
  top_expense_category: string | null;
  top_income_source: string | null;
  month_over_month_trend: TrendItem[];
  event_pnl: EventPnLItem[];
  category_breakdown: CategoryItem[];
}

const DONUT_COLORS = ['#3b82f6', '#a855f7', '#ef4444', '#eab308', '#22c55e', '#06b6d4', '#f97316'];

export default function Dashboard() {
  const { user } = useAuth();
  const [summary, setSummary] = useState<Summary | null>(null);
  const [analytics, setAnalytics] = useState<Analytics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchData = async () => {
      try {
        if (user?.role === 'viewer') {
          const res = await api.get('/dashboard/summary');
          setSummary(res.data);
        } else {
          const res = await api.get('/dashboard/analytics');
          const finalData = { ...res.data };
          
          finalData.month_over_month_trend = finalData.month_over_month_trend.map((t: any) => ({
            ...t,
            income: Number(t.income),
            expenses: Number(t.expenses)
          }));
          
          finalData.event_pnl = finalData.event_pnl.map((e: any) => ({
            ...e,
            income: Number(e.income),
            expenses: Number(e.expenses),
            profit_loss: Number(e.profit_loss)
          }));
          
          finalData.category_breakdown = finalData.category_breakdown.map((c: any) => ({
            ...c,
            amount: Number(c.amount),
            percentage: Number(c.percentage)
          }));

          setAnalytics(finalData);
          setSummary(finalData.summary);
        }
      } catch (err: any) {
        console.error(err);
        setError(err.response?.data?.error?.message || 'Failed to load dashboard data.');
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [user]);

  const formatCurrency = (val: number) =>
    `₹${Number(val).toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="h-8 w-64 bg-bg-card rounded animate-pulse" />
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {[1,2,3,4].map(i => <div key={i} className="glass-card p-6 h-28 animate-pulse" />)}
        </div>
        <div className="glass-card h-80 animate-pulse" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="glass-card p-8 text-center">
        <AlertTriangle className="mx-auto mb-4 text-accent-red" size={40} />
        <p className="text-accent-red font-semibold">{error}</p>
      </div>
    );
  }

  const depRatio = analytics?.sponsorship_dependency_ratio ?? 0;
  const depColor = depRatio < 50 ? 'text-accent-green' : depRatio < 70 ? 'text-accent-yellow' : 'text-accent-red';

  return (
    <div className="space-y-6">
      {/* Header */}
      <header className="flex justify-between items-end mb-2">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Dashboard Overview</h1>
          <p className="text-text-secondary text-sm mt-1">
            Real-time metrics &bull; as of {summary?.as_of}
            {user?.assigned_event_id && (
              <span className="ml-3 text-accent-yellow text-xs font-semibold uppercase tracking-wider">
                ● Restricted View
              </span>
            )}
          </p>
        </div>
      </header>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <SummaryCard icon={<TrendingUp size={20}/>} label="Total Society Funds" value={formatCurrency(summary?.total_income ?? 0)} color="accent-green" />
        <SummaryCard icon={<TrendingDown size={20}/>} label="Total Expenses" value={formatCurrency(summary?.total_expenses ?? 0)} color="accent-red" />
        <SummaryCard icon={<Wallet size={20}/>} label="Net Balance" value={formatCurrency(summary?.net_balance ?? 0)} color="accent-blue" />
        <SummaryCard icon={<FileText size={20}/>} label="Active Records" value={String(summary?.total_records ?? 0)} color="accent-purple" />
      </div>

      {/* Viewer-only message */}
      {user?.role === 'viewer' && (
        <div className="glass-card p-8 text-center text-text-secondary">
          <p className="text-sm">Contact an Admin or Analyst for detailed analytics and charts.</p>
        </div>
      )}

      {/* Analytics Section (Admin + Analyst only) */}
      {analytics && (
        <>
          {/* Top insights bar */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div className="glass-card p-4 flex flex-col">
              <span className="text-[10px] uppercase tracking-widest text-text-secondary font-semibold mb-1">Sponsorship Dependency</span>
              <span className={`text-2xl font-mono font-bold ${depColor}`}>{Number(depRatio).toFixed(1)}%</span>
              <span className="text-[10px] text-text-secondary mt-1">of total income from sponsors</span>
            </div>
            <div className="glass-card p-4 flex flex-col">
              <span className="text-[10px] uppercase tracking-widest text-text-secondary font-semibold mb-1">Top Income Source</span>
              <span className="text-sm font-semibold text-accent-green capitalize">{analytics.top_income_source?.replace(/_/g, ' ') || '—'}</span>
            </div>
            <div className="glass-card p-4 flex flex-col">
              <span className="text-[10px] uppercase tracking-widest text-text-secondary font-semibold mb-1">Top Expense Category</span>
              <span className="text-sm font-semibold text-accent-red capitalize">{analytics.top_expense_category?.replace(/_/g, ' ') || '—'}</span>
            </div>
          </div>

          {/* Trend Chart */}
          {analytics.month_over_month_trend.length > 0 && (
            <div className="glass-card p-6">
              <h3 className="text-xs font-semibold uppercase tracking-widest text-text-secondary mb-6">Income vs Expenses Trend</h3>
              <div className="h-72">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={analytics.month_over_month_trend} margin={{ top: 5, right: 10, left: 0, bottom: 0 }}>
                    <defs>
                      <linearGradient id="gIncome" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#22c55e" stopOpacity={0.25} />
                        <stop offset="95%" stopColor="#22c55e" stopOpacity={0} />
                      </linearGradient>
                      <linearGradient id="gExpense" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#ef4444" stopOpacity={0.25} />
                        <stop offset="95%" stopColor="#ef4444" stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <XAxis dataKey="month" stroke="#2d2d4a" tick={{ fill: '#94a3b8', fontSize: 11 }} />
                    <YAxis stroke="#2d2d4a" tick={{ fill: '#94a3b8', fontSize: 11 }} tickFormatter={(v: number) => `₹${(v / 1000).toFixed(0)}k`} />
                    <Tooltip
                      contentStyle={{ backgroundColor: '#1a1a2e', borderColor: '#2d2d4a', borderRadius: '8px', fontSize: '12px' }}
                      formatter={(value: any) => formatCurrency(Number(value))}
                      labelStyle={{ color: '#94a3b8' }}
                    />
                    <Area type="monotone" dataKey="income" name="Income" stroke="#22c55e" strokeWidth={2} fillOpacity={1} fill="url(#gIncome)" />
                    <Area type="monotone" dataKey="expenses" name="Expenses" stroke="#ef4444" strokeWidth={2} fillOpacity={1} fill="url(#gExpense)" />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </div>
          )}

          {/* Bottom Row: Event P&L + Category Donut */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Event P&L */}
            <div className="glass-card p-6">
              <h3 className="text-xs font-semibold uppercase tracking-widest text-text-secondary mb-4">Event Profit & Loss</h3>
              {analytics.event_pnl.length > 0 ? (
                <div className="space-y-3">
                  {analytics.event_pnl.map((ev) => (
                    <div key={ev.event_id} className="flex items-center justify-between p-3 rounded-lg bg-[#13131b] border border-border-layer hover:border-accent-blue/40 transition-colors group">
                      <div>
                        <span className="font-semibold text-sm group-hover:text-accent-blue transition-colors">{ev.event_name}</span>
                        <div className="flex gap-3 mt-1 text-[11px] text-text-secondary font-mono">
                          <span>IN: <span className="text-accent-green">{formatCurrency(ev.income)}</span></span>
                          <span>OUT: <span className="text-accent-red">{formatCurrency(ev.expenses)}</span></span>
                        </div>
                      </div>
                      <span className={`font-mono text-sm font-bold ${ev.profit_loss >= 0 ? 'text-accent-green' : 'text-accent-red'}`}>
                        {ev.profit_loss >= 0 ? '+' : ''}{formatCurrency(ev.profit_loss)}
                      </span>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-text-secondary text-sm text-center py-6">No event data available for your scope.</p>
              )}
            </div>

            {/* Category Breakdown Donut */}
            <div className="glass-card p-6">
              <h3 className="text-xs font-semibold uppercase tracking-widest text-text-secondary mb-4">Expense Category Breakdown</h3>
              {analytics.category_breakdown.length > 0 ? (
                <div className="flex flex-col items-center">
                  <div className="h-52 w-52">
                    <ResponsiveContainer width="100%" height="100%">
                      <PieChart>
                        <Pie
                          data={analytics.category_breakdown}
                          dataKey="amount"
                          nameKey="category"
                          cx="50%"
                          cy="50%"
                          innerRadius={55}
                          outerRadius={80}
                          paddingAngle={3}
                          strokeWidth={0}
                        >
                          {analytics.category_breakdown.map((_, i) => (
                            <Cell key={i} fill={DONUT_COLORS[i % DONUT_COLORS.length]} />
                          ))}
                        </Pie>
                        <Tooltip
                          contentStyle={{ backgroundColor: '#1a1a2e', borderColor: '#2d2d4a', borderRadius: '8px', fontSize: '12px' }}
                          formatter={(value: any) => formatCurrency(Number(value))}
                        />
                      </PieChart>
                    </ResponsiveContainer>
                  </div>
                  <div className="w-full mt-4 space-y-2">
                    {analytics.category_breakdown.map((cat, i) => (
                      <div key={cat.category} className="flex items-center justify-between text-sm">
                        <div className="flex items-center gap-2">
                          <div className="w-3 h-3 rounded-sm" style={{ backgroundColor: DONUT_COLORS[i % DONUT_COLORS.length] }} />
                          <span className="text-text-secondary capitalize">{cat.category.replace(/_/g, ' ')}</span>
                        </div>
                        <div className="flex items-center gap-3">
                          <span className="font-mono text-text-primary text-xs">{formatCurrency(cat.amount)}</span>
                          <span className="text-text-secondary text-xs font-mono">{Number(cat.percentage).toFixed(1)}%</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              ) : (
                <p className="text-text-secondary text-sm text-center py-6">No expense data available.</p>
              )}
            </div>
          </div>
        </>
      )}
    </div>
  );
}

function SummaryCard({ icon, label, value, color }: { icon: React.ReactNode; label: string; value: string; color: string }) {
  return (
    <div className="glass-card p-5 relative overflow-hidden group">
      <div className="flex items-center gap-2 mb-3">
        <div className={`w-8 h-8 rounded-lg flex items-center justify-center bg-${color}/10 text-${color}`}>
          {icon}
        </div>
        <span className="text-[10px] uppercase tracking-widest text-text-secondary font-semibold">{label}</span>
      </div>
      <div className={`text-2xl font-mono font-bold text-${color}`}>{value}</div>
      {/* subtle ambient glow */}
      <div className={`absolute -bottom-4 -right-4 w-20 h-20 rounded-full bg-${color}/10 blur-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-500`} />
    </div>
  );
}
