import { useState, useEffect } from 'react'
import {
  BarChart, Bar, LineChart, Line, XAxis, YAxis,
  CartesianGrid, Tooltip, ResponsiveContainer
} from 'recharts'
import { useDateRange } from '../context/DateRangeContext'
import { fulfillmentApi } from '../api/fulfillment'
import KPICard from '../components/KPICard'
import SectionCard from '../components/SectionCard'
import LoadingSpinner from '../components/LoadingSpinner'
import ErrorMessage from '../components/ErrorMessage'

export default function FulfillmentPage() {
  const { dateRange } = useDateRange()
  const [kpis, setKpis] = useState<any>(null)
  const [byCarrier, setByCarrier] = useState<any[]>([])
  const [trend, setTrend] = useState<any[]>([])
  const [failedOrders, setFailedOrders] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const params = { start_date: dateRange.startDate, end_date: dateRange.endDate }

  useEffect(() => {
    setLoading(true)
    setError('')
    Promise.all([
      fulfillmentApi.getKpis(params),
      fulfillmentApi.getByCarrier(params),
      fulfillmentApi.getDeliveryTrend(params),
      fulfillmentApi.getFulfillmentCycle(params),
    ])
      .then(([k, c, t, f]) => {
        setKpis(k.data)
        setByCarrier(c.data)
        setTrend(t.data)
        setFailedOrders(f.data)
      })
      .catch(() => setError('Failed to load fulfillment data.'))
      .finally(() => setLoading(false))
  }, [dateRange])

  if (loading) return <LoadingSpinner />
  if (error) return <ErrorMessage message={error} />

  return (
    <div className="space-y-6">
      <h2 className="text-lg font-bold text-gray-900 dark:text-white">Fulfillment & Logistics</h2>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <KPICard label="Avg Delivery Days" value={kpis?.avg_delivery_days ?? 0} />
        <KPICard label="Late Delivery Rate" value={`${kpis?.late_delivery_rate ?? 0}%`} />
        <KPICard label="Failed Delivery Rate" value={`${kpis?.failed_delivery_rate ?? 0}%`} />
        <KPICard label="Fulfillment Cycle" value={`${kpis?.avg_fulfillment_cycle_days ?? 0} days`} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <SectionCard title="Avg Delivery Days by Carrier">
          {byCarrier.length === 0 ? (
            <p className="text-center text-gray-400 py-8 text-sm">No data available</p>
          ) : (
            <ResponsiveContainer width="100%" height={240}>
              <BarChart data={byCarrier}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                <XAxis dataKey="carrier" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 11 }} />
                <Tooltip />
                <Bar dataKey="avg_delivery_days" fill="#f59e0b" name="Avg Days" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          )}
        </SectionCard>

        <SectionCard title="Delivery Time Trend">
          {trend.length === 0 ? (
            <p className="text-center text-gray-400 py-8 text-sm">No data available</p>
          ) : (
            <ResponsiveContainer width="100%" height={240}>
              <LineChart data={trend}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                <XAxis dataKey="month" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 11 }} />
                <Tooltip />
                <Line type="monotone" dataKey="avg_delivery_days" stroke="#f59e0b" strokeWidth={2} dot={false} name="Avg Delivery Days" />
              </LineChart>
            </ResponsiveContainer>
          )}
        </SectionCard>
      </div>

      <SectionCard title="Failed / In-Transit Orders">
        {failedOrders.length === 0 ? (
          <p className="text-center text-gray-400 py-4 text-sm">No failed or in-transit orders</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-200 dark:border-gray-700">
                  <th className="text-left py-2 px-3 text-gray-500 font-medium">Order ID</th>
                  <th className="text-left py-2 px-3 text-gray-500 font-medium">Carrier</th>
                  <th className="text-left py-2 px-3 text-gray-500 font-medium">Order Date</th>
                  <th className="text-left py-2 px-3 text-gray-500 font-medium">Shipped</th>
                  <th className="text-left py-2 px-3 text-gray-500 font-medium">Status</th>
                  <th className="text-right py-2 px-3 text-gray-500 font-medium">Cycle Days</th>
                </tr>
              </thead>
              <tbody>
                {failedOrders.map((row: any) => (
                  <tr key={row.order_id} className="border-b border-gray-100 dark:border-gray-700/50">
                    <td className="py-2 px-3 font-mono text-xs">{row.order_id}</td>
                    <td className="py-2 px-3">{row.carrier}</td>
                    <td className="py-2 px-3 text-gray-500">{row.order_date}</td>
                    <td className="py-2 px-3 text-gray-500">{row.shipped_date ?? '—'}</td>
                    <td className="py-2 px-3">
                      <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${
                        row.status === 'failed' ? 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400' : 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400'
                      }`}>
                        {row.status}
                      </span>
                    </td>
                    <td className="py-2 px-3 text-right">{row.cycle_days ?? '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </SectionCard>
    </div>
  )
}
