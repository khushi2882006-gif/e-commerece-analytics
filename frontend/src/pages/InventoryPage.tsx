import { useState, useEffect } from 'react'
import {
  BarChart, Bar, LineChart, Line, XAxis, YAxis,
  CartesianGrid, Tooltip, ResponsiveContainer
} from 'recharts'
import { useDateRange } from '../context/DateRangeContext'
import { inventoryApi } from '../api/inventory'
import KPICard from '../components/KPICard'
import SectionCard from '../components/SectionCard'
import LoadingSpinner from '../components/LoadingSpinner'
import ErrorMessage from '../components/ErrorMessage'

export default function InventoryPage() {
  const { dateRange } = useDateRange()
  const [kpis, setKpis] = useState<any>(null)
  const [stockLevels, setStockLevels] = useState<any[]>([])
  const [stockouts, setStockouts] = useState<any[]>([])
  const [restockTimeline, setRestockTimeline] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const params = { start_date: dateRange.startDate, end_date: dateRange.endDate }

  useEffect(() => {
    setLoading(true)
    setError('')
    Promise.all([
      inventoryApi.getKpis(params),
      inventoryApi.getStockLevels(),
      inventoryApi.getStockoutEvents(params),
      inventoryApi.getRestockTimeline(params),
    ])
      .then(([k, s, so, rt]) => {
        setKpis(k.data)
        setStockLevels(s.data)
        setStockouts(so.data)
        setRestockTimeline(rt.data)
      })
      .catch(() => setError('Failed to load inventory data.'))
      .finally(() => setLoading(false))
  }, [dateRange])

  if (loading) return <LoadingSpinner />
  if (error) return <ErrorMessage message={error} />

  return (
    <div className="space-y-6">
      <h2 className="text-lg font-bold text-gray-900 dark:text-white">Inventory & Supply Chain</h2>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <KPICard label="Total SKUs" value={kpis?.total_skus ?? 0} />
        <KPICard label="Out of Stock" value={kpis?.out_of_stock_count ?? 0} />
        <KPICard label="Avg Turnover Ratio" value={kpis?.avg_turnover_ratio ?? 0} />
        <KPICard label="Avg DIO (days)" value={kpis?.avg_dio ?? 0} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <SectionCard title="Stock Levels by Category">
          {stockLevels.length === 0 ? (
            <p className="text-center text-gray-400 py-8 text-sm">No data available</p>
          ) : (
            <ResponsiveContainer width="100%" height={240}>
              <BarChart data={stockLevels}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                <XAxis dataKey="category" tick={{ fontSize: 9 }} />
                <YAxis tick={{ fontSize: 11 }} />
                <Tooltip />
                <Bar dataKey="total_stock" fill="#10b981" name="Total Stock" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          )}
        </SectionCard>

        <SectionCard title="Restock Events Over Time">
          {restockTimeline.length === 0 ? (
            <p className="text-center text-gray-400 py-8 text-sm">No data available</p>
          ) : (
            <ResponsiveContainer width="100%" height={240}>
              <LineChart data={restockTimeline}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                <XAxis dataKey="month" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 11 }} />
                <Tooltip />
                <Line type="monotone" dataKey="total_restocked" stroke="#10b981" strokeWidth={2} dot={false} name="Units Restocked" />
              </LineChart>
            </ResponsiveContainer>
          )}
        </SectionCard>
      </div>

      <SectionCard title="Low Stock / Out-of-Stock Products">
        {stockouts.length === 0 ? (
          <p className="text-center text-gray-400 py-4 text-sm">No low-stock products found</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-200 dark:border-gray-700">
                  <th className="text-left py-2 px-3 text-gray-500 font-medium">Product</th>
                  <th className="text-left py-2 px-3 text-gray-500 font-medium">Category</th>
                  <th className="text-right py-2 px-3 text-gray-500 font-medium">Stock Qty</th>
                </tr>
              </thead>
              <tbody>
                {stockouts.map((row: any) => (
                  <tr key={row.name} className="border-b border-gray-100 dark:border-gray-700/50">
                    <td className="py-2 px-3">{row.name}</td>
                    <td className="py-2 px-3 text-gray-500">{row.category}</td>
                    <td className={`py-2 px-3 text-right font-medium ${row.stock_quantity === 0 ? 'text-red-500' : 'text-yellow-500'}`}>
                      {row.stock_quantity}
                    </td>
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
