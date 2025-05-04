import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import axios from 'axios';

interface Source {
  title: string;
  url?: string;
  snippet: string;
  confidence: number;
}

interface QueryResponse {
  answer: string;
  sources: Source[];
  confidence_score: number;
}

interface QueryState {
  response: QueryResponse | null;
  loading: boolean;
  error: string | null;
}

const initialState: QueryState = {
  response: null,
  loading: false,
  error: null,
};

export const submitQuery = createAsyncThunk(
  'query/submit',
  async (queryText: string, { rejectWithValue }) => {
    try {
      const response = await axios.post('/api/query', {
        text: queryText,
        user_id: 'guest',
      });
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error) && error.response) {
        return rejectWithValue(error.response.data.detail || 'An error occurred');
      }
      return rejectWithValue('An error occurred while processing your query');
    }
  }
);

const querySlice = createSlice({
  name: 'query',
  initialState,
  reducers: {
    clearResponse: (state) => {
      state.response = null;
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(submitQuery.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(submitQuery.fulfilled, (state, action: PayloadAction<QueryResponse>) => {
        state.loading = false;
        state.response = action.payload;
      })
      .addCase(submitQuery.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string || 'An error occurred';
      });
  },
});

export const { clearResponse } = querySlice.actions;
export default querySlice.reducer;
