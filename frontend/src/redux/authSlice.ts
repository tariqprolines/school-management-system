import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import api, { type ApiResponse } from '../services/api';
import type { User } from '../types';

interface AuthState {
  user: User | null;
  token: string | null;
  loading: boolean;
  error: string | null;
}

const stored = localStorage.getItem('user');
const initialState: AuthState = stored
  ? { ...JSON.parse(stored), loading: false, error: null }
  : { user: null, token: null, loading: false, error: null };

export const login = createAsyncThunk(
  'auth/login',
  async (credentials: { email: string; password: string }, { rejectWithValue }) => {
    try {
      const response = await api.post<ApiResponse<{ access_token: string; user: User }>>(
        '/users/login',
        credentials
      );
      return response.data.data;
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string; message?: string } } };
      return rejectWithValue(error.response?.data?.detail || error.response?.data?.message || 'Login failed');
    }
  }
);

export const fetchMe = createAsyncThunk('auth/fetchMe', async (_, { rejectWithValue }) => {
  try {
    const response = await api.get<ApiResponse<User>>('/users/me');
    return response.data.data;
  } catch {
    return rejectWithValue('Failed to fetch user');
  }
});

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    logout: (state) => {
      state.user = null;
      state.token = null;
      localStorage.removeItem('user');
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(login.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(login.fulfilled, (state, action) => {
        state.loading = false;
        state.user = action.payload!.user;
        state.token = action.payload!.access_token;
        localStorage.setItem(
          'user',
          JSON.stringify({ user: action.payload!.user, token: action.payload!.access_token })
        );
      })
      .addCase(login.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      .addCase(fetchMe.fulfilled, (state, action) => {
        state.user = action.payload!;
      });
  },
});

export const { logout } = authSlice.actions;
export default authSlice.reducer;
