'use client'

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  return (
    <html>
      <body style={{
        backgroundColor: '#111827',
        color: '#fff',
        fontFamily: 'system-ui, sans-serif',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '100vh',
        margin: 0,
      }}>
        <div style={{ textAlign: 'center', padding: '2rem' }}>
          <h1 style={{ fontSize: '2rem', marginBottom: '1rem', color: '#f87171' }}>
            Something went wrong
          </h1>
          <p style={{ color: '#9ca3af', marginBottom: '1.5rem' }}>
            A critical error occurred. Please refresh the page.
          </p>
          {error.message && (
            <div style={{
              padding: '1rem',
              backgroundColor: '#1f2937',
              borderRadius: '0.5rem',
              marginBottom: '1.5rem',
              fontFamily: 'monospace',
              fontSize: '0.875rem',
              color: '#6b7280',
            }}>
              {error.message}
            </div>
          )}
          <button
            onClick={reset}
            style={{
              backgroundColor: '#8b5cf6',
              color: 'white',
              padding: '0.75rem 1.5rem',
              borderRadius: '0.5rem',
              border: 'none',
              cursor: 'pointer',
              fontSize: '1rem',
            }}
          >
            Try Again
          </button>
        </div>
      </body>
    </html>
  )
}
