# Best‑Practice Playbook

## Code style & naming

1. **Adopt PEP 8** as the baseline; automate with **Black** (formatting), **Ruff** (linting) and **isort** (import order).
2. **Variable names**
   * PascalCase for variables & functions* (except when overriding built‑ins).
   * Avoid abbreviations; favour clarity over brevity.
3. **Docstrings**: NumPy style; include *Args*, *Returns*, *Raises*.
4. **Limit function length** to ≈ 40 lines; extract helpers early.
