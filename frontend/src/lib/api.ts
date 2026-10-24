import axios from "axios";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

const api = axios.create({
  baseURL: API_BASE,
  headers: { "Content-Type": "application/json" },
});

// Auth token injection
api.interceptors.request.use((config) => {
  const token = typeof window !== "undefined" ? localStorage.getItem("eventra_token") : null;
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// Global error handling
api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401 && typeof window !== "undefined") {
      localStorage.removeItem("eventra_token");
      localStorage.removeItem("eventra_user");
      window.location.href = "/login";
    }
    return Promise.reject(err);
  }
);

export default api;

// ─── Auth ─────────────────────────────────────────────────────────────────────

export const authApi = {
  register: (data: { email: string; full_name: string; password: string }) =>
    api.post("/auth/register", data),
  login: (data: { email: string; password: string }) =>
    api.post("/auth/login", data),
  me: () => api.get("/auth/me"),
  updateMe: (data: object) => api.put("/auth/me", data),
};

// ─── Events ───────────────────────────────────────────────────────────────────

export const eventsApi = {
  list: () => api.get("/events"),
  get: (id: number) => api.get(`/events/${id}`),
  create: (data: object) => api.post("/events", data),
  update: (id: number, data: object) => api.put(`/events/${id}`, data),
  delete: (id: number) => api.delete(`/events/${id}`),
  generatePlan: (id: number) => api.post(`/events/${id}/generate-plan`),
  getBudget: (id: number) => api.get(`/events/${id}/budget`),
  createCategory: (eventId: number, data: object) =>
    api.post(`/events/${eventId}/budget/categories`, data),
  updateCategory: (eventId: number, catId: number, data: object) =>
    api.put(`/events/${eventId}/budget/categories/${catId}`, data),
  addExpense: (eventId: number, catId: number, data: object) =>
    api.post(`/events/${eventId}/budget/categories/${catId}/expenses`, data),
  updateExpense: (eventId: number, catId: number, expId: number, data: object) =>
    api.put(`/events/${eventId}/budget/categories/${catId}/expenses/${expId}`, data),
  getTasks: (id: number) => api.get(`/events/${id}/tasks`),
  createTask: (eventId: number, data: object) =>
    api.post(`/events/${eventId}/tasks`, data),
  updateTask: (eventId: number, taskId: number, data: object) =>
    api.put(`/events/${eventId}/tasks/${taskId}`, data),
  deleteTask: (eventId: number, taskId: number) =>
    api.delete(`/events/${eventId}/tasks/${taskId}`),
};

// ─── Guests ───────────────────────────────────────────────────────────────────

export const guestsApi = {
  list: (eventId: number) => api.get(`/events/${eventId}/guests`),
  add: (eventId: number, data: object) => api.post(`/events/${eventId}/guests`, data),
  update: (eventId: number, guestId: number, data: object) =>
    api.put(`/events/${eventId}/guests/${guestId}`, data),
  delete: (eventId: number, guestId: number) =>
    api.delete(`/events/${eventId}/guests/${guestId}`),
};

// ─── Vendors ──────────────────────────────────────────────────────────────────

export const vendorsApi = {
  list: () => api.get("/vendors"),
  create: (data: object) => api.post("/vendors", data),
  update: (id: number, data: object) => api.put(`/vendors/${id}`, data),
  delete: (id: number) => api.delete(`/vendors/${id}`),
  listForEvent: (eventId: number) => api.get(`/events/${eventId}/vendors`),
  addToEvent: (eventId: number, data: object) =>
    api.post(`/events/${eventId}/vendors`, data),
  updateEventVendor: (eventId: number, evId: number, data: object) =>
    api.put(`/events/${eventId}/vendors/${evId}`, data),
};

// ─── AI ───────────────────────────────────────────────────────────────────────

export const aiApi = {
  chat: (data: { message: string; conversation_id?: number }, eventId?: number) =>
    api.post(`/ai/chat${eventId ? `?event_id=${eventId}` : ""}`, data),
  conversations: () => api.get("/ai/conversations"),
  conversation: (id: number) => api.get(`/ai/conversations/${id}`),
  simulate: (eventId: number, data: { scenario_type: string; parameters: object }) =>
    api.post(`/ai/simulate?event_id=${eventId}`, data),
  themes: (eventId: number) => api.get(`/ai/themes/${eventId}`),
  dashboardStats: () => api.get("/ai/dashboard-stats"),
};
