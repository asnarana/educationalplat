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
        Formatted string of missed questions (truncated for long passages)
    """
    missed = []
    for question in questions:
        student_answer = attempt.answers.get(question.id, "")
        is_correct = str(student_answer).strip().lower() == str(question.correct_answer).strip().lower()
        
        if not is_correct:
            # Truncate very long prompts (reading passages can be very long)
            prompt_text = question.prompt
            if len(prompt_text) > 1000:
                # For reading questions, try to extract just the question part
                if "Read" in prompt_text or "passage" in prompt_text.lower():
                    # Find the actual question (usually after the passage)
                    parts = prompt_text.split("\n\n")
                    if len(parts) > 1:
                        # Use the last part as the question
                        prompt_text = parts[-1][:500] + "..."
                    else:
                        prompt_text = prompt_text[:500] + "..."
                else:
                    prompt_text = prompt_text[:500] + "..."
            
            missed.append(
                f"Question: {prompt_text}\n"
                f"Your answer: {student_answer}\n"
                f"Correct answer: {question.correct_answer}\n"
                f"Explanation: {question.explanation or 'No explanation provided'}\n"
            )
    
    if not missed:
        return "No questions were missed. Great job!"
    
    # Limit to first 5 missed questions to avoid extremely long prompts
    if len(missed) > 5:
        # Count how many more questions were missed
        total_missed = len(missed)
        missed = missed[:5]
        missed.append(f"\n... and {total_missed - 5} more questions were missed.")
    
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
    
    Handles incomplete JSON by attempting to fix common truncation issues.
    Falls back to building structure from prose if JSON parsing fails.
    
    Args:
        response: Raw LLM response string
        
    Returns:
        Parsed JSON dictionary
    """
    import re
    
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
    
    # Try parsing the response as-is
    try:
        return json.loads(response)
    except json.JSONDecodeError:
        pass
    
    # If parsing fails, try to find JSON object in the response
    start_idx = response.find("{")
    if start_idx != -1:
        # Try to find the end of the JSON object
        end_idx = response.rfind("}")
        if end_idx != -1 and end_idx > start_idx:
            try:
                return json.loads(response[start_idx:end_idx + 1])
            except json.JSONDecodeError:
                pass
            
        # If still failing, try to fix incomplete JSON by closing brackets/braces
        try:
            fixed_response = _fix_incomplete_json(response[start_idx:])
            return json.loads(fixed_response)
        except (json.JSONDecodeError, ValueError):
            pass
    
    # If no JSON found or parsing failed, try to build structure from prose
    print(f"[DEBUG] JSON parsing failed, attempting to extract from prose response")
    return _parse_prose_response(response)


def _parse_prose_response(response: str) -> Dict[str, Any]:
    """
    Parse a prose/markdown response and extract feedback structure.
    
    This is a fallback when the LLM doesn't return valid JSON.
    
    Args:
        response: Prose response from LLM
        
    Returns:
        Dictionary with feedback structure
    """
    import re
    
    result = {
        "summary": "",
        "topics": {}
    }
    
    # Try to extract summary - look for first paragraph or sentence
    lines = response.split('\n')
    for line in lines:
        line = line.strip()
        if line and not line.startswith('*') and not line.startswith('-') and not line.startswith('#'):
            # Skip JSON-looking content
            if not line.startswith('{') and not line.startswith('"'):
                # Found a prose line - use as summary
                # Clean up any partial JSON
                if '"summary"' in line:
                    match = re.search(r'"summary"[:\s]*"([^"]*)"?', line)
                    if match:
                        result["summary"] = match.group(1)
                        break
                else:
                    result["summary"] = line[:300]  # Limit summary length
                    break
    
    if not result["summary"]:
        result["summary"] = "Review the weak topics identified below and practice with the recommended questions."
    
    # Try to extract topics from the prose
    # Look for topic headers followed by bullet points
    topic_patterns = [
        r'(?:^|\n)([A-Z][^:\n]+?):\s*\n\s*[\*\-]',  # "Topic Name:\n* bullet"
        r'(?:^|\n)#+\s*([A-Z][^\n]+?)\s*\n',  # "## Topic Name"
        r'"([^"]+)":\s*\{',  # JSON-style topic names
    ]
    
    found_topics = set()
    for pattern in topic_patterns:
        matches = re.findall(pattern, response, re.MULTILINE)
        for match in matches:
            topic = match.strip()
            # Filter out non-topic strings
            if topic and len(topic) > 3 and len(topic) < 50:
                if not any(skip in topic.lower() for skip in ['summary', 'json', 'response', 'here', 'following']):
                    found_topics.add(topic)
    
    # Extract actions (bullet points)
    action_pattern = r'[\*\-]\s*([^*\-\n][^\n]+)'
    all_actions = re.findall(action_pattern, response)
    
    # Distribute actions across topics (or use defaults)
    action_idx = 0
    for topic in found_topics:
        topic_actions = []
        # Try to get 3 actions for this topic
        while len(topic_actions) < 3 and action_idx < len(all_actions):
            action = all_actions[action_idx].strip()
            # Only use if it looks like an action (not a question)
            if action and not action.endswith('?') and len(action) > 10:
                topic_actions.append(action[:200])  # Limit length
            action_idx += 1
        
        result["topics"][topic] = {
            "actions": topic_actions,
            "practice": []
        }
    
    # If no topics found, return minimal structure
    if not result["topics"]:
        result["topics"]["General Review"] = {
            "actions": ["Review the material from your lessons"],
            "practice": []
        }
    
    print(f"[DEBUG] Extracted {len(result['topics'])} topics from prose response")
    return result


