# Design Decisions

## Why tool_use instead of prompt-only?

The obvious alternative is to put all the order/product data in the system prompt and let the model answer directly. That works for small datasets but breaks fast -- you'd hit context limits, the model hallucinates details it half-remembers, and there's no way to add real DB calls later without rewriting everything.

With `tool_use`, the model decides what to look up based on the question. It only fetches what it needs. The logic is clean: tools = data layer, model = reasoning layer. Swapping mock tools for real DB calls later is just changing the function body.

## How tool chaining works

The agent runs a loop (max 6 rounds):
1. Send user question + tool definitions to Bedrock `converse`
2. If `stopReason == "tool_use"`, extract tool calls from the response
3. Execute each tool, collect results
4. Send results back as `toolResult` blocks in a new user message
5. Repeat until `stopReason == "end_turn"` or we hit the round limit

The model handles the chaining logic itself -- it'll call `get_order` first to get a product_id, then call `get_product` with that ID without being explicitly told to. That's the useful part.

## Error handling

Three places things can go wrong:

- **Tool not found**: if the model hallucinates a tool name, `TOOL_MAP.get()` returns None and we return `{"error": "unknown tool"}` -- safe fallback
- **Order/product not found**: tools return `{"error": "..."}` dicts, not exceptions. The model sees this and tells the user naturally ("I couldn't find that order")
- **Bedrock failure**: the `/api/chat` endpoint catches any exception from `run_agent` and returns a 500 with the message -- the UI shows a red error card

We don't re-raise tool errors as HTTP 500s because the agent can recover from them. A missing order isn't a server error, it's a valid outcome.

## FastAPI over Flask

FastAPI gives async support out of the box (useful if we ever stream Bedrock responses), auto-generated docs at `/api/docs`, and Pydantic models for request/response validation. For a project this small the difference is minor, but the dev experience is nicer.

## Mangum for Lambda

Mangum is an ASGI adapter that maps API Gateway events to WSGI-style requests. One line: `handler = Mangum(app)`. The same FastAPI app runs locally with `uvicorn` and on Lambda unchanged -- no separate Lambda-specific code.

## What I'd improve with more time

- **Streaming responses**: Bedrock supports streaming; FastAPI supports SSE. Combining them would make the UI feel much faster for long answers
- **Real database**: Replace the dicts in tools.py with DynamoDB calls -- the interface is already the same
- **Auth**: API Gateway + Cognito or a simple API key header
- **Better trace UI**: The tool trace panel is collapsed by default; could expand it with step-by-step animations
- **Persistent chat history**: Currently chat context lives in the browser session only; a real app would store it server-side per user
