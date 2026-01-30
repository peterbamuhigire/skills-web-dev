---
name: custom-sub-agents
description: "Guidance for creating and organizing custom sub-agents in local repos, including folder conventions, per-agent structure, and AGENTS.md indexing. Use when asked where to store sub-agents or how to document them."
---

# Custom Sub-Agents Skill

## Overview

This skill defines the standards and workflow for creating, organizing, and documenting custom sub-agents (AI agents, code assistants, or workflow bots) within the BIRDC ERP project. It ensures that all sub-agents are discoverable, maintainable, and compatible with both GitHub Copilot and Claude in VS Code.

## Folder Structure

```
skills/
└── custom-sub-agents/
	 ├── SKILL.md                ← This skill file (standards, checklist)
	 ├── references/
	 │   └── CUSTOM_SUB_AGENTS_GUIDE.md  ← Reference guide
	 └── [agent folders]/        ← One folder per sub-agent
		  ├── agent-name/
		  │   ├── agent.js|php|py|ts  ← Agent implementation
		  │   ├── README.md           ← Agent documentation
		  │   └── ...
```

## Requirements

1. **One Folder per Sub-Agent**
   - Each sub-agent must have its own folder under `skills/custom-sub-agents/`.
   - Folder name: `agent-name` (kebab-case, descriptive).

2. **Documentation**
   - Each agent folder must include a `README.md` describing:
     - Agent purpose and capabilities
     - Usage instructions
     - Configuration (if any)
     - Example prompts or API calls

3. **Entry Point**
   - The main agent file must be named `agent.js`, `agent.php`, `agent.py`, or `agent.ts` as appropriate.
   - The entry file must export or define a function/class named after the agent (PascalCase).

4. **Reference Guide**
   - All sub-agents must be listed in `references/CUSTOM_SUB_AGENTS_GUIDE.md` with a summary and link to their folder.

5. **Compatibility**
   - Agents must be compatible with both GitHub Copilot and Claude (Anthropic) in VS Code.
   - Use only supported APIs and avoid proprietary features unless polyfilled.

6. **Testing**
   - Each agent must include a test or usage example in its README.md.

7. **Versioning**
   - Update this SKILL.md and the reference guide when adding, removing, or changing agents.

## VS Code Integration & Enforcement Checklist

- [ ] Register agent folder in `references/CUSTOM_SUB_AGENTS_GUIDE.md`
- [ ] Ensure agent entry file and README.md exist
- [ ] Confirm agent is discoverable by Copilot/Claude (test in VS Code)
- [ ] Add usage example in README.md
- [ ] **Enable sub-agent support in VS Code settings:**
  - Add the following to your `.vscode/settings.json`:

    ```json
    {
      "chat.customAgentInSubagent.enabled": true
    }
    ```

  - This setting is required for both GitHub Copilot and Claude to use custom sub-agents in the latest VS Code Insiders build.

## Example Agent Folder

```
skills/custom-sub-agents/
└── smart-approver/
	 ├── agent.js
	 ├── README.md
```

## See Also

- [references/CUSTOM_SUB_AGENTS_GUIDE.md](references/CUSTOM_SUB_AGENTS_GUIDE.md)

## Last Updated

30 January 2026
