/**
 * Dashboard Home Page
 */
import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { contentApi, projectsApi } from '../lib/api';
import type { ProcessedContent, Project } from '../lib/api';

const Dashboard: React.FC = () => {
  const [recentContent, setRecentContent] = useState<ProcessedContent[]>([]);
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      const [contentRes, projectsRes] = await Promise.all([
        contentApi.list({ limit: 5 }),
        projectsApi.list(),
      ]);
      setRecentContent(contentRes.data);
      setProjects(projectsRes.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div>Loading...</div>;
  }

  if (error) {
    return <div style={{ color: 'red' }}>Error: {error}</div>;
  }

  return (
    <div>
      <h1>Dashboard</h1>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '20px', marginBottom: '30px' }}>
        {/* Stats Cards */}
        <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '8px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>
          <h3 style={{ margin: '0 0 10px 0', color: '#7f8c8d' }}>Projects</h3>
          <p style={{ fontSize: '32px', fontWeight: 'bold', margin: 0 }}>{projects.length}</p>
        </div>

        <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '8px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>
          <h3 style={{ margin: '0 0 10px 0', color: '#7f8c8d' }}>Content Items</h3>
          <p style={{ fontSize: '32px', fontWeight: 'bold', margin: 0 }}>{recentContent.length}</p>
        </div>
      </div>

      {/* Recent Content */}
      <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '8px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)', marginBottom: '20px' }}>
        <h2 style={{ marginTop: 0 }}>Recent Content</h2>
        {recentContent.length === 0 ? (
          <p style={{ color: '#7f8c8d' }}>No content yet. Process your first YouTube video!</p>
        ) : (
          <ul style={{ listStyle: 'none', padding: 0 }}>
            {recentContent.map((content) => (
              <li key={content.id} style={{ borderBottom: '1px solid #ecf0f1', padding: '15px 0' }}>
                <Link to={`/content/${content.id}`} style={{ textDecoration: 'none', color: '#2c3e50' }}>
                  <h3 style={{ margin: '0 0 5px 0' }}>{content.title}</h3>
                  <p style={{ margin: '0', color: '#7f8c8d', fontSize: '14px' }}>
                    {content.content_type} • {new Date(content.created_at).toLocaleDateString()}
                  </p>
                  {content.summary && (
                    <p style={{ margin: '10px 0 0 0', color: '#34495e' }}>
                      {content.summary.substring(0, 150)}...
                    </p>
                  )}
                </Link>
              </li>
            ))}
          </ul>
        )}
        <Link to="/content" style={{ color: '#3498db', textDecoration: 'none' }}>
          View all content →
        </Link>
      </div>

      {/* Projects */}
      <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '8px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>
        <h2 style={{ marginTop: 0 }}>Projects</h2>
        {projects.length === 0 ? (
          <p style={{ color: '#7f8c8d' }}>No projects yet. Create your first project!</p>
        ) : (
          <ul style={{ listStyle: 'none', padding: 0 }}>
            {projects.map((project) => (
              <li key={project.id} style={{ borderBottom: '1px solid #ecf0f1', padding: '15px 0' }}>
                <Link to={`/projects/${project.id}`} style={{ textDecoration: 'none', color: '#2c3e50' }}>
                  <h3 style={{ margin: '0 0 5px 0' }}>{project.name}</h3>
                  <p style={{ margin: '0', color: '#7f8c8d' }}>{project.description}</p>
                </Link>
              </li>
            ))}
          </ul>
        )}
        <Link to="/projects" style={{ color: '#3498db', textDecoration: 'none' }}>
          View all projects →
        </Link>
      </div>
    </div>
  );
};

export default Dashboard;
