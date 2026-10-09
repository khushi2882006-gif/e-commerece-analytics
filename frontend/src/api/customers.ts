import apiClient from './client'
interface DateParams { start_date?: string; end_date?: string }
export const customersApi = {
  getKpis: (p: DateParams) => apiClient.get('/api/customers/kpis', { params: p }),
  getAcquisition: (p: DateParams) => apiClient.get('/api/customers/acquisition', { params: p }),
  getByTier: (p: DateParams) => apiClient.get('/api/customers/by-tier', { params: p }),
  getByGeography: (p: DateParams) => apiClient.get('/api/customers/by-geography', { params: p }),
  getCohortRetention: () => apiClient.get('/api/customers/cohort-retention'),
}
