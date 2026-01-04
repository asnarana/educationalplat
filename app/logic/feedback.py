"""
Feedback generation logic using LLM for personalized study recommendations.
"""
import json
import os
from typing import Dict, List, Any
from pathlib import Path
from sqlalchemy.orm import Session
from app.models import Attempt, Quiz, Question
from app.logic.llm_provider import get_llm_provider, LLMProvider


def load_prompt_template() -> str:
    """Load the feedback prompt template."""
    template_path = Path(__file__).parent.parent / "prompts" / "feedback_prompt.txt"
    if not template_path.exists():
        raise FileNotFoundError(f"Prompt template not found: {template_path}")
    return template_path.read_text()


def format_missed_questions(attempt: Attempt, questions: List[Question]) -> str:
    """
    Format missed questions for the prompt.
    
    Args:
        attempt: Attempt object with answers
        questions: List of Question objects from the quiz
        
    Returns:
        Formatted string of missed questions
    """
    missed = []
    for question in questions:
        student_answer = attempt.answers.get(question.id, "")
        is_correct = str(student_answer).strip().lower() == str(question.correct_answer).strip().lower()
        
        if not is_correct:
            missed.append(
                f"Question: {question.prompt}\n"
                f"Your answer: {student_answer}\n"
                f"Correct answer: {question.correct_answer}\n"
                f"Explanation: {question.explanation or 'No explanation provided'}\n"
            )
    
    if not missed:
        return "No questions were missed. Great job!"
    
    return "\n---\n".join(missed)


def format_performance_summary(attempt: Attempt, all_topics: List[str]) -> str:
    """
    Format performance summary for the prompt.
    
    Args:
        attempt: Attempt object
        all_topics: List of all topics in the quiz
        
    Returns:
        Formatted performance summary
    """
    summary_parts = []
    
    for topic in all_topics:
        if topic in attempt.topic_metrics:
            metrics = attempt.topic_metrics[topic]
            score_pct = metrics["weighted_score"] * 100
            summary_parts.append(
                f"{topic}: {metrics['correct']}/{metrics['total']} correct "
                f"({score_pct:.1f}% weighted score)"
            )
    
    return "\n".join(summary_parts)


def format_weak_topics_section(attempt: Attempt) -> str:
    """Format weak topics section for the prompt."""
    if not attempt.weak_topics:
        return ""
    
    weak_details = []
    for topic in attempt.weak_topics:
        if topic in attempt.topic_metrics:
            metrics = attempt.topic_metrics[topic]
            score_pct = metrics["weighted_score"] * 100
            weak_details.append(
                f"- {topic}: {score_pct:.1f}% (below 80% mastery threshold)"
            )
    
    return f"WEAK TOPICS (need improvement):\n" + "\n".join(weak_details)


def format_strong_topics_section(attempt: Attempt, all_topics: List[str]) -> str:
    """Format strong topics section for the prompt."""
    strong_topics = [t for t in all_topics if t not in attempt.weak_topics]
    
    if not strong_topics:
        return ""
    
    strong_details = []
    for topic in strong_topics:
        if topic in attempt.topic_metrics:
            metrics = attempt.topic_metrics[topic]
            score_pct = metrics["weighted_score"] * 100
            strong_details.append(f"- {topic}: {score_pct:.1f}% (mastered)")
    
    return f"STRONG TOPICS (well done!):\n" + "\n".join(strong_details)


