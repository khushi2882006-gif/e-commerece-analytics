import apiClient from './client'
interface DateParams { start_date?: string; end_date?: string }
export const marketingApi = {
  getKpis: (p: DateParams) => apiClient.get('/api/marketing/kpis', { params: p }),
  getPromoImpact: (p: DateParams) => apiClient.get('/api/marketing/promo-impact', { params: p }),
  getChannelConversion: (p: DateParams) => apiClient.get('/api/marketing/channel-conversion', { params: p }),
  getSpendVsRevenue: (p: DateParams) => apiClient.get('/api/marketing/spend-vs-revenue', { params: p }),
}
