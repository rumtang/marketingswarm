import React, { useState } from 'react';
import SystemDiagram from '../components/SystemDiagram';
import './DiagramViewer.css';

const DiagramViewer = () => {
  const [selectedDiagram, setSelectedDiagram] = useState('architecture');

  const diagramOptions = [
    { value: 'architecture', label: 'System Architecture' },
    { value: 'personality', label: 'Agent Personality System' },
    { value: 'conversation', label: 'Conversation Flow' },
    { value: 'selection', label: 'Agent Selection Algorithm' },
    { value: 'relationships', label: 'Relationship Tracking' },
    { value: 'output', label: 'Output Generation' },
    { value: 'communication', label: 'Real-Time Communication' }
  ];

  return (
    <div className="diagram-viewer">
      <div className="viewer-header">
        <h1>Marketing Swarm System Diagrams</h1>
        <p>Interactive visualization of the dynamic agent collaboration system</p>
      </div>
      
      <div className="diagram-controls">
        <label htmlFor="diagram-select">Select Diagram:</label>
        <select 
          id="diagram-select"
          value={selectedDiagram} 
          onChange={(e) => setSelectedDiagram(e.target.value)}
          className="diagram-select"
        >
          {diagramOptions.map(option => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      </div>

      <div className="diagram-info">
        <h2>{diagramOptions.find(opt => opt.value === selectedDiagram)?.label}</h2>
        {selectedDiagram === 'architecture' && (
          <p>Shows how Frontend, Backend, and Agent System components interact via WebSocket connections.</p>
        )}
        {selectedDiagram === 'personality' && (
          <p>Illustrates how agent personality traits (assertiveness, contrarianism, creativity, patience) influence behavior.</p>
        )}
        {selectedDiagram === 'conversation' && (
          <p>Details the dynamic conversation flow with interruptions, reactions, and phase transitions.</p>
        )}
        {selectedDiagram === 'selection' && (
          <p>Explains how the system selects the next agent based on context, personality, and history.</p>
        )}
        {selectedDiagram === 'relationships' && (
          <p>Shows how agent relationships (alliances, conflicts, respect) are tracked and evolve.</p>
        )}
        {selectedDiagram === 'output' && (
          <p>Demonstrates how conversations are synthesized into professional briefing documents.</p>
        )}
        {selectedDiagram === 'communication' && (
          <p>Sequence diagram showing real-time message flow between system components.</p>
        )}
      </div>

      <SystemDiagram diagramType={selectedDiagram} />

      <div className="diagram-footer">
        <button 
          onClick={() => window.print()} 
          className="export-button"
        >
          Export as PDF
        </button>
        <p className="hint">Tip: Right-click on any diagram to save as image</p>
      </div>
    </div>
  );
};

export default DiagramViewer;