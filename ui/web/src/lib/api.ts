/**
 * API Client
 *
 * Axios instance configured with Firebase authentication
 */
import axios from 'axios';
import { auth } from '../config/firebase';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8001';

// Create axios instance
const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
apiClient.interceptors.request.use(
  async (config) => {
    const user = auth.currentUser;
    if (user) {
      const token = await user.getIdToken();
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      // Server responded with error
      console.error('API Error:', error.response.data);
    } else if (error.request) {
      // Request made but no response
      console.error('Network Error:', error.request);
    } else {
      // Something else happened
      console.error('Error:', error.message);
    }
    return Promise.reject(error);
  }
);

export default apiClient;

// API Methods

export interface Project {
  id: string;
  tenant_id: string;
  name: string;
  description?: string;
  tech_stack: Record<string, any>;
  context_replacements: Record<string, string>;
  default_visibility: string;
  created_at: string;
  updated_at: string;
}

export interface ProcessedContent {
  id: string;
  tenant_id: string;
  tenant_user_id: string;
  created_by_user_id: string;
  title: string;
  content_type: string;
  source_url?: string;
  source_id?: string;
  summary?: string;
  key_insights?: string[];
  action_items?: string[];
  tags?: string[];
  relevance_score?: number;
  visibility: string;
  shared_with: string[];
  created_at: string;
  updated_at: string;
}

// Projects API
export const projectsApi = {
  list: () => apiClient.get<Project[]>('/api/v1/projects'),
  get: (id: string) => apiClient.get<Project>(`/api/v1/projects/${id}`),
  create: (data: Partial<Project>) => apiClient.post<Project>('/api/v1/projects', data),
  update: (id: string, data: Partial<Project>) => apiClient.put<Project>(`/api/v1/projects/${id}`, data),
  delete: (id: string) => apiClient.delete(`/api/v1/projects/${id}`),
};

// Content API
export const contentApi = {
  list: (params?: { project_id?: string; content_type?: string; limit?: number; offset?: number }) =>
    apiClient.get<ProcessedContent[]>('/api/v1/content', { params }),
  get: (id: string) => apiClient.get<ProcessedContent>(`/api/v1/content/${id}`),
  create: (data: Partial<ProcessedContent>) => apiClient.post<ProcessedContent>('/api/v1/content', data),
  updateSharing: (id: string, visibility: string, shared_with: string[]) =>
    apiClient.put<ProcessedContent>(`/api/v1/content/${id}/share`, null, {
      params: { visibility, shared_with: shared_with.join(',') },
    }),
  delete: (id: string) => apiClient.delete(`/api/v1/content/${id}`),
};

// YouTube API
export const youtubeApi = {
  subscribePlaylist: (data: { playlist_id: string; playlist_name?: string; project_id?: string; auto_process?: boolean }) =>
    apiClient.post('/api/v1/youtube/playlists/subscribe', data),
  subscribeChannel: (data: { channel_id: string; channel_name?: string; project_id?: string; auto_process?: boolean }) =>
    apiClient.post('/api/v1/youtube/channels/subscribe', data),
  listSubscriptions: (source_type?: string) =>
    apiClient.get('/api/v1/youtube/subscriptions', { params: { source_type } }),
  unsubscribe: (id: string) => apiClient.delete(`/api/v1/youtube/subscriptions/${id}`),
  processVideo: (video_id: string, project_id?: string) =>
    apiClient.post<ProcessedContent>(`/api/v1/youtube/process/${video_id}`, null, {
      params: { project_id },
    }),
};
