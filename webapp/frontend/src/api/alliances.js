import api from './client';

export const fetchAlliances = () => api.get('/alliances/').then((res) => res.data);
export const createAlliance = (payload) => api.post('/alliances/', payload).then((res) => res.data);
export const updateAlliance = (id, payload) => api.put(`/alliances/${id}`, payload).then((res) => res.data);
export const deleteAlliance = (id) => api.delete(`/alliances/${id}`);
