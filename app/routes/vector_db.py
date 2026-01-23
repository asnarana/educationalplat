"""
Routes for Vector Database management.

Provides endpoints to sync questions from Oracle DB to ChromaDB
and check vector store statistics.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any
from app.db import get_db

router = APIRouter(prefix="/vector-db", tags=["vector-db"])


@router.post("/sync", response_model=Dict[str, Any])
def sync_vector_db(db: Session = Depends(get_db)):
    """
    Sync all questions from Oracle DB to ChromaDB vector stores.
    
    Creates/updates 6 vector stores:
    - grade3_math, grade3_reading
    - grade4_math, grade4_reading
    - grade5_math, grade5_reading
    
    Returns:
        Dict with sync results for each collection
    """
    try:
        from app.logic.vector_db import sync_all_from_oracle
        results = sync_all_from_oracle(db)
        return {
            "status": "success",
            "message": "Vector database synced successfully",
            "collections": results
        }
    except ImportError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Vector DB module not available. Make sure chromadb and sentence-transformers are installed: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to sync vector database: {str(e)}"
        )


@router.get("/stats", response_model=Dict[str, Any])
def get_vector_db_stats():
    """
    Get statistics for all ChromaDB collections.
    
    Returns:
        Dict with stats for each collection (question count, etc.)
    """
    try:
        from app.logic.vector_db import get_collection_stats
        stats = get_collection_stats()
        return {
            "status": "success",
            "collections": stats
        }
    except ImportError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Vector DB module not available: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get vector database stats: {str(e)}"
        )


@router.delete("/clear", response_model=Dict[str, Any])
def clear_vector_db():
    """
    Clear all ChromaDB collections. Use with caution!
    
    Returns:
        Dict with clear results for each collection
    """
    try:
        from app.logic.vector_db import clear_all_collections
        results = clear_all_collections()
        return {
            "status": "success",
            "message": "Vector database cleared",
            "collections": results
        }
    except ImportError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Vector DB module not available: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to clear vector database: {str(e)}"
        )


@router.post("/query", response_model=Dict[str, Any])
def query_similar_questions(
    question_text: str,
    grade_level: int,
    subject: str,
    n_results: int = 5,
    topic: str = None
):
    """
    Query for similar questions using semantic search.
    
    Args:
        question_text: The question text to search for
        grade_level: 3, 4, or 5
        subject: "Math" or "Reading"
        n_results: Number of results to return (default 5)
        topic: Optional topic filter
        
    Returns:
        List of similar questions with metadata
    """
    try:
        from app.logic.vector_db import query_similar_questions as query_fn
        
        results = query_fn(
            question_text=question_text,
            grade_level=grade_level,
            subject=subject,
            n_results=n_results,
            topic_filter=topic
        )
        
        return {
            "status": "success",
            "query": question_text[:100] + "..." if len(question_text) > 100 else question_text,
            "grade_level": grade_level,
            "subject": subject,
            "n_results": len(results),
            "results": results
        }
    except ImportError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Vector DB module not available: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to query vector database: {str(e)}"
        )
