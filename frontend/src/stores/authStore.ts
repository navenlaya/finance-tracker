import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { authApi } from '../services/api';

interface User {
  id: string;
  email: string;
  firstName?: string;
  lastName?: string;
  hasPlaidConnection: boolean;
}

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  isInitialized: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (userData: RegisterData) => Promise<void>;
  logout: () => void;
  setLoading: (loading: boolean) => void;
  refreshToken: () => Promise<void>;
  initializeAuth: () => Promise<void>;
}

interface RegisterData {
  email: string;
  password: string;
  firstName?: string;
  lastName?: string;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,
      isInitialized: false,

      initializeAuth: async () => {
        const state = get();
        if (!state.token) {
          set({ isInitialized: true });
          return;
        }

        try {
          set({ isLoading: true });
          // Try to get current user to validate token
          const response = await authApi.getCurrentUser();
          
          // Map backend response to frontend format
          const mappedUser: User = {
            id: response.id,
            email: response.email,
            firstName: response.first_name,
            lastName: response.last_name,
            hasPlaidConnection: response.has_plaid_connection,
          };
          
          set({
            user: mappedUser,
            isAuthenticated: true,
            isLoading: false,
            isInitialized: true,
          });
        } catch (error) {
          // Token is invalid, clear auth state
          set({
            user: null,
            token: null,
            isAuthenticated: false,
            isLoading: false,
            isInitialized: true,
          });
        }
      },

      login: async (email: string, password: string) => {
        try {
          set({ isLoading: true });
          const response = await authApi.login({ email, password });
          
          // Map backend response to frontend format
          const user: User = {
            id: response.user.id,
            email: response.user.email,
            firstName: response.user.first_name,
            lastName: response.user.last_name,
            hasPlaidConnection: response.user.has_plaid_connection,
          };
          
          set({
            user: user,
            token: response.access_token,
            isAuthenticated: true,
            isLoading: false,
          });
        } catch (error) {
          set({ isLoading: false });
          throw error;
        }
      },

      register: async (userData: RegisterData) => {
        try {
          set({ isLoading: true });
          const response = await authApi.register(userData);
          
          // Map backend response to frontend format
          const user: User = {
            id: response.user.id,
            email: response.user.email,
            firstName: response.user.first_name,
            lastName: response.user.last_name,
            hasPlaidConnection: response.user.has_plaid_connection,
          };
          
          set({
            user: user,
            token: response.access_token,
            isAuthenticated: true,
            isLoading: false,
          });
        } catch (error) {
          set({ isLoading: false });
          throw error;
        }
      },

      logout: () => {
        set({
          user: null,
          token: null,
          isAuthenticated: false,
          isLoading: false,
        });
      },

      setLoading: (loading: boolean) => {
        set({ isLoading: loading });
      },

      refreshToken: async () => {
        try {
          const response = await authApi.refreshToken();
          
          // Map backend response to frontend format
          const user: User = {
            id: response.user.id,
            email: response.user.email,
            firstName: response.user.first_name,
            lastName: response.user.last_name,
            hasPlaidConnection: response.user.has_plaid_connection,
          };
          
          set({
            token: response.access_token,
            user: user,
          });
        } catch (error) {
          // If refresh fails, logout the user
          get().logout();
          throw error;
        }
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        token: state.token,
        user: state.user,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
); 