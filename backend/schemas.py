from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    stock: int = 0
    is_active: bool = True

class ProductCreate(ProductBase):
    pass

class Product(ProductBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class CartItemBase(BaseModel):
    product_id: int
    quantity: int = 1

class CartItemCreate(CartItemBase):
    pass

class CartItem(CartItemBase):
    id: int
    product: Product
    
    class Config:
        from_attributes = True

class CartBase(BaseModel):
    telegram_user_id: int

class CartCreate(CartBase):
    pass

class Cart(CartBase):
    id: int
    items: List[CartItem] = []
    
    class Config:
        from_attributes = True

class OrderItem(BaseModel):
    id: int
    name: str
    price: float
    quantity: int

class OrderBase(BaseModel):
    total_amount: float
    items: List[OrderItem]

class OrderCreate(OrderBase):
    pass

class Order(OrderBase):
    id: int
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True