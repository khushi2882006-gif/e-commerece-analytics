import { useState, useEffect } from 'react'
import {
  LineChart, Line, PieChart, Pie, Cell, XAxis, YAxis,
  CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts'
import { useDateRange } from '../context/DateRangeContext'
import { customersApi } from '../api/customers'
import KPICard from '../components/KPICard'
import SectionCard from '../components/SectionCard'
import LoadingSpinner from '../components/LoadingSpinner'
import ErrorMessage from '../components/ErrorMessage'

const TIER_COLORS: Record<string, string> = { gold: '#f59e0b', silver: '#9ca3af', bronze: '#b45309' }
const PIE_COLORS = ['#f59e0b', '#9ca3af', '#b45309']

export default function CustomersPage() {
  const { dateRange } = useDateRange()
  const [kpis, setKpis] = useState<any>(null)
  const [acquisition, setAcquisition] = useState<any[]>([])
  const [tiers, setTiers] = useState<any[]>([])
  const [geo, setGeo] = useState<any[]>([])
  const [cohort, setCohort] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const params = { start_date: dateRange.startDate, end_date: dateRange.endDate }

  useEffect(() => {
    setLoading(true)
    setError('')
    Promise.all([
      customersApi.getKpis(params),
      customersApi.getAcquisition(params),
      customersApi.getByTier(params),
      customersApi.getByGeography(params),
      customersApi.getCohortRetention(),
    ])
      .then(([k, a, t, g, c]) => {
        setKpis(k.data)
        setAcquisition(a.data)
        setTiers(t.data)
        setGeo(g.data)
        setCohort(c.data)
      })
      .catch(() => setError('Failed to load customer data.'))
      .finally(() => setLoading(false))
  }, [dateRange])

  if (loading) return <LoadingSpinner />
  if (error) return <ErrorMessage message={error} />

  const retentionColor = (pct: number) =>
    pct >= 50 ? 'bg-green-600 text-white' : pct >= 25 ? 'bg-yellow-400 text-black' : 'bg-red-400 text-white'

  return (
    <div className="space-y-6">
      <h2 className="text-lg font-bold text-gray-900 dark:text-white">Customer Analytics</h2>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <KPICard label="Total Customers" value={kpis?.total_customers ?? 0} />
        <KPICard label="New Customers" value={kpis?.new_customers ?? 0} />
        <KPICard label="Returning Customers" value={kpis?.returning_customers ?? 0} />
        <KPICard label="Avg Lifetime Value" value={`$${kpis?.avg_clv ?? 0}`} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <SectionCard title="Customer Acquisition Over Time">
          {acquisition.length === 0 ? (
            <p className="text-center text-gray-400 py-8 text-sm">No data available</p>
          ) : (
            <ResponsiveContainer width="100%" height={220}>
              <LineChart data={acquisition}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                <XAxis dataKey="month" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 11 }} />
                <Tooltip />
                <Line type="monotone" dataKey="new_customers" stroke="#8b5cf6" strokeWidth={2} dot={false} name="New Customers" />
              </LineChart>
            </ResponsiveContainer>
          )}
        </SectionCard>

        <SectionCard title="Customers by Tier">
          {tiers.length === 0 ? (
            <p className="text-center text-gray-400 py-8 text-sm">No data available</p>
          ) : (
            <ResponsiveContainer width="100%" height={220}>
              <PieChart>
                <Pie data={tiers} dataKey="customer_count" nameKey="tier" cx="50%" cy="50%" innerRadius={55} outerRadius={90} label>
                  {tiers.map((entry: any, index: number) => (
                    <Cell key={entry.tier} fill={PIE_COLORS[index % PIE_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          )}
        </SectionCard>
      </div>

      {/* Geography Table */}
      <SectionCard title="Revenue by Country (Top 10)">
        {geo.length === 0 ? (
          <p className="text-center text-gray-400 py-4 text-sm">No data available</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-200 dark:border-gray-700">
                  <th className="text-left py-2 px-3 text-gray-500 dark:text-gray-400 font-medium">Country</th>
                  <th className="text-right py-2 px-3 text-gray-500 dark:text-gray-400 font-medium">Orders</th>
                  <th className="text-right py-2 px-3 text-gray-500 dark:text-gray-400 font-medium">Revenue</th>
                </tr>
              </thead>
              <tbody>
                {geo.slice(0, 10).map((row: any) => (
                  <tr key={row.country} className="border-b border-gray-100 dark:border-gray-700/50 hover:bg-gray-50 dark:hover:bg-gray-700/30">
                    <td className="py-2 px-3">{row.country}</td>
                    <td className="py-2 px-3 text-right">{row.orders}</td>
                    <td className="py-2 px-3 text-right font-medium">${row.revenue.toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </SectionCard>

      {/* Cohort Retention */}
      {cohort && cohort.cohorts?.length > 0 && (
        <SectionCard title="Cohort Retention (%)">
          <div className="overflow-x-auto">
            <table className="text-xs border-collapse">
              <thead>
                <tr>
                  <th className="px-2 py-1 text-left text-gray-500">Cohort</th>
                  <th className="px-2 py-1 text-right text-gray-500">Size</th>
                  {cohort.months.slice(0, 8).map((m: string) => (
                    <th key={m} className="px-2 py-1 text-center text-gray-500">{m}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {cohort.cohorts.map((row: any) => (
                  <tr key={row.cohort_month}>
                    <td className="px-2 py-1 font-medium">{row.cohort_month}</td>
                    <td className="px-2 py-1 text-right text-gray-400">{row.cohort_size}</td>
                    {row.retention.slice(0, 8).map((pct: number, i: number) => (
                      <td key={i} className={`px-2 py-1 text-center rounded ${retentionColor(pct)}`}>
                        {pct}%
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </SectionCard>
      )}
    </div>
  )
}
