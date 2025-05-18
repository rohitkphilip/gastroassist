import { useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { submitQuery } from '../store/querySlice';
import { RootState } from '../store/store';
import QueryInput from '../components/QueryInput';
import ResponseDisplay from '../components/ResponseDisplay';
import SourcesList from '../components/SourcesList';
import LoadingIndicator from '../components/LoadingIndicator';
import Head from 'next/head';

export default function Home() {
  const dispatch = useDispatch();
  const { response, loading, error } = useSelector((state: RootState) => state.query);
  const [query, setQuery] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      dispatch(submitQuery(query) as any);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Head>
        <title>GastroAssist AI</title>
        <meta name="description" content="AI-powered gastroenterology assistant" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
          <h1 className="text-3xl font-bold text-gray-900">GastroAssist AI</h1>
        </div>
      </header>

      <main>
        <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
          <div className="px-4 py-6 sm:px-0">
            <div className="bg-white rounded-lg shadow p-6">
              <QueryInput 
                value={query} 
                onChange={(e) => setQuery(e.target.value)} 
                onSubmit={handleSubmit} 
                disabled={loading}
              />
            </div>

            {loading && <LoadingIndicator />}
            
            {error && (
              <div className="mt-6 bg-red-50 border-l-4 border-red-400 p-4">
                <div className="flex">
                  <div className="flex-shrink-0">
                    <svg className="h-5 w-5 text-red-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <div className="ml-3">
                    <p className="text-sm text-red-700">{error}</p>
                  </div>
                </div>
              </div>
            )}

            {response && (
              <div className="mt-6">
                <ResponseDisplay answer={response.answer} />
                <SourcesList sources={response.sources} />
              </div>
            )}
          </div>
        </div>
      </main>

      <footer className="bg-white border-t border-gray-200 py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-center space-x-4">
            <a href="https://github.com/your-username/gastroassist" target="_blank" rel="noopener noreferrer" className="text-gray-500 hover:text-gray-700">
              GitHub
            </a>
            <a href="https://www.linkedin.com/in/your-linkedin-profile" target="_blank" rel="noopener noreferrer" className="text-gray-500 hover:text-gray-700">
              LinkedIn
            </a>
            <a href="https://twitter.com/your_twitter_handle" target="_blank" rel="noopener noreferrer" className="text-gray-500 hover:text-gray-700">
              Twitter
            </a>
          </div>
        </div>
      </footer>
    </div>
  );
}
