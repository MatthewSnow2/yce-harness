"""
API routes for the AI Agent Analytics Platform
This module will contain all API endpoints
"""
from typing import List
from fastapi import APIRouter, HTTPException
from database import get_db
from models import UserResponse, ItemResponse

router = APIRouter()

@router.get("/users", response_model=List[UserResponse])
async def get_users():
    """Get all users"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, email, created_at FROM users LIMIT 100")
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to fetch users")

@router.get("/items", response_model=List[ItemResponse])
async def get_items():
    """Get all items"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, user_id, title, description, status, created_at FROM items LIMIT 100")
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to fetch items")
