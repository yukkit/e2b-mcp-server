---
"@yukkit/e2b-mcp-server-python": minor
"@yukkit/e2b-mcp-server": minor
---

Upgrade E2B SDK dependencies and add enhanced sandbox parameters:
- Upgrade @e2b/code-interpreter from ^1.0.4 to ^2.3.3 (JS)
- Upgrade e2b-code-interpreter from ^1.0.2 to ^2.3.3 (Python)
- Add 'secure' parameter to create_sandbox for optional secure sandbox creation
- Add 'useSignatureExpiration' parameter to get_file_download_url for customizable URL expiration (in seconds)
