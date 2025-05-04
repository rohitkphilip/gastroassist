import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import QueryInput from '../../../frontend/components/QueryInput';

describe('QueryInput Component', () => {
  const mockOnChange = jest.fn();
  const mockOnSubmit = jest.fn();
  
  beforeEach(() => {
    jest.clearAllMocks();
  });
  
  test('renders correctly', () => {
    render(
      <QueryInput 
        value="" 
        onChange={mockOnChange} 
        onSubmit={mockOnSubmit} 
        disabled={false} 
      />
    );
    
    expect(screen.getByPlaceholderText('Enter your gastroenterology question...')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Submit Question' })).toBeInTheDocument();
  });
  
  test('calls onChange when input changes', () => {
    render(
      <QueryInput 
        value="" 
        onChange={mockOnChange} 
        onSubmit={mockOnSubmit} 
        disabled={false} 
      />
    );
    
    const textarea = screen.getByPlaceholderText('Enter your gastroenterology question...');
    fireEvent.change(textarea, { target: { value: 'New question' } });
    
    expect(mockOnChange).toHaveBeenCalledTimes(1);
  });
  
  test('calls onSubmit when form is submitted', () => {
    render(
      <QueryInput 
        value="Test question" 
        onChange={mockOnChange} 
        onSubmit={mockOnSubmit} 
        disabled={false} 
      />
    );
    
    const form = screen.getByRole('button', { name: 'Submit Question' }).closest('form');
    fireEvent.submit(form);
    
    expect(mockOnSubmit).toHaveBeenCalledTimes(1);
  });
  
  test('disables input and button when disabled prop is true', () => {
    render(
      <QueryInput 
        value="" 
        onChange={mockOnChange} 
        onSubmit={mockOnSubmit} 
        disabled={true} 
      />
    );
    
    const textarea = screen.getByPlaceholderText('Enter your gastroenterology question...');
    const button = screen.getByRole('button', { name: 'Processing...' });
    
    expect(textarea).toBeDisabled();
    expect(button).toBeDisabled();
    expect(button).toHaveTextContent('Processing...');
  });
});