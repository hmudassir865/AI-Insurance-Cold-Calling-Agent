import { api } from './client';
import type { AuthResponse, User } from '../types';

export function login(email: string, password: string) {
  return api.post<AuthResponse>('/auth/login', { email, password });
}

export function signup(email: string, password: string, full_name: string) {
  return api.post<AuthResponse>('/auth/signup', { email, password, full_name });
}

export function refreshToken(refresh_token: string) {
  return api.post<AuthResponse>('/auth/refresh', { refresh_token });
}

export function getMe() {
  return api.get<User>('/auth/me');
}
