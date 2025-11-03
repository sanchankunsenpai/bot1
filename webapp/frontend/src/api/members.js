import api from './client';

export const fetchMembers = (allianceId) => {
  const params = {};
  if (allianceId) {
    params.alliance_id = allianceId;
  }
  return api.get('/members/', { params }).then((res) => res.data);
};
export const createMember = (payload) => api.post('/members/', payload).then((res) => res.data);
export const updateMember = (id, payload) => api.put(`/members/${id}`, payload).then((res) => res.data);
export const deleteMember = (id) => api.delete(`/members/${id}`);
