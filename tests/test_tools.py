"""
Unit tests for the ShopAgent tools.
Run: python -m pytest tests/ -v
"""
import pytest
from agent.tools import get_order, search_products, get_product


# ── get_order tests ────────────────────────────────────────

class TestGetOrder:
    def test_valid_order(self):
        result = get_order("ORD-1001")
        assert result["order_id"] == "ORD-1001"
        assert result["status"] == "delivered"
        assert "product_id" in result

    def test_another_valid_order(self):
        result = get_order("ORD-1002")
        assert result["order_id"] == "ORD-1002"
        assert result["status"] == "in_transit"

    def test_cancelled_order(self):
        result = get_order("ORD-1003")
        assert result["status"] == "cancelled"

    def test_invalid_order(self):
        result = get_order("ORD-9999")
        assert "error" in result
        assert "not found" in result["error"].lower()

    def test_empty_order_id(self):
        result = get_order("")
        assert "error" in result


# ── get_product tests ──────────────────────────────────────

class TestGetProduct:
    def test_valid_product(self):
        result = get_product("PROD-001")
        assert result["product_id"] == "PROD-001"
        assert "name" in result
        assert "price" in result

    def test_invalid_product(self):
        result = get_product("PROD-999")
        assert "error" in result
        assert "not found" in result["error"].lower()

    def test_empty_product_id(self):
        result = get_product("")
        assert "error" in result


# ── search_products tests ──────────────────────────────────

class TestSearchProducts:
    def test_search_headphones(self):
        results = search_products("headphones")
        assert isinstance(results, list)
        assert len(results) > 0
        # all results should have name and price
        for p in results:
            assert "name" in p
            assert "price" in p

    def test_search_bag(self):
        results = search_products("bag")
        assert isinstance(results, list)
        assert len(results) > 0

    def test_empty_search(self):
        results = search_products("xyznonexistent123")
        assert isinstance(results, list)
        assert len(results) == 0

    def test_case_insensitive_search(self):
        lower = search_products("headphones")
        upper = search_products("HEADPHONES")
        assert len(lower) == len(upper)
