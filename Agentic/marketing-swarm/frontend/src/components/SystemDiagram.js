import React, { useEffect, useRef } from 'react';
import mermaid from 'mermaid';
import './SystemDiagram.css';

const SystemDiagram = ({ diagramType = 'architecture' }) => {
  const mermaidRef = useRef(null);

  const diagrams = {
    architecture: `
graph TB
    subgraph "Frontend Layer"
        UI[React UI<br/>Port 3001]
        WS[WebSocket Client]
        CI[Conversation Interface]
        BD[Briefing Document View]
    end

    subgraph "Backend Layer"
        API[FastAPI Server<br/>Port 8001]
        SIO[Socket.IO Server]
        AM[Agent Manager]
        SF[Safety Filters]
    end

    subgraph "Agent System"
        A1[Sarah<br/>Brand Strategy Lead<br/>👔]
        A2[Marcus<br/>Digital Campaign Manager<br/>📱]
        A3[Elena<br/>Content Marketing<br/>✍️]
        A4[David<br/>Customer Experience<br/>🎨]
        A5[Priya<br/>Marketing Analytics<br/>📊]
        A6[Alex<br/>Growth Marketing<br/>🚀]
    end

    UI --> WS
    WS <--> SIO
    SIO <--> AM
    AM --> SF
    AM <--> A1
    AM <--> A2
    AM <--> A3
    AM <--> A4
    AM <--> A5
    AM <--> A6
`,
    personality: `
graph LR
    subgraph "Agent Traits"
        AS[Assertiveness<br/>0.0-1.0]
        CO[Contrarianism<br/>0.0-1.0]
        CR[Creativity<br/>0.0-1.0]
        PA[Patience<br/>0.0-1.0]
    end

    subgraph "Behavioral Outcomes"
        IN[Interruption<br/>Likelihood]
        RT[Response<br/>Time]
        CT[Conflict<br/>Tendency]
        AL[Alliance<br/>Formation]
    end

    AS --> IN
    CO --> CT
    CR --> RT
    PA --> RT
    AS --> AL
    CO --> AL
`,
    conversation: `
flowchart TD
    Start([User Query]) --> Init[Initialize Conversation]
    Init --> CM[Create Conversation Memory]
    
    CM --> P1{Phase: Discovery}
    P1 --> SA[Sarah Starts<br/>Strategic Framing]
    
    SA --> DL[Dynamic Loop]
    
    subgraph "Dynamic Response Loop"
        DL --> TT[Calculate Thinking Time<br/>patience × 3 + random]
        TT --> GR[Generate Response<br/>Based on Context]
        GR --> CR{Check for<br/>Reactions?}
        CR -->|Yes| RR[Generate Reactive<br/>Response]
        CR -->|No| PR[Generate Primary<br/>Response]
        RR --> EM[Emit Response]
        PR --> EM
        EM --> UR[Update Relationships]
        UR --> NA[Select Next Agent]
        NA --> CI{Check<br/>Interruption?}
        CI -->|Yes| INT[Interrupt Current<br/>Speaker]
        CI -->|No| CONT[Continue Normal<br/>Flow]
        INT --> DL
        CONT --> DL
    end
    
    DL --> PC{Phase<br/>Complete?}
    PC -->|No| DL
    PC -->|Yes| NP{Next Phase?}
    
    NP -->|Analysis| P2[Phase: Analysis]
    NP -->|Recommendation| P3[Phase: Recommendation]
    NP -->|Synthesis| P4[Phase: Synthesis]
    NP -->|Complete| END
    
    P2 --> DL
    P3 --> DL
    P4 --> DL
    
    END[Generate Briefing<br/>Document]
`,
    selection: `
flowchart LR
    subgraph "Selection Factors"
        CF[Current Agent<br/>Personality]
        LM[Last Message<br/>Content]
        AS[Agents Who<br/>Haven't Spoken]
        RH[Relationship<br/>History]
    end
    
    subgraph "Selection Rules"
        R1[High Assertiveness<br/>→ Triggers Contrarians]
        R2[Domain Keywords<br/>→ Domain Experts]
        R3[Unspoken Agents<br/>→ Higher Priority]
        R4[Conflict History<br/>→ More Likely to Respond]
    end
    
    CF --> R1
    LM --> R2
    AS --> R3
    RH --> R4
    
    R1 --> NA[Next Agent]
    R2 --> NA
    R3 --> NA
    R4 --> NA
`,
    relationships: `
graph TD
    subgraph "Relationship Types"
        AL[Alliances<br/>Agreement Counter]
        CF[Conflicts<br/>Disagreement Counter]
        RL[Respect Levels<br/>-10 to +10]
    end
    
    subgraph "Triggers"
        AG[Agreement Phrases<br/>"building on"<br/>"exactly"<br/>"brilliant"]
        DG[Disagreement Phrases<br/>"disagree"<br/>"wrong"<br/>"stop"]
        RF[Reference Phrases<br/>Mentioning other<br/>agents by name]
    end
    
    AG --> AL
    DG --> CF
    RF --> RL
    
    AL --> RS[Relationship<br/>Summary]
    CF --> RS
    RL --> RS
`,
    output: `
flowchart TD
    CH[Conversation History] --> AN[Analyze Contributions]
    
    AN --> KP[Extract Key Points]
    AN --> AR[Identify Agreements]
    AN --> DB[Note Debates]
    AN --> DP[Collect Data Points]
    AN --> RC[Compile Recommendations]
    
    subgraph "Briefing Document Sections"
        ES[Executive Summary]
        SA[Situation Analysis]
        SR[Strategic Recommendations]
        IT[Implementation Timeline]
        SM[Success Metrics]
        RA[Risk Assessment]
        NS[Next Steps]
    end
    
    KP --> ES
    AR --> ES
    DB --> SA
    DP --> SA
    RC --> SR
    SR --> IT
    SR --> SM
    DB --> RA
    IT --> NS
    
    ES --> BD[Final Briefing<br/>Document]
    SA --> BD
    SR --> BD
    IT --> BD
    SM --> BD
    RA --> BD
    NS --> BD
`,
    communication: `
sequenceDiagram
    participant User
    participant Frontend
    participant WebSocket
    participant Backend
    participant AgentManager
    participant Agents
    
    User->>Frontend: Enter query
    Frontend->>WebSocket: start_conversation
    WebSocket->>Backend: Process request
    Backend->>AgentManager: Initialize conversation
    
    loop Dynamic Conversation
        AgentManager->>Agents: Select agent based on context
        Agents->>Agents: Calculate thinking time
        Agents->>AgentManager: Generate response
        AgentManager->>Backend: Update relationships
        Backend->>WebSocket: Emit agent_response
        WebSocket->>Frontend: Display response
        Frontend->>User: Show agent message
    end
    
    AgentManager->>Backend: Generate briefing
    Backend->>WebSocket: conversation_complete
    WebSocket->>Frontend: Display briefing
    Frontend->>User: Show final document
`
  };

  useEffect(() => {
    mermaid.initialize({
      startOnLoad: true,
      theme: 'dark',
      themeVariables: {
        primaryColor: '#bb86fc',
        primaryTextColor: '#fff',
        primaryBorderColor: '#7700ff',
        lineColor: '#f4f4f4',
        secondaryColor: '#03dac6',
        tertiaryColor: '#121212',
        background: '#121212',
        mainBkg: '#1e1e1e',
        secondBkg: '#2e2e2e',
        tertiaryBkg: '#121212',
        textColor: '#e1e1e1',
        borderColor: '#333',
        fontSize: '14px'
      }
    });

    if (mermaidRef.current && diagrams[diagramType]) {
      mermaidRef.current.innerHTML = diagrams[diagramType];
      mermaid.run();
    }
  }, [diagramType]);

  return (
    <div className="diagram-container">
      <div className="mermaid" ref={mermaidRef}>
        {diagrams[diagramType]}
      </div>
    </div>
  );
};

export default SystemDiagram;