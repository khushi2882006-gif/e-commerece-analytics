import apiClient from './client'
interface DateParams { start_date?: string; end_date?: string }
export const fulfillmentApi = {
  getKpis: (p: DateParams) => apiClient.get('/api/fulfillment/kpis', { params: p }),
  getByCarrier: (p: DateParams) => apiClient.get('/api/fulfillment/by-carrier', { params: p }),
  getDeliveryTrend: (p: DateParams) => apiClient.get('/api/fulfillment/delivery-trend', { params: p }),
  getFulfillmentCycle: (p: DateParams) => apiClient.get('/api/fulfillment/fulfillment-cycle', { params: p }),
}
