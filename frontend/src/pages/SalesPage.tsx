import { useState, useEffect } from 'react'
import {
  LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, Legend, ResponsiveContainer, ReferenceLine
} from 'recharts'
import { useDateRange } from '../context/DateRangeContext'
import { salesApi } from '../api/sales'
import KPICard from '../components/KPICard'
import SectionCard from '../components/SectionCard'
import LoadingSpinner from '../components/LoadingSpinner'
import ErrorMessage from '../components/ErrorMessage'

type Period = 'day' | 'week' | 'month'

export default function SalesPage() {
  const { dateRange } = useDateRange()
  const [kpis, setKpis] = useState<any>(null)
  const [trend, setTrend] = useState<any[]>([])
  const [channels, setChannels] = useState<any[]>([])
  const [targets, setTargets] = useState<any[]>([])
  const [period, setPeriod] = useState<Period>('month')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const params = { start_date: dateRange.startDate, end_date: dateRange.endDate }

  useEffect(() => {
    setLoading(true)
    setError('')
    Promise.all([
      salesApi.getKpis(params),
      salesApi.getTrend({ ...params, period }),
      salesApi.getByChannel(params),
      salesApi.getRevenueVsTarget(params),
    ])
      .then(([k, t, c, rv]) => {
        setKpis(k.data)
        setTrend(t.data)
        setChannels(c.data)
        setTargets(rv.data)
      })
      .catch(() => setError('Failed to load sales data.'))
      .finally(() => setLoading(false))
  }, [dateRange, period])

  if (loading) return <LoadingSpinner />
  if (error) return <ErrorMessage message={error} />

  return (
    <div className="space-y-6">
      <h2 className="text-lg font-bold text-gray-900 dark:text-white">Sales Overview</h2>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <KPICard label="Total Revenue" value={`$${(kpis?.total_revenue ?? 0).toLocaleString()}`} change={kpis?.mom_change} />
        <KPICard label="Total Orders" value={kpis?.total_orders ?? 0} change={kpis?.mom_change} />
        <KPICard label="Avg Order Value" value={`$${kpis?.aov ?? 0}`} />
        <KPICard label="Refund Rate" value={`${kpis?.refund_rate ?? 0}%`} subtitle="of all orders" />
      </div>

      {/* Revenue Trend */}
      <SectionCard title="Revenue Trend">
        <div className="flex gap-2 mb-4">
          {(['day', 'week', 'month'] as Period[]).map(p => (
            <button
              key={p}
              onClick={() => setPeriod(p)}
              className={`px-3 py-1 rounded text-xs font-medium ${period === p ? 'bg-blue-600 text-white' : 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300'}`}
            >
              {p.charAt(0).toUpperCase() + p.slice(1)}
            </button>
          ))}
        </div>
        {trend.length === 0 ? (
          <p className="text-center text-gray-400 py-8 text-sm">No data available</p>
        ) : (
          <ResponsiveContainer width="100%" height={260}>
            <LineChart data={trend}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis dataKey="period" tick={{ fontSize: 11 }} />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip formatter={(v: any) => `$${Number(v).toLocaleString()}`} />
              <Line type="monotone" dataKey="revenue" stroke="#3b82f6" strokeWidth={2} dot={false} name="Revenue" />
            </LineChart>
          </ResponsiveContainer>
        )}
      </SectionCard>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Revenue by Channel */}
        <SectionCard title="Revenue by Channel">
          {channels.length === 0 ? (
            <p className="text-center text-gray-400 py-8 text-sm">No data available</p>
          ) : (
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={channels}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                <XAxis dataKey="channel" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 11 }} />
                <Tooltip formatter={(v: any) => `$${Number(v).toLocaleString()}`} />
                <Bar dataKey="revenue" fill="#3b82f6" name="Revenue" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          )}
        </SectionCard>

        {/* Revenue vs Target */}
        <SectionCard title="Revenue vs Monthly Target">
          {targets.length === 0 ? (
            <p className="text-center text-gray-400 py-8 text-sm">No data available</p>
          ) : (
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={targets}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                <XAxis dataKey="month" tick={{ fontSize: 10 }} />
                <YAxis tick={{ fontSize: 11 }} />
                <Tooltip formatter={(v: any) => `$${Number(v).toLocaleString()}`} />
                <Legend />
                <Bar dataKey="revenue" fill="#3b82f6" name="Revenue" radius={[4, 4, 0, 0]} />
                <Bar dataKey="target" fill="#e5e7eb" name="Target" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          )}
        </SectionCard>
      </div>
    </div>
  )
}
