import api from './client';

export const fetchMinisters = (allianceId) => {
  const params = {};
  if (allianceId) {
    params.alliance_id = allianceId;
  }
  return api.get('/ministers/', { params }).then((res) => res.data);
};
export const createMinister = (payload) => api.post('/ministers/', payload).then((res) => res.data);
export const updateMinister = (id, payload) => api.put(`/ministers/${id}`, payload).then((res) => res.data);
export const deleteMinister = (id) => api.delete(`/ministers/${id}`);
