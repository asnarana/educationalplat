"""
ChromaDB Vector Database Module for RAG Pipeline

This module manages 6 separate vector stores:
- Grade 3 Math, Grade 3 Reading
- Grade 4 Math, Grade 4 Reading  
- Grade 5 Math, Grade 5 Reading

Each store contains embedded questions with full metadata for semantic similarity search.
Used to find similar questions when analyzing student mistake patterns.
"""

import chromadb
from chromadb.config import Settings
from typing import List, Dict, Optional, Any
import os
import hashlib

# Embedding function using sentence-transformers
VECTOR_DB_AVAILABLE = False
EMBEDDING_FUNCTION = None

try:
    from chromadb.utils import embedding_functions
    EMBEDDING_FUNCTION = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"  # Fast, lightweight model
    )
    VECTOR_DB_AVAILABLE = True
except ImportError:
    print("WARNING: sentence-transformers not installed. Vector DB will not work.")

# ChromaDB client (persistent storage)
CHROMA_PERSIST_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "chroma_db")

# Collection names for each grade/subject combination
COLLECTION_NAMES = {
    (3, "Math"): "grade3_math",
    (3, "Reading"): "grade3_reading",
    (4, "Math"): "grade4_math",
    (4, "Reading"): "grade4_reading",
    (5, "Math"): "grade5_math",
    (5, "Reading"): "grade5_reading",
}

# Global client instance
_chroma_client = None


def get_chroma_client():
    """Get or create the ChromaDB client."""
    global _chroma_client
    if _chroma_client is None:
        os.makedirs(CHROMA_PERSIST_DIR, exist_ok=True)
        _chroma_client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
        print(f"ChromaDB initialized at: {CHROMA_PERSIST_DIR}")
    return _chroma_client


def get_collection(grade_level: int, subject: str):
    """
    Get the ChromaDB collection for a specific grade/subject.
    
    Args:
        grade_level: 3, 4, or 5
        subject: "Math" or "Reading"
    
    Returns:
        ChromaDB collection
    """
    client = get_chroma_client()
    collection_name = COLLECTION_NAMES.get((grade_level, subject))
    
    if not collection_name:
        raise ValueError(f"Invalid grade_level/subject combination: {grade_level}/{subject}")
    
    if EMBEDDING_FUNCTION:
        return client.get_or_create_collection(
            name=collection_name,
            embedding_function=EMBEDDING_FUNCTION,
            metadata={"grade_level": grade_level, "subject": subject}
        )
    else:
        return client.get_or_create_collection(
            name=collection_name,
            metadata={"grade_level": grade_level, "subject": subject}
        )


def generate_question_id(question: Dict) -> str:
    """Generate a unique ID for a question based on its content and database ID."""
    # Use database ID if available (most reliable), otherwise use content hash
    db_id = question.get('id')
    if db_id:
        return f"q_{db_id}"
    
    # Fallback to content-based hash with more fields for uniqueness
    content = f"{question.get('prompt', '')}{question.get('correct_answer', '')}{question.get('topic', '')}{question.get('choices', '')}"
    return hashlib.md5(content.encode()).hexdigest()


