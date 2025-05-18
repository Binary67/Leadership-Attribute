# Leadership Attribute Identification with Azure OpenAI

Identify leadership‑related strengths and development areas in qualitative talent feedback at scale.

---

## ✨ What this project does

1. **Relevance check** – Given a piece of talent feedback and the name of a leadership attribute (e.g., *Strategic Thinking*), Azure OpenAI is prompted to:

   * Judge whether the feedback actually speaks to that attribute.
   * Highlight the exact substring that is relevant.
2. **Strength vs. Development** – A second prompt determines whether the extracted substring describes a **strength** or a **development need**.
3. **Attribute scoring** – The system then assigns a numeric rating (1‑5) to that substring, based on the project’s attribute‑rating rubric.

The result is a structured JSON record for every comment, ready for dashboards or downstream analytics.

---

## 🗺️ Architecture

```text
┌──────────────────┐     Prompt #1      ┌────────────────────┐
│ Raw Feedback CSV │ ─────────────────▶ │  Relevance Checker │
└──────────────────┘                    └────────────────────┘
                                              │
                              Relevant? No ───┘
                              │
                              ▼  Yes
                      ┌───────────────────┐    Prompt #2     ┌───────────────────────┐
                      │ Relevant Substring│ ───────────────▶ │ Strength/Development │
                      └───────────────────┘                  └───────────────────────┘
                              │
                              ▼
                      ┌───────────────────┐    Prompt #3     ┌──────────────────┐
                      │   Classifier      │ ───────────────▶ │  Rating (1‑5)   │
                      └───────────────────┘                  └──────────────────┘

```

## Mermaid Diagram

```
flowchart TD
    Start([Input: Talent Feedback]) --> A[Azure OpenAI API]
    
    subgraph "Stage 1: Relevance Detection & Substring Extraction"
        A --> B{Is feedback relevant\nto leadership attribute?}
        B -->|No| C[Discard Feedback]
        B -->|Yes| D[Extract Relevant Substring]
    end
    
    subgraph "Stage 2: Strength/Development Classification"
        D --> E{Analyze Substring}
        E -->|Strength| F[Classify as Strength]
        E -->|Development Area| G[Classify as Development Need]
    end
    
    subgraph "Stage 3: Score Assignment"
        F --> H[Evaluate Against\nAttribute Rating Definition]
        G --> H
        H --> I[Assign Numerical Score]
        I --> J[Generate Score Justification]
    end
    
    J --> Output([Output Results])
    C --> End([End Process])
    Output --> End
    
    classDef azure fill:#0078D4,color:white,stroke:#0078D4;
    classDef process fill:#E6F7FF,stroke:#0078D4,color:black;
    classDef decision fill:#CCE4F9,stroke:#0078D4,color:black;
    classDef terminal fill:#F2F8FD,stroke:#0078D4,color:black;
    
    class A azure;
    class B,E decision;
    class D,F,G,H,I,J process;
    class Start,End,Output,C terminal;
