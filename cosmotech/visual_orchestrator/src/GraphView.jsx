import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import {
  ReactFlow,
  ReactFlowProvider,
  addEdge,
  Background,
  Controls,
  Handle,
  MiniMap,
  Position,
  useNodesState,
  useEdgesState,
  useReactFlow,
} from '@xyflow/react';
import Dagre from '@dagrejs/dagre';
import '@xyflow/react/dist/style.css';
import MEME_GIFS from './memeList.json';
const MEME_SET = new Set(MEME_GIFS);

function MemeNode({ data }) {
  const gifName = MEME_GIFS.find((g) => g === data.label);
  return (
    <div className="meme-node">
      <Handle type="target" position={Position.Top} />
      {gifName && (
        <img
          src={`/memes/${gifName}.gif`}
          alt={gifName}
          className="meme-node-bg"
        />
      )}
      <Handle type="source" position={Position.Bottom} />
    </div>
  );
}

const KONAMI_CODE = [
  'ArrowUp','ArrowUp','ArrowDown','ArrowDown',
  'ArrowLeft','ArrowRight','ArrowLeft','ArrowRight',
  'b','a',
];

const EGG_EMOJIS = ['🥚','🐣','🐥','🪺','🐔','🐤','🍳'];

function useKonamiCode() {
  const [activated, setActivated] = useState(false);
  const buffer = useRef([]);

  useEffect(() => {
    const handler = (e) => {
      buffer.current = [...buffer.current, e.key].slice(-KONAMI_CODE.length);
      if (buffer.current.length === KONAMI_CODE.length &&
          buffer.current.every((k, i) => k === KONAMI_CODE[i])) {
        setActivated(true);
        buffer.current = [];
        // Auto-hide after 10 seconds
        setTimeout(() => setActivated(false), 10000);
      }
    };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, []);

  return activated;
}

function FallingEggs() {
  const eggs = useRef(
    Array.from({ length: 30 }, (_, i) => ({
      id: i,
      emoji: EGG_EMOJIS[Math.floor(Math.random() * EGG_EMOJIS.length)],
      left: Math.random() * 100,
      delay: Math.random() * 3,
      duration: 3 + Math.random() * 4,
      size: 16 + Math.random() * 24,
      rotation: Math.random() * 360,
    }))
  ).current;

  return (
    <div className="falling-eggs-container">
      {eggs.map((egg) => (
        <span
          key={egg.id}
          className="falling-egg"
          style={{
            left: `${egg.left}%`,
            animationDelay: `${egg.delay}s`,
            animationDuration: `${egg.duration}s`,
            fontSize: `${egg.size}px`,
            '--egg-rotation': `${egg.rotation}deg`,
          }}
        >
          {egg.emoji}
        </span>
      ))}
    </div>
  );
}

const NODE_WIDTH = 172;
const NODE_HEIGHT = 36;

function getLayoutedElements(nodes, edges) {
  const g = new Dagre.graphlib.Graph().setDefaultEdgeLabel(() => ({}));
  g.setGraph({ rankdir: 'TB', nodesep: 50, ranksep: 80 });

  nodes.forEach((node) => {
    g.setNode(node.id, { width: NODE_WIDTH, height: NODE_HEIGHT });
  });

  edges.forEach((edge) => {
    g.setEdge(edge.source, edge.target);
  });

  Dagre.layout(g);

  const layoutedNodes = nodes.map((node) => {
    const pos = g.node(node.id);
    return {
      ...node,
      position: {
        x: pos.x - NODE_WIDTH / 2,
        y: pos.y - NODE_HEIGHT / 2,
      },
    };
  });

  return { nodes: layoutedNodes, edges };
}

function stepsToNodes(steps) {
  return steps.map((stepId) => ({
    id: stepId,
    type: MEME_SET.has(stepId) ? 'meme' : undefined,
    data: { label: stepId },
    position: { x: 0, y: 0 },
  }));
}

function linksToEdges(links) {
  return links.map(([source, target], index) => ({
    id: `e${index}-${source}-${target}`,
    source,
    target,
    animated: true,
  }));
}

function EmptyValue() {
  return <span className="empty-value">—</span>;
}

function TemplatesPanel({ onClose, projectName, onStepCreated, onSelectStep }) {
  const [templates, setTemplates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedId, setSelectedId] = useState(null);
  const [detail, setDetail] = useState(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [creatingFrom, setCreatingFrom] = useState(null);
  const [newStepName, setNewStepName] = useState('');
  const [createError, setCreateError] = useState(null);
  const [creating, setCreating] = useState(false);

  const handleCreateFromTemplate = (templateId) => {
    if (!newStepName.trim()) return;
    setCreating(true);
    setCreateError(null);
    fetch(`/project/${projectName}/step`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ id: newStepName.trim(), commandId: templateId }),
    })
      .then((res) => {
        if (!res.ok) return res.json().then((d) => { throw new Error(d.detail || `HTTP ${res.status}`); });
        return res.json();
      })
      .then(() => {
        const id = newStepName.trim();
        setNewStepName('');
        setCreatingFrom(null);
        setCreating(false);
        if (onStepCreated) onStepCreated();
        if (onSelectStep) onSelectStep(id);
      })
      .catch((err) => {
        setCreateError(err.message);
        setCreating(false);
      });
  };

  useEffect(() => {
    fetch('/template/list')
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
      })
      .then((data) => { setTemplates(data); setLoading(false); })
      .catch((err) => { setError(err.message); setLoading(false); });
  }, []);

  useEffect(() => {
    if (!selectedId) { setDetail(null); return; }
    setDetailLoading(true);
    fetch(`/template/${selectedId}`)
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
      })
      .then((data) => { setDetail(data); setDetailLoading(false); })
      .catch((err) => { setDetail(null); setDetailLoading(false); setError(err.message); });
  }, [selectedId]);

  const renderTemplateList = () => (
    <>
      {loading && <p className="status">Loading…</p>}
      {error && <p className="status error">{error}</p>}
      {!loading && templates.length === 0 && <p className="status">No templates available.</p>}
      {!loading && templates.length > 0 && (
        <div className="template-list">
          {templates.map((id) => (
            <button
              key={id}
              className="template-list-item"
              draggable
              onDragStart={(e) => {
                e.dataTransfer.setData('application/template-id', id);
                e.dataTransfer.effectAllowed = 'copy';
              }}
              onClick={() => setSelectedId(id)}
            >
              <span className="mono">{id}</span>
              <span className="drag-hint">⠿</span>
            </button>
          ))}
        </div>
      )}
    </>
  );

  const renderTemplateDetail = () => (
    <>
      {detailLoading && <p className="status">Loading template…</p>}
      {detail && !detailLoading && (
        <div className="template-detail">
          {projectName && (
            <div className="template-create-section">
              {creatingFrom !== selectedId ? (
                <button
                  className="panel-btn panel-btn-primary"
                  style={{ width: '100%' }}
                  onClick={() => { setCreatingFrom(selectedId); setNewStepName(''); setCreateError(null); }}
                >
                  + Create Step from this Template
                </button>
              ) : (
                <div className="add-step-inline" style={{ flexWrap: 'wrap' }}>
                  <input
                    type="text"
                    className="edit-input"
                    placeholder="Step name…"
                    value={newStepName}
                    onChange={(e) => setNewStepName(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter') handleCreateFromTemplate(selectedId);
                      if (e.key === 'Escape') { setCreatingFrom(null); setCreateError(null); }
                    }}
                    autoFocus
                    disabled={creating}
                  />
                  <button className="panel-btn panel-btn-primary" onClick={() => handleCreateFromTemplate(selectedId)} disabled={creating}>
                    {creating ? 'Creating…' : 'Create'}
                  </button>
                  <button className="panel-btn" onClick={() => { setCreatingFrom(null); setCreateError(null); }} disabled={creating}>
                    Cancel
                  </button>
                  {createError && <span className="toolbar-error" style={{ width: '100%' }}>{createError}</span>}
                </div>
              )}
            </div>
          )}
          <div className="step-sections">
              <section className="panel-section">
                <h4 className="panel-section-title">General</h4>
                <dl className="panel-fields">
                  <div className="panel-field">
                    <dt>ID</dt>
                    <dd className="mono">{detail.id}</dd>
                  </div>
                  {detail.description && (
                    <div className="panel-field">
                      <dt>Description</dt>
                      <dd>{detail.description}</dd>
                    </div>
                  )}
                </dl>
              </section>

              <section className="panel-section">
                <h4 className="panel-section-title">Command</h4>
                <dl className="panel-fields">
                  {detail.command && (
                    <div className="panel-field">
                      <dt>Command</dt>
                      <dd className="mono">{detail.command}</dd>
                    </div>
                  )}
                  {detail.arguments && detail.arguments.length > 0 && (
                    <div className="panel-field">
                      <dt>Arguments</dt>
                      <dd className="mono">{detail.arguments.join(' ')}</dd>
                    </div>
                  )}
                  {detail.useSystemEnvironment && (
                    <div className="panel-field">
                      <dt>Use System Env</dt>
                      <dd>Yes</dd>
                    </div>
                  )}
                </dl>
              </section>

              {detail.environment && Object.keys(detail.environment).length > 0 && (
                <section className="panel-section">
                  <h4 className="panel-section-title">Environment Variables</h4>
                  <table className="panel-table">
                    <thead>
                      <tr>
                        <th>Variable</th>
                        <th>Value</th>
                        <th>Default</th>
                      </tr>
                    </thead>
                    <tbody>
                      {Object.entries(detail.environment).map(([name, desc]) => (
                        <tr key={name}>
                          <td className="mono">{name}</td>
                          <td>{desc.value || <EmptyValue />}</td>
                          <td>{desc.defaultValue || <EmptyValue />}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </section>
              )}
          </div>
        </div>
      )}
    </>
  );

  return (
    <div className="templates-panel">
      <div className="side-panel-header">
        {selectedId ? (
          <>
            <button className="panel-btn" onClick={() => { setSelectedId(null); setCreatingFrom(null); }}>← Back</button>
            <h3 className="mono">{selectedId}</h3>
          </>
        ) : (
          <h3>Templates</h3>
        )}
      </div>
      <div className="side-panel-body">
        {selectedId ? renderTemplateDetail() : renderTemplateList()}
      </div>
    </div>
  );
}

export default function GraphView({ projectName }) {
  return (
    <ReactFlowProvider>
      <GraphViewInner projectName={projectName} />
    </ReactFlowProvider>
  );
}

function getDescendants(stepId, links) {
  const children = new Map();
  for (const [src, tgt] of links) {
    if (!children.has(src)) children.set(src, []);
    children.get(src).push(tgt);
  }
  const visited = new Set();
  const queue = [stepId];
  while (queue.length > 0) {
    const current = queue.shift();
    if (visited.has(current)) continue;
    visited.add(current);
    for (const child of children.get(current) || []) {
      queue.push(child);
    }
  }
  visited.delete(stepId);
  return visited;
}

function getAncestors(stepId, links) {
  const parents = new Map();
  for (const [src, tgt] of links) {
    if (!parents.has(tgt)) parents.set(tgt, []);
    parents.get(tgt).push(src);
  }
  const visited = new Set();
  const queue = [stepId];
  while (queue.length > 0) {
    const current = queue.shift();
    if (visited.has(current)) continue;
    visited.add(current);
    for (const parent of parents.get(current) || []) {
      queue.push(parent);
    }
  }
  visited.delete(stepId);
  return visited;
}

function StepDetailPanel({ projectName, stepId, onClose, onStepUpdated, onStepIdChanged, allStepIds, allLinks, allStepOutputs }) {
  const [stepData, setStepData] = useState(null);
  const [editData, setEditData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [editing, setEditing] = useState(false);
  const [saving, setSaving] = useState(false);
  const [saveError, setSaveError] = useState(null);
  const [deleting, setDeleting] = useState(false);
  const [templateData, setTemplateData] = useState(null);

  useEffect(() => {
    setLoading(true);
    setError(null);
    setEditing(false);
    setTemplateData(null);

    fetch(`/project/${projectName}/step/${stepId}`)
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
      })
      .then((data) => {
        setStepData(data);
        setLoading(false);
        // Fetch template if step has a commandId
        if (data.commandId) {
          fetch(`/template/${data.commandId}`)
            .then((res) => {
              if (!res.ok) return null;
              return res.json();
            })
            .then((tpl) => setTemplateData(tpl))
            .catch(() => setTemplateData(null));
        }
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, [projectName, stepId]);

  const startEditing = () => {
    const useCommandId = !stepData.command && !!stepData.commandId;
    setEditData({
      id: stepData.id || '',
      description: stepData.description || '',
      commandMode: useCommandId ? 'commandId' : 'command',
      command: stepData.command || '',
      commandId: stepData.commandId || '',
      arguments: [...(stepData.arguments || [])],
      useSystemEnvironment: stepData.useSystemEnvironment ?? false,
      precedents: [...(stepData.precedents || [])],
      environment: stepData.environment
        ? Object.fromEntries(
            Object.entries(stepData.environment).map(([k, v]) => [
              k,
              { ...v },
            ]),
          )
        : {},
      outputs: stepData.outputs
        ? Object.fromEntries(
            Object.entries(stepData.outputs).map(([k, v]) => [k, { ...v }]),
          )
        : {},
      inputs: stepData.inputs
        ? Object.fromEntries(
            Object.entries(stepData.inputs).map(([k, v]) => [k, { ...v }]),
          )
        : {},
    });
    setSaveError(null);
    setEditing(true);
  };

  const cancelEditing = () => {
    setEditing(false);
    setEditData(null);
    setSaveError(null);
  };

  const updateField = (field, value) => {
    setEditData((prev) => ({ ...prev, [field]: value }));
  };

  const updateArgument = (index, value) => {
    setEditData((prev) => {
      const args = [...prev.arguments];
      args[index] = value;
      return { ...prev, arguments: args };
    });
  };

  const addArgument = () => {
    setEditData((prev) => ({ ...prev, arguments: [...prev.arguments, ''] }));
  };

  const removeArgument = (index) => {
    setEditData((prev) => ({
      ...prev,
      arguments: prev.arguments.filter((_, i) => i !== index),
    }));
  };

  const handleSave = () => {
    setSaving(true);
    setSaveError(null);

    const payload = {
      id: editData.id,
      description: editData.description || undefined,
    };

    if (editData.commandMode === 'command') {
      payload.command = editData.command || undefined;
    } else {
      payload.commandId = editData.commandId || undefined;
    }

    const filteredArgs = editData.arguments.filter((a) => a.trim() !== '');
    if (filteredArgs.length > 0) {
      payload.arguments = filteredArgs;
    }

    if (editData.useSystemEnvironment) {
      payload.useSystemEnvironment = true;
    }

    if (editData.precedents.length > 0) {
      payload.precedents = editData.precedents;
    }

    if (Object.keys(editData.environment).length > 0) {
      payload.environment = editData.environment;
    }

    if (Object.keys(editData.outputs).length > 0) {
      payload.outputs = editData.outputs;
    }

    if (Object.keys(editData.inputs).length > 0) {
      payload.inputs = editData.inputs;
    }

    // Remove undefined keys
    Object.keys(payload).forEach((k) => {
      if (payload[k] === undefined) delete payload[k];
    });

    fetch(`/project/${projectName}/step/${stepId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
      })
      .then((data) => {
        setStepData(data);
        setEditing(false);
        setEditData(null);
        setSaving(false);
        if (data.id !== stepId && onStepIdChanged) {
          onStepIdChanged(data.id);
        }
        if (onStepUpdated) onStepUpdated();
      })
      .catch((err) => {
        setSaveError(err.message);
        setSaving(false);
      });
  };

  const [confirmDelete, setConfirmDelete] = useState(false);

  const handleDelete = () => {
    setDeleting(true);

    fetch(`/project/${projectName}/step/${stepId}`, { method: 'DELETE' })
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        onClose();
        if (onStepUpdated) onStepUpdated();
      })
      .catch((err) => {
        setSaveError(`Delete failed: ${err.message}`);
        setDeleting(false);
        setConfirmDelete(false);
      });
  };

  const renderViewEnvironment = (env) => {
    if (!env || Object.keys(env).length === 0) return <EmptyValue />;
    return (
      <table className="panel-table">
        <thead>
          <tr>
            <th>Variable</th>
            <th>Value</th>
            <th>Default</th>
            <th>Optional</th>
          </tr>
        </thead>
        <tbody>
          {Object.entries(env).map(([name, desc]) => (
            <tr key={name}>
              <td className="mono">{name}</td>
              <td>{desc.value || <EmptyValue />}</td>
              <td>{desc.defaultValue || <EmptyValue />}</td>
              <td>{desc.optional ? 'Yes' : 'No'}</td>
            </tr>
          ))}
        </tbody>
      </table>
    );
  };

  const renderViewOutputs = (outputs) => {
    if (!outputs || Object.keys(outputs).length === 0) return <EmptyValue />;
    return (
      <table className="panel-table">
        <thead>
          <tr>
            <th>Name</th>
            <th>Description</th>
            <th>Default</th>
            <th>Optional</th>
            <th>Hidden</th>
          </tr>
        </thead>
        <tbody>
          {Object.entries(outputs).map(([name, desc]) => (
            <tr key={name}>
              <td className="mono">{name}</td>
              <td>{desc.description || <EmptyValue />}</td>
              <td>{desc.defaultValue || <EmptyValue />}</td>
              <td>{desc.optional ? 'Yes' : 'No'}</td>
              <td>{desc.hidden ? 'Yes' : 'No'}</td>
            </tr>
          ))}
        </tbody>
      </table>
    );
  };

  const renderViewInputs = (inputs) => {
    if (!inputs || Object.keys(inputs).length === 0) return <EmptyValue />;
    return (
      <table className="panel-table">
        <thead>
          <tr>
            <th>Name</th>
            <th>From Step</th>
            <th>Output</th>
            <th>Env Var</th>
            <th>Default</th>
            <th>Optional</th>
          </tr>
        </thead>
        <tbody>
          {Object.entries(inputs).map(([name, desc]) => (
            <tr key={name}>
              <td className="mono">{name}</td>
              <td className="mono">{desc.stepId}</td>
              <td className="mono">{desc.output}</td>
              <td className="mono">{desc.as}</td>
              <td>{desc.defaultValue || <EmptyValue />}</td>
              <td>{desc.optional ? 'Yes' : 'No'}</td>
            </tr>
          ))}
        </tbody>
      </table>
    );
  };

  // Merge template + step data for the unified view
  const merged = (() => {
    if (!stepData) return null;
    const tpl = templateData || {};
    const step = stepData;
    const command = step.command || tpl.command || null;
    const description = step.description || tpl.description || null;
    const useSystemEnvironment = step.useSystemEnvironment ?? tpl.useSystemEnvironment ?? false;
    const tplArgs = tpl.arguments || [];
    const stepArgs = step.arguments || [];
    const mergedArgs = [...tplArgs, ...stepArgs];
    const tplEnv = tpl.environment || {};
    const stepEnv = step.environment || {};
    const mergedEnv = { ...tplEnv };
    for (const [k, v] of Object.entries(stepEnv)) {
      mergedEnv[k] = { ...(mergedEnv[k] || {}), ...v };
    }
    const envSources = {};
    for (const k of Object.keys(mergedEnv)) {
      const inTpl = k in tplEnv;
      const inStep = k in stepEnv;
      if (inStep && inTpl) envSources[k] = 'overridden';
      else if (inStep) envSources[k] = 'step';
      else envSources[k] = 'template';
    }
    return { command, description, useSystemEnvironment, mergedArgs, tplArgs, stepArgs, mergedEnv, envSources };
  })();

  const hasEnv = merged && Object.keys(merged.mergedEnv).length > 0;
  const hasOutputs = stepData && stepData.outputs && Object.keys(stepData.outputs).length > 0;
  const hasInputs = stepData && stepData.inputs && Object.keys(stepData.inputs).length > 0;
  const hasArgs = merged && merged.mergedArgs.length > 0;

  const renderViewMode = () => (
    <div className="step-sections">
      <section className="panel-section">
        <h4 className="panel-section-title">General</h4>
        <dl className="panel-fields">
          <div className="panel-field">
            <dt>ID</dt>
            <dd className="mono">{stepData.id}</dd>
          </div>
          {merged.description && (
            <div className="panel-field">
              <dt>Description</dt>
              <dd>{merged.description}{templateData && !stepData.description && templateData.description && <span className="source-badge tpl">template</span>}</dd>
            </div>
          )}
          {stepData.commandId && (
            <div className="panel-field">
              <dt>Template</dt>
              <dd className="mono">{stepData.commandId}</dd>
            </div>
          )}
        </dl>
      </section>

      <section className="panel-section">
        <h4 className="panel-section-title">Command</h4>
        <dl className="panel-fields">
          {merged.command && (
            <div className="panel-field">
              <dt>Command</dt>
              <dd className="mono">{merged.command}{templateData && !stepData.command && templateData.command && <span className="source-badge tpl">template</span>}</dd>
            </div>
          )}
          {hasArgs && (
            <div className="panel-field">
              <dt>Arguments</dt>
              <dd className="mono">
                {merged.tplArgs.map((a, i) => (
                  <span key={`t${i}`} className="arg-chip tpl">{a}</span>
                ))}
                {merged.stepArgs.map((a, i) => (
                  <span key={`s${i}`} className="arg-chip step">{a}</span>
                ))}
              </dd>
            </div>
          )}
          <div className="panel-field">
            <dt>Use System Env</dt>
            <dd>{merged.useSystemEnvironment ? 'Yes' : 'No'}</dd>
          </div>
        </dl>
      </section>

      {hasEnv && (
        <section className="panel-section">
          <h4 className="panel-section-title">Environment Variables</h4>
          <table className="panel-table">
            <thead>
              <tr>
                <th>Variable</th>
                <th>Value</th>
                <th>Default</th>
                <th>Source</th>
              </tr>
            </thead>
            <tbody>
              {Object.entries(merged.mergedEnv).map(([name, desc]) => (
                <tr key={name} className={merged.envSources[name] === 'template' ? 'row-from-template' : ''}>
                  <td className="mono">{name}</td>
                  <td>{desc.value || <EmptyValue />}</td>
                  <td>{desc.defaultValue || <EmptyValue />}</td>
                  <td><span className={`source-badge ${merged.envSources[name]}`}>{merged.envSources[name]}</span></td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>
      )}


      {hasOutputs && (
        <section className="panel-section">
          <h4 className="panel-section-title">Outputs</h4>
          {renderViewOutputs(stepData.outputs)}
        </section>
      )}

      {hasInputs && (
        <section className="panel-section">
          <h4 className="panel-section-title">Inputs</h4>
          {renderViewInputs(stepData.inputs)}
        </section>
      )}
    </div>
  );

  const renderEditMode = () => (
    <div className="step-sections">
      <section className="panel-section">
        <h4 className="panel-section-title">General</h4>
        <div className="edit-fields">
          <label className="edit-field">
            <span className="edit-label">ID</span>
            <input
              type="text"
              className="edit-input"
              value={editData.id}
              onChange={(e) => updateField('id', e.target.value)}
            />
          </label>
          <label className="edit-field">
            <span className="edit-label">Description</span>
            <textarea
              className="edit-input edit-textarea"
              value={editData.description}
              onChange={(e) => updateField('description', e.target.value)}
              rows={2}
            />
          </label>
        </div>
      </section>

      <section className="panel-section">
        <h4 className="panel-section-title">Command</h4>
        <div className="edit-fields">
          {/* Toggle between command and commandId */}
          <div className="edit-toggle">
            <button
              type="button"
              className={`toggle-btn ${editData.commandMode === 'command' ? 'active' : ''}`}
              onClick={() => updateField('commandMode', 'command')}
            >
              Command
            </button>
            <button
              type="button"
              className={`toggle-btn ${editData.commandMode === 'commandId' ? 'active' : ''}`}
              onClick={() => updateField('commandMode', 'commandId')}
            >
              Command Template ID
            </button>
          </div>

          {editData.commandMode === 'command' ? (
            <label className="edit-field">
              <span className="edit-label">Command</span>
              <input
                type="text"
                className="edit-input"
                value={editData.command}
                onChange={(e) => updateField('command', e.target.value)}
              />
            </label>
          ) : (
            <label className="edit-field">
              <span className="edit-label">Command Template ID</span>
              <input
                type="text"
                className="edit-input"
                value={editData.commandId}
                onChange={(e) => updateField('commandId', e.target.value)}
              />
            </label>
          )}

          {/* Arguments list */}
          <div className="edit-field">
            <div className="edit-label-row">
              <span className="edit-label">Arguments</span>
              <button type="button" className="list-btn" onClick={addArgument}>+</button>
            </div>
            {editData.arguments.length === 0 && (
              <span className="empty-value">No arguments</span>
            )}
            {editData.arguments.map((arg, i) => (
              <div key={i} className="list-item-row">
                <input
                  type="text"
                  className="edit-input"
                  value={arg}
                  onChange={(e) => updateArgument(i, e.target.value)}
                  placeholder={`arg ${i + 1}`}
                />
                <button type="button" className="list-btn list-btn-remove" onClick={() => removeArgument(i)}>−</button>
              </div>
            ))}
          </div>

          <label className="edit-field edit-checkbox-field">
            <input
              type="checkbox"
              checked={editData.useSystemEnvironment}
              onChange={(e) => updateField('useSystemEnvironment', e.target.checked)}
            />
            <span className="edit-label">Use System Environment</span>
          </label>
        </div>
      </section>

      <section className="panel-section">
        <h4 className="panel-section-title">Dependencies</h4>
        <div className="edit-fields">
          <div className="edit-field">
            <div className="edit-label-row">
              <span className="edit-label">Precedents</span>
            </div>
            {editData.precedents.length === 0 && (
              <span className="empty-value">No precedents</span>
            )}
            {editData.precedents.map((p, i) => (
              <div key={i} className="list-item-row">
                <span className="edit-input mono" style={{ flex: 1, display: 'flex', alignItems: 'center' }}>{p}</span>
                <button
                  type="button"
                  className="list-btn list-btn-remove"
                  onClick={() => updateField('precedents', editData.precedents.filter((_, idx) => idx !== i))}
                >−</button>
              </div>
            ))}
            {(() => {
              const descendants = getDescendants(stepId, allLinks);
              const available = allStepIds.filter(
                (id) => id !== stepId && !descendants.has(id) && !editData.precedents.includes(id)
              );
              if (available.length === 0) return null;
              return (
                <select
                  className="edit-input"
                  value=""
                  onChange={(e) => {
                    if (e.target.value) {
                      updateField('precedents', [...editData.precedents, e.target.value]);
                    }
                  }}
                >
                  <option value="">+ Add precedent…</option>
                  {available.map((id) => (
                    <option key={id} value={id}>{id}</option>
                  ))}
                </select>
              );
            })()}
          </div>
        </div>
      </section>

      {/* Environment Variables - editable */}
      <section className="panel-section">
        <h4 className="panel-section-title">Environment Variables</h4>
        <div className="edit-fields">
          {Object.keys(editData.environment).length === 0 && (
            <span className="empty-value">No environment variables</span>
          )}
          {Object.entries(editData.environment).map(([varName, varDef]) => (
            <div key={varName} className="env-card">
              <div className="env-card-header">
                <span className="mono env-card-name">{varName}</span>
                <button
                  type="button"
                  className="list-btn list-btn-remove"
                  onClick={() => {
                    const env = { ...editData.environment };
                    delete env[varName];
                    updateField('environment', env);
                  }}
                >−</button>
              </div>
              <div className="env-card-fields">
                <label className="edit-field">
                  <span className="edit-label">Value</span>
                  <input
                    type="text"
                    className="edit-input"
                    value={varDef.value || ''}
                    onChange={(e) => {
                      const env = { ...editData.environment };
                      env[varName] = { ...env[varName], value: e.target.value };
                      updateField('environment', env);
                    }}
                  />
                </label>
                <label className="edit-field">
                  <span className="edit-label">Default Value</span>
                  <input
                    type="text"
                    className="edit-input"
                    value={varDef.defaultValue || ''}
                    onChange={(e) => {
                      const env = { ...editData.environment };
                      env[varName] = { ...env[varName], defaultValue: e.target.value };
                      updateField('environment', env);
                    }}
                  />
                </label>
                <label className="edit-field">
                  <span className="edit-label">Description</span>
                  <input
                    type="text"
                    className="edit-input"
                    value={varDef.description || ''}
                    onChange={(e) => {
                      const env = { ...editData.environment };
                      env[varName] = { ...env[varName], description: e.target.value };
                      updateField('environment', env);
                    }}
                  />
                </label>
                <label className="edit-field edit-checkbox-field">
                  <input
                    type="checkbox"
                    checked={varDef.optional || false}
                    onChange={(e) => {
                      const env = { ...editData.environment };
                      env[varName] = { ...env[varName], optional: e.target.checked };
                      updateField('environment', env);
                    }}
                  />
                  <span className="edit-label">Optional</span>
                </label>
              </div>
            </div>
          ))}
          <div className="env-add-row">
            <input
              type="text"
              className="edit-input"
              placeholder="New variable name…"
              id="new-env-var-name"
              onKeyDown={(e) => {
                if (e.key === 'Enter' && e.target.value.trim()) {
                  const name = e.target.value.trim();
                  if (!editData.environment[name]) {
                    updateField('environment', {
                      ...editData.environment,
                      [name]: {},
                    });
                  }
                  e.target.value = '';
                }
              }}
            />
            <button
              type="button"
              className="list-btn"
              onClick={() => {
                const input = document.getElementById('new-env-var-name');
                const name = input.value.trim();
                if (name && !editData.environment[name]) {
                  updateField('environment', {
                    ...editData.environment,
                    [name]: {},
                  });
                  input.value = '';
                }
              }}
            >+</button>
          </div>
        </div>
      </section>

      {/* Outputs - editable */}
      <section className="panel-section">
        <h4 className="panel-section-title">Outputs</h4>
        <div className="edit-fields">
          {Object.keys(editData.outputs).length === 0 && (
            <span className="empty-value">No outputs</span>
          )}
          {Object.entries(editData.outputs).map(([name, def]) => (
            <div key={name} className="env-card">
              <div className="env-card-header">
                <span className="mono env-card-name">{name}</span>
                <button type="button" className="list-btn list-btn-remove" onClick={() => {
                  const o = { ...editData.outputs }; delete o[name]; updateField('outputs', o);
                }}>−</button>
              </div>
              <div className="env-card-fields">
                <label className="edit-field">
                  <span className="edit-label">Description</span>
                  <input type="text" className="edit-input" value={def.description || ''} onChange={(e) => {
                    const o = { ...editData.outputs }; o[name] = { ...o[name], description: e.target.value }; updateField('outputs', o);
                  }} />
                </label>
                <label className="edit-field">
                  <span className="edit-label">Default Value</span>
                  <input type="text" className="edit-input" value={def.defaultValue || ''} onChange={(e) => {
                    const o = { ...editData.outputs }; o[name] = { ...o[name], defaultValue: e.target.value }; updateField('outputs', o);
                  }} />
                </label>
                <label className="edit-field edit-checkbox-field">
                  <input type="checkbox" checked={def.optional || false} onChange={(e) => {
                    const o = { ...editData.outputs }; o[name] = { ...o[name], optional: e.target.checked }; updateField('outputs', o);
                  }} />
                  <span className="edit-label">Optional</span>
                </label>
                <label className="edit-field edit-checkbox-field">
                  <input type="checkbox" checked={def.hidden || false} onChange={(e) => {
                    const o = { ...editData.outputs }; o[name] = { ...o[name], hidden: e.target.checked }; updateField('outputs', o);
                  }} />
                  <span className="edit-label">Hidden</span>
                </label>
              </div>
            </div>
          ))}
          <div className="env-add-row">
            <input type="text" className="edit-input" placeholder="New output name…" id="new-output-name"
              onKeyDown={(e) => {
                if (e.key === 'Enter' && e.target.value.trim()) {
                  const n = e.target.value.trim();
                  if (!editData.outputs[n]) { updateField('outputs', { ...editData.outputs, [n]: {} }); }
                  e.target.value = '';
                }
              }} />
            <button type="button" className="list-btn" onClick={() => {
              const input = document.getElementById('new-output-name');
              const n = input.value.trim();
              if (n && !editData.outputs[n]) { updateField('outputs', { ...editData.outputs, [n]: {} }); input.value = ''; }
            }}>+</button>
          </div>
        </div>
      </section>

      {/* Inputs - editable (only if upstream steps have outputs) */}
      {(() => {
        const directPrecedents = allLinks.filter(([, tgt]) => tgt === stepId).map(([src]) => src);
        const precedentsWithOutputs = directPrecedents.filter((id) => allStepOutputs[id] && allStepOutputs[id].length > 0);
        if (precedentsWithOutputs.length === 0 && Object.keys(editData.inputs).length === 0) return null;
        return (
          <section className="panel-section">
            <h4 className="panel-section-title">Inputs</h4>
            <div className="edit-fields">
              {Object.keys(editData.inputs).length === 0 && (
                <span className="empty-value">No inputs</span>
              )}
              {Object.entries(editData.inputs).map(([name, def]) => {
                const selectedStepOutputs = def.stepId && allStepOutputs[def.stepId] ? allStepOutputs[def.stepId] : [];
                return (
                  <div key={name} className="env-card">
                    <div className="env-card-header">
                      <span className="mono env-card-name">{name}</span>
                      <button type="button" className="list-btn list-btn-remove" onClick={() => {
                        const inp = { ...editData.inputs }; delete inp[name]; updateField('inputs', inp);
                      }}>−</button>
                    </div>
                    <div className="env-card-fields">
                      <label className="edit-field">
                        <span className="edit-label">Step ID <span style={{color:'#ef4444'}}>*</span></span>
                        <select className="edit-input" value={def.stepId || ''} onChange={(e) => {
                          const inp = { ...editData.inputs };
                          inp[name] = { ...inp[name], stepId: e.target.value, output: '' };
                          updateField('inputs', inp);
                        }}>
                          <option value="">— Select step —</option>
                          {precedentsWithOutputs.map((id) => (
                            <option key={id} value={id}>{id}</option>
                          ))}
                        </select>
                      </label>
                      <label className="edit-field">
                        <span className="edit-label">Output <span style={{color:'#ef4444'}}>*</span></span>
                        <select className="edit-input" value={def.output || ''} onChange={(e) => {
                          const inp = { ...editData.inputs }; inp[name] = { ...inp[name], output: e.target.value }; updateField('inputs', inp);
                        }} disabled={!def.stepId}>
                          <option value="">— Select output —</option>
                          {selectedStepOutputs.map((o) => (
                            <option key={o} value={o}>{o}</option>
                          ))}
                        </select>
                      </label>
                      <label className="edit-field">
                        <span className="edit-label">As (env var) <span style={{color:'#ef4444'}}>*</span></span>
                        <input type="text" className="edit-input" value={def.as || ''} onChange={(e) => {
                          const inp = { ...editData.inputs }; inp[name] = { ...inp[name], as: e.target.value }; updateField('inputs', inp);
                        }} />
                      </label>
                      <label className="edit-field">
                        <span className="edit-label">Default Value</span>
                        <input type="text" className="edit-input" value={def.defaultValue || ''} onChange={(e) => {
                          const inp = { ...editData.inputs }; inp[name] = { ...inp[name], defaultValue: e.target.value }; updateField('inputs', inp);
                        }} />
                      </label>
                      <label className="edit-field edit-checkbox-field">
                        <input type="checkbox" checked={def.optional || false} onChange={(e) => {
                          const inp = { ...editData.inputs }; inp[name] = { ...inp[name], optional: e.target.checked }; updateField('inputs', inp);
                        }} />
                        <span className="edit-label">Optional</span>
                      </label>
                      <label className="edit-field edit-checkbox-field">
                        <input type="checkbox" checked={def.hidden || false} onChange={(e) => {
                          const inp = { ...editData.inputs }; inp[name] = { ...inp[name], hidden: e.target.checked }; updateField('inputs', inp);
                        }} />
                        <span className="edit-label">Hidden</span>
                      </label>
                    </div>
                  </div>
                );
              })}
              {precedentsWithOutputs.length > 0 && (
                <div className="env-add-row">
                  <input type="text" className="edit-input" placeholder="New input name…" id="new-input-name"
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' && e.target.value.trim()) {
                        const n = e.target.value.trim();
                        if (!editData.inputs[n]) { updateField('inputs', { ...editData.inputs, [n]: { stepId: '', output: '', as: '' } }); }
                        e.target.value = '';
                      }
                    }} />
                  <button type="button" className="list-btn" onClick={() => {
                    const input = document.getElementById('new-input-name');
                    const n = input.value.trim();
                    if (n && !editData.inputs[n]) { updateField('inputs', { ...editData.inputs, [n]: { stepId: '', output: '', as: '' } }); input.value = ''; }
                  }}>+</button>
                </div>
              )}
            </div>
          </section>
        );
      })()}

      {saveError && (
        <p className="status error">Save failed: {saveError}</p>
      )}
    </div>
  );

  return (
    <div className="side-panel">
      <div className="side-panel-header">
        <h3>{stepId}</h3>
        <div className="side-panel-actions">
          {!editing && stepData && !confirmDelete && (
            <>
              <button className="panel-btn" onClick={startEditing}>
                ✎ Edit
              </button>
              <button
                className="panel-btn panel-btn-danger"
                onClick={() => setConfirmDelete(true)}
              >
                🗑 Delete
              </button>
            </>
          )}
          {!editing && confirmDelete && (
            <>
              <span className="delete-confirm-label">Delete?</span>
              <button
                className="panel-btn panel-btn-danger"
                onClick={handleDelete}
                disabled={deleting}
              >
                {deleting ? 'Deleting…' : 'Yes, delete'}
              </button>
              <button className="panel-btn" onClick={() => setConfirmDelete(false)} disabled={deleting}>
                Cancel
              </button>
            </>
          )}
          {editing && (
            <>
              <button
                className="panel-btn panel-btn-primary"
                onClick={handleSave}
                disabled={saving}
              >
                {saving ? 'Saving…' : '✓ Save'}
              </button>
              <button className="panel-btn" onClick={cancelEditing} disabled={saving}>
                ✕ Cancel
              </button>
            </>
          )}
          {!editing && (
            <button className="side-panel-close" onClick={onClose}>
              ✕
            </button>
          )}
        </div>
      </div>
      <div className="side-panel-body">
        {loading && <p className="status">Loading…</p>}
        {error && <p className="status error">Error: {error}</p>}
        {stepData && (editing ? renderEditMode() : renderViewMode())}
      </div>
    </div>
  );
}

function GraphViewInner({ projectName }) {
  const { fitView } = useReactFlow();
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedStep, setSelectedStep] = useState(null);
  const [stepOutputs, setStepOutputs] = useState({});
  const fetchGraph = useCallback(
    (showLoading) => {
      if (!projectName) return;
      if (showLoading) {
        setLoading(true);
        setError(null);
      }

      Promise.all([
        fetch(`/project/${projectName}/steps`).then((res) => {
          if (!res.ok) throw new Error(`Steps: HTTP ${res.status}`);
          return res.json();
        }),
        fetch(`/project/${projectName}/links`).then((res) => {
          if (!res.ok) throw new Error(`Links: HTTP ${res.status}`);
          return res.json();
        }),
        fetch(`/project/${projectName}/outputs`).then((res) => {
          if (!res.ok) throw new Error(`Outputs: HTTP ${res.status}`);
          return res.json();
        }),
      ])
        .then(([steps, links, outputs]) => {
          const rawNodes = stepsToNodes(steps);
          const rawEdges = linksToEdges(links);
          const { nodes: layoutedNodes, edges: layoutedEdges } =
            getLayoutedElements(rawNodes, rawEdges);
          setNodes(layoutedNodes);
          setEdges(layoutedEdges);
          setStepOutputs(outputs);
          setLoading(false);
        })
        .catch((err) => {
          setError(err.message);
          setLoading(false);
        });
    },
    [projectName, setNodes, setEdges],
  );

  // Initial load (with loading indicator) + reset selection on project change
  useEffect(() => {
    setSelectedStep(null);
    fetchGraph(true);
  }, [fetchGraph]);

  const resetRunState = useCallback(() => {
    setRunning(false);
    setRunStatus(null);
    setRunLogs([]);
    setRunExitCode(null);
    setShowLogs(false);
    setStepStatuses({});
  }, []);

  const refreshGraph = useCallback(() => {
    resetRunState();
    fetchGraph(false);
  }, [fetchGraph, resetRunState]);

  const [graphError, setGraphError] = useState(null);

  const showGraphError = useCallback((msg) => {
    setGraphError(msg);
    setTimeout(() => setGraphError(null), 5000);
  }, []);

  const onConnect = useCallback(
    (params) => {
      const { source, target } = params;
      setEdges((eds) => addEdge({ ...params, animated: true }, eds));
      fetch(`/project/${projectName}/link`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ source, target }),
      })
        .then((res) => {
          if (!res.ok) return res.json().then((d) => { throw new Error(d.detail || `HTTP ${res.status}`); });
          refreshGraph();
        })
        .catch((err) => {
          setEdges((eds) => eds.filter((e) => !(e.source === source && e.target === target)));
          showGraphError(err.message);
        });
    },
    [setEdges, projectName, refreshGraph, showGraphError],
  );

  const onEdgesDelete = useCallback(
    (deletedEdges) => {
      for (const edge of deletedEdges) {
        fetch(`/project/${projectName}/link`, {
          method: 'DELETE',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ source: edge.source, target: edge.target }),
        })
          .then((res) => {
            if (!res.ok) return res.json().then((d) => { throw new Error(d.detail || `HTTP ${res.status}`); });
            refreshGraph();
          })
          .catch((err) => {
            showGraphError(`Failed to delete link: ${err.message}`);
            refreshGraph();
          });
      }
    },
    [projectName, refreshGraph, showGraphError],
  );

  const onNodeClick = useCallback((_event, node) => {
    setSelectedStep(node.id);
  }, []);

  const onDragOver = useCallback((e) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'copy';
  }, []);

  const onDrop = useCallback(
    (e) => {
      e.preventDefault();
      const templateId = e.dataTransfer.getData('application/template-id');
      if (!templateId || !projectName) return;

      // Generate a unique step name
      const existingIds = new Set(nodes.map((n) => n.id));
      let stepName = templateId;
      let counter = 1;
      while (existingIds.has(stepName)) {
        stepName = `${templateId}-${counter}`;
        counter++;
      }

      fetch(`/project/${projectName}/step`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id: stepName, commandId: templateId }),
      })
        .then((res) => {
          if (!res.ok) return res.json().then((d) => { throw new Error(d.detail || `HTTP ${res.status}`); });
          return res.json();
        })
        .then(() => {
          refreshGraph();
          setSelectedStep(stepName);
        })
        .catch((err) => {
          showGraphError(`Failed to create step: ${err.message}`);
        });
    },
    [projectName, nodes, refreshGraph, showGraphError],
  );

  // Track per-step run status from log analysis
  const [stepStatuses, setStepStatuses] = useState({}); // stepId -> 'running' | 'success' | 'error' | 'skipped'

  const parseLogForStepStatus = useCallback((logText) => {
    // Patterns matching orchestrator log output (log lines have timestamp+level prefix)
    const patterns = [
      { regex: /Starting (?:step|exit handler) (.+)/, status: 'running' },
      { regex: /Done running (?:step|exit handler) (.+)/, status: 'success' },
      { regex: /Error during (?:step|exit handler) (.+)/, status: 'error' },
      { regex: /Skipping (?:step|exit handler) (.+?) due to previous errors/, status: 'skipped' },
      { regex: /Skipping (?:step|exit handler) (.+?) as required/, status: 'skipped' },
    ];
    for (const { regex, status } of patterns) {
      const match = logText.match(regex);
      if (match) {
        const stepId = match[1].trim();
        setStepStatuses((prev) => ({ ...prev, [stepId]: status }));
        return;
      }
    }
  }, []);

  const stepStatusColors = {
    running: { background: '#3b82f6', color: '#fff', borderColor: '#2563eb', borderWidth: 2 },
    success: { background: '#10b981', color: '#fff', borderColor: '#059669', borderWidth: 2 },
    error: { background: '#ef4444', color: '#fff', borderColor: '#dc2626', borderWidth: 2 },
    skipped: { background: '#f59e0b', color: '#fff', borderColor: '#d97706', borderWidth: 2 },
  };

  const styledNodes = nodes.map((node) => {
    const isSelected = node.id === selectedStep;
    const runSt = stepStatuses[node.id];
    let style = {};
    if (isSelected) {
      style = { background: '#6366f1', color: '#fff', borderColor: '#4f46e5', borderWidth: 2 };
    }
    if (runSt && stepStatusColors[runSt]) {
      // Run status takes priority, but outline for selection
      style = { ...stepStatusColors[runSt] };
      if (isSelected) {
        style.boxShadow = '0 0 0 3px #6366f1';
      }
    }
    return { ...node, style };
  });

  const [addingStep, setAddingStep] = useState(false);
  const [newStepId, setNewStepId] = useState('');
  const [addError, setAddError] = useState(null);
  const [showTemplates, setShowTemplates] = useState(false);
  const [running, setRunning] = useState(false);
  const [runStatus, setRunStatus] = useState(null);
  const [runLogs, setRunLogs] = useState([]);
  const [showLogs, setShowLogs] = useState(false);
  const [runExitCode, setRunExitCode] = useState(null);
  const [showEnvPanel, setShowEnvPanel] = useState(false);
  const [envVars, setEnvVars] = useState(null); // from API
  const [envValues, setEnvValues] = useState({}); // user-filled values
  const [envLoading, setEnvLoading] = useState(false);
  const [customEnvVars, setCustomEnvVars] = useState([]); // [{name, value}]
  const [newCustomName, setNewCustomName] = useState('');
  const [skippedSteps, setSkippedSteps] = useState(new Set());

  const fetchEnvVars = () => {
    setEnvLoading(true);
    fetch(`/project/${projectName}/environment`)
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
      })
      .then((data) => {
        setEnvVars(data);
        // Pre-fill values from API data (matching orchestrator resolution: value → system → default)
        const prefilled = {};
        for (const [name, def] of Object.entries(data)) {
          prefilled[name] = def.value || def.systemValue || def.defaultValue || '';
        }
        setEnvValues((prev) => {
          // Keep any previously user-entered values
          const merged = { ...prefilled };
          for (const [k, v] of Object.entries(prev)) {
            if (v !== '' && k in merged) merged[k] = v;
          }
          return merged;
        });
        setEnvLoading(false);
      })
      .catch((err) => {
        showGraphError(`Failed to load environment: ${err.message}`);
        setEnvLoading(false);
      });
  };

  const handleRunClick = () => {
    if (!projectName || running) return;
    setShowEnvPanel(true);
    fetchEnvVars();
  };

  const getUnfilledRequired = () => {
    if (!envVars) return [];
    return Object.entries(envVars)
      .filter(([name, def]) => !def.optional && !envValues[name] && !def.defaultValue && !def.value && !def.systemValue)
      .map(([name]) => name);
  };

  const startRun = () => {
    setRunning(true);
    setRunStatus(null);
    setRunLogs([]);
    setRunExitCode(null);
    setStepStatuses({});
    setShowLogs(true);
    setShowEnvPanel(false);

    // Merge project env values with custom vars
    const allEnv = { ...envValues };
    for (const cv of customEnvVars) {
      if (cv.name.trim()) allEnv[cv.name.trim()] = cv.value;
    }

    fetch(`/project/${projectName}/run`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ environment: allEnv, skippedSteps: [...skippedSteps] }),
    })
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const reader = res.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';

        function processChunk({ done, value }) {
          if (done) {
            setRunning(false);
            return;
          }
          buffer += decoder.decode(value, { stream: true });
          const parts = buffer.split('\n\n');
          buffer = parts.pop(); // keep incomplete chunk
          for (const part of parts) {
            const line = part.replace(/^data: /, '');
            if (!line) continue;
            try {
              const evt = JSON.parse(line);
              if (evt.type === 'log') {
                setRunLogs((prev) => [...prev, evt.text]);
                parseLogForStepStatus(evt.text);
              } else if (evt.type === 'exit') {
                setRunExitCode(evt.code);
                setRunStatus(evt.code === 0 ? 'success' : 'error');
                setRunning(false);
              } else if (evt.type === 'error') {
                setRunLogs((prev) => [...prev, `ERROR: ${evt.text}`]);
                setRunStatus('error');
                setRunning(false);
              }
            } catch { /* ignore parse errors */ }
          }
          return reader.read().then(processChunk);
        }

        return reader.read().then(processChunk);
      })
      .catch((err) => {
        showGraphError(`Run failed: ${err.message}`);
        setRunStatus('error');
        setRunning(false);
      });
  };

  const handleAddStep = () => {
    // Generate a unique step name
    const existingIds = new Set(nodes.map((n) => n.id));
    let stepName = 'new-step';
    let counter = 1;
    while (existingIds.has(stepName)) {
      stepName = `new-step-${counter}`;
      counter++;
    }

    fetch(`/project/${projectName}/step`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ id: stepName }),
    })
      .then((res) => {
        if (!res.ok) return res.json().then((d) => { throw new Error(d.detail || `HTTP ${res.status}`); });
        return res.json();
      })
      .then(() => {
        refreshGraph();
        setSelectedStep(stepName);
      })
      .catch((err) => {
        showGraphError(`Failed to create step: ${err.message}`);
      });
  };

  // Re-center graph when side panels are toggled
  useEffect(() => {
    const timer = setTimeout(() => {
      fitView({ duration: 300 });
    }, 50);
    return () => clearTimeout(timer);
  }, [showLogs, showTemplates, selectedStep, showEnvPanel, fitView]);

  const konamiActive = useKonamiCode();

  const nodeTypes = useMemo(() => ({ meme: MemeNode }), []);

  if (loading) return <p className="status">Loading steps…</p>;
  if (error) return <p className="status error">Error: {error}</p>;

  return (
    <div className="graph-wrapper">
      {graphError && (
        <div className="graph-error-banner">
          <span>{graphError}</span>
          <button className="banner-close" onClick={() => setGraphError(null)}>✕</button>
        </div>
      )}
      <div className="graph-main-area">
      <div className="collapse-bar left" onClick={() => setShowTemplates((v) => !v)} title={showTemplates ? 'Hide Templates' : 'Show Templates'}>
        <span className="collapse-bar-label">{showTemplates ? '◀' : '▶'}</span>
        {!showTemplates && <span className="collapse-bar-text">Templates</span>}
      </div>
      {showTemplates && (
        <TemplatesPanel
          projectName={projectName}
          onStepCreated={refreshGraph}
          onSelectStep={(id) => setSelectedStep(id)}
        />
      )}
      <div className="graph-center-column">
        <div className="graph-container">
          <ReactFlow
            nodes={styledNodes}
            edges={edges}
            nodeTypes={nodeTypes}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onConnect={onConnect}
            onEdgesDelete={onEdgesDelete}
            onNodeClick={onNodeClick}
            onDragOver={onDragOver}
            onDrop={onDrop}
            fitView
            deleteKeyCode="Delete"
          >
            <Background />
            <Controls />
            <MiniMap />
            <div className="graph-fab-container">
              <button
                className="graph-fab"
                onClick={handleAddStep}
                title="Add new step"
              >+</button>
            </div>
            {konamiActive && <FallingEggs />}
          </ReactFlow>
        </div>
        <div className="collapse-bar bottom" onClick={() => { if (!running) { setShowEnvPanel((v) => { if (!v) fetchEnvVars(); return !v; }); } }} title={showEnvPanel ? 'Hide Environment' : 'Show Environment / Run'}>
          <span className="collapse-bar-label">{showEnvPanel ? '▼' : '▲'}</span>
          <span className="collapse-bar-text-h">Run</span>
        </div>
        {showEnvPanel && (
          <div className="env-bottom-panel">
            <div className="env-bottom-header">
              <h3>Environment Variables</h3>
              <div className="env-modal-actions">
                {getUnfilledRequired().length > 0 && (
                  <span className="env-missing-hint">
                    {getUnfilledRequired().length} required variable{getUnfilledRequired().length > 1 ? 's' : ''} missing
                  </span>
                )}
                <button className="panel-btn" onClick={() => setShowEnvPanel(false)}>Cancel</button>
                <button
                  className="panel-btn panel-btn-run"
                  onClick={startRun}
                  disabled={getUnfilledRequired().length > 0}
                >
                  ▶ Start Run
                </button>
              </div>
            </div>
            <div className="env-bottom-body">
              {/* Skipped Steps section */}
              {nodes.length > 0 && (
                <div className="env-skip-section">
                  <h4 className="panel-section-title">Skip Steps</h4>
                  <div className="env-skip-list">
                    {nodes.map((node) => (
                      <label key={node.id} className="env-skip-item">
                        <input
                          type="checkbox"
                          checked={skippedSteps.has(node.id)}
                          onChange={(e) => {
                            setSkippedSteps((prev) => {
                              const next = new Set(prev);
                              if (e.target.checked) next.add(node.id);
                              else next.delete(node.id);
                              return next;
                            });
                          }}
                        />
                        <span className="mono">{node.id}</span>
                      </label>
                    ))}
                  </div>
                </div>
              )}
              {envLoading && <p className="status">Loading environment…</p>}
              {!envLoading && envVars && (
                <table className="panel-table env-table">
                  <thead>
                    <tr>
                      <th>Variable</th>
                      <th>Value</th>
                      <th>System</th>
                      <th>Default</th>
                      <th>Required</th>
                      <th>Source</th>
                    </tr>
                  </thead>
                  <tbody>
                    {Object.entries(envVars).map(([name, def]) => {
                      const isMissing = !def.optional && !envValues[name] && !def.defaultValue && !def.value && !def.systemValue;
                      return (
                        <tr key={name} className={isMissing ? 'env-row-missing' : ''}>
                          <td className="mono">{name}</td>
                          <td>
                            <input
                              type="text"
                              className="edit-input env-table-input"
                              value={envValues[name] || ''}
                              onChange={(e) => setEnvValues((prev) => ({ ...prev, [name]: e.target.value }))}
                              placeholder={def.systemValue || def.defaultValue || ''}
                            />
                          </td>
                          <td className="mono">{def.systemValue || <EmptyValue />}</td>
                          <td className="mono">{def.defaultValue || <EmptyValue />}</td>
                          <td>{def.optional ? 'No' : <span className="env-required">Yes</span>}</td>
                          <td>
                            {def.sources.map((s, i) => (
                              <span key={i} className={`source-badge ${s.type}`}>
                                {s.type === 'template' ? `tpl:${s.templateId}` : `step:${s.stepId}`}
                              </span>
                            ))}
                          </td>
                        </tr>
                      );
                    })}
                    {customEnvVars.map((cv, idx) => (
                      <tr key={`custom-${idx}`} className="env-row-custom">
                        <td>
                          <input
                            type="text"
                            className="edit-input env-table-input"
                            value={cv.name}
                            onChange={(e) => {
                              setCustomEnvVars((prev) => prev.map((c, i) => i === idx ? { ...c, name: e.target.value } : c));
                            }}
                            placeholder="VAR_NAME"
                          />
                        </td>
                        <td>
                          <input
                            type="text"
                            className="edit-input env-table-input"
                            value={cv.value}
                            onChange={(e) => {
                              setCustomEnvVars((prev) => prev.map((c, i) => i === idx ? { ...c, value: e.target.value } : c));
                            }}
                            placeholder="value"
                          />
                        </td>
                        <td><EmptyValue /></td>
                        <td><EmptyValue /></td>
                        <td>—</td>
                        <td>
                          <span className="source-badge step">custom</span>
                          <button
                            type="button"
                            className="list-btn list-btn-remove"
                            style={{ marginLeft: 4, width: 22, height: 22, fontSize: 13 }}
                            onClick={() => setCustomEnvVars((prev) => prev.filter((_, i) => i !== idx))}
                          >−</button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
              {!envLoading && envVars && (
                <div className="env-add-row" style={{ marginTop: 12 }}>
                  <input
                    type="text"
                    className="edit-input"
                    placeholder="New variable name…"
                    value={newCustomName}
                    onChange={(e) => setNewCustomName(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' && newCustomName.trim()) {
                        setCustomEnvVars((prev) => [...prev, { name: newCustomName.trim(), value: '' }]);
                        setNewCustomName('');
                      }
                    }}
                  />
                  <button
                    type="button"
                    className="list-btn"
                    onClick={() => {
                      if (newCustomName.trim()) {
                        setCustomEnvVars((prev) => [...prev, { name: newCustomName.trim(), value: '' }]);
                        setNewCustomName('');
                      }
                    }}
                  >+</button>
                </div>
              )}
            </div>
          </div>
        )}
        </div>
      {selectedStep && (
        <StepDetailPanel
          projectName={projectName}
          stepId={selectedStep}
          onClose={() => setSelectedStep(null)}
          onStepUpdated={refreshGraph}
          onStepIdChanged={(newId) => setSelectedStep(newId)}
          allStepIds={nodes.map((n) => n.id)}
          allLinks={edges.map((e) => [e.source, e.target])}
          allStepOutputs={stepOutputs}
        />
      )}
      <div className="collapse-bar right" onClick={() => { if (runLogs.length > 0 || showLogs) setShowLogs((v) => !v); }} title={showLogs ? 'Hide Logs' : 'Show Logs'}>
        {!showLogs && <span className="collapse-bar-text">Logs{runLogs.length > 0 ? ` (${runLogs.length})` : ''}</span>}
        <span className="collapse-bar-label">{showLogs ? '▶' : '◀'}</span>
      </div>
      {showLogs && (
        <div className="run-log-panel">
          <div className="run-log-header">
            <span className="run-log-title">
              Run Output
              {running && <span className="run-log-status running">● Running</span>}
              {!running && runExitCode !== null && (
                <span className={`run-log-status ${runExitCode === 0 ? 'success' : 'error'}`}>
                  Exit code: {runExitCode}
                </span>
              )}
            </span>
            <button className="side-panel-close" onClick={() => setShowLogs(false)}>✕</button>
          </div>
          <div className="run-log-body" ref={(el) => { if (el) el.scrollTop = el.scrollHeight; }}>
            {runLogs.length === 0 && running && <p className="status">Waiting for output…</p>}
            {runLogs.map((line, i) => (
              <div key={i} className="run-log-line">{line}</div>
            ))}
          </div>
        </div>
      )}
      </div>
    </div>
  );
}
