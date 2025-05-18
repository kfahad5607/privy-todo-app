export interface User {
  id: number;
  username: string;
  email: string;
  name: string;
}

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface RegisterCredentials {
  username: string;
  email: string;
  name: string;
  password: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
} 

export interface AccessTokenJWTPayload {
  sub: string;
  user: User;
}

export interface AuthState {
  access_token: string;
  user: User;
}