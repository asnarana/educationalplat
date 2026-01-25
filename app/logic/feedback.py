"""
Feedback generation logic using LLM with RAG for personalized study recommendations.

Uses ChromaDB vector stores to retrieve similar questions for pattern analysis.
"""
import json
import os
from typing import Dict, List, Any
from pathlib import Path
from sqlalchemy.orm import Session
from app.models import Attempt, Quiz, Question
from app.logic.llm_provider import get_llm_provider, LLMProvider

# Import vector DB for RAG
try:
    from app.logic.vector_db import get_similar_questions_for_missed, get_collection_stats
    VECTOR_DB_AVAILABLE = True
except ImportError:
    VECTOR_DB_AVAILABLE = False
    print("WARNING: Vector DB not available. RAG will be disabled.")


def load_prompt_template() -> str:
    """Load the feedback prompt template."""
    template_path = Path(__file__).parent.parent / "prompts" / "feedback_prompt.txt"
    if not template_path.exists():
        raise FileNotFoundError(f"Prompt template not found: {template_path}")
    return template_path.read_text()


def get_missed_questions_data(attempt: Attempt, questions: List[Question]) -> List[Dict]:
    """
    Get data about missed questions for RAG pipeline.
    
    Args:
        attempt: Attempt object with answers
        questions: List of Question objects from the quiz
        
    Returns:
        List of dicts with missed question data
    """
    missed = []
    for question in questions:
        student_answer = attempt.answers.get(question.id, "")
        is_correct = str(student_answer).strip().lower() == str(question.correct_answer).strip().lower()
        
        if not is_correct:
            missed.append({
                "id": question.id,
                "topic": question.topic,
                "prompt": question.prompt,
                "student_answer": student_answer,
                "correct_answer": question.correct_answer,
                "explanation": question.explanation
            })
    
    return missed


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
                f"Topic: {question.topic}\n"
                f"Question: {prompt_text}\n"
                f"Student's answer: {student_answer or '(no answer)'}\n"
                f"Correct answer: {question.correct_answer}\n"
                f"Why correct: {question.explanation or 'Not provided'}\n"
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


