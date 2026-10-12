# Portable Agents

Defining breeds independent of the agent vendor: instructions, skills, agent definitions, runtime, permissions.

* [Portable Agents Research Summary](summary.md) - Which existing standard or convention fits each breed feature independent of the agent vendor, what has no standard, and a proposed vendor-neutral breed layout rendered per agent CLI.
* [Custom Agent Definitions Across Vendors](agent-definitions.md) - Field-by-field comparison of custom agent and subagent files in Claude Code, Codex, Copilot, Gemini CLI, Cursor, OpenCode, Kiro, goose and Amp, the state of portable agent standards, and how to express model choice without vendor ids.
* [Declarative Agent Specifications](declarative-specs.md) - Whole-agent and multi-agent definition formats (Oracle Agent Spec, AGNTCY OASF, A2A Agent Card, docker-agent, kagent, Microsoft AgentSchema, OpenGAP, Snap Agent Format, CrewAI, ADK and others) compared against the breed and formation features.
* [Portable Instructions and Skills](instructions-and-skills.md) - AGENTS.md and the per-vendor instruction files, and the Agent Skills load paths, across Claude Code, Codex, Gemini CLI, Copilot, Cursor, OpenCode, Kiro, Amp and goose.
* [Portable Runtime, Permissions, MCP, Limits and Hooks](runtime-and-permissions.md) - How runtime features, OS and tool permissions, MCP servers, limits and hooks are expressed in Claude Code, Codex, Gemini CLI, Copilot CLI, OpenCode and goose, which standards exist (Dev Container Features, agent-sandbox, MCP server.json), and which tools translate one definition into many.
