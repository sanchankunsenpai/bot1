import api from './client';

export const login = (payload) => api.post('/auth/login', payload).then((res) => res.data);
export const logout = () => api.post('/auth/logout').then((res) => res.data);
export const fetchMe = () => api.get('/auth/me').then((res) => res.data);
