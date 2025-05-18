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
