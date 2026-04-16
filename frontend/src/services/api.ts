import axios from 'axios';

export interface CurveSummary {
  id: string;
  name: string;
  description: string;
}

export interface CurveDetail {
  id: string;
  name: string;
  description: string;
  p: string;
  a: string;
  b: string;
  gx: string;
  gy: string;
  q: string;
}

const api = axios.create({
  baseURL: '/api/v1',
});

export const curvesApi = {
  listCurves: async (): Promise<CurveSummary[]> => {
    const response = await api.get<CurveSummary[]>('/curves');
    return response.data;
  },

  getCurve: async (curveId: string): Promise<CurveDetail> => {
    const response = await api.get<CurveDetail>(`/curves/${curveId}`);
    return response.data;
  },
};

export default api;