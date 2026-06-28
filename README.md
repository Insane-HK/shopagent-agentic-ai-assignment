# 🛍️ ShopAgent — Agentic AI Customer Support

An AI-powered customer support chatbot built with **Amazon Bedrock (Nova Pro)**, **FastAPI**, and deployed as a **serverless application** on AWS Lambda. The agent autonomously decides which tools to call — looking up orders, searching products, and browsing categories — to deliver natural, human-friendly responses.

> **🔗 Live Demo:** [https://akkp7m0s45.execute-api.us-east-1.amazonaws.com/prod/](https://akkp7m0s45.execute-api.us-east-1.amazonaws.com/prod/)

---

## ✨ Features

| Feature | Details |
|---|---|
| **Agentic Tool Use** | The AI autonomously decides when to call `get_order`, `search_products`, `get_product`, or `get_categories` — no hardcoded if/else routing |
| **Multi-Turn Conversations** | Full conversation context is maintained across messages within a session |
| **Persistent Chat Threads** | All chat threads are saved in `localStorage` — refresh the page and your history stays intact |
| **Dark Mode** | One-click toggle with preference saved to `localStorage` |
| **Collapsible Sidebar** | Hamburger menu works on both desktop and mobile screens |
| **Tool Execution Trace** | Every response includes an expandable panel showing which tools were called, with their inputs and outputs |
| **System Prompt Guardrails** | The agent politely refuses off-topic questions (politics, general knowledge, etc.) and stays focused on customer support |
| **Serverless Deployment** | Runs on AWS Lambda + API Gateway — zero server management, pay-per-request |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend                             │
│         Vanilla HTML/CSS/JS  ·  Dark Mode  ·  localStorage  │
└──────────────────────────┬──────────────────────────────────┘
                           │  POST /ask
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Backend                           │
│             app/main.py  ·  Mangum (Lambda adapter)         │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                   Agent Loop (agent.py)                      │
│         Amazon Bedrock  ·  Nova Pro  ·  Converse API        │
│                                                             │
│    ┌──────────────────────────────────────────────────┐     │
│    │              Tool Selection                       │     │
│    │  ┌──────────────┐  ┌────────────────┐            │     │
│    │  │  get_order()  │  │search_products()│           │     │
│    │  └──────────────┘  └────────────────┘            │     │
│    │  ┌──────────────┐  ┌────────────────┐            │     │
│    │  │ get_product() │  │get_categories()│            │     │
│    │  └──────────────┘  └────────────────┘            │     │
│    └──────────────────────────────────────────────────┘     │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
               Customer-Friendly Response
```

---

## 📁 Project Structure

```
shopagent/
├── agent/
│   ├── agent.py           # Bedrock Converse API loop with tool orchestration
│   └── tools.py           # Mock database: orders, products, categories
├── app/
│   ├── main.py            # FastAPI routes (/ask, static files)
│   └── static/
│       ├── index.html     # Chat UI
│       ├── style.css      # Light/Dark mode theming
│       └── app.js         # Frontend logic, chat threads, localStorage
├── tests/
│   └── test_tools.py      # 12 unit tests for all tool functions
├── lambda_handler.py      # AWS Lambda entry point (Mangum wrapper)
├── template.yaml          # SAM/CloudFormation infrastructure-as-code
├── build.py               # Packages Lambda deployment zip
├── deploy.py              # Deploys to AWS via CloudFormation
├── requirements.txt       # Python dependencies
├── design_decisions.md    # Architectural rationale document
└── README.md
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- AWS CLI configured with Bedrock access (`aws configure`)

### Run Locally

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set your model (optional — defaults to Nova Pro)
set BEDROCK_MODEL_ID=amazon.nova-pro-v1:0

# 3. Start the dev server
uvicorn app.main:app --reload --port 8000

# 4. Open in browser
# http://localhost:8000
```

### Deploy to AWS

```bash
python build.py    # → Creates lambda_package.zip (20 MB)
python deploy.py   # → Deploys via CloudFormation to AWS Lambda + API Gateway
```

---

## 🧪 Running Tests

```bash
python -m pytest tests/ -v
```

**12 tests** covering all tool functions:

| Test | What it validates |
|---|---|
| `test_get_order_valid` | Returns correct order data for known IDs |
| `test_get_order_invalid` | Returns error for non-existent orders |
| `test_get_order_case_insensitive` | Handles `ord-1001` / `ORD-1001` |
| `test_search_products_*` | Keyword matching, empty results, multi-word queries |
| `test_get_product_valid` | Returns correct product by ID |
| `test_get_product_invalid` | Returns error for non-existent products |
| `test_get_categories` | Returns all 6 categories with counts and price ranges |

---

## 💬 Sample Interactions

**Q: Where is my order ORD-1002?**
> Your order ORD-1002 (Sony WH-1000XM5 Headphones) is currently in transit and expected to arrive soon. Tracking number: 1Z999AA10123456785.

**Q: Do you have noise-cancelling headphones?**
> Yes! We have two options: the Sony WH-1000XM5 at $279.99 (industry-leading ANC, 30hr battery) and the JBL Tune 760NC at $79.99 (35hr battery, great budget pick).

**Q: Show me bags under $100**
> We have two bags under $100: the Leather Tote Bag at $89.99 and the Canvas Backpack Pro at $54.99.

**Q: What categories do you have?**
> We carry products across 6 categories: Electronics (5 products), Accessories (3), Shoes (2), Apparel (2), Bags (2), and Home (1).

**Q: Who is the president?**
> I appreciate your curiosity, but I'm specifically designed to help with our store's products and orders. Is there anything I can help you with regarding your shopping experience?

---

## 🛠️ Tech Stack

| Layer | Technology | Why |
|---|---|---|
| **LLM** | Amazon Nova Pro (Bedrock) | Native tool-use support via Converse API, low latency, pay-per-token |
| **Backend** | FastAPI + Python | Async-first, auto-generates OpenAPI docs, modern Python standard |
| **Lambda Adapter** | Mangum | Bridges FastAPI ↔ Lambda with zero code changes |
| **Frontend** | Vanilla HTML/CSS/JS | Zero build step, instant load, full control over UX |
| **Infrastructure** | AWS SAM / CloudFormation | Reproducible, version-controlled infrastructure-as-code |
| **Hosting** | AWS Lambda + API Gateway | Serverless = $0 at idle, auto-scales to thousands of requests |

---

## 🔒 Design Decisions

1. **Custom agent loop over LangChain** — Direct Bedrock SDK calls give us full control over the tool-use cycle, error handling, and response cleaning without framework overhead.
2. **No external database** — Mock data in `tools.py` keeps the project self-contained and instantly deployable for evaluation.
3. **System prompt guardrails** — The agent is explicitly instructed to refuse off-topic queries, ensuring it stays within its customer-support role.
4. **localStorage for chat persistence** — Avoids the need for a session database while still providing a seamless multi-conversation experience.
5. **Cache-busted static assets** — `?v=N` query params on CSS/JS ensures browsers always load the latest version after deployments.

For the full rationale, see [`design_decisions.md`](design_decisions.md).

---

## 📄 License

This project was built as part of an academic assignment. All rights reserved.
