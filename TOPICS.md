# GitHub Topics

Suggested repository topics for discovery (apply via GitHub UI or API):

```text
ai-agents
langgraph
human-in-the-loop
multi-agent-systems
agent-orchestration
llm-ops
developer-tools
fastapi
react
mcp
agentic-workflow
control-plane
claude-code
pipeline
sortie-deck
```

Apply with GitHub CLI (when available):

```bash
gh repo edit lpliu-art/sortie-deck-todos --add-topic ai-agents,langgraph,human-in-the-loop,multi-agent-systems,agent-orchestration,llm-ops,developer-tools,fastapi,react,mcp,agentic-workflow,control-plane,claude-code,pipeline,sortie-deck
```

Or REST:

```bash
curl -X PUT \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer $GITHUB_TOKEN" \
  https://api.github.com/repos/lpliu-art/sortie-deck-todos/topics \
  -d '{"names":["ai-agents","langgraph","human-in-the-loop","multi-agent-systems","agent-orchestration","llm-ops","developer-tools","fastapi","react","mcp","agentic-workflow","control-plane","claude-code","pipeline","sortie-deck"]}'
```
