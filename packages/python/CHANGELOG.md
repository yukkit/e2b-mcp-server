# @yukkit/e2b-mcp-server

## 0.6.0

### Minor Changes

- 589b7da: fix: set useSignatureExpiration default to 5 minutes (300000ms)

## 0.5.0

### Minor Changes

- 2fbdbfd: Upgrade E2B SDK dependencies and add enhanced sandbox parameters:
  - Upgrade @e2b/code-interpreter from ^1.0.4 to ^2.3.3 (JS)
  - Upgrade e2b-code-interpreter from ^1.0.2 to ^2.3.3 (Python)
  - Add 'secure' parameter to create_sandbox for optional secure sandbox creation
  - Add 'useSignatureExpiration' parameter to get_file_download_url for customizable URL expiration (in seconds)

## 0.4.1

### Patch Changes

- 1dd827a: fix: get download url

## 0.4.0

### Minor Changes

- cc1ba05: Add list_sandbox_ids tool to list all active sandboxes

  - Add new `list_sandbox_ids` tool that returns all active sandbox IDs and statistics
  - Update tool count from 9 to 10 in all documentation
  - The tool returns: sandbox_ids (array), active_sandboxes (count), max_sandboxes (limit)
  - Implemented in both JavaScript/TypeScript and Python versions

## 0.3.0

### Minor Changes

- fe4c5b2: support get_file_download_url api

## 0.2.1

### Patch Changes

- 98d171a: init

## 0.2.0

### Minor Changes

- Complete rewrite of JavaScript implementation with production-grade features matching Python version
