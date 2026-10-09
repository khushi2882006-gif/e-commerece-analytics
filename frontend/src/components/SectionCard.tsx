import { ReactNode } from 'react'

interface SectionCardProps {
  title: string
  children: ReactNode
}

export default function SectionCard({ title, children }: SectionCardProps) {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
      <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-4">{title}</h3>
      {children}
    </div>
  )
}
