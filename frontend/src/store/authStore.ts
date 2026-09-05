import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface User {
  id: number;
  username: string;
  email: string;
  full_name?: string;
  role: string;
}

interface AuthState {
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  login: (accessToken: string, refreshToken: string) => void;
  logout: () => void;
  setUser: (user: User) => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,
      
      login: (accessToken: string, refreshToken: string) => {
        set({ 
          accessToken, 
          refreshToken, 
          isAuthenticated: true 
        });
      },
      
      logout: () => {
        set({ 
          user: null, 
          accessToken: null, 
          refreshToken: null, 
          isAuthenticated: false 
        });
      },
      
      setUser: (user: User) => {
        set({ user });
      },
    }),
    {
      name: 'auth-storage',
    }
  )
);
