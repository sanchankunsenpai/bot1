import api from './client';

export const fetchLogs = (limit = 200) =>
  api.get('/logs/', { params: { limit } }).then((res) => res.data);
