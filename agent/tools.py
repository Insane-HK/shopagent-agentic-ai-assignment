from datetime import datetime, timedelta

# Helper to generate relative dates
def days_ago(d):
    return (datetime.now() - timedelta(days=d)).strftime("%Y-%m-%d")

def days_hence(d):
    return (datetime.now() + timedelta(days=d)).strftime("%Y-%m-%d")

# fake orders db
ORDERS = {
    "ORD-1001": {
        "order_id": "ORD-1001",
        "status": "delivered",
        "product_id": "PROD-001",
        "product_name": "Nike Air Max 270",
        "price": 129.99,
        "order_date": days_ago(7),
        "delivery_date": days_ago(4),
        "shipping_address": "42 Elm Street, Austin TX",
        "tracking": "1Z999AA10123456784",
    },
    "ORD-1002": {
        "order_id": "ORD-1002",
        "status": "in_transit",
        "product_id": "PROD-004",
        "product_name": "Sony WH-1000XM5 Headphones",
        "price": 279.99,
        "order_date": days_ago(2),
        "delivery_date": days_hence(3),
        "shipping_address": "17 Oak Lane, Seattle WA",
        "tracking": "1Z999AA10123456785",
    },
    "ORD-1003": {
        "order_id": "ORD-1003",
        "status": "cancelled",
        "product_id": "PROD-003",
        "product_name": "Leather Tote Bag",
        "price": 89.99,
        "order_date": days_ago(10),
        "delivery_date": None,
        "shipping_address": "9 Pine Ave, Chicago IL",
        "tracking": None,
        "cancel_reason": "Customer requested cancellation",
    },
    "ORD-1004": {
        "order_id": "ORD-1004",
        "status": "in_transit",
        "product_id": "PROD-007",
        "product_name": "Mechanical Gaming Keyboard",
        "price": 119.99,
        "order_date": days_ago(3),
        "delivery_date": days_hence(1),
        "shipping_address": "104 Maple Drive, Atlanta GA",
        "tracking": "1Z999AA10123456786",
    },
    "ORD-1005": {
        "order_id": "ORD-1005",
        "status": "processing",
        "product_id": "PROD-011",
        "product_name": "Classic Denim Jacket",
        "price": 69.99,
        "order_date": days_ago(1),
        "delivery_date": days_hence(5),
        "shipping_address": "555 Cedar Blvd, Boston MA",
        "tracking": None,
    },
    "ORD-1006": {
        "order_id": "ORD-1006",
        "status": "refunded",
        "product_id": "PROD-010",
        "product_name": "Wool Blend Winter Coat",
        "price": 189.99,
        "order_date": days_ago(15),
        "delivery_date": days_ago(12),
        "shipping_address": "77 Walnut Ave, Denver CO",
        "tracking": "1Z999AA10123456787",
        "refund_reason": "Item size too large, returned and refunded",
        "refund_date": days_ago(8),
    },
    "ORD-1007": {
        "order_id": "ORD-1007",
        "status": "delivered",
        "product_id": "PROD-014",
        "product_name": "Slim Leather Wallet",
        "price": 34.99,
        "order_date": days_ago(20),
        "delivery_date": days_ago(15),
        "shipping_address": "88 Birch St, Miami FL",
        "tracking": "1Z999AA10123456788",
    },
    "ORD-1008": {
        "order_id": "ORD-1008",
        "status": "payment_pending",
        "product_id": "PROD-015",
        "product_name": "Smart Fitness Watch",
        "price": 159.99,
        "order_date": days_ago(0),
        "delivery_date": None,
        "shipping_address": "12 High Rd, Portland OR",
        "tracking": None,
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
    {
        "product_id": "PROD-007",
        "name": "Mechanical Gaming Keyboard",
        "category": "electronics",
        "price": 119.99,
        "stock": 15,
        "description": "RGB backlit mechanical keyboard with tactile blue switches and custom keys.",
    },
    {
        "product_id": "PROD-008",
        "name": "Wireless Ergonomic Mouse",
        "category": "electronics",
        "price": 49.99,
        "stock": 25,
        "description": "Rechargeable vertical mouse designed to reduce wrist strain and fatigue.",
    },
    {
        "product_id": "PROD-009",
        "name": "Stainless Steel Water Bottle",
        "category": "accessories",
        "price": 24.99,
        "stock": 40,
        "description": "Double-walled vacuum insulated water bottle, keeps cold for 24h, hot for 12h.",
    },
    {
        "product_id": "PROD-010",
        "name": "Wool Blend Winter Coat",
        "category": "apparel",
        "price": 189.99,
        "stock": 6,
        "description": "Stylish and warm double-breasted wool coat for winter and cold weather.",
    },
    {
        "product_id": "PROD-011",
        "name": "Classic Denim Jacket",
        "category": "apparel",
        "price": 69.99,
        "stock": 18,
        "description": "Rugged cotton denim jacket with button closures, a timeless wardrobe staple.",
    },
    {
        "product_id": "PROD-012",
        "name": "Ceramic Coffee Travel Mug",
        "category": "home",
        "price": 19.99,
        "stock": 30,
        "description": "Spill-proof ceramic travel mug with protective silicone sleeve, microwave safe.",
    },
    {
        "product_id": "PROD-013",
        "name": "Polarized Sport Sunglasses",
        "category": "accessories",
        "price": 39.99,
        "stock": 22,
        "description": "UV400 protection polarized sunglasses, ideal for running, cycling, and hiking.",
    },
    {
        "product_id": "PROD-014",
        "name": "Slim Leather Wallet",
        "category": "accessories",
        "price": 34.99,
        "stock": 50,
        "description": "Minimalist RFID blocking leather wallet with multiple card slots and money clip.",
    },
    {
        "product_id": "PROD-015",
        "name": "Smart Fitness Watch",
        "category": "electronics",
        "price": 159.99,
        "stock": 10,
        "description": "Waterproof smartwatch with built-in GPS, heart rate monitor, and sleep tracking.",
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
