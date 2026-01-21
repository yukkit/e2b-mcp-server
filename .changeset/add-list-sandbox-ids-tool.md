---
"@yukkit/e2b-mcp-server": minor
"@yukkit/e2b-mcp-server-python": minor
---

Add list_sandbox_ids tool to list all active sandboxes

- Add new `list_sandbox_ids` tool that returns all active sandbox IDs and statistics
- Update tool count from 9 to 10 in all documentation
- The tool returns: sandbox_ids (array), active_sandboxes (count), max_sandboxes (limit)
- Implemented in both JavaScript/TypeScript and Python versions
