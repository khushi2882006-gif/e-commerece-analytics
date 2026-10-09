import apiClient from './client'

interface DateParams {
  start_date?: string
  end_date?: string
}

export const salesApi = {
  getKpis: (params: DateParams) => apiClient.get('/api/sales/kpis', { params }),
  getTrend: (params: DateParams & { period?: string }) => apiClient.get('/api/sales/trend', { params }),
  getByChannel: (params: DateParams) => apiClient.get('/api/sales/by-channel', { params }),
  getRevenueVsTarget: (params: DateParams) => apiClient.get('/api/sales/revenue-vs-target', { params }),
}
