#!/usr/bin/env node
/**
 * E2B MCP Server - Production-grade Model Context Protocol server for E2B sandboxes.
 *
 * This module provides a robust MCP server implementation that allows AI models to
 * interact with E2B code execution sandboxes securely and efficiently.
 */

import { Sandbox } from "@e2b/code-interpreter";
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  ListToolsRequestSchema,
  CallToolRequestSchema,
  ErrorCode,
  McpError,
} from "@modelcontextprotocol/sdk/types.js";
import { z } from "zod";
import { zodToJsonSchema } from "zod-to-json-schema";
import dotenv from "dotenv";
import { readFileSync } from "fs";
import { fileURLToPath } from "url";
import { dirname, join } from "path";

dotenv.config();

// Read version from package.json
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const packageJson = JSON.parse(
  readFileSync(join(__dirname, "../package.json"), "utf-8")
);
const VERSION = packageJson.version;

// Constants
const DEFAULT_SANDBOX_TIMEOUT_MS = 300000; // 5 minutes
const MAX_SANDBOX_TIMEOUT_MS = 3600000; // 1 hour
const MAX_ACTIVE_SANDBOXES = parseInt(
  process.env.MAX_ACTIVE_SANDBOXES || "10",
  10
);
const LOG_LEVEL = process.env.LOG_LEVEL || "INFO";

// Schemas
const createSandboxSchema = z.object({
  timeoutMs: z
    .number()
    .min(1000)
    .max(MAX_SANDBOX_TIMEOUT_MS)
    .optional()
    .describe("Timeout in milliseconds"),
});

const runCommandSchema = z.object({
  command: z.string().min(1).describe("Shell command to execute"),
  sandboxId: z.string().describe("Sandbox ID"),
  background: z.boolean().default(false).describe("Run command in background"),
});

const readFileSchema = z.object({
  filePath: z.string().min(1).describe("Path to the file"),
  sandboxId: z.string().describe("Sandbox ID"),
});

const writeFileSchema = z.object({
  filePath: z.string().min(1).describe("Path to the file"),
  sandboxId: z.string().describe("Sandbox ID"),
  fileContents: z.string().describe("Content to write to the file"),
});

const listFilesSchema = z.object({
  sandboxId: z.string().describe("Sandbox ID"),
  folderPath: z.string().min(1).describe("Path to the folder"),
});

const runCodeSchema = z.object({
  code: z.string().min(1).describe("Python code to execute"),
  sandboxId: z
    .string()
    .optional()
    .describe(
      "Optional sandbox ID. If not provided, a temporary sandbox will be created."
    ),
});

const getSandboxUrlSchema = z.object({
  port: z.number().min(1).max(65535).describe("Port number"),
  sandboxId: z.string().describe("Sandbox ID"),
});

const killSandboxSchema = z.object({
  sandboxId: z.string().describe("Sandbox ID"),
});

// Custom Errors
class SandboxError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "SandboxError";
  }
}

class SandboxNotFoundError extends SandboxError {
  constructor(message: string) {
    super(message);
    this.name = "SandboxNotFoundError";
  }
}

class SandboxLimitExceededError extends SandboxError {
  constructor(message: string) {
    super(message);
    this.name = "SandboxLimitExceededError";
  }
}

// Logger utility
class Logger {
  private level: string;

  constructor(level: string = "INFO") {
    this.level = level;
  }

  private log(level: string, message: string, ...args: any[]): void {
    const timestamp = new Date().toISOString();
    console.error(`${timestamp} - e2b-mcp-server - ${level} - ${message}`, ...args);
  }

  info(message: string, ...args: any[]): void {
    this.log("INFO", message, ...args);
  }

  debug(message: string, ...args: any[]): void {
    if (this.level === "DEBUG") {
      this.log("DEBUG", message, ...args);
    }
  }

  warning(message: string, ...args: any[]): void {
    this.log("WARNING", message, ...args);
  }

  error(message: string, ...args: any[]): void {
    this.log("ERROR", message, ...args);
  }
}

const logger = new Logger(LOG_LEVEL);

// Sandbox Manager
class SandboxManager {
  private sandboxes: Map<string, Sandbox> = new Map();
  private maxSandboxes: number;

  constructor(maxSandboxes: number = MAX_ACTIVE_SANDBOXES) {
    this.maxSandboxes = maxSandboxes;
    logger.info(`SandboxManager initialized with max_sandboxes=${maxSandboxes}`);
  }