def sync_questions_to_vector_db(questions: List[Dict], grade_level: int, subject: str) -> Dict[str, int]:
    """
    Sync questions from Oracle DB to the appropriate ChromaDB collection.
    
    Args:
        questions: List of question dicts with prompt, choices, correct_answer, etc.
        grade_level: 3, 4, or 5
        subject: "Math" or "Reading"
    
    Returns:
        Dict with counts: {"added": n, "updated": n, "total": n}
    """
    if not EMBEDDING_FUNCTION:
        return {"error": "Embedding function not available", "added": 0, "updated": 0, "total": 0}
    
    collection = get_collection(grade_level, subject)
    
    # Get existing IDs in collection
    existing = collection.get()
    existing_ids = set(existing.get("ids", []))
    
    documents = []
    metadatas = []
    ids = []
    
    for q in questions:
        # Create document text for embedding (question prompt + choices)
        choices_text = ""
        if q.get("choices"):
            choices_text = " | ".join(str(c) for c in q["choices"])
        
        doc_text = f"{q.get('prompt', '')} Choices: {choices_text}"
        
        # Create metadata
        metadata = {
            "question_id": str(q.get("id", "")),
            "topic": q.get("topic", ""),
            "prompt": q.get("prompt", "")[:1000],  # Truncate long prompts
            "choices": str(q.get("choices", [])),
            "correct_answer": str(q.get("correct_answer", "")),
            "explanation": q.get("explanation", "") or "",
            "grade_level": grade_level,
            "subject": subject,
            "difficulty": q.get("difficulty", 1),
            "weight": q.get("weight", 1.0),
        }
        
        # Generate unique ID
        q_id = generate_question_id(q)
        
        documents.append(doc_text)
        metadatas.append(metadata)
        ids.append(q_id)
    
    # Upsert all questions (add new, update existing)
    if documents:
        collection.upsert(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
    
    added = len(set(ids) - existing_ids)
    updated = len(set(ids) & existing_ids)
    
    return {
        "added": added,
        "updated": updated,
        "total": len(documents)
    }


def sync_all_from_oracle(db_session) -> Dict[str, Any]:
    """
    Sync all questions from Oracle DB to all 6 ChromaDB collections.
    
    Args:
        db_session: SQLAlchemy session
    
    Returns:
        Dict with sync results for each collection
    """
    from app.models import Question
    
    results = {}
    
    for (grade_level, subject), collection_name in COLLECTION_NAMES.items():
        # Determine subject filter based on topic keywords
        math_keywords = ['addition', 'subtraction', 'multiplication', 'division', 'fraction', 
                        'algebra', 'geometry', 'decimal', 'percentage', 'word problem',
                        'measurement', 'number operations', 'operations']
        reading_keywords = ['vocabulary', 'reading', 'comprehension', 'character', 'main idea', 
                          'text structure', 'inference', 'word meaning']
        
        # Get questions for this grade level
        questions_query = db_session.query(Question).filter(Question.grade_level == grade_level)
        all_questions = questions_query.all()
        
        # Filter by subject
        filtered_questions = []
        for q in all_questions:
            topic_lower = q.topic.lower() if q.topic else ""
            
            if subject == "Math":
                if any(kw in topic_lower for kw in math_keywords):
                    filtered_questions.append(q.to_dict(include_answer=True))
            else:  # Reading
                if any(kw in topic_lower for kw in reading_keywords):
                    filtered_questions.append(q.to_dict(include_answer=True))
        
        # Sync to vector DB
        if filtered_questions:
            sync_result = sync_questions_to_vector_db(filtered_questions, grade_level, subject)
            results[collection_name] = sync_result
        else:
            results[collection_name] = {"added": 0, "updated": 0, "total": 0, "note": "No questions found"}
    
    return results


def query_similar_questions(
    question_text: str,
    grade_level: int,
    subject: str,
    n_results: int = 5,
    topic_filter: Optional[str] = None
) -> List[Dict]:
    """
    Find similar questions using semantic search.
    
    Args:
        question_text: The question prompt to find similar questions for
        grade_level: 3, 4, or 5
        subject: "Math" or "Reading"
        n_results: Number of similar questions to return
        topic_filter: Optional topic to filter by
    
    Returns:
        List of similar questions with metadata
    """
    if not EMBEDDING_FUNCTION:
        return []
    
    try:
        collection = get_collection(grade_level, subject)
        
        # Build where filter if topic specified
        where_filter = None
        if topic_filter:
            where_filter = {"topic": topic_filter}
        
        # Query for similar questions
        results = collection.query(
            query_texts=[question_text],
            n_results=n_results,
            where=where_filter
        )
        
        # Format results
        similar_questions = []
        if results and results.get("metadatas") and results["metadatas"][0]:
            for i, metadata in enumerate(results["metadatas"][0]):
                distance = results["distances"][0][i] if results.get("distances") else None
                similar_questions.append({
                    **metadata,
                    "similarity_score": 1 - distance if distance else None  # Convert distance to similarity
                })
        
        return similar_questions
    
    except Exception as e:
        print(f"Error querying similar questions: {e}")
        return []


def get_similar_questions_for_missed(
    missed_questions: List[Dict],
    grade_level: int,
    subject: str,
    n_per_question: int = 3
) -> Dict[str, List[Dict]]:
    """
    For each missed question, find similar questions to analyze patterns.
    
    Args:
        missed_questions: List of questions the student got wrong
        grade_level: 3, 4, or 5
        subject: "Math" or "Reading"
        n_per_question: Number of similar questions per missed question
    
    Returns:
        Dict mapping topic -> list of similar questions
    """
    topic_similar_questions = {}
    
    for q in missed_questions:
        topic = q.get("topic", "Unknown")
        prompt = q.get("prompt", "")
        
        if not prompt:
            continue
        
        # Find similar questions
        similar = query_similar_questions(
            question_text=prompt,
            grade_level=grade_level,
            subject=subject,
            n_results=n_per_question,
            topic_filter=topic
        )
        
        if topic not in topic_similar_questions:
            topic_similar_questions[topic] = []
        
        topic_similar_questions[topic].extend(similar)
    
    # Deduplicate by question_id within each topic
    for topic in topic_similar_questions:
        seen = set()
        unique = []
        for q in topic_similar_questions[topic]:
            qid = q.get("question_id")
            if qid not in seen:
                seen.add(qid)
                unique.append(q)
        topic_similar_questions[topic] = unique[:5]  # Limit to 5 per topic
    
    return topic_similar_questions


def get_collection_stats() -> Dict[str, Dict]:
    """Get statistics for all collections."""
    stats = {}
    client = get_chroma_client()
    
    for (grade_level, subject), collection_name in COLLECTION_NAMES.items():
        try:
            collection = client.get_collection(name=collection_name)
            count = collection.count()
            stats[collection_name] = {
                "grade_level": grade_level,
                "subject": subject,
                "question_count": count
            }
        except Exception:
            stats[collection_name] = {
                "grade_level": grade_level,
                "subject": subject,
                "question_count": 0,
                "note": "Collection not created yet"
            }
    
    return stats


def clear_collection(grade_level: int, subject: str) -> bool:
    """Clear all documents from a collection."""
    try:
        client = get_chroma_client()
        collection_name = COLLECTION_NAMES.get((grade_level, subject))
        if collection_name:
            client.delete_collection(name=collection_name)
            return True
    except Exception as e:
        print(f"Error clearing collection: {e}")
    return False


def clear_all_collections() -> Dict[str, bool]:
    """Clear all collections."""
    results = {}
    for (grade_level, subject), collection_name in COLLECTION_NAMES.items():
        results[collection_name] = clear_collection(grade_level, subject)
    return results
