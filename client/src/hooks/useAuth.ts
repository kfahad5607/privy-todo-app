import { register, login, logout, refreshToken } from '@/services/authService';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { jwtDecode } from 'jwt-decode';
import type { AccessTokenJWTPayload, AuthState } from '../types/auth';

const AUTH_STATE_KEY = 'me';

export const useRegister = () => {
    return useMutation({
        mutationFn: register,
        onSuccess: (data) => {
            console.log("Register successful", data);
        },
    });
};

export const useLogin = () => {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: login,
        onSuccess: (data) => {
            const decoded = jwtDecode<AccessTokenJWTPayload>(data.access_token);
            console.log("Login successful", decoded, data);

            queryClient.setQueryData([AUTH_STATE_KEY], {
                access_token: data.access_token,
                user: decoded.user,
            });
        },
    });
};

export const useLogout = () => {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: logout,
        onSuccess: () => {
            queryClient.removeQueries({ queryKey: [AUTH_STATE_KEY] });
        },
    });
};

export const useRefreshToken = () => {
    const queryClient = useQueryClient();
    const controller = new AbortController();

    const mutation = useMutation({
        mutationFn: () => refreshToken({ signal: controller.signal }),
        onSuccess: (data) => {
            console.log("Refresh token successful", data);
            const decoded = jwtDecode<AccessTokenJWTPayload>(data.access_token);
            console.log("Login successful", decoded, data);

            queryClient.setQueryData([AUTH_STATE_KEY], {
                access_token: data.access_token,
                user: decoded.user,
            });
        },
    });

    return {
        ...mutation,
        cancel: () => {
            console.log("Refresh token cancelled");
            controller.abort();
        },
    };
};

export const useAuth = () => {
    const queryClient = useQueryClient();
    const authState = queryClient.getQueryData<AuthState>([AUTH_STATE_KEY]);

    return {
        authState,
        isAuthenticated: !!authState
    };
};
