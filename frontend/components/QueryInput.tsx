import React from 'react';

interface QueryInputProps {
  value: string;
  onChange: (e: React.ChangeEvent<HTMLTextAreaElement>) => void;
  onSubmit: (e: React.FormEvent) => void;
  disabled: boolean;
}

const QueryInput: React.FC<QueryInputProps> = ({ value, onChange, onSubmit, disabled }) => {
  return (
    <form onSubmit={onSubmit} className="w-full">
      <div className="mb-4">
        <label htmlFor="query" className="block text-sm font-medium text-gray-700 mb-2">
          Ask a gastroenterology question:
        </label>
        <textarea
          id="query"
          name="query"
          rows={3}
          className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
          placeholder="e.g., What are the latest treatment options for GERD?"
          value={value}
          onChange={onChange}
          disabled={disabled}
        />
      </div>
      <div className="flex justify-end">
        <button
          type="submit"
          disabled={disabled}
          className={`px-4 py-2 rounded-md text-white ${
            disabled 
              ? 'bg-gray-400 cursor-not-allowed' 
              : 'bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500'
          }`}
        >
          {disabled ? 'Processing...' : 'Submit'}
        </button>
      </div>
    </form>
  );
};

export default QueryInput;
