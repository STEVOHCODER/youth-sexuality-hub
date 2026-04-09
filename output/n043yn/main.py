# filename: main.py
import sqlite3
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn
from typing import List

app = FastAPI()

# Database Initialization
def init_db():
    conn = sqlite3.connect("ecommerce.db")
    cursor = conn.cursor()
    # Create products table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            description TEXT,
            price REAL,
            image_url TEXT
        )
    ''')
    # Create orders table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            total REAL
        )
    ''')
    
    # Seed data if the products table is empty
    cursor.execute("SELECT COUNT(*) FROM products")
    if cursor.fetchone()[0] == 0:
        dummy_products = [
            ("Premium Wireless Headphones", "Noise-cancelling over-ear headphones with 30-hour battery life.", 299.99, "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500&q=80"),
            ("Minimalist Analog Watch", "Elegant analog watch with a premium leather strap.", 120.00, "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=500&q=80"),
            ("Smart Home Hub", "Control your entire home with your voice and this central hub.", 89.50, "https://images.unsplash.com/photo-1558089687-f282ffcbc126?w=500&q=80"),
            ("Ergonomic Keyboard", "Split design mechanical keyboard for comfortable typing.", 150.00, "https://images.unsplash.com/photo-1595225476474-87563907a212?w=500&q=80"),
            ("Leather Bifold Wallet", "Slim bifold wallet with RFID blocking technology.", 45.00, "https://images.unsplash.com/photo-1627123424574-724758594e93?w=500&q=80"),
            ("High-Capacity Power Bank", "10000mAh portable charger with ultra-fast charging.", 35.99, "https://images.unsplash.com/photo-1609091839311-d5365f9ff1c5?w=500&q=80")
        ]
        cursor.executemany("INSERT INTO products (name, description, price, image_url) VALUES (?, ?, ?, ?)", dummy_products)
    
    conn.commit()
    conn.close()

init_db()

# Pydantic Models for API requests
class CartItem(BaseModel):
    product_id: int
    quantity: int

class CheckoutRequest(BaseModel):
    items: List[CartItem]
    total: float

@app.get("/api/products")
def get_products():
    conn = sqlite3.connect("ecommerce.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products")
    products = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return products

@app.post("/api/checkout")
def checkout(request: CheckoutRequest):
    if not request.items:
        return {"error": "Cart is empty"}
        
    conn = sqlite3.connect("ecommerce.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO orders (total) VALUES (?)", (request.total,))
    order_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return {"message": "Order placed successfully", "order_id": order_id}

# Mount static files (this serves index.html at the root)
app.mount("/", StaticFiles(directory=".", html=True), name="static")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
