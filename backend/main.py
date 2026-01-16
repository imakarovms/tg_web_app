import os
from dotenv import load_dotenv
load_dotenv()  # Загружаем переменные окружения из .env файла
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session
from typing import List
import json

from database import SessionLocal, engine, Base
from models import Product, Cart, CartItem, Order
from schemas import Product, ProductCreate, Cart, CartItem, CartItemCreate, Order, OrderCreate, OrderItem
from crud import (
    get_product, get_products, create_product, update_product,
    get_or_create_cart, get_cart_items, add_to_cart, update_cart_item, 
    remove_cart_item, clear_cart, create_order, get_user_orders
)

# Создаем таблицы в базе данных
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Telegram Shop API", version="1.0.0")

# Определение origins для разных окружений
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

if ENVIRONMENT == "production":
    origins = [
        "https://todoapp-fbdc4.web.app",
        "https://todoapp-fbdc4.firebaseapp.com"
    ]
else:
    origins = ["*"]  # Разрешаем все для разработки


# Настройка CORS для работы с Telegram Mini Apps
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Dependency для получения сессии базы данных
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/health")
async def health_check():
    try:
        # Проверка подключения к PostgreSQL
        db = SessionLocal()
        # Используем text() для raw SQL запроса
        db.execute(text("SELECT 1"))
        db.close()
        return {
            "status": "healthy",
            "database": "connected",
            "database_url": "postgresql://shop_user_2024:***@localhost:5432/telegram_shop_db",
            "environment": ENVIRONMENT
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Database connection failed: {str(e)}"
        )

@app.get("/")
async def root():
    return {
        "message": "Telegram Shop API",
        "version": "1.0.0",
        "endpoints": {
            "products": "/api/products/",
            "cart": "/api/cart/{telegram_user_id}/",
            "checkout": "/api/cart/{telegram_user_id}/checkout/"
        }
    }

# Эндпоинты для товаров
@app.get("/api/products/", response_model=List[Product])
async def read_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    products = get_products(db, skip=skip, limit=limit)
    return products

@app.post("/api/products/", response_model=Product, status_code=status.HTTP_201_CREATED)
async def create_new_product(product: ProductCreate, db: Session = Depends(get_db)):
    return create_product(db=db, product=product)

@app.get("/api/products/{product_id}", response_model=Product)
async def read_product(product_id: int, db: Session = Depends(get_db)):
    db_product = get_product(db, product_id=product_id)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return db_product

@app.put("/api/products/{product_id}", response_model=Product)
async def update_product_endpoint(product_id: int, product: ProductCreate, db: Session = Depends(get_db)):
    db_product = update_product(db, product_id=product_id, product=product)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return db_product

# Эндпоинты для корзины
@app.get("/api/cart/{telegram_user_id}/", response_model=Cart)
async def get_user_cart(telegram_user_id: int, db: Session = Depends(get_db)):
    cart = get_or_create_cart(db, telegram_user_id=telegram_user_id)
    cart_items = get_cart_items(db, cart_id=cart.id)
    
    # Обогащаем ответ данными о товарах
    cart_response = Cart(
        id=cart.id,
        telegram_user_id=cart.telegram_user_id,
        items=[]
    )
    
    for item in cart_items:
        product = get_product(db, item.product_id)
        if product:
            cart_response.items.append(
                CartItem(
                    id=item.id,
                    product_id=item.product_id,
                    quantity=item.quantity,
                    product=product
                )
            )
    
    return cart_response

@app.post("/api/cart/{telegram_user_id}/add/", response_model=Cart)
async def add_item_to_cart(telegram_user_id: int, item: CartItemCreate, db: Session = Depends(get_db)):
    cart = get_or_create_cart(db, telegram_user_id=telegram_user_id)
    add_to_cart(db, cart_id=cart.id, item=item)
    
    # Возвращаем обновленную корзину
    return await get_user_cart(telegram_user_id, db)

