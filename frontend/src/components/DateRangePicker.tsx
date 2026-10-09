import { useDateRange } from '../context/DateRangeContext'

export default function DateRangePicker() {
  const { dateRange, setDateRange } = useDateRange()

  return (
    <div className="flex items-center gap-2 text-sm">
      <label className="text-gray-500 dark:text-gray-400">From</label>
      <input
        type="date"
        value={dateRange.startDate}
        onChange={e => setDateRange({ ...dateRange, startDate: e.target.value })}
        className="border border-gray-300 dark:border-gray-600 rounded px-2 py-1 text-sm bg-white dark:bg-gray-700 dark:text-white"
      />
      <label className="text-gray-500 dark:text-gray-400">To</label>
      <input
        type="date"
        value={dateRange.endDate}
        onChange={e => setDateRange({ ...dateRange, endDate: e.target.value })}
        className="border border-gray-300 dark:border-gray-600 rounded px-2 py-1 text-sm bg-white dark:bg-gray-700 dark:text-white"
      />
    </div>
  )
}
