import { useState, useEffect } from 'react'
import {
  BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis,
  CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts'
import { useDateRange } from '../context/DateRangeContext'
import { productsApi } from '../api/products'
import KPICard from '../components/KPICard'
import SectionCard from '../components/SectionCard'
import LoadingSpinner from '../components/LoadingSpinner'
import ErrorMessage from '../components/ErrorMessage'

const COLORS = ['#3b82f6','#8b5cf6','#10b981','#f59e0b','#ef4444','#6366f1','#14b8a6','#f97316','#ec4899','#84cc16']

export default function ProductsPage() {
  const { dateRange } = useDateRange()
  const [kpis, setKpis] = useState<any>(null)
  const [topSelling, setTopSelling] = useState<any[]>([])
  const [categories, setCategories] = useState<any[]>([])
  const [slowMoving, setSlowMoving] = useState<any[]>([])
  const [priceDist, setPriceDist] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const params = { start_date: dateRange.startDate, end_date: dateRange.endDate }

  useEffect(() => {
    setLoading(true)
    setError('')
    Promise.all([
      productsApi.getKpis(params),
      productsApi.getTopSelling({ ...params, limit: 10 }),
      productsApi.getByCategory(params),
      productsApi.getSlowMoving(params),
      productsApi.getPriceDistribution(params),
    ])
      .then(([k, t, c, s, p]) => {
        setKpis(k.data)
        setTopSelling(t.data)
        setCategories(c.data)
        setSlowMoving(s.data)
        setPriceDist(p.data)
      })
      .catch(() => setError('Failed to load product data.'))
      .finally(() => setLoading(false))
  }, [dateRange])

  if (loading) return <LoadingSpinner />
  if (error) return <ErrorMessage message={error} />

  return (
    <div className="space-y-6">
      <h2 className="text-lg font-bold text-gray-900 dark:text-white">Product Performance</h2>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <KPICard label="Total Products" value={kpis?.total_products ?? 0} />
        <KPICard label="Units Sold" value={kpis?.total_units_sold ?? 0} />
        <KPICard label="Top Category" value={kpis?.top_category ?? 'N/A'} />
        <KPICard label="Avg Sell Price" value={`$${kpis?.avg_sell_price ?? 0}`} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <SectionCard title="Top 10 Products by Revenue">
          {topSelling.length === 0 ? (
            <p className="text-center text-gray-400 py-8 text-sm">No data available</p>
          ) : (
            <ResponsiveContainer width="100%" height={280}>
              <BarChart layout="vertical" data={topSelling} margin={{ left: 80 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                <XAxis type="number" tick={{ fontSize: 10 }} />
                <YAxis type="category" dataKey="name" tick={{ fontSize: 10 }} width={80} />
                <Tooltip formatter={(v: any) => `$${Number(v).toLocaleString()}`} />
                <Bar dataKey="revenue" fill="#3b82f6" name="Revenue" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          )}
        </SectionCard>

        <SectionCard title="Revenue by Category">
          {categories.length === 0 ? (
            <p className="text-center text-gray-400 py-8 text-sm">No data available</p>
          ) : (
            <ResponsiveContainer width="100%" height={280}>
              <PieChart>
                <Pie data={categories} dataKey="revenue" nameKey="category" cx="50%" cy="50%" outerRadius={100} label={({ category }) => category}>
                  {categories.map((_: any, i: number) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                </Pie>
                <Tooltip formatter={(v: any) => `$${Number(v).toLocaleString()}`} />
              </PieChart>
            </ResponsiveContainer>
          )}
        </SectionCard>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <SectionCard title="Price Distribution">
          {priceDist.length === 0 ? (
            <p className="text-center text-gray-400 py-8 text-sm">No data available</p>
          ) : (
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={priceDist}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                <XAxis dataKey="range" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 11 }} />
                <Tooltip />
                <Bar dataKey="count" fill="#8b5cf6" name="Items" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          )}
        </SectionCard>

        <SectionCard title="Slow-Moving Products">
          {slowMoving.length === 0 ? (
            <p className="text-center text-gray-400 py-4 text-sm text-green-600">All products had sales in this period!</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-gray-200 dark:border-gray-700">
                    <th className="text-left py-2 px-2 text-gray-500 font-medium">Product</th>
                    <th className="text-left py-2 px-2 text-gray-500 font-medium">Category</th>
                    <th className="text-right py-2 px-2 text-gray-500 font-medium">Stock</th>
                  </tr>
                </thead>
                <tbody>
                  {slowMoving.slice(0, 8).map((row: any) => (
                    <tr key={row.id} className="border-b border-gray-100 dark:border-gray-700/50">
                      <td className="py-1.5 px-2">{row.name}</td>
                      <td className="py-1.5 px-2 text-gray-500">{row.category}</td>
                      <td className="py-1.5 px-2 text-right">{row.stock_quantity}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </SectionCard>
      </div>
    </div>
  )
}