def format_similar_questions_for_rag(
    similar_questions: Dict[str, List[Dict]],
    missed_questions: List[Dict]
) -> str:
    """
    Format similar questions from vector DB for the RAG prompt.
    
    This shows the LLM similar questions to help it understand mistake patterns.
    
    Args:
        similar_questions: Dict mapping topic -> list of similar questions from vector DB
        missed_questions: List of questions the student missed
        
    Returns:
        Formatted string for the prompt
    """
    if not similar_questions:
        return "No similar questions available for pattern analysis."
    
    sections = []
    
    for topic, questions in similar_questions.items():
        if not questions:
            continue
            
        topic_section = f"SIMILAR {topic.upper()} QUESTIONS (for pattern analysis):\n"
        
        for i, q in enumerate(questions[:3], 1):  # Limit to 3 per topic
            prompt = q.get("prompt", "")[:300]  # Truncate long prompts
            if len(q.get("prompt", "")) > 300:
                prompt += "..."
            
            topic_section += f"""
{i}. Question: {prompt}
   Answer: {q.get('correct_answer', 'N/A')}
   Concept: {q.get('explanation', 'N/A')[:150]}
"""
        
        sections.append(topic_section)
    
    if not sections:
        return "No similar questions available for pattern analysis."
    
    return "\n".join(sections)


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
    questions: List[Question],
    similar_questions_rag: str = ""
) -> str:
    """
    Generate the full prompt for LLM feedback generation with RAG.
    
    Args:
        attempt: Attempt object
        quiz: Quiz object
        questions: List of Question objects
        similar_questions_rag: Formatted similar questions from vector DB
        
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
    
    # Generate topics JSON hint to show exact structure with real topic names
    # This helps smaller LLMs understand the expected output format
    topics_hint_parts = []
    for topic in focus_topics:
        topics_hint_parts.append(f'"{topic}":{{"why_struggling":"...","actions":["tip1","tip2","tip3"]}}')
    topics_json_hint = ",".join(topics_hint_parts)
    
    # Build prompt
    overall_score_pct = f"{attempt.score_total * 100:.1f}%"
    prompt = template.format(
        grade_level=quiz.grade_level,
        overall_score=overall_score_pct,
        all_topics=", ".join(all_topics),
        weak_topics=", ".join(attempt.weak_topics) if attempt.weak_topics else "None",
        performance_summary=performance_summary,
        weak_topics_section=weak_topics_section,
        strong_topics_section=strong_topics_section,
        missed_questions=missed_questions,
        similar_questions_rag=similar_questions_rag or "No similar questions available.",
        topics_json_hint=topics_json_hint
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
    Generate personalized feedback using LLM with RAG pipeline.
    
    RAG Pipeline:
    1. Get missed questions from the attempt
    2. Query vector DB for similar questions (semantic search)
    3. Augment prompt with similar questions for pattern analysis
    4. LLM analyzes patterns and generates study recommendations
    
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
                    "why_struggling": "...",
                    "actions": ["...", "...", "..."]
                }
            }
        }
    """
    if llm_provider is None:
        llm_provider = get_llm_provider()
    
    # RAG Step 1: Get missed questions
    missed_questions_data = get_missed_questions_data(attempt, questions)
    
    # RAG Step 2: Query vector DB for similar questions
    similar_questions_rag = ""
    if VECTOR_DB_AVAILABLE and missed_questions_data:
        try:
            # Subject keywords for classification
            math_keywords = ['addition', 'subtraction', 'multiplication', 'division', 'fraction', 
                           'algebra', 'geometry', 'decimal', 'percentage', 'word problem',
                           'measurement', 'number operations', 'operations']
            reading_keywords = ['vocabulary', 'reading', 'comprehension', 'character', 'main idea',
                              'text structure', 'inference', 'word meaning', 'context clues',
                              'author', 'passage', 'literary', 'figurative']
            
            # Classify ALL missed questions by subject
            math_questions = []
            reading_questions = []
            
            for q in missed_questions_data:
                topic_lower = q.get("topic", "").lower()
                prompt_lower = q.get("prompt", "").lower()
                
                # Check if it's a Math or Reading question
                is_math = any(kw in topic_lower for kw in math_keywords)
                is_reading = any(kw in topic_lower for kw in reading_keywords)
                
                # Also check prompt for reading passages (they typically have "read" or "passage")
                if not is_math and not is_reading:
                    if "read the" in prompt_lower or "passage" in prompt_lower or "according to" in prompt_lower:
                        is_reading = True
                    else:
                        # Default to Math if unclear
                        is_math = True
                
                if is_reading:
                    reading_questions.append(q)
                else:
                    math_questions.append(q)
            
            similar_by_topic = {}
            
            # Query Math vector store for Math questions
            if math_questions:
                math_similar = get_similar_questions_for_missed(
                    missed_questions=math_questions,
                    grade_level=quiz.grade_level,
                    subject="Math",
                    n_per_question=3
                )
                similar_by_topic.update(math_similar)
                print(f"[RAG] Retrieved Math similar questions for {len(math_similar)} topics")
            
            # Query Reading vector store for Reading questions
            if reading_questions:
                reading_similar = get_similar_questions_for_missed(
                    missed_questions=reading_questions,
                    grade_level=quiz.grade_level,
                    subject="Reading",
                    n_per_question=3
                )
                similar_by_topic.update(reading_similar)
                print(f"[RAG] Retrieved Reading similar questions for {len(reading_similar)} topics")
            
            # Format for prompt
            similar_questions_rag = format_similar_questions_for_rag(
                similar_by_topic,
                missed_questions_data
            )
            
            print(f"[RAG] Total: Retrieved similar questions for {len(similar_by_topic)} topics")
        except Exception as e:
            print(f"[RAG] Warning: Could not retrieve similar questions: {e}")
            similar_questions_rag = ""
    
    # RAG Step 3: Generate prompt with augmented context
    prompt = generate_feedback_prompt(attempt, quiz, questions, similar_questions_rag)
    
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
    
    # Always ensure summary has the correct score and mentions all topics
    actual_score_pct = f"{attempt.score_total * 100:.0f}%"
    summary = feedback.get("summary", "")
    
    # Check if summary has wrong score (e.g., copied from example)
    # Common wrong scores that LLMs copy from examples
    wrong_scores = ["40%", "50%", "60%", "70%", "80%"]
    has_wrong_score = any(ws in summary for ws in wrong_scores) and actual_score_pct not in summary
    
    # Check if all topics are mentioned
    missing_from_summary = [t for t in actual_topics if t.lower() not in summary.lower()] if actual_topics else []
    
    if has_wrong_score or missing_from_summary:
        # Rebuild summary with correct score and all topics
        all_topics_str = ", ".join(actual_topics) if actual_topics else "the topics below"
        feedback["summary"] = f"You scored {actual_score_pct}. Focus on {all_topics_str} - review the specific recommendations below for each topic."
        print(f"[DEBUG] Fixed summary: correct score={actual_score_pct}, topics={len(actual_topics)}")
    
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
                # Topic doesn't match - will use defaults (this is expected with smaller LLMs)
                pass
    
    # Add missing topics with default structure
    for actual_topic in actual_topics:
        if actual_topic not in valid_topics:
            valid_topics[actual_topic] = {
                "why_struggling": f"Review {actual_topic} concepts and practice more.",
                "actions": []
            }
    
    # Update feedback with validated topics
    feedback["topics"] = valid_topics
    
    # Ensure all required fields are present and properly filled
    for topic_name, topic_data in feedback["topics"].items():
        if "actions" not in topic_data:
            topic_data["actions"] = []
        if "why_struggling" not in topic_data:
            topic_data["why_struggling"] = f"You need more practice with {topic_name} concepts."
        
        # Filter out empty actions, short actions, and actions with math equations
        def is_valid_action(a):
            if not a or not isinstance(a, str):
                return False
            a = a.strip()
            # Reject if too short (single word or just a couple words)
            if len(a.split()) < 4:
                return False
            # Reject if it contains math equations (signs that LLM is generating nonsense)
            # Look for patterns like "15 + 7 = 22" or "24 - 9 = 15"
            import re
            math_equation_pattern = r'\d+\s*[\+\-\*\/\=]\s*\d+\s*[\=]?\s*\d*'
            if re.search(math_equation_pattern, a):
                print(f"[DEBUG] Rejecting action with math equation: {a[:50]}...")
                return False
            # Reject if it has "..." suggesting copied/incomplete content
            if "..." in a and a.count("...") > 1:
                print(f"[DEBUG] Rejecting action with multiple ellipses: {a[:50]}...")
                return False
            # Reject if it looks like a random calculation
            if re.search(r':\s*\d+\s*(apples|oranges|items|things)', a, re.IGNORECASE):
                print(f"[DEBUG] Rejecting action with random calculation: {a[:50]}...")
                return False
            return True
        
        topic_data["actions"] = [a.strip() for a in topic_data["actions"] if is_valid_action(a)]
        
        # Topic-specific default actions based on common math/reading topics
        topic_lower = topic_name.lower()
        
        # Define more helpful defaults based on topic type
        if "fraction" in topic_lower:
            default_actions = [
                "Draw fraction bars or pie charts to visualize parts of a whole",
                "Practice identifying numerator (top = parts you have) and denominator (bottom = total parts)",
                "Use real objects like pizza slices or blocks to model fraction problems"
            ]
        elif "geometry" in topic_lower:
            default_actions = [
                "Create a reference chart of shapes with their properties (sides, angles, parallel lines)",
                "Practice identifying shapes in real-world objects around your home",
                "Draw and label shapes, marking equal sides and right angles"
            ]
        elif "measurement" in topic_lower:
            default_actions = [
                "Create a conversion chart for common units (inches to feet, cups to quarts, etc.)",
                "Practice measuring real objects with a ruler or measuring tape",
                "Use visual aids: draw number lines to help convert between units"
            ]
        elif "operation" in topic_lower or "number" in topic_lower:
            default_actions = [
                "Use visual aids: draw diagrams, number lines, or use manipulatives for each step",
                "Practice mental math by breaking large numbers into smaller parts",
                "Show all your work and check answers by using the inverse operation"
            ]
        elif "reading" in topic_lower or "comprehension" in topic_lower:
            default_actions = [
                "Read the passage twice: first for the main idea, then for details",
                "Underline or highlight key information as you read",
                "Before answering, go back to the passage to find evidence for your answer"
            ]
        elif "vocabulary" in topic_lower or "word meaning" in topic_lower or "context" in topic_lower:
            default_actions = [
                "Look for context clues in the sentences before and after unknown words",
                "Break words into parts (prefixes, roots, suffixes) to guess meaning",
                "Keep a vocabulary journal and review new words daily"
            ]
        elif "main idea" in topic_lower or "central" in topic_lower:
            default_actions = [
                "Ask yourself: What is this passage mostly about? That's the main idea",
                "Look at the first and last sentences of paragraphs - they often state the main idea",
                "Eliminate answer choices that are too specific (details) or too broad"
            ]
        elif "inference" in topic_lower:
            default_actions = [
                "Use clues from the text plus what you already know to make inferences",
                "Ask: What is the author suggesting but not directly saying?",
                "Look for words like 'probably', 'suggests', 'implies' in questions"
            ]
        elif "character" in topic_lower:
            default_actions = [
                "Pay attention to what characters say, do, and think",
                "Look for how characters change from the beginning to end of the story",
                "Notice how other characters react to or describe the character"
            ]
        elif "text structure" in topic_lower or "structure" in topic_lower:
            default_actions = [
                "Learn the 5 main text structures: cause/effect, compare/contrast, sequence, problem/solution, description",
                "Look for signal words: 'because' (cause/effect), 'first/then' (sequence), 'however' (compare/contrast)",
                "Ask: How did the author organize this information and why?"
            ]
        elif "author" in topic_lower or "purpose" in topic_lower:
            default_actions = [
                "Ask: Is the author trying to inform, persuade, or entertain?",
                "Look at word choice - positive/negative words reveal author's attitude",
                "Consider: Who is the intended audience for this text?"
            ]
        elif "figurative" in topic_lower or "literary" in topic_lower:
            default_actions = [
                "Learn common figurative language: simile (like/as), metaphor, personification, hyperbole",
                "Ask: Is the author speaking literally or comparing something to something else?",
                "Look for unusual word combinations that don't make literal sense"
            ]
        else:
            # Generic but still useful defaults
            default_actions = [
                f"Break down {topic_name} problems into smaller steps and solve one step at a time",
                f"Practice {topic_name} using the Practice button to get targeted questions",
                f"Work through examples slowly, writing out each step before checking answers"
            ]
        
        while len(topic_data["actions"]) < 3:
            # Use default actions that haven't been used yet
            default_idx = len(topic_data["actions"])
            if default_idx < len(default_actions):
                topic_data["actions"].append(default_actions[default_idx])
            else:
                topic_data["actions"].append(f"Continue practicing {topic_name} to build confidence")
        
        topic_data["actions"] = topic_data["actions"][:3]
        
        # Remove practice field if present (we don't generate practice questions anymore)
        # Practice questions come from Oracle DB via the Practice Topic button
        if "practice" in topic_data:
            del topic_data["practice"]
    
    return feedback

