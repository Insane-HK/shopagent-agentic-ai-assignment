# Learning Plan — Building AI Agents & Deploying on AWS

This is a practical roadmap. No fluff. Each week has one clear goal, what to build, and where to learn it for free.

---

## Quick Checklist: Test This Project First

Before learning more, make sure this project actually works:

- [ ] **Step 1**: Go to AWS Console → Bedrock → Model Access → make sure **Claude Sonnet 4** is enabled
- [ ] **Step 2**: Open `http://localhost:8000` in browser
- [ ] **Step 3**: Ask: "Where is my order ORD-1002?"
- [ ] **Step 4**: Ask: "Do you have any headphones?"
- [ ] **Step 5**: Ask: "What happened to ORD-1003? Also show me bags"
- [ ] **Step 6**: Check the tool trace panel (click the "▶ 1 tool call" text under the response)

If it works → you've got a working AI agent. Now learn how it all fits together.

---

## Phase 1: Foundations (Week 1-2)

### Week 1 — Python + APIs basics

**Goal**: Understand how the code in this project works line by line.

| What to learn | Resource |
|---|---|
| Python dicts, lists, functions | [Python Tutorial](https://docs.python.org/3/tutorial/) — chapters 3-5 |
| HTTP basics (GET, POST, JSON) | [MDN HTTP Guide](https://developer.mozilla.org/en-US/docs/Web/HTTP/Overview) |
| FastAPI basics | [FastAPI Tutorial](https://fastapi.tiangolo.com/tutorial/) — first 4 sections |

**Mini-project**: Build a simple FastAPI app with 2-3 endpoints that return mock data (like a todo list API). Run it with uvicorn.

**Apply to this project**: Read through [app/main.py](file:///d:/Coding/CLGPL/metabiukl/app/main.py) and understand every line — the `/api/chat` POST endpoint, Pydantic models, error handling.

---

### Week 2 — AWS Basics + Boto3

**Goal**: Understand what Bedrock is and how your code talks to it.

| What to learn | Resource |
|---|---|
| AWS IAM (users, roles, policies) | [AWS IAM Getting Started](https://docs.aws.amazon.com/IAM/latest/UserGuide/getting-started.html) |
| Boto3 basics | [Boto3 Quickstart](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/quickstart.html) |
| Bedrock overview | [Bedrock User Guide](https://docs.aws.amazon.com/bedrock/latest/userguide/what-is-bedrock.html) |

**Mini-project**: Write a Python script that calls Bedrock with a simple prompt (no tools) and prints the response. Just `client.converse(modelId=..., messages=[...])`.

**Apply to this project**: Read [agent/agent.py](file:///d:/Coding/CLGPL/metabiukl/agent/agent.py) — focus on `_get_client()` and the `client.converse()` call on line 92.

---

## Phase 2: AI Agents Core Concepts (Week 3-4)

### Week 3 — LLM Tool Use (the key concept)

**Goal**: Understand how Claude decides to call tools and how you feed results back.

| What to learn | Resource |
|---|---|
| What is tool_use / function calling | [Anthropic Tool Use Docs](https://docs.anthropic.com/en/docs/build-with-claude/tool-use/overview) |
| Bedrock Converse API with tools | [Bedrock Converse API](https://docs.aws.amazon.com/bedrock/latest/userguide/conversation-inference-call.html) |
| JSON Schema basics (for tool definitions) | [JSON Schema Guide](https://json-schema.org/learn/getting-started-step-by-step) |

**Key insight**: The tool definitions in `TOOL_CONFIG` (lines 6-53 of agent.py) are like a menu. You describe what each tool does in plain English. Claude reads the menu, picks the right tool based on the user's question, and returns a structured JSON call. Your code executes it and sends the result back.

**Mini-project**: Add a 4th tool to this project — e.g. `check_refund_status(order_id)`. Write the mock function in tools.py, add the schema in agent.py, update TOOL_MAP. Test it.

---

### Week 4 — The Agent Loop (tool chaining)

**Goal**: Understand the while-loop pattern that makes agents "agentic".

```
User asks question
  → LLM picks a tool → you run it → send result back
  → LLM picks ANOTHER tool (or answers) → you run it → send back
  → LLM gives final answer
```

This is the loop in `run_agent()` (lines 91-146 of agent.py). The `for _ in range(6)` is the loop. Each iteration:
1. Call Bedrock
2. Check `stopReason` — if `"end_turn"`, we're done
3. If `"tool_use"`, extract tool calls, run them, send results back
4. Repeat

**Mini-project**: Add print statements to the loop so you can watch it step by step. Ask a question that requires 2 tools (e.g. "What product is in order ORD-1001 and is it still in stock?") — Claude will call `get_order` first, then `get_product`.

**Read**: [design_decisions.md](file:///d:/Coding/CLGPL/metabiukl/design_decisions.md) — I explained the chaining logic there.

---

## Phase 3: Deployment (Week 5-6)

### Week 5 — AWS SAM + Lambda

**Goal**: Deploy this app to AWS so it's live on the internet.

| What to learn | Resource |
|---|---|
| What is Lambda | [Lambda Getting Started](https://docs.aws.amazon.com/lambda/latest/dg/getting-started.html) |
| What is API Gateway | [HTTP API Docs](https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api.html) |
| SAM CLI tutorial | [SAM Getting Started](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-getting-started.html) |
| What Mangum does | [Mangum GitHub](https://github.com/jordanerber/mangum) |

**Deploy steps** (once you have SAM CLI installed):
```bash
sam build
sam deploy --guided   # first time, walks you through options
```

**Apply to this project**: Read [template.yaml](file:///d:/Coding/CLGPL/metabiukl/template.yaml) — it defines the Lambda function, API Gateway, and IAM permissions. Read [lambda_handler.py](file:///d:/Coding/CLGPL/metabiukl/lambda_handler.py) — Mangum wraps FastAPI so Lambda can run it.

---

### Week 6 — Monitoring + Debugging in Production

**Goal**: Know what to do when something breaks in AWS.

| What to learn | Resource |
|---|---|
| CloudWatch Logs | [CloudWatch Logs Guide](https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/WhatIsCloudWatchLogs.html) |
| Lambda debugging | [Lambda troubleshooting](https://docs.aws.amazon.com/lambda/latest/dg/troubleshooting.html) |
| API Gateway CORS issues | [CORS on API Gateway](https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-cors.html) |

**Mini-project**: Deploy the agent, send a few questions, then go to CloudWatch and find the `[tool]` print statements in the logs.

---

## Phase 4: Level Up (Week 7-8)

### Week 7 — Streaming Responses

**Goal**: Make the UI show the response word-by-word instead of waiting for the full answer.

| What to learn | Resource |
|---|---|
| Server-Sent Events (SSE) | [MDN SSE Guide](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events) |
| FastAPI StreamingResponse | [FastAPI Streaming](https://fastapi.tiangolo.com/advanced/custom-response/#streamingresponse) |
| Bedrock ConverseStream | [Bedrock Streaming](https://docs.aws.amazon.com/bedrock/latest/userguide/conversation-inference-stream.html) |

This is the single biggest UX improvement you can make.

---

### Week 8 — Multi-Agent Patterns

**Goal**: Understand how production AI systems work.

| What to learn | Resource |
|---|---|
| Agent patterns overview | [Anthropic Agent Patterns](https://docs.anthropic.com/en/docs/build-with-claude/agentic-systems) |
| ReAct pattern | [ReAct Paper](https://arxiv.org/abs/2210.03629) (read the intro + examples) |
| LangGraph / CrewAI (optional) | [LangGraph Docs](https://langchain-ai.github.io/langgraph/) |

**Key takeaway**: What you've built here IS a real agent. The loop + tools pattern is the foundation of every agent framework. LangChain, CrewAI, etc. just add abstractions on top.

---

## Daily Practice Suggestion

> [!TIP]
> Spend 30 min reading docs/code, then 30 min building. Don't watch YouTube tutorials passively — type the code yourself, break it, fix it.

---

## Key Files in This Project to Study

| File | What it teaches |
|---|---|
| [tools.py](file:///d:/Coding/CLGPL/metabiukl/agent/tools.py) | Mock data design, simple function APIs |
| [agent.py](file:///d:/Coding/CLGPL/metabiukl/agent/agent.py) | The core agent loop, Bedrock API, tool schemas |
| [app/main.py](file:///d:/Coding/CLGPL/metabiukl/app/main.py) | FastAPI endpoints, Pydantic models |
| [template.yaml](file:///d:/Coding/CLGPL/metabiukl/template.yaml) | SAM/CloudFormation, Lambda + API Gateway |
| [lambda_handler.py](file:///d:/Coding/CLGPL/metabiukl/lambda_handler.py) | ASGI→Lambda adapter pattern |
| [app.js](file:///d:/Coding/CLGPL/metabiukl/app/static/app.js) | Vanilla JS fetch, DOM manipulation |
