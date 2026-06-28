from datetime import datetime, timedelta

# fake orders db
ORDERS = {
    "ORD-1001": {
        "order_id": "ORD-1001",
        "status": "delivered",
        "product_id": "PROD-001",
        "product_name": "Nike Air Max 270",
        "price": 129.99,
        "delivery_date": "2025-06-20",
        "shipping_address": "42 Elm Street, Austin TX",
        "tracking": "1Z999AA10123456784",
    },
    "ORD-1002": {
        "order_id": "ORD-1002",
        "status": "in_transit",
        "product_id": "PROD-004",
        "product_name": "Sony WH-1000XM5 Headphones",
        "price": 279.99,
        "delivery_date": (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d"),
        "shipping_address": "17 Oak Lane, Seattle WA",
        "tracking": "1Z999AA10123456785",
    },
    "ORD-1003": {
        "order_id": "ORD-1003",
        "status": "cancelled",
        "product_id": "PROD-003",
        "product_name": "Leather Tote Bag",
        "price": 89.99,
        "delivery_date": None,
        "shipping_address": "9 Pine Ave, Chicago IL",
        "tracking": None,
        "cancel_reason": "Customer requested cancellation",
    },
}

# fake products catalog
PRODUCTS = [
    {
        "product_id": "PROD-001",
        "name": "Nike Air Max 270",
        "category": "shoes",
        "price": 129.99,
        "stock": 14,
        "description": "Lightweight running shoe with Max Air unit, great for daily wear.",
    },
    {
        "product_id": "PROD-002",
        "name": "Adidas Ultraboost 22",
        "category": "shoes",
        "price": 149.99,
        "stock": 8,
        "description": "Premium running shoe with Boost midsole, responsive and comfortable.",
    },
    {
        "product_id": "PROD-003",
        "name": "Leather Tote Bag",
        "category": "bags",
        "price": 89.99,
        "stock": 5,
        "description": "Handcrafted full-grain leather tote, fits laptop up to 15 inches.",
    },
    {
        "product_id": "PROD-004",
        "name": "Sony WH-1000XM5 Headphones",
        "category": "electronics",
        "price": 279.99,
        "stock": 3,
        "description": "Industry-leading noise cancellation, 30hr battery, multipoint connect.",
    },
    {
        "product_id": "PROD-005",
        "name": "JBL Tune 760NC",
        "category": "electronics",
        "price": 79.99,
        "stock": 20,
        "description": "Foldable wireless headphones with active noise cancelling, 35hr battery.",
    },
    {
        "product_id": "PROD-006",
        "name": "Canvas Backpack Pro",
        "category": "bags",
        "price": 54.99,
        "stock": 12,
        "description": "Water-resistant canvas backpack with USB charging port, 30L capacity.",
    },
]


def get_order(order_id: str) -> dict:
    order_id = order_id.strip().upper()
    res = ORDERS.get(order_id)
    if not res:
        return {"error": "Order not found"}
    return res


def search_products(query: str) -> list:
    import re
    # Split query into words, ignoring hyphens/punctuation
    words = [w for w in re.split(r'[^a-z0-9]+', query.lower()) if w]
    if not words:
        return []

    out = []
    for p in PRODUCTS:
        # Combine searchable fields
        text = f"{p['name']} {p['category']} {p['description']}".lower()
        
        # Check if ALL words from the query exist in the text
        if all(w in text for w in words):
            out.append(p)

    return out


def get_product(product_id: str) -> dict:
    pid = product_id.strip().upper()
    for p in PRODUCTS:
        if p["product_id"] == pid:
            return p
    return {"error": "Product not found"}


# map tool names → functions
TOOL_MAP = {
    "get_order": get_order,
    "search_products": search_products,
    "get_product": get_product,
}