  async createSandbox(
    timeoutMs?: number
  ): Promise<{ sandboxId: string; sandbox: Sandbox }> {
    if (this.sandboxes.size >= this.maxSandboxes) {
      throw new SandboxLimitExceededError(
        `Maximum number of sandboxes (${this.maxSandboxes}) reached`
      );
    }

    const timeout = Math.min(
      timeoutMs || DEFAULT_SANDBOX_TIMEOUT_MS,
      MAX_SANDBOX_TIMEOUT_MS
    );

    try {
      const sandbox = await Sandbox.create({ timeoutMs: timeout });
      const sandboxId = sandbox.sandboxId;
      this.sandboxes.set(sandboxId, sandbox);
      logger.info(
        `Sandbox created: ${sandboxId} (timeout=${timeout}ms, active=${this.sandboxes.size})`
      );
      return { sandboxId, sandbox };
    } catch (error) {
      logger.error(`Failed to create sandbox: ${error}`);
      throw new SandboxError(`Failed to create sandbox: ${error}`);
    }
  }

  getSandbox(sandboxId: string): Sandbox {
    const sandbox = this.sandboxes.get(sandboxId);
    if (!sandbox) {
      throw new SandboxNotFoundError(`Sandbox ${sandboxId} not found`);
    }
    return sandbox;
  }

  async killSandbox(sandboxId: string): Promise<void> {
    if (!this.sandboxes.has(sandboxId)) {
      throw new SandboxNotFoundError(`Sandbox ${sandboxId} not found`);
    }

    try {
      const sandbox = this.sandboxes.get(sandboxId)!;
      await sandbox.kill();
      this.sandboxes.delete(sandboxId);
      logger.info(
        `Sandbox killed: ${sandboxId} (active=${this.sandboxes.size})`
      );
    } catch (error) {
      logger.error(`Error killing sandbox ${sandboxId}: ${error}`);
      // Still remove it from tracking even if kill fails
      this.sandboxes.delete(sandboxId);
      throw new SandboxError(`Error killing sandbox: ${error}`);
    }
  }

  async cleanupAll(): Promise<void> {
    const sandboxIds = Array.from(this.sandboxes.keys());
    logger.info(`Cleaning up ${sandboxIds.length} sandboxes`);

    for (const sandboxId of sandboxIds) {
      try {
        const sandbox = this.sandboxes.get(sandboxId);
        if (sandbox) {
          await sandbox.kill();
          logger.info(`Cleaned up sandbox: ${sandboxId}`);
        }
      } catch (error) {
        logger.error(`Error cleaning up sandbox ${sandboxId}: ${error}`);
      }
    }

    this.sandboxes.clear();
    logger.info("All sandboxes cleaned up");
  }

  getStats() {
    return {
      active_sandboxes: this.sandboxes.size,
      max_sandboxes: this.maxSandboxes,
      sandbox_ids: Array.from(this.sandboxes.keys()),
    };
  }
}

// E2B MCP Server
class E2BServer {
  private server: Server;
  private sandboxManager: SandboxManager;

  constructor() {
    this.server = new Server(
      {
        name: "e2b-code-mcp-server",
        version: VERSION,
      },
      {
        capabilities: {
          tools: {},
        },
      }
    );

    this.sandboxManager = new SandboxManager();
    this.setupHandlers();
    this.setupErrorHandling();
  }

  private setupErrorHandling(): void {
    this.server.onerror = (error) => {
      logger.error("[MCP Error]", error);
    };

    process.on("SIGINT", async () => {
      logger.info("Received shutdown signal");
      await this.cleanup();
      process.exit(0);
    });

    process.on("SIGTERM", async () => {
      logger.info("Received shutdown signal");
      await this.cleanup();
      process.exit(0);
    });
  }

  private async cleanup(): Promise<void> {
    logger.info("Shutting down server...");
    await this.sandboxManager.cleanupAll();
    await this.server.close();
    logger.info("Server shutdown complete");
  }

