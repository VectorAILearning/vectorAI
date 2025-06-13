export interface RegisterPayload {
  username: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}
export type LoginRequest = RegisterPayload;

export interface ErrorResponse {
  detail: string;
}

export interface MessageResponse {
  result: string;
}
