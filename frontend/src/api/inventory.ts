import apiClient from './client'
interface DateParams { start_date?: string; end_date?: string }
export const inventoryApi = {
  getKpis: (p: DateParams) => apiClient.get('/api/inventory/kpis', { params: p }),
  getStockLevels: () => apiClient.get('/api/inventory/stock-levels'),
  getTurnover: () => apiClient.get('/api/inventory/turnover'),
  getStockoutEvents: (p: DateParams) => apiClient.get('/api/inventory/stockout-events', { params: p }),
  getRestockTimeline: (p: DateParams) => apiClient.get('/api/inventory/restock-timeline', { params: p }),
}
