import { createContext, useContext, useState, ReactNode } from 'react'

function formatDate(d: Date): string {
  return d.toISOString().split('T')[0]
}

interface DateRange {
  startDate: string
  endDate: string
}

interface DateRangeContextType {
  dateRange: DateRange
  setDateRange: (range: DateRange) => void
}

const DateRangeContext = createContext<DateRangeContextType | null>(null)

export function DateRangeProvider({ children }: { children: ReactNode }) {
  const now = new Date()
  const thirtyDaysAgo = new Date(now)
  thirtyDaysAgo.setDate(now.getDate() - 30)

  const [dateRange, setDateRange] = useState<DateRange>({
    startDate: formatDate(thirtyDaysAgo),
    endDate: formatDate(now),
  })

  return (
    <DateRangeContext.Provider value={{ dateRange, setDateRange }}>
      {children}
    </DateRangeContext.Provider>
  )
}

export function useDateRange() {
  const ctx = useContext(DateRangeContext)
  if (!ctx) throw new Error('useDateRange must be used within DateRangeProvider')
  return ctx
}
