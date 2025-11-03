import api from './client';

export const fetchGiftCodes = (allianceId) => {
  const params = {};
  if (allianceId) {
    params.alliance_id = allianceId;
  }
  return api.get('/gift-codes/', { params }).then((res) => res.data);
};
export const trackGiftCode = (payload) => api.post('/gift-codes/', payload).then((res) => res.data);
export const solveCaptcha = (file) => {
  const formData = new FormData();
  formData.append('file', file);
  return api.post('/gift-codes/solve', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }).then((res) => res.data);
};
export const updateGiftCode = (id, payload) => api.put(`/gift-codes/${id}`, payload).then((res) => res.data);
export const deleteGiftCode = (id) => api.delete(`/gift-codes/${id}`);
