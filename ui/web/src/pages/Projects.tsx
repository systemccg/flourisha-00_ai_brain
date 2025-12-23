/**
 * Projects List Page
 */
import React, { useEffect, useState } from 'react';
import { projectsApi } from '../lib/api';
import type { Project } from '../lib/api';

const Projects: React.FC = () => {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    tech_stack: '',
    context_replacements: '',
  });

  useEffect(() => {
    loadProjects();
  }, []);

  const loadProjects = async () => {
    try {
      setLoading(true);
      const res = await projectsApi.list();
      setProjects(res.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load projects');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const tech_stack = formData.tech_stack ? JSON.parse(formData.tech_stack) : {};
      const context_replacements = formData.context_replacements ? JSON.parse(formData.context_replacements) : {};

      await projectsApi.create({
        name: formData.name,
        description: formData.description,
        tech_stack,
        context_replacements,
        default_visibility: 'private',
      });

      setShowForm(false);
      setFormData({ name: '', description: '', tech_stack: '', context_replacements: '' });
      loadProjects();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to create project');
    }
  };

  if (loading) return <div>Loading...</div>;
  if (error) return <div style={{ color: 'red' }}>Error: {error}</div>;

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h1>Projects</h1>
        <button
          onClick={() => setShowForm(!showForm)}
          style={{
            padding: '10px 20px',
            backgroundColor: '#28a745',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
          }}
        >
          {showForm ? 'Cancel' : '+ New Project'}
        </button>
      </div>

      {showForm && (
        <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '8px', marginBottom: '20px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>
          <h2>Create Project</h2>
          <form onSubmit={handleSubmit}>
            <div style={{ marginBottom: '15px' }}>
              <label style={{ display: 'block', marginBottom: '5px' }}>Name *</label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                required
                style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ccc' }}
              />
            </div>
            <div style={{ marginBottom: '15px' }}>
              <label style={{ display: 'block', marginBottom: '5px' }}>Description</label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                rows={3}
                style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ccc' }}
              />
            </div>
            <div style={{ marginBottom: '15px' }}>
              <label style={{ display: 'block', marginBottom: '5px' }}>Tech Stack (JSON)</label>
              <textarea
                value={formData.tech_stack}
                onChange={(e) => setFormData({ ...formData, tech_stack: e.target.value })}
                rows={3}
                placeholder='{"backend": "FastAPI", "vector_db": "Supabase/PG Vector"}'
                style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ccc', fontFamily: 'monospace' }}
              />
            </div>
            <div style={{ marginBottom: '15px' }}>
              <label style={{ display: 'block', marginBottom: '5px' }}>Context Replacements (JSON)</label>
              <textarea
                value={formData.context_replacements}
                onChange={(e) => setFormData({ ...formData, context_replacements: e.target.value })}
                rows={2}
                placeholder='{"Qdrant": "Supabase/PG Vector"}'
                style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ccc', fontFamily: 'monospace' }}
              />
            </div>
            <button
              type="submit"
              style={{
                padding: '10px 20px',
                backgroundColor: '#007bff',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer',
              }}
            >
              Create Project
            </button>
          </form>
        </div>
      )}

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '20px' }}>
        {projects.map((project) => (
          <div key={project.id} style={{ backgroundColor: 'white', padding: '20px', borderRadius: '8px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>
            <h3 style={{ marginTop: 0 }}>{project.name}</h3>
            <p style={{ color: '#7f8c8d' }}>{project.description}</p>
            <div style={{ marginTop: '15px', fontSize: '12px', color: '#95a5a6' }}>
              <div>Created: {new Date(project.created_at).toLocaleDateString()}</div>
              {Object.keys(project.tech_stack).length > 0 && (
                <div style={{ marginTop: '10px' }}>
                  <strong>Tech Stack:</strong>
                  <ul style={{ margin: '5px 0', paddingLeft: '20px' }}>
                    {Object.entries(project.tech_stack).map(([key, value]) => (
                      <li key={key}>{key}: {String(value)}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      {projects.length === 0 && !showForm && (
        <div style={{ textAlign: 'center', padding: '40px', color: '#7f8c8d' }}>
          <p>No projects yet. Create your first project to get started!</p>
        </div>
      )}
    </div>
  );
};

export default Projects;
