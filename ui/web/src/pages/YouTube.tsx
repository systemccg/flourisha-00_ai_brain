/**
 * YouTube Processing Page
 */
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { youtubeApi, projectsApi } from '../lib/api';
import type { Project } from '../lib/api';

const YouTube: React.FC = () => {
  const [videoId, setVideoId] = useState('');
  const [videoUrl, setVideoUrl] = useState('');
  const [projectId, setProjectId] = useState('');
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    loadProjects();
  }, []);

  const loadProjects = async () => {
    try {
      const res = await projectsApi.list();
      setProjects(res.data);
    } catch (err) {
      console.error('Failed to load projects:', err);
    }
  };

  const extractVideoId = (url: string): string | null => {
    // Handle various YouTube URL formats
    const patterns = [
      /(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)/,
      /^([a-zA-Z0-9_-]{11})$/,
    ];

    for (const pattern of patterns) {
      const match = url.match(pattern);
      if (match) return match[1];
    }

    return null;
  };

  const handleUrlChange = (value: string) => {
    setVideoUrl(value);
    const id = extractVideoId(value);
    if (id) {
      setVideoId(id);
      setError('');
    }
  };

  const handleProcess = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    const id = videoId || extractVideoId(videoUrl);
    if (!id) {
      setError('Invalid YouTube URL or video ID');
      return;
    }

    setLoading(true);

    try {
      const res = await youtubeApi.processVideo(id, projectId || undefined);
      setSuccess('Video processed successfully!');
      setTimeout(() => {
        navigate(`/content/${res.data.id}`);
      }, 1500);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to process video');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h1>Process YouTube Video</h1>

      <div style={{ backgroundColor: 'white', padding: '30px', borderRadius: '8px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)', maxWidth: '600px' }}>
        {error && (
          <div style={{ color: 'red', marginBottom: '15px', padding: '10px', backgroundColor: '#ffe6e6', borderRadius: '4px' }}>
            {error}
          </div>
        )}

        {success && (
          <div style={{ color: 'green', marginBottom: '15px', padding: '10px', backgroundColor: '#d4edda', borderRadius: '4px' }}>
            {success}
          </div>
        )}

        <form onSubmit={handleProcess}>
          <div style={{ marginBottom: '20px' }}>
            <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold' }}>
              YouTube Video URL or ID *
            </label>
            <input
              type="text"
              value={videoUrl}
              onChange={(e) => handleUrlChange(e.target.value)}
              placeholder="https://www.youtube.com/watch?v=dQw4w9WgXcQ or dQw4w9WgXcQ"
              required
              style={{
                width: '100%',
                padding: '10px',
                borderRadius: '4px',
                border: '1px solid #ccc',
                fontSize: '14px',
              }}
            />
            {videoId && (
              <p style={{ margin: '5px 0 0 0', fontSize: '12px', color: '#7f8c8d' }}>
                Video ID: <code>{videoId}</code>
              </p>
            )}
          </div>

          <div style={{ marginBottom: '20px' }}>
            <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold' }}>
              Project (Optional)
            </label>
            <select
              value={projectId}
              onChange={(e) => setProjectId(e.target.value)}
              style={{
                width: '100%',
                padding: '10px',
                borderRadius: '4px',
                border: '1px solid #ccc',
                fontSize: '14px',
              }}
            >
              <option value="">No project (generic processing)</option>
              {projects.map((project) => (
                <option key={project.id} value={project.id}>
                  {project.name}
                </option>
              ))}
            </select>
            <p style={{ margin: '5px 0 0 0', fontSize: '12px', color: '#7f8c8d' }}>
              Selecting a project enables context-aware AI processing with tech stack translation.
            </p>
          </div>

          <button
            type="submit"
            disabled={loading}
            style={{
              width: '100%',
              padding: '12px',
              backgroundColor: loading ? '#95a5a6' : '#3498db',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: loading ? 'not-allowed' : 'pointer',
              fontSize: '16px',
              fontWeight: 'bold',
            }}
          >
            {loading ? 'Processing...' : 'Process Video'}
          </button>
        </form>

        <div style={{ marginTop: '30px', padding: '15px', backgroundColor: '#f8f9fa', borderRadius: '4px' }}>
          <h3 style={{ marginTop: 0, fontSize: '14px' }}>How it works:</h3>
          <ol style={{ margin: 0, paddingLeft: '20px', fontSize: '13px', color: '#34495e' }}>
            <li>Fetches video metadata from YouTube</li>
            <li>Retrieves the video transcript</li>
            <li>Processes with AI (Claude) for summary, insights, and action items</li>
            <li>Stores in database with tags and relevance score</li>
            <li>If project selected: AI translates tech concepts to your stack</li>
          </ol>
        </div>
      </div>
    </div>
  );
};

export default YouTube;
