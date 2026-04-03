import { useState, useEffect } from 'react'
import './App.css'
import GraphView from './GraphView'

function ProjectSelector({ selectedProject, onSelect }) {
  const [projects, setProjects] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
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

  if (loading) return <p className="status">Loading…</p>
  if (error) return <p className="status error">Error: {error}</p>
  if (projects.length === 0) return <p className="status">No projects found.</p>

  return (
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
  )
}

function App() {
  const [selectedProject, setSelectedProject] = useState(null)

  return (
    <div id="layout">
      <header id="header">
        <h1>Visual Orchestrator</h1>
        <ProjectSelector
          selectedProject={selectedProject}
          onSelect={setSelectedProject}
        />
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
