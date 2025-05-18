import { api, setAccessToken } from '../../../services/api';
import type { AuthResponse, LoginCredentials, RegisterCredentials, User } from '../../../types/auth';


export const login = async (credentials: LoginCredentials): Promise<AuthResponse> => {
  const formData = new FormData();
  formData.append('username', credentials.username);
  formData.append('password', credentials.password);
  
  const response = await api.post<AuthResponse>(`/auth/login`, formData, {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    withCredentials: true,
  });
  
  setAccessToken(response.data.access_token);
  
  return response.data;
};

export const register = async (credentials: RegisterCredentials): Promise<User> => {
  const response = await api.post<User>(`/auth/register`, credentials);
  return response.data;
};

export const logout = async (): Promise<void> => {
  await api.post(`/auth/logout`, {}, { withCredentials: true });
}; 

export const refreshToken = async ({ signal }: { signal?: AbortSignal }): Promise<AuthResponse> => {
  const response = await api.post<AuthResponse>(`/auth/refresh`, {}, { withCredentials: true, signal });

  return response.data;
};