export interface Station {
  id: number;
  api_id: string;
  name: string;
  address: string;
  postal_code: string;
  municipality: number;
  latitude: string;
  longitude: string;
  schedule: string;
  margin: string;
  sale_type: string;
  price?: string;
  price_recorded_at?: string;
}