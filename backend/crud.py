from sqlalchemy.orm import Session
from models import Product, Cart, CartItem, Order
from schemas import ProductCreate, CartItemCreate, OrderCreate
from datetime import datetime
import json

# Product CRUD
def get_product(db: Session, product_id: int):
    return db.query(Product).filter(Product.id == product_id).first()

def get_products(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Product).filter(Product.is_active == True).offset(skip).limit(limit).all()

def create_product(db: Session, product: ProductCreate):
    db_product = Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

def update_product(db: Session, product_id: int, product: ProductCreate):
    db_product = get_product(db, product_id)
    if db_product:
        for key, value in product.dict().items():
            setattr(db_product, key, value)
        db.commit()
        db.refresh(db_product)
    return db_product

# Cart CRUD
def get_or_create_cart(db: Session, telegram_user_id: int):
    cart = db.query(Cart).filter(Cart.telegram_user_id == telegram_user_id).first()
    if not cart:
        cart = Cart(telegram_user_id=telegram_user_id)
        db.add(cart)
        db.commit()
        db.refresh(cart)
    return cart

def get_cart_items(db: Session, cart_id: int):
    return db.query(CartItem).filter(CartItem.cart_id == cart_id).all()

def add_to_cart(db: Session, cart_id: int, item: CartItemCreate):
    # Проверяем, есть ли уже такой товар в корзине
    existing_item = db.query(CartItem).filter(
        CartItem.cart_id == cart_id,
        CartItem.product_id == item.product_id
    ).first()
    
    if existing_item:
        existing_item.quantity += item.quantity
    else:
        db_item = CartItem(
            cart_id=cart_id,
            product_id=item.product_id,
            quantity=item.quantity
        )
        db.add(db_item)
    
    db.commit()
    return get_cart_items(db, cart_id)

def update_cart_item(db: Session, cart_id: int, item_id: int, quantity: int):
    item = db.query(CartItem).filter(
        CartItem.id == item_id,
        CartItem.cart_id == cart_id
    ).first()
    
    if item and quantity > 0:
        item.quantity = quantity
        db.commit()
        return item
    elif item and quantity <= 0:
        db.delete(item)
        db.commit()
        return None
    return None

def remove_cart_item(db: Session, cart_id: int, item_id: int):
    item = db.query(CartItem).filter(
        CartItem.id == item_id,
        CartItem.cart_id == cart_id
    ).first()
    
    if item:
        db.delete(item)
        db.commit()
        return True
    return False

def clear_cart(db: Session, cart_id: int):
    db.query(CartItem).filter(CartItem.cart_id == cart_id).delete()
    db.commit()
    return True

# Order CRUD
def create_order(db: Session, order: OrderCreate, telegram_user_id: int):
    # Создаем заказ
    db_order = Order(
        telegram_user_id=telegram_user_id,
        total_amount=order.total_amount,
        status="pending",
        items_data=json.dumps([item.dict() for item in order.items])
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    
    return db_order

def get_user_orders(db: Session, telegram_user_id: int, skip: int = 0, limit: int = 10):
    return db.query(Order).filter(Order.telegram_user_id == telegram_user_id).order_by(Order.created_at.desc()).offset(skip).limit(limit).all()