@app.put("/api/cart/{telegram_user_id}/{item_id}/", response_model=CartItem)
async def update_cart_item_quantity(telegram_user_id: int, item_id: int, quantity: int, db: Session = Depends(get_db)):
    cart = get_or_create_cart(db, telegram_user_id=telegram_user_id)
    updated_item = update_cart_item(db, cart_id=cart.id, item_id=item_id, quantity=quantity)
    
    if updated_item is None:
        raise HTTPException(status_code=404, detail="Cart item not found or quantity <= 0")
    
    # Получаем обновленную информацию о товаре
    product = get_product(db, updated_item.product_id)
    return CartItem(
        id=updated_item.id,
        product_id=updated_item.product_id,
        quantity=updated_item.quantity,
        product=product
    )

@app.delete("/api/cart/{telegram_user_id}/{item_id}/")
async def remove_item_from_cart(telegram_user_id: int, item_id: int, db: Session = Depends(get_db)):
    cart = get_or_create_cart(db, telegram_user_id=telegram_user_id)
    success = remove_cart_item(db, cart_id=cart.id, item_id=item_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Cart item not found")
    
    return {"message": "Item removed successfully"}

@app.delete("/api/cart/{telegram_user_id}/clear/")
async def clear_user_cart(telegram_user_id: int, db: Session = Depends(get_db)):
    cart = get_or_create_cart(db, telegram_user_id=telegram_user_id)
    clear_cart(db, cart_id=cart.id)
    return {"message": "Cart cleared successfully"}

# Эндпоинты для оформления заказа
@app.post("/api/cart/{telegram_user_id}/checkout/", response_model=Order)
async def checkout_cart(telegram_user_id: int, order: OrderCreate, db: Session = Depends(get_db)):
    cart = get_or_create_cart(db, telegram_user_id=telegram_user_id)
    cart_items = get_cart_items(db, cart_id=cart.id)
    
    if not cart_items:
        raise HTTPException(status_code=400, detail="Cart is empty")
    
    # Создаем заказ
    db_order = create_order(db, order=order, telegram_user_id=telegram_user_id)
    
    # Очищаем корзину после оформления заказа
    clear_cart(db, cart_id=cart.id)
    
    return db_order

@app.get("/api/orders/{telegram_user_id}/", response_model=List[Order])
async def get_user_orders_endpoint(telegram_user_id: int, skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    orders = get_user_orders(db, telegram_user_id=telegram_user_id, skip=skip, limit=limit)
    
    # Преобразуем данные о товарах из JSON
    result = []
    for order in orders:
        items = json.loads(order.items_data) if order.items_data else []
        result.append({
            "id": order.id,
            "total_amount": order.total_amount,
            "status": order.status,
            "created_at": order.created_at,
            "items": items
        })
    
    return result

# Эндпоинт для инициализации тестовых данных (для разработки)
@app.post("/api/init-test-data/", status_code=status.HTTP_201_CREATED)
async def init_test_data(db: Session = Depends(get_db)):
    # Проверяем, есть ли уже товары
    if get_products(db, limit=1):
        raise HTTPException(status_code=400, detail="Test data already exists")
    
    # Создаем тестовые товары
    products = [
        {
            "name": "Умные часы",
            "description": "Современные умные часы с множеством функций",
            "price": 2990.0,
            "stock": 10
        },
        {
            "name": "Беспроводные наушники",
            "description": "Беспроводные наушники с шумоподавлением",
            "price": 4500.0,
            "stock": 15
        },
        {
            "name": "Портативная колонка",
            "description": "Водонепроницаемая портативная колонка",
            "price": 3200.0,
            "stock": 8
        },
        {
            "name": "Планшет",
            "description": "Современный планшет с большим экраном",
            "price": 24500.0,
            "stock": 5
        }
    ]
    
    for product_data in products:
        create_product(db, ProductCreate(**product_data))
    
    return {"message": "Test data created successfully", "products_count": len(products)}