def _fix_incomplete_json(json_str: str) -> str:
    """
    Attempt to fix incomplete JSON by closing brackets and braces.
    
    Args:
        json_str: Potentially incomplete JSON string
        
    Returns:
        Fixed JSON string
    """
    # Count open/close brackets and braces
    open_braces = json_str.count("{")
    close_braces = json_str.count("}")
    open_brackets = json_str.count("[")
    close_brackets = json_str.count("]")
    
    # Add missing closing braces
    missing_braces = open_braces - close_braces
    if missing_braces > 0:
        # Check if we're in the middle of a string (don't close if we are)
        if not json_str.rstrip().endswith('"'):
            json_str += "}" * missing_braces
    
    # Add missing closing brackets
    missing_brackets = open_brackets - close_brackets
    if missing_brackets > 0:
        # Check if we're in the middle of a string
        if not json_str.rstrip().endswith('"'):
            json_str += "]" * missing_brackets
    
    return json_str


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
    
    # Debug: Log prompt (first 500 chars) to help diagnose issues
    print(f"[DEBUG] Feedback prompt preview (first 500 chars):\n{prompt[:500]}...")
    
    # Get LLM response
    try:
        response_text = llm_provider.generate(prompt)
        print(f"[DEBUG] LLM response preview (first 500 chars):\n{response_text[:500]}...")
    except Exception as e:
        raise RuntimeError(f"Failed to generate feedback from LLM: {str(e)}")
    
    # Parse response
    try:
        feedback = parse_llm_response(response_text)
    except Exception as e:
        print(f"[ERROR] Failed to parse LLM response: {e}")
        print(f"[ERROR] Full response: {response_text}")
        raise ValueError(f"LLM returned invalid response format: {str(e)}")
    
    # Validate structure
    if "summary" not in feedback:
        raise ValueError("LLM response missing 'summary' field")
    
    if "topics" not in feedback:
        raise ValueError("LLM response missing 'topics' field")
    
    # Get actual topics from the attempt
    actual_topics = attempt.weak_topics if attempt.weak_topics else list(set([q.topic for q in questions]))
    
    # Validate that feedback topics match actual topics (case-insensitive)
    feedback_topics = list(feedback["topics"].keys())
    actual_topics_lower = [t.lower() for t in actual_topics]
    
    # Filter out topics that don't match actual topics
    valid_topics = {}
    for topic_name, topic_data in feedback["topics"].items():
        # Check if topic matches (case-insensitive)
        topic_matches = any(topic_name.lower() == actual.lower() for actual in actual_topics)
        if topic_matches:
            valid_topics[topic_name] = topic_data
        else:
            # Try to find a matching actual topic
            matching_actual = None
            for actual in actual_topics:
                if actual.lower() in topic_name.lower() or topic_name.lower() in actual.lower():
                    matching_actual = actual
                    break
            
            if matching_actual:
                valid_topics[matching_actual] = topic_data
            else:
                # Topic doesn't match - skip it
                print(f"Warning: LLM generated topic '{topic_name}' that doesn't match actual topics: {actual_topics}")
    
    # Add missing topics with default structure
    for actual_topic in actual_topics:
        if actual_topic not in valid_topics:
            valid_topics[actual_topic] = {
                "actions": [],
                "practice": []
            }
    
    # Update feedback with validated topics
    feedback["topics"] = valid_topics
    
    # Ensure all required fields are present and properly filled
    for topic_name, topic_data in feedback["topics"].items():
        if "actions" not in topic_data:
            topic_data["actions"] = []
        if "practice" not in topic_data:
            topic_data["practice"] = []
        
        # Filter out empty actions and single-word actions (they should be full sentences)
        def is_valid_action(a):
            if not a or not isinstance(a, str):
                return False
            a = a.strip()
            # Reject if too short (single word or just a couple words)
            if len(a.split()) < 3:
                return False
            return True
        
        topic_data["actions"] = [a.strip() for a in topic_data["actions"] if is_valid_action(a)]
        
        # Ensure actions is a list of exactly 3 (fill with meaningful defaults if needed)
        default_actions = [
            f"Review {topic_name} concepts by re-reading your notes and textbook",
            f"Practice {topic_name} by completing 5-10 similar questions each day",
            f"Ask your teacher or a classmate to explain {topic_name} concepts you find confusing"
        ]
        
        while len(topic_data["actions"]) < 3:
            # Use default actions that haven't been used yet
            default_idx = len(topic_data["actions"])
            if default_idx < len(default_actions):
                topic_data["actions"].append(default_actions[default_idx])
            else:
                topic_data["actions"].append(f"Continue practicing {topic_name} to improve")
        
        topic_data["actions"] = topic_data["actions"][:3]
        
        # Filter out empty practice questions and ones with placeholder "..." answers
        def is_placeholder(text):
            """Check if text is a placeholder like 'The answer is...' or 'The main idea is...'"""
            if not text:
                return True
            text = text.strip()
            # Check for common placeholder patterns
            if text.endswith("..."):
                return True
            if "..." in text and len(text) < 50:
                return True
            if text.lower().startswith(("the main", "the character", "the answer", "the passage", "sure,")):
                if "..." in text or text.endswith("is") or len(text.split()) < 5:
                    return True
            return False
        
        # Filter out practice questions with placeholder answers
        topic_data["practice"] = [
            p for p in topic_data["practice"] 
            if p and isinstance(p, dict) and p.get("q") and p.get("answer") 
            and p.get("q").strip() and p.get("answer").strip()
            and not is_placeholder(p.get("answer", ""))
        ]
        
        # Fix explanations that are questions or placeholders
        for practice in topic_data["practice"]:
            explanation = practice.get("explanation", "")
            answer = practice.get("answer", "")
            
            # Check if explanation is bad (question, placeholder, or too short)
            needs_fix = False
            if not explanation or len(explanation.strip()) < 10:
                needs_fix = True
            elif explanation.strip().endswith("?"):
                needs_fix = True
            elif explanation.strip().startswith(("Why ", "How ", "What ")):
                needs_fix = True
            elif "..." in explanation:
                needs_fix = True
            elif is_placeholder(explanation):
                needs_fix = True
            
            if needs_fix:
                # Replace with a proper explanation based on the answer
                if answer and not is_placeholder(answer):
                    practice["explanation"] = f"This answer is correct because it accurately describes {topic_name.lower()}. {answer}."
                else:
                    practice["explanation"] = f"Review {topic_name} concepts in your textbook and practice with similar questions."
        
        # Ensure practice is a list of exactly 2 (fill with meaningful defaults if needed)
        default_practice = [
            {
                "q": f"What is an important concept in {topic_name}?",
                "answer": "Review your notes and textbook",
                "explanation": f"Focus on understanding {topic_name} concepts. Review the material and practice with similar questions."
            },
            {
                "q": f"How can you improve your {topic_name} skills?",
                "answer": "Practice regularly and ask for help",
                "explanation": f"Practice {topic_name} regularly, review missed questions, and ask your teacher for clarification when needed."
            }
        ]
        
        while len(topic_data["practice"]) < 2:
            # Use default practice questions that haven't been used yet
            default_idx = len(topic_data["practice"])
            if default_idx < len(default_practice):
                topic_data["practice"].append(default_practice[default_idx])
            else:
                topic_data["practice"].append({
                    "q": f"Practice question about {topic_name}",
                    "answer": "Review the material",
                    "explanation": f"Continue practicing {topic_name} to improve your understanding."
                })
        
        topic_data["practice"] = topic_data["practice"][:2]
    
    return feedback

