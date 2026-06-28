import json
import boto3
from agent.tools import TOOL_MAP

# tool schemas for bedrock converse API
TOOL_CONFIG = {
    "tools": [
        {
            "toolSpec": {
                "name": "get_order",
                "description": "Fetch details about a customer order by order ID. Use when the user mentions an order number like ORD-1001.",
                "inputSchema": {
                    "json": {
                        "type": "object",
                        "properties": {
                            "order_id": {"type": "string", "description": "The order ID, e.g. ORD-1001"}
                        },
                        "required": ["order_id"]
                    }
                }
            }
        },
        {
            "toolSpec": {
                "name": "search_products",
                "description": "Search the product catalog by keyword. ONLY pass the core product type (e.g. 'shoes', 'headphones', 'bag'). Do NOT include price filters or constraints like 'under $100' in the query — the tool will break. Instead, search for the category, then filter the results yourself before answering.",
                "inputSchema": {
                    "json": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "Core product name or category (e.g. 'bag', 'shoes'). NO price constraints."}
                        },
                        "required": ["query"]
                    }
                }
            }
        },
        {
            "toolSpec": {
                "name": "get_product",
                "description": "Fetch full details for a specific product by product ID. Use when you already have a product_id.",
                "inputSchema": {
                    "json": {
                        "type": "object",
                        "properties": {
                            "product_id": {"type": "string", "description": "Product ID, e.g. PROD-001"}
                        },
                        "required": ["product_id"]
                    }
                }
            }
        }
    ]
}

SYSTEM_PROMPT = """You are a helpful customer support agent for an online store. 
You have access to tools to look up orders and products.
Always use the tools to get real data — never guess or make up info.
Keep your tone warm, friendly, and concise. Don't repeat tool output verbatim — summarize it naturally.
If something isn't found, say so honestly.
If the user mentions an order but doesn't give an order ID, ask them for it — don't guess.
If a query is vague, ask a short clarifying question before calling any tools.
Do not include any thinking tags or internal reasoning in your response. Just respond directly."""

import re
def _clean(text):
    # strip <thinking>...</thinking> tags that Nova sometimes leaks
    return re.sub(r'<thinking>.*?</thinking>\s*', '', text, flags=re.DOTALL).strip()

import os
MODEL_ID = os.environ.get("BEDROCK_MODEL_ID", "amazon.nova-pro-v1:0")


def _get_client():
    region = os.environ.get("AWS_REGION", "us-east-1")
    return boto3.client("bedrock-runtime", region_name=region)


def _run_tool(name, inp):
    fn = TOOL_MAP.get(name)
    if not fn:
        return {"error": f"unknown tool: {name}"}
    try:
        return fn(**inp)
    except Exception as e:
        return {"error": str(e)}


def run_agent_with_trace(question: str, history: list = None) -> dict:
    """
    Internal agent loop. Sends question to Bedrock Nova Pro,
    handles tool_use blocks, re-submits results, returns final answer
    plus a trace of tool calls for the UI.
    """
    client = _get_client()
    messages = []
    
    # Add previous conversation history if provided
    if history:
        for msg in history:
            messages.append({"role": msg["role"], "content": [{"text": msg["text"]}]})
            
    # Add current question
    messages.append({"role": "user", "content": [{"text": question}]})
    
    tool_trace = []  # collect tool calls for UI display

    for i in range(6):  # max 6 rounds, avoid infinite loops
        try:
            resp = client.converse(
                modelId=MODEL_ID,
                system=[{"text": SYSTEM_PROMPT}],
                messages=messages,
                toolConfig=TOOL_CONFIG,
            )
        except Exception as e:
            print(f"[error] bedrock call failed: {e}")
            return {"answer": f"Sorry, something went wrong talking to the AI model: {e}", "trace": tool_trace}

        msg = resp["output"]["message"]
        messages.append(msg)

        stop_reason = resp.get("stopReason", "")
        print(f"[loop {i}] stopReason={stop_reason}, blocks={len(msg['content'])}")

        if stop_reason == "end_turn":
            # done, pull the text out
            for block in msg["content"]:
                if "text" in block:
                    return {"answer": _clean(block["text"]), "trace": tool_trace}

        if stop_reason != "tool_use":
            # try to extract text anyway
            for block in msg["content"]:
                if "text" in block:
                    return {"answer": _clean(block["text"]), "trace": tool_trace}
            break

        # process tool calls
        tool_results = []
        for block in msg["content"]:
            if "toolUse" not in block:
                continue

            tool_call = block["toolUse"]
            tool_name = tool_call["name"]
            tool_input = tool_call["input"]
            tool_id = tool_call["toolUseId"]

            print(f"[tool] {tool_name}({tool_input})")  # debug
            result = _run_tool(tool_name, tool_input)
            print(f"[result] {result}")

            tool_trace.append({
                "tool": tool_name,
                "input": tool_input,
                "output": result,
            })

            # bedrock requires toolResult json to be a dict, not a list
            json_result = result if isinstance(result, dict) else {"results": result}

            tool_results.append({
                "toolUseId": tool_id,
                "content": [{"json": json_result}],
            })

        if not tool_results:
            break

        messages.append({
            "role": "user",
            "content": [{"toolResult": r} for r in tool_results]
        })

    return {"answer": "Sorry, I couldn't process that right now.", "trace": tool_trace}


def run_agent(question: str) -> str:
    """
    Required API: takes a question string, returns an answer string.
    Wraps run_agent_with_trace for a simpler interface.
    """
    result = run_agent_with_trace(question)
    return result["answer"]


if __name__ == "__main__":
    # quick smoke test
    test_questions = [
        "Where is my order ORD-1002?",
        "Do you have any headphones?",
        "Tell me about product PROD-001",
    ]
    for q in test_questions:
        print(f"\nQ: {q}")
        print(f"A: {run_agent(q)}")
