# Leadership Attribute Identification with Azure OpenAI

Identify leadership‑related strengths and development areas in qualitative talent feedback at scale.

## 🔧 Setup

1. Create a `.env` file in the project root with your Azure OpenAI credentials:
```
AZURE_OPENAI_API_KEY=your_api_key_here
AZURE_OPENAI_ENDPOINT=your_endpoint_here
AZURE_OPENAI_API_VERSION=2024-02-01
AZURE_OPENAI_DEPLOYMENT=your_deployment_name
```

2. Install required dependencies:
```bash
pip install python-dotenv openai pandas numpy tqdm
```

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
```

---

## 🚀 Recent Improvements

### Async Azure OpenAI Implementation (Latest)
- **Replaced multithreading with async/await pattern**: Converted from `concurrent.futures.ThreadPoolExecutor` to native async operations using `asyncio`
- **Enhanced API efficiency**: Now uses `AsyncAzureOpenAI` client for non-blocking I/O operations
- **Maintained robust error handling**: Preserved the 25-attempt retry logic with exponential backoff using `asyncio.sleep()`
- **Improved performance**: Async operations are more efficient for I/O-bound tasks like API calls, reducing overhead compared to thread-based concurrency

### Technical Changes
1. **FeedbackAnalyzer.py**: Converted to async with `AsyncAzureOpenAI` client
2. **AttributeRater.py**: Converted to async with `AsyncAzureOpenAI` client  
3. **main.py**: Replaced `ThreadPoolExecutor` with `asyncio.gather()` for concurrent execution
4. **Progress tracking**: Updated to use `tqdm.asyncio` for async-compatible progress bars
