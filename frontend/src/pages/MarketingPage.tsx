import { useState, useEffect } from 'react'
import {
  BarChart, Bar, LineChart, Line, XAxis, YAxis,
  CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts'
import { useDateRange } from '../context/DateRangeContext'
import { marketingApi } from '../api/marketing'
import KPICard from '../components/KPICard'
import SectionCard from '../components/SectionCard'
import LoadingSpinner from '../components/LoadingSpinner'
import ErrorMessage from '../components/ErrorMessage'

export default function MarketingPage() {
  const { dateRange } = useDateRange()
  const [kpis, setKpis] = useState<any>(null)
  const [promoImpact, setPromoImpact] = useState<any[]>([])
  const [channelConv, setChannelConv] = useState<any[]>([])
  const [spendVsRevenue, setSpendVsRevenue] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const params = { start_date: dateRange.startDate, end_date: dateRange.endDate }

  useEffect(() => {
    setLoading(true)
    setError('')
    Promise.all([
      marketingApi.getKpis(params),
      marketingApi.getPromoImpact(params),
      marketingApi.getChannelConversion(params),
      marketingApi.getSpendVsRevenue(params),
    ])
      .then(([k, p, c, s]) => {
        setKpis(k.data)
        setPromoImpact(p.data)
        setChannelConv(c.data)
        setSpendVsRevenue(s.data)
      })
      .catch(() => setError('Failed to load marketing data.'))
      .finally(() => setLoading(false))
  }, [dateRange])

  if (loading) return <LoadingSpinner />
  if (error) return <ErrorMessage message={error} />

  return (
    <div className="space-y-6">
      <h2 className="text-lg font-bold text-gray-900 dark:text-white">Marketing Effectiveness</h2>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <KPICard label="Total Spend" value={`$${(kpis?.total_spend ?? 0).toLocaleString()}`} />
        <KPICard label="Promo Revenue" value={`$${(kpis?.promo_revenue ?? 0).toLocaleString()}`} />
        <KPICard label="ROAS" value={kpis?.roas ?? 0} subtitle="Revenue per $1 spent" />
        <KPICard label="CPA" value={`$${kpis?.cpa ?? 0}`} subtitle="Cost per acquisition" />
      </div>

      <SectionCard title="Monthly Spend vs Revenue">
        {spendVsRevenue.length === 0 ? (
          <p className="text-center text-gray-400 py-8 text-sm">No data available</p>
        ) : (
          <ResponsiveContainer width="100%" height={260}>
            <LineChart data={spendVsRevenue}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis dataKey="month" tick={{ fontSize: 11 }} />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip formatter={(v: any) => `$${Number(v).toLocaleString()}`} />
              <Legend />
              <Line type="monotone" dataKey="revenue" stroke="#3b82f6" strokeWidth={2} dot={false} name="Revenue" />
              <Line type="monotone" dataKey="spend" stroke="#ef4444" strokeWidth={2} dot={false} name="Spend" />
            </LineChart>
          </ResponsiveContainer>
        )}
      </SectionCard>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <SectionCard title="Promo Code Revenue Impact">
          {promoImpact.length === 0 ? (
            <p className="text-center text-gray-400 py-8 text-sm">No data available</p>
          ) : (
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={promoImpact}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                <XAxis dataKey="promo_code" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 11 }} />
                <Tooltip formatter={(v: any) => `$${Number(v).toLocaleString()}`} />
                <Bar dataKey="revenue" fill="#8b5cf6" name="Revenue" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          )}
        </SectionCard>

        <SectionCard title="Orders by Channel">
          {channelConv.length === 0 ? (
            <p className="text-center text-gray-400 py-8 text-sm">No data available</p>
          ) : (
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={channelConv}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                <XAxis dataKey="channel" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 11 }} />
                <Tooltip />
                <Legend />
                <Bar dataKey="orders" fill="#3b82f6" name="Orders" radius={[4, 4, 0, 0]} />
                <Bar dataKey="returns" fill="#ef4444" name="Returns" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          )}
        </SectionCard>
      </div>
    </div>
  )
}
