import { useState, useEffect, useCallback } from 'react'
import './App.css'
import GraphView from './GraphView'

function getInitialTheme() {
  const stored = localStorage.getItem('theme')
  if (stored === 'dark' || stored === 'light') return stored
  return 'light'
}

function applyTheme(theme) {
  const root = document.documentElement
  root.setAttribute('data-theme', theme === 'dark' ? 'dark' : 'light')
}

function ThemeToggle({ theme, onToggle }) {
  const icon = theme === 'dark' ? '🌙' : '☀️'
  const title = theme === 'dark' ? 'Dark mode' : 'Light mode'

  return (
    <button className="theme-toggle" onClick={onToggle} title={title}>
      {icon}
    </button>
  )
}

function ProjectSelector({ selectedProject, onSelect }) {
  const [projects, setProjects] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [creating, setCreating] = useState(false)
  const [newName, setNewName] = useState('')
  const [createError, setCreateError] = useState(null)
  const [submitting, setSubmitting] = useState(false)

  const fetchProjects = useCallback(() => {
    fetch('/project/list')
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`)
        return res.json()
      })
      .then((data) => {
        setProjects(data)
        setLoading(false)
      })
      .catch((err) => {
        setError(err.message)
        setLoading(false)
      })
  }, [])

  useEffect(() => {
    fetchProjects()
  }, [fetchProjects])

  const handleCreate = () => {
    const name = newName.trim()
    if (!name) return
    setSubmitting(true)
    setCreateError(null)
    fetch('/project/create', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name }),
    })
      .then((res) => {
        if (!res.ok) return res.json().then((d) => { throw new Error(d.detail || `HTTP ${res.status}`) })
        return res.json()
      })
      .then((data) => {
        setNewName('')
        setCreating(false)
        setSubmitting(false)
        fetchProjects()
        onSelect(data.name)
      })
      .catch((err) => {
        setCreateError(err.message)
        setSubmitting(false)
      })
  }

  if (loading) return <p className="status">Loading…</p>
  if (error) return <p className="status error">Error: {error}</p>

  return (
    <div className="project-selector-group">
      <select
        className="project-select"
        value={selectedProject ?? ''}
        onChange={(e) => onSelect(e.target.value || null)}
      >
        <option value="">-- Select a run template --</option>
        {projects.map((name) => (
          <option key={name} value={name}>
            {name}
          </option>
        ))}
      </select>

      {!creating ? (
        <button
          className="panel-btn panel-btn-primary new-project-btn"
          onClick={() => { setCreating(true); setCreateError(null); setNewName(''); }}
        >
          + New
        </button>
      ) : (
        <div className="new-project-inline">
          <input
            type="text"
            className="edit-input new-project-input"
            placeholder="project-name"
            value={newName}
            onChange={(e) => setNewName(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter') handleCreate()
              if (e.key === 'Escape') { setCreating(false); setCreateError(null); }
            }}
            autoFocus
            disabled={submitting}
          />
          <button className="panel-btn panel-btn-primary" onClick={handleCreate} disabled={submitting || !newName.trim()}>
            {submitting ? '…' : 'Create'}
          </button>
          <button className="panel-btn" onClick={() => { setCreating(false); setCreateError(null); }} disabled={submitting}>
            ✕
          </button>
          {createError && <span className="toolbar-error">{createError}</span>}
        </div>
      )}
    </div>
  )
}

function App() {
  const [selectedProject, setSelectedProject] = useState(null)
  const [theme, setTheme] = useState(getInitialTheme)

  useEffect(() => {
    applyTheme(theme)
    localStorage.setItem('theme', theme)
  }, [theme])

  useEffect(() => {
    document.documentElement.classList.toggle('comic-sans', selectedProject === 'ComicSans')
  }, [selectedProject])

  const toggleTheme = useCallback(() => {
    setTheme((prev) => (prev === 'dark' ? 'light' : 'dark'))
  }, [])

  const logoSrc = theme === 'dark' ? '/cosmotech_dark_logo.png' : '/cosmotech_light_logo.png'

  return (
    <div id="layout">
      <header id="header">
        <img src={logoSrc} alt="Cosmo Tech" className="header-logo" />
        <h1>Visual Orchestrator</h1>
        <ProjectSelector
          selectedProject={selectedProject}
          onSelect={setSelectedProject}
        />
        <div className="header-spacer" />
        <ThemeToggle theme={theme} onToggle={toggleTheme} />
      </header>

      <main id="main">
        {selectedProject ? (
          <GraphView projectName={selectedProject} />
        ) : (
          <p className="status">Select a run template to view its graph.</p>
        )}
      </main>
    </div>
  )
}

export default App