  private setupHandlers(): void {
    this.server.setRequestHandler(ListToolsRequestSchema, async () => ({
      tools: [
        {
          name: "create_sandbox",
          description: "Create a new E2B sandbox",
          inputSchema: zodToJsonSchema(createSandboxSchema),
        },
        {
          name: "run_command",
          description: "Run a command in the sandbox",
          inputSchema: zodToJsonSchema(runCommandSchema),
        },
        {
          name: "read_file",
          description: "Read a file from the sandbox",
          inputSchema: zodToJsonSchema(readFileSchema),
        },
        {
          name: "write_file",
          description: "Write content to a file in the sandbox",
          inputSchema: zodToJsonSchema(writeFileSchema),
        },
        {
          name: "list_files",
          description: "List files in a directory",
          inputSchema: zodToJsonSchema(listFilesSchema),
        },
        {
          name: "run_code",
          description:
            "Run python code in a secure sandbox by E2B. Using the Jupyter Notebook syntax. Optionally specify sandboxId to use an existing sandbox.",
          inputSchema: zodToJsonSchema(runCodeSchema),
        },
        {
          name: "get_sandbox_url",
          description: "Get the URL for a sandbox on a specific port",
          inputSchema: zodToJsonSchema(getSandboxUrlSchema),
        },
        {
          name: "kill_sandbox",
          description: "Kill a sandbox",
          inputSchema: zodToJsonSchema(killSandboxSchema),
        },
      ],
    }));

    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      logger.debug(`Tool called: ${request.params.name}`, request.params.arguments);

      try {
        switch (request.params.name) {
          case "create_sandbox":
            return await this.handleCreateSandbox(request.params.arguments);
          case "run_command":
            return await this.handleRunCommand(request.params.arguments);
          case "read_file":
            return await this.handleReadFile(request.params.arguments);
          case "write_file":
            return await this.handleWriteFile(request.params.arguments);
          case "list_files":
            return await this.handleListFiles(request.params.arguments);
          case "run_code":
            return await this.handleRunCode(request.params.arguments);
          case "get_sandbox_url":
            return await this.handleGetSandboxUrl(request.params.arguments);
          case "kill_sandbox":
            return await this.handleKillSandbox(request.params.arguments);
          default:
            throw new McpError(
              ErrorCode.MethodNotFound,
              `Unknown tool: ${request.params.name}`
            );
        }
      } catch (error) {
        if (error instanceof McpError) {
          throw error;
        }
        if (error instanceof z.ZodError) {
          logger.warning(`Validation error for tool ${request.params.name}: ${error}`);
          throw new McpError(
            ErrorCode.InvalidParams,
            `Invalid arguments: ${error.message}`
          );
        }
        if (error instanceof SandboxError) {
          logger.error(`Sandbox error in tool ${request.params.name}: ${error}`);
          throw new McpError(ErrorCode.InternalError, error.message);
        }
        logger.error(`Unexpected error executing tool ${request.params.name}: ${error}`);
        throw new McpError(
          ErrorCode.InternalError,
          `Unexpected error: ${error}`
        );
      }
    });
  }

  private async handleCreateSandbox(args: any) {
    const parsed = createSandboxSchema.parse(args);
    const { sandboxId } = await this.sandboxManager.createSandbox(
      parsed.timeoutMs
    );
    const timeout = parsed.timeoutMs || DEFAULT_SANDBOX_TIMEOUT_MS;

    const result = {
      sandboxId,
      message: `Sandbox created successfully with timeout ${timeout}ms`,
      stats: this.sandboxManager.getStats(),
    };

    return {
      content: [
        {
          type: "text",
          text: JSON.stringify(result, null, 2),
        },
      ],
    };
  }

  private async handleRunCommand(args: any) {
    const parsed = runCommandSchema.parse(args);
    const sandbox = this.sandboxManager.getSandbox(parsed.sandboxId);

    try {
      let response: any;
      
      if (parsed.background) {
        const result = await sandbox.commands.run(parsed.command, { background: true });
        response = {
          message: "Command started in background",
          pid: result.pid,
          sandboxId: parsed.sandboxId,
        };
      } else {
        const result = await sandbox.commands.run(parsed.command);
        response = {
          stdout: result.stdout,
          stderr: result.stderr,
          exit_code: result.exitCode,
          sandboxId: parsed.sandboxId,
        };
      }

      logger.info(
        `Command executed in sandbox ${parsed.sandboxId}: background=${parsed.background}`
      );

      return {
        content: [
          {
            type: "text",
            text: JSON.stringify(response, null, 2),
          },
        ],
      };
    } catch (error) {
      logger.error(`Error running command in sandbox ${parsed.sandboxId}: ${error}`);
      throw new SandboxError(`Failed to run command: ${error}`);
    }
  }

  private async handleReadFile(args: any) {
    const parsed = readFileSchema.parse(args);
    const sandbox = this.sandboxManager.getSandbox(parsed.sandboxId);

    try {
      const content = await sandbox.files.read(parsed.filePath);
      const result = {
        filePath: parsed.filePath,
        content,
        sandboxId: parsed.sandboxId,
      };

      logger.info(`Read file ${parsed.filePath} from sandbox ${parsed.sandboxId}`);

      return {
        content: [
          {
            type: "text",
            text: JSON.stringify(result, null, 2),
          },
        ],
      };
    } catch (error) {
      logger.error(`Error reading file ${parsed.filePath}: ${error}`);
      throw new SandboxError(`Failed to read file: ${error}`);
    }
  }

  private async handleWriteFile(args: any) {
    const parsed = writeFileSchema.parse(args);
    const sandbox = this.sandboxManager.getSandbox(parsed.sandboxId);

    try {
      await sandbox.files.write(parsed.filePath, parsed.fileContents);
      const result = {
        filePath: parsed.filePath,
        message: "File written successfully",
        sandboxId: parsed.sandboxId,
        size: parsed.fileContents.length,
      };

      logger.info(
        `Wrote file ${parsed.filePath} to sandbox ${parsed.sandboxId} (${parsed.fileContents.length} bytes)`
      );

      return {
        content: [
          {
            type: "text",
            text: JSON.stringify(result, null, 2),
          },
        ],
      };
    } catch (error) {
      logger.error(`Error writing file ${parsed.filePath}: ${error}`);
      throw new SandboxError(`Failed to write file: ${error}`);
    }
  }

  private async handleListFiles(args: any) {
    const parsed = listFilesSchema.parse(args);
    const sandbox = this.sandboxManager.getSandbox(parsed.sandboxId);

    try {
      const files = await sandbox.files.list(parsed.folderPath);
      const result = {
        folderPath: parsed.folderPath,
        files: files.map((f) => ({ name: f.name, type: f.type })),
        sandboxId: parsed.sandboxId,
        count: files.length,
      };

      logger.info(
        `Listed ${files.length} files in ${parsed.folderPath} from sandbox ${parsed.sandboxId}`
      );

      return {
        content: [
          {
            type: "text",
            text: JSON.stringify(result, null, 2),
          },
        ],
      };
    } catch (error) {
      logger.error(`Error listing files in ${parsed.folderPath}: ${error}`);
      throw new SandboxError(`Failed to list files: ${error}`);
    }
  }

  private async handleRunCode(args: any) {
    const parsed = runCodeSchema.parse(args);
    let shouldCleanup = false;
    let sandbox: Sandbox | null = null;

    try {
      if (parsed.sandboxId) {
        sandbox = this.sandboxManager.getSandbox(parsed.sandboxId);
        logger.info(`Running code in existing sandbox ${parsed.sandboxId}`);
      } else {
        sandbox = await Sandbox.create();
        shouldCleanup = true;
        logger.info("Running code in temporary sandbox");
      }

      const execution = await sandbox.runCode(parsed.code);

      const result: any = {
        stdout: execution.logs.stdout.join("\n"),
        stderr: execution.logs.stderr.join("\n"),
      };

      if (parsed.sandboxId) {
        result.sandboxId = parsed.sandboxId;
      } else {
        result.message = "Executed in temporary sandbox";
      }

      logger.info(
        `Code execution completed: stdout=${result.stdout.length} chars, stderr=${result.stderr.length} chars`
      );

      return {
        content: [
          {
            type: "text",
            text: JSON.stringify(result, null, 2),
          },
        ],
      };
    } catch (error) {
      logger.error(`Error running code: ${error}`);
      throw new SandboxError(`Failed to run code: ${error}`);
    } finally {
      if (shouldCleanup && sandbox) {
        try {
          await sandbox.kill();
          logger.info("Temporary sandbox cleaned up");
        } catch (error) {
          logger.warning(`Error cleaning up temporary sandbox: ${error}`);
        }
      }
    }
  }

  private async handleGetSandboxUrl(args: any) {
    const parsed = getSandboxUrlSchema.parse(args);
    const sandbox = this.sandboxManager.getSandbox(parsed.sandboxId);

    try {
      const url = sandbox.getHost(parsed.port);
      const result = {
        sandboxId: parsed.sandboxId,
        port: parsed.port,
        url,
      };

      logger.info(
        `Got URL for sandbox ${parsed.sandboxId} on port ${parsed.port}: ${url}`
      );

      return {
        content: [
          {
            type: "text",
            text: JSON.stringify(result, null, 2),
          },
        ],
      };
    } catch (error) {
      logger.error(`Error getting sandbox URL: ${error}`);
      throw new SandboxError(`Failed to get sandbox URL: ${error}`);
    }
  }

  private async handleKillSandbox(args: any) {
    const parsed = killSandboxSchema.parse(args);
    await this.sandboxManager.killSandbox(parsed.sandboxId);

    const result = {
      sandboxId: parsed.sandboxId,
      message: "Sandbox killed successfully",
      stats: this.sandboxManager.getStats(),
    };

    return {
      content: [
        {
          type: "text",
          text: JSON.stringify(result, null, 2),
        },
      ],
    };
  }

  async run(): Promise<void> {
    const transport = new StdioServerTransport();
    await this.server.connect(transport);

    logger.info("=".repeat(60));
    logger.info("E2B MCP Server - Production Grade");
    logger.info("=".repeat(60));
    logger.info(`Max active sandboxes: ${MAX_ACTIVE_SANDBOXES}`);
    logger.info(`Default sandbox timeout: ${DEFAULT_SANDBOX_TIMEOUT_MS}ms`);
    logger.info(`Max sandbox timeout: ${MAX_SANDBOX_TIMEOUT_MS}ms`);
    logger.info("=".repeat(60));
    logger.info("Server ready to accept connections");
  }
}

// Main entry point
const server = new E2BServer();
server.run().catch((error) => {
  logger.error("Server error:", error);
  process.exit(1);
});
