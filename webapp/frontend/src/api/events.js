import api from './client';

export const fetchEvents = (allianceId) => {
  const params = {};
  if (allianceId) {
    params.alliance_id = allianceId;
  }
  return api.get('/events/', { params }).then((res) => res.data);
};
export const createEvent = (payload) => api.post('/events/', payload).then((res) => res.data);
export const updateEvent = (id, payload) => api.put(`/events/${id}`, payload).then((res) => res.data);
export const deleteEvent = (id) => api.delete(`/events/${id}`);
export const updateAttendance = (eventId, payload) =>
  api.post(`/events/${eventId}/attendance`, payload).then((res) => res.data);
export const fetchAttendance = (eventId) =>
  api.get(`/events/${eventId}/attendance`).then((res) => res.data);
export const fetchAttendanceSummary = (allianceId) =>
  api.get(`/events/summary/${allianceId}`).then((res) => res.data);
