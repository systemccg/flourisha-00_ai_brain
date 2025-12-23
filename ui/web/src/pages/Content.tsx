/**
 * Content List Page
 */
import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { contentApi } from '../lib/api';
import type { ProcessedContent } from '../lib/api';

const Content: React.FC = () => {
  const [content, setContent] = useState<ProcessedContent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadContent();
  }, []);

  const loadContent = async () => {
    try {
      setLoading(true);
      const res = await contentApi.list({ limit: 100 });
      setContent(res.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load content');
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div>Loading...</div>;
  if (error) return <div style={{ color: 'red' }}>Error: {error}</div>;

  return (
    <div>
      <h1>Processed Content</h1>

      <div style={{ backgroundColor: 'white', borderRadius: '8px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>
        {content.length === 0 ? (
          <div style={{ padding: '40px', textAlign: 'center', color: '#7f8c8d' }}>
            <p>No content yet. Process your first YouTube video!</p>
            <Link to="/youtube" style={{ color: '#3498db', textDecoration: 'none' }}>
              Go to YouTube →
            </Link>
          </div>
        ) : (
          <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
            {content.map((item, index) => (
              <li
                key={item.id}
                style={{
                  borderBottom: index < content.length - 1 ? '1px solid #ecf0f1' : 'none',
                  padding: '20px',
                }}
              >
                <Link to={`/content/${item.id}`} style={{ textDecoration: 'none', color: '#2c3e50' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                    <div style={{ flex: 1 }}>
                      <h3 style={{ margin: '0 0 10px 0' }}>{item.title}</h3>
                      {item.summary && (
                        <p style={{ margin: '0 0 10px 0', color: '#34495e' }}>
                          {item.summary.substring(0, 200)}...
                        </p>
                      )}
                      <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
                        <span style={{ fontSize: '12px', color: '#7f8c8d' }}>
                          {item.content_type}
                        </span>
                        <span style={{ fontSize: '12px', color: '#7f8c8d' }}>
                          {new Date(item.created_at).toLocaleDateString()}
                        </span>
                        {item.relevance_score !== undefined && (
                          <span
                            style={{
                              fontSize: '12px',
                              padding: '2px 8px',
                              borderRadius: '12px',
                              backgroundColor: item.relevance_score > 0.7 ? '#d4edda' : '#fff3cd',
                              color: item.relevance_score > 0.7 ? '#155724' : '#856404',
                            }}
                          >
                            Relevance: {(item.relevance_score * 100).toFixed(0)}%
                          </span>
                        )}
                      </div>
                      {item.tags && item.tags.length > 0 && (
                        <div style={{ marginTop: '10px', display: 'flex', gap: '5px', flexWrap: 'wrap' }}>
                          {item.tags.slice(0, 5).map((tag, i) => (
                            <span
                              key={i}
                              style={{
                                fontSize: '11px',
                                padding: '3px 8px',
                                borderRadius: '3px',
                                backgroundColor: '#e8f4f8',
                                color: '#2980b9',
                              }}
                            >
                              {tag}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                </Link>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
};

export default Content;
