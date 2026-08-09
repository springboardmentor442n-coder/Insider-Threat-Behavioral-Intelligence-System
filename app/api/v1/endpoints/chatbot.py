"""
AI Chatbot API Endpoints
========================
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import require_analyst
from app.services.chatbot import handle_chat_query

router = APIRouter(prefix="/chatbot", tags=["AI Security Assistant"])


class ChatQuery(BaseModel):
    query: str


@router.post("/query")
def chat_query(payload: ChatQuery, db: Session = Depends(get_db), _=Depends(require_analyst)):
    """
    Send a natural language question to the SOC Security Assistant chatbot.
    """
    if not payload.query:
        raise HTTPException(400, "Query cannot be empty")
    try:
        response = handle_chat_query(db, payload.query)
        return {"query": payload.query, "response": response}
    except Exception as e:
        raise HTTPException(500, f"Chat assistant failed: {str(e)}")
