import { TrendingUp, TrendingDown, Minus } from 'lucide-react'

interface KPICardProps {
  label: string
  value: string | number
  change?: number
  unit?: string
  subtitle?: string
}

export default function KPICard({ label, value, change, unit, subtitle }: KPICardProps) {
  const changeColor =
    change === undefined || change === 0
      ? 'text-gray-500'
      : change > 0
      ? 'text-green-600 dark:text-green-400'
      : 'text-red-500 dark:text-red-400'

  const ChangeIcon = change === undefined || change === 0 ? Minus : change > 0 ? TrendingUp : TrendingDown

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-700">
      <p className="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wide">{label}</p>
      <p className="mt-1 text-2xl font-bold text-gray-900 dark:text-white">
        {unit && <span className="text-base font-normal mr-0.5">{unit}</span>}
        {typeof value === 'number' ? value.toLocaleString() : value}
      </p>
      {change !== undefined && (
        <div className={`flex items-center gap-1 mt-1 text-xs font-medium ${changeColor}`}>
          <ChangeIcon size={12} />
          <span>{Math.abs(change)}% vs prev period</span>
        </div>
      )}
      {subtitle && <p className="text-xs text-gray-400 mt-1">{subtitle}</p>}
    </div>
  )
}
