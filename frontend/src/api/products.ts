import apiClient from './client'
interface DateParams { start_date?: string; end_date?: string }
export const productsApi = {
  getKpis: (p: DateParams) => apiClient.get('/api/products/kpis', { params: p }),
  getTopSelling: (p: DateParams & { limit?: number }) => apiClient.get('/api/products/top-selling', { params: p }),
  getByCategory: (p: DateParams) => apiClient.get('/api/products/by-category', { params: p }),
  getSlowMoving: (p: DateParams) => apiClient.get('/api/products/slow-moving', { params: p }),
  getPriceDistribution: (p: DateParams) => apiClient.get('/api/products/price-distribution', { params: p }),
}