def generate_feedback_prompt(
    attempt: Attempt,
    quiz: Quiz,
    questions: List[Question]
) -> str:
    """
    Generate the full prompt for LLM feedback generation.
    
    Args:
        attempt: Attempt object
        quiz: Quiz object
        questions: List of Question objects
        
    Returns:
        Formatted prompt string
    """
    template = load_prompt_template()
    
    all_topics = list(set([q.topic for q in questions]))
    
    # Format sections
    performance_summary = format_performance_summary(attempt, all_topics)
    weak_topics_section = format_weak_topics_section(attempt)
    strong_topics_section = format_strong_topics_section(attempt, all_topics)
    missed_questions = format_missed_questions(attempt, questions)
    
    # Determine which topics to focus on
    focus_topics = attempt.weak_topics if attempt.weak_topics else all_topics
    focus_label = "weak topics" if attempt.weak_topics else "all topics (review plan)"
    
    # Build prompt
    overall_score_pct = f"{attempt.score_total * 100:.1f}%"
    prompt = template.format(
        grade_level=quiz.grade_level,
        overall_score=overall_score_pct,
        all_topics=", ".join(all_topics),
        performance_summary=performance_summary,
        weak_topics_section=weak_topics_section,
        strong_topics_section=strong_topics_section,
        missed_questions=missed_questions
    )
    
    return prompt


def parse_llm_response(response: str) -> Dict[str, Any]:
    """
    Parse LLM response and extract JSON.
    
    Args:
        response: Raw LLM response string
        
    Returns:
        Parsed JSON dictionary
    """
    # Try to extract JSON from response (may have markdown code blocks)
    response = response.strip()
    
    # Remove markdown code blocks if present
    if response.startswith("```json"):
        response = response[7:]
    elif response.startswith("```"):
        response = response[3:]
    
    if response.endswith("```"):
        response = response[:-3]
    
    response = response.strip()
    
    try:
        return json.loads(response)
    except json.JSONDecodeError as e:
        # If parsing fails, try to find JSON object in the response
        start_idx = response.find("{")
        end_idx = response.rfind("}")
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            try:
                return json.loads(response[start_idx:end_idx + 1])
            except json.JSONDecodeError:
                pass
        
        raise ValueError(f"Failed to parse LLM response as JSON: {str(e)}\nResponse: {response[:500]}")


def generate_feedback(
    attempt: Attempt,
    quiz: Quiz,
    questions: List[Question],
    llm_provider: LLMProvider = None
) -> Dict[str, Any]:
    """
    Generate personalized feedback using LLM.
    
    Args:
        attempt: Attempt object
        quiz: Quiz object
        questions: List of Question objects
        llm_provider: LLM provider instance (if None, uses get_llm_provider())
        
    Returns:
        Dictionary with feedback structure:
        {
            "summary": "...",
            "topics": {
                "TopicName": {
                    "actions": ["...", "...", "..."],
                    "practice": [
                        {"q": "...", "answer": "...", "explanation": "..."},
                        ...
                    ]
                }
            }
        }
    """
    if llm_provider is None:
        llm_provider = get_llm_provider()
    
    # Generate prompt
    prompt = generate_feedback_prompt(attempt, quiz, questions)
    
    # Get LLM response
    try:
        response_text = llm_provider.generate(prompt)
    except Exception as e:
        raise RuntimeError(f"Failed to generate feedback from LLM: {str(e)}")
    
    # Parse response
    feedback = parse_llm_response(response_text)
    
    # Validate structure
    if "summary" not in feedback:
        raise ValueError("LLM response missing 'summary' field")
    
    if "topics" not in feedback:
        raise ValueError("LLM response missing 'topics' field")
    
    # Ensure all required fields are present
    for topic_name, topic_data in feedback["topics"].items():
        if "actions" not in topic_data:
            topic_data["actions"] = []
        if "practice" not in topic_data:
            topic_data["practice"] = []
        
        # Ensure actions is a list of 3
        if len(topic_data["actions"]) < 3:
            topic_data["actions"].extend([""] * (3 - len(topic_data["actions"])))
        topic_data["actions"] = topic_data["actions"][:3]
        
        # Ensure practice is a list of 2
        if len(topic_data["practice"]) < 2:
            topic_data["practice"].extend([{}] * (2 - len(topic_data["practice"])))
        topic_data["practice"] = topic_data["practice"][:2]
    
    return feedback

