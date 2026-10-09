import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import { DateRangeProvider } from './context/DateRangeContext'
import { ThemeProvider } from './context/ThemeContext'
import ProtectedRoute from './components/ProtectedRoute'
import Layout from './components/Layout'
import LoginPage from './pages/LoginPage'
import SignUpPage from './pages/SignUpPage'
import SalesPage from './pages/SalesPage'
import CustomersPage from './pages/CustomersPage'
import ProductsPage from './pages/ProductsPage'
import InventoryPage from './pages/InventoryPage'
import MarketingPage from './pages/MarketingPage'
import FulfillmentPage from './pages/FulfillmentPage'

export default function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <DateRangeProvider>
          <BrowserRouter>
            <Routes>
              <Route path="/login" element={<LoginPage />} />
              <Route path="/signup" element={<SignUpPage />} />
              <Route
                path="/"
                element={
                  <ProtectedRoute>
                    <Layout />
                  </ProtectedRoute>
                }
              >
                <Route index element={<Navigate to="/sales" replace />} />
                <Route path="sales" element={<SalesPage />} />
                <Route path="customers" element={<CustomersPage />} />
                <Route path="products" element={<ProductsPage />} />
                <Route path="inventory" element={<InventoryPage />} />
                <Route path="marketing" element={<MarketingPage />} />
                <Route path="fulfillment" element={<FulfillmentPage />} />
              </Route>
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </BrowserRouter>
        </DateRangeProvider>
      </AuthProvider>
    </ThemeProvider>
  )
}
