import React, { useState } from 'react';
import { mcpApi } from '../utils/api';

const SemanticSearch = ({ onSearchResults }) => {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState([]);
  const [error, setError] = useState('');

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    try {
      setLoading(true);
      setError('');
      
      const response = await mcpApi.executeTool('semantic_search', { 
        query: query,
        k: 5
      });
      
      const searchResults = response.data?.results || response.data;
      setResults(searchResults);
      
      if (onSearchResults) {
        onSearchResults(searchResults);
      }
    } catch (err) {
      console.error('Semantic search error:', err);
      setError('Failed to perform semantic search. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="semantic-search-component">
      <form onSubmit={handleSearch} className="mb-4">
        <div className="flex">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Ask anything about your calendar, location, or activities..."
            className="flex-1 px-4 py-2 border border-gray-300 rounded-l-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
          <button
            type="submit"
            disabled={loading}
            className="px-6 py-2 bg-blue-500 text-white rounded-r-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {loading ? 'Searching...' : 'Search'}
          </button>
        </div>
      </form>

      {error && (
        <div className="mb-4 p-3 bg-red-100 text-red-700 rounded-lg">
          {error}
        </div>
      )}

      {results.length > 0 && (
        <div className="search-results bg-white rounded-lg shadow-md border border-gray-200">
          <div className="p-4 border-b border-gray-200">
            <h3 className="text-lg font-semibold text-gray-800">Search Results</h3>
            <p className="text-sm text-gray-600">Found {results.length} relevant items</p>
          </div>
          
          <div className="divide-y divide-gray-200">
            {results.map((result, index) => (
              <div key={index} className="p-4 hover:bg-gray-50 transition-colors">
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <h4 className="font-medium text-gray-900">{result.metadata?.title || result.document_id}</h4>
                    <p className="text-sm text-gray-600 mt-1">{result.metadata?.summary || result.metadata?.description}</p>
                    
                    {result.metadata?.start_time && (
                      <div className="mt-2 text-xs text-gray-500">
                        ⏰ {new Date(result.metadata.start_time).toLocaleString()}
                      </div>
                    )}
                    
                    {result.metadata?.location && (
                      <div className="mt-1 text-xs text-gray-500">
                        📍 {result.metadata.location}
                      </div>
                    )}
                    
                    <div className="mt-2 text-xs text-blue-600">
                      Relevance: {(result.similarity_score * 100).toFixed(1)}%
                    </div>
                  </div>
                </div>
                
                {result.relevance_explanation && (
                  <div className="mt-2 pt-2 border-t border-gray-100">
                    <p className="text-xs text-gray-600 italic">
                      {result.relevance_explanation}
                    </p>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default SemanticSearch;