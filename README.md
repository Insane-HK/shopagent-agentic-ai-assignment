# ShopAgent

An AI-powered customer support agent for an online store. It uses **Amazon Nova Pro** on AWS Bedrock to answer questions about orders and products — deciding which tools to call and chaining them automatically.

## What it does

- Answers questions like "where is my order?" or "do you have cheaper headphones?"
- Calls the right tools (`get_order`, `search_products`, `get_product`) in the right order
- Maintains conversation context across multi-turn chats
- Returns friendly, human responses — not raw JSON

## Architecture

```
User → FastAPI → run_agent()
                     │
                     ▼
              Amazon Bedrock
              (Nova Pro via
               Converse API)
                     │
                     ▼
            Tool Selection
            ├── get_order()
            ├── search_products()
            └── get_product()
                     │
                     ▼
          Customer-friendly Response
```

## How to run locally

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
# open http://localhost:8000
```

Make sure your AWS credentials are configured with Bedrock access:
```bash
aws configure  # or use env vars: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION
```

## Deploy to AWS

```bash
python build.py   # packages Lambda zip
python deploy.py  # deploys via CloudFormation
```

## Sample questions and outputs

**Q: Where is my order ORD-1002?**
> Your order ORD-1002 (Sony WH-1000XM5 Headphones) is currently in transit and expected to arrive soon. Tracking number: 1Z999AA10123456785.

**Q: Do you have noise-cancelling headphones?**
> Yes! We have two options: the Sony WH-1000XM5 at $279.99 (industry-leading ANC, 30hr battery) and the JBL Tune 760NC at $79.99 (35hr battery, great budget pick).

**Q: Show me bags under $100**
> We have two bags under $100: the Leather Tote Bag at $89.99 and the Canvas Backpack Pro at $54.99. Would you like more details on either?

**Q: What happened to order ORD-9999?**
> I'm sorry, I wasn't able to find an order with ID ORD-9999. Please double-check the order number and try again.

**Q: Do you have a hoverboard?**
> Unfortunately, we don't carry hoverboards in our current catalog. Is there something else I can help you find?

## Running tests

```bash
python -m pytest tests/ -v
```

12 tests cover `get_order`, `get_product`, and `search_products` — valid, invalid, empty, and case-insensitive cases.

## Notes

- Model: `amazon.nova-pro-v1:0` (configurable via `BEDROCK_MODEL_ID` env var)
- Static files (HTML/CSS/JS) are served directly by the Lambda via FastAPI + Mangum
- No real database — all data is mocked in `agent/tools.py`
