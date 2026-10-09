import { Outlet, NavLink, useNavigate } from 'react-router-dom'
import {
  ShoppingCart, Users, Package, Warehouse, Megaphone, Truck,
  LogOut, Moon, Sun, BarChart2,
} from 'lucide-react'
import { useAuth } from '../context/AuthContext'
import { useTheme } from '../context/ThemeContext'
import DateRangePicker from './DateRangePicker'

const navItems = [
  { to: '/sales', label: 'Sales', icon: BarChart2 },
  { to: '/customers', label: 'Customers', icon: Users },
  { to: '/products', label: 'Products', icon: Package },
  { to: '/inventory', label: 'Inventory', icon: Warehouse },
  { to: '/marketing', label: 'Marketing', icon: Megaphone },
  { to: '/fulfillment', label: 'Fulfillment', icon: Truck },
]

export default function Layout() {
  const { logout } = useAuth()
  const { isDark, toggle } = useTheme()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <div className="flex h-screen overflow-hidden bg-gray-50 dark:bg-gray-900">
      {/* Sidebar */}
      <aside className="w-56 flex-shrink-0 flex flex-col bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700">
        <div className="px-4 py-5 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center gap-2">
            <ShoppingCart className="text-blue-600" size={20} />
            <span className="font-bold text-sm text-gray-800 dark:text-white">Sales Analytics</span>
          </div>
        </div>
        <nav className="flex-1 px-2 py-4 space-y-1 overflow-y-auto">
          {navItems.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300'
                    : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700'
                }`
              }
            >
              <Icon size={16} />
              {label}
            </NavLink>
          ))}
        </nav>
        <div className="px-2 py-4 border-t border-gray-200 dark:border-gray-700 space-y-1">
          <button
            onClick={toggle}
            className="flex items-center gap-3 w-full px-3 py-2 rounded-md text-sm text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700"
          >
            {isDark ? <Sun size={16} /> : <Moon size={16} />}
            {isDark ? 'Light Mode' : 'Dark Mode'}
          </button>
          <button
            onClick={handleLogout}
            className="flex items-center gap-3 w-full px-3 py-2 rounded-md text-sm text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20"
          >
            <LogOut size={16} />
            Logout
          </button>
        </div>
      </aside>

      {/* Main content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        <header className="flex items-center justify-end gap-4 px-6 py-3 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
          <DateRangePicker />
        </header>
        <main className="flex-1 overflow-y-auto p-6">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
