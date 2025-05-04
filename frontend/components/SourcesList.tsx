import React from 'react';

interface Source {
  title: string;
  url?: string;
  snippet: string;
  confidence: number;
}

interface SourcesListProps {
  sources: Source[];
}

const SourcesList: React.FC<SourcesListProps> = ({ sources }) => {
  if (!sources || sources.length === 0) {
    return null;
  }

  return (
    <div className="mt-6">
      <h2 className="text-xl font-semibold mb-4">Sources</h2>
      <div className="space-y-4">
        {sources.map((source, index) => (
          <div key={index} className="border border-gray-200 rounded-md p-4">
            <h3 className="font-medium text-lg">
              {source.url ? (
                <a 
                  href={source.url} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="text-primary-600 hover:underline"
                >
                  {source.title}
                </a>
              ) : (
                source.title
              )}
            </h3>
            <p className="text-gray-600 mt-1">{source.snippet}</p>
            <div className="mt-2 flex items-center">
              <span className="text-sm text-gray-500">
                Confidence: {Math.round(source.confidence * 100)}%
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default SourcesList;