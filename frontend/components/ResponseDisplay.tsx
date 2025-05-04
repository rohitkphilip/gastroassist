import React from 'react';
import ReactMarkdown from 'react-markdown';

interface ResponseDisplayProps {
  answer: string;
}

const ResponseDisplay: React.FC<ResponseDisplayProps> = ({ answer }) => {
  return (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <h2 className="text-xl font-semibold mb-4">Answer</h2>
      <div className="prose max-w-none">
        <ReactMarkdown>{answer}</ReactMarkdown>
      </div>
    </div>
  );
};

export default ResponseDisplay;