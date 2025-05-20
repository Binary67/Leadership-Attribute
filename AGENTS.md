# Best‑Practice Playbook

## Code style & naming

1. **Adopt PEP 8** as the baseline: Use spaces around “=” in assignments and around binary operators, but no space just inside brackets or parentheses. For example: spam = ham[1] good  ⟶  spam = ham[ 1 ] bad.
2. **Variable names**
   * PascalCase for variables & functions* (except when overriding built‑ins).
   * Avoid abbreviations; favour clarity over brevity.
3. **Docstrings**: NumPy style; include *Args*, *Returns*, *Raises*.
4. **Limit function length** to ≈ 40 lines; extract helpers early.
