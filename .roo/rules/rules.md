# Book Creator Project Rules

## 🏗️ Project Fundamentals
- Always read/update `architecture_plan.md` before coding and after completing features
- Document complete database schema and migrations in architecture_plan.md
- Work incrementally with thorough testing
- Solve problems autonomously before reporting back

## 📄 Content Management
- **Append, Don't Overwrite**: Add to files rather than replacing content
- **Format & Structure**: Preserve original structure; timestamp entries `[YYYY-MM-DD HH:MM:SS]`
- **Memory Bank Status**: Begin responses with `[MEMORY BANK: ACTIVE/INACTIVE]`
- **File Modifications**: Use `insert_content` for adding, `apply_diff` for changes
- **Preservation**: Never delete content unless explicitly instructed
- **Verification**: Always verify file modifications succeeded
- **Task Management**: Use `/memory-bank/tasks/_TASK_TEMPLATE.md`; name files as `TASK-YYYY-MM-DD-task-name.md`
- **Chronological Order**: Preserve order in logs; add changelog entries at top

## 🛠️ Tool Usage
- Provide all required parameters, especially complete file paths with directories
- Format tool uses with proper XML tags and parameters
- For `ask_followup_question`, always include a specific question parameter
- When using `<update_memory_bank>`, use appropriate file modification tools
- For Python modules, use `python -m [file_name.py]` from project root

## ⚠️ Error Handling
- Log all errors in Memory Bank with context
- Use sensible defaults when parameters are unavailable
- Verify parameters before executing tools
- Implement graceful degradation for unavailable features
- Explain error resolution process
- Before attempting to read/write a file:
  1. Verify the file exists using `os.path.exists(file_path)`.
  3. Ask the user first to advise if to handle missing files by creating them or skipping operations.


## 💻 Code Quality & Development
- **Code Standards**: Maintain consistent formatting; create modular functions under 500 lines
- **Documentation**: Document interfaces clearly; use meaningful names
- **Workflow**:
  1. Understand problems deeply before coding
  2. Investigate codebase thoroughly
  3. Plan changes step-by-step
  4. Implement incrementally with frequent testing
  5. Address root causes, not just symptoms
  6. Verify changes comprehensively
  7. Seek approval before additional modifications
