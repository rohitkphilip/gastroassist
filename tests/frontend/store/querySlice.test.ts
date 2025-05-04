import { configureStore } from '@reduxjs/toolkit';
import queryReducer, { submitQuery, clearResponse } from '../../../frontend/store/querySlice';
import { api } from '../../../frontend/services/api';

// Mock the API service
jest.mock('../../../frontend/services/api', () => ({
  api: {
    post: jest.fn()
  }
}));

describe('Query Slice', () => {
  let store;
  
  beforeEach(() => {
    store = configureStore({
      reducer: {
        query: queryReducer
      }
    });
    jest.clearAllMocks();
  });
  
  test('should handle initial state', () => {
    expect(store.getState().query).toEqual({
      response: null,
      loading: false,
      error: null
    });
  });
  
  test('should handle clearResponse', () => {
    // First set some data
    store.dispatch({
      type: 'query/submitQuery/fulfilled',
      payload: {
        answer: 'Test answer',
        sources: [],
        confidence_score: 0.9
      }
    });
    
    // Then clear it
    store.dispatch(clearResponse());
    
    expect(store.getState().query).toEqual({
      response: null,
      loading: false,
      error: null
    });
  });
  
  test('should handle submitQuery.pending', () => {
    store.dispatch({ type: 'query/submit/pending' });
    
    expect(store.getState().query).toEqual({
      response: null,
      loading: true,
      error: null
    });
  });
  
  test('should handle submitQuery.fulfilled', () => {
    const mockResponse = {
      answer: 'Test answer',
      sources: [{ title: 'Source 1', snippet: 'Info...', confidence: 0.8 }],
      confidence_score: 0.9
    };
    
    store.dispatch({
      type: 'query/submit/fulfilled',
      payload: mockResponse
    });
    
    expect(store.getState().query).toEqual({
      response: mockResponse,
      loading: false,
      error: null
    });
  });
  
  test('should handle submitQuery.rejected', () => {
    store.dispatch({
      type: 'query/submit/rejected',
      payload: 'Error message'
    });
    
    expect(store.getState().query).toEqual({
      response: null,
      loading: false,
      error: 'Error message'
    });
  });
  
  test('submitQuery thunk dispatches correct actions on success', async () => {
    const mockResponse = {
      answer: 'Test answer',
      sources: [{ title: 'Source 1', snippet: 'Info...', confidence: 0.8 }],
      confidence_score: 0.9
    };
    
    (api.post as jest.Mock).mockResolvedValue({ data: mockResponse });
    
    await store.dispatch(submitQuery('Test query'));
    
    expect(api.post).toHaveBeenCalledWith('/api/query', {
      text: 'Test query',
      user_id: 'current-user-id'
    });
    
    expect(store.getState().query.response).toEqual(mockResponse);
    expect(store.getState().query.loading).toBe(false);
    expect(store.getState().query.error).toBe(null);
  });
  
  test('submitQuery thunk dispatches correct actions on failure', async () => {
    (api.post as jest.Mock).mockRejectedValue(new Error('API error'));
    
    await store.dispatch(submitQuery('Test query'));
    
    expect(store.getState().query.response).toBe(null);
    expect(store.getState().query.loading).toBe(false);
    expect(store.getState().query.error).toBe('Failed to get response. Please try again.');
  });
});