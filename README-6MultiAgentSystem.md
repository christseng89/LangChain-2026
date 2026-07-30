# Multi Agent System

## Why Multi Agent?

###　Single Agent
```mermaid
flowchart LR

subgraph Single_Agent
    U1["User"]
    A["Single LLM"]
    O1["Answer"]

    U1 --> A --> O1
end

style U1 fill:#DBEAFE,stroke:#2563EB,stroke-width:3px
style A fill:#FECACA,stroke:#DC2626,stroke-width:2px
style O1 fill:#E9D5FF,stroke:#7E22CE,stroke-width:3px

```
> One LLM does everything 

- ❌ Confused by complexity 
- ❌ No specialization 
- ❌ Hard to debug

### Multi-Agent

```mermaid
flowchart TB

    U["User Request"]

    U --> S["Supervisor Agent"]

    S --> R["Research Agent"]
    S --> W["Writer Agent"]
    S --> RV["Reviewer Agent"]

    R --> S
    W --> S
    RV --> S

    style U fill:#DBEAFE,stroke:#2563EB,stroke-width:2px
    style S fill:#E9D5FF,stroke:#7E22CE,stroke-width:3px
    style R fill:#DCFCE7,stroke:#16A34A,stroke-width:2px
    style W fill:#FDE68A,stroke:#D97706,stroke-width:2px
    style RV fill:#FECACA,stroke:#DC2626,stroke-width:2px
  
```
> ✅ Specialized, modular, debuggable

---

## Multi-Agent Patterns

| Pattern | Description | Typical Use Case |
|----------|-------------|------------------|
| **Supervisor** | One agent coordinates other agents. | **Complex** workflows |
| **Hierarchical** | Multiple levels of supervisors. | Large organizations |
| **Collaborative** | Agents communicate peer-to-peer. | Creative tasks |
| **Sequential** | Agents process tasks in order. | Processing pipelines |
| **Parallel** | Agents work simultaneously. | Speed optimization |

> This course focuses on the **Supervisor Pattern**.
