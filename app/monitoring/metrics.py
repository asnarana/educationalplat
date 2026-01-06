"""
Prometheus metrics for educational platform monitoring.
Tracks API performance, quiz activity, and student engagement.
"""
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from typing import Optional

# API Performance Metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status_code']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint'],
    buckets=(0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0, 10.0)
)

# Quiz Activity Metrics
quizzes_generated_total = Counter(
    'quizzes_generated_total',
    'Total quizzes generated',
    ['grade_level', 'quiz_type']  # quiz_type: 'full' or 'practice'
)

quizzes_submitted_total = Counter(
    'quizzes_submitted_total',
    'Total quizzes submitted',
    ['grade_level', 'passed']  # passed: 'true' or 'false'
)

quiz_scores = Histogram(
    'quiz_scores',
    'Quiz scores distribution',
    ['grade_level'],
    buckets=(0, 20, 40, 60, 70, 80, 90, 95, 100)
)

# Student Engagement Metrics
active_students = Gauge(
    'active_students',
    'Number of active students (students who took quizzes in last 24h)'
)

students_total = Gauge(
    'students_total',
    'Total number of unique students'
)

# Topic Performance Metrics
topic_weak_count = Counter(
    'topic_weak_count',
    'Number of times a topic was marked as weak',
    ['grade_level', 'topic']
)

topic_mastery_count = Counter(
    'topic_mastery_count',
    'Number of times a topic was mastered',
    ['grade_level', 'topic']
)

# LLM/AI Metrics (if using AI feedback)
llm_requests_total = Counter(
    'llm_requests_total',
    'Total LLM feedback requests',
    ['provider', 'status']  # status: 'success' or 'error'
)

llm_request_duration_seconds = Histogram(
    'llm_request_duration_seconds',
    'LLM request duration in seconds',
    ['provider'],
    buckets=(0.5, 1.0, 2.0, 5.0, 10.0, 20.0, 30.0)
)

# Database Metrics
db_query_duration_seconds = Histogram(
    'db_query_duration_seconds',
    'Database query duration in seconds',
    ['operation'],  # operation: 'select', 'insert', 'update', 'delete'
    buckets=(0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0)
)

# Question Bank Metrics
questions_total = Gauge(
    'questions_total',
    'Total number of questions in database',
    ['grade_level', 'topic']
)


def get_metrics():
    """Return Prometheus metrics in text format."""
    return generate_latest()


def track_quiz_generated(grade_level: int, quiz_type: str = 'full'):
    """Track when a quiz is generated."""
    quizzes_generated_total.labels(
        grade_level=str(grade_level),
        quiz_type=quiz_type
    ).inc()


def track_quiz_submitted(grade_level: int, score: float, passed: bool):
    """Track when a quiz is submitted."""
    quizzes_submitted_total.labels(
        grade_level=str(grade_level),
        passed='true' if passed else 'false'
    ).inc()
    quiz_scores.labels(grade_level=str(grade_level)).observe(score)


def track_weak_topic(grade_level: int, topic: str):
    """Track when a topic is marked as weak."""
    topic_weak_count.labels(
        grade_level=str(grade_level),
        topic=topic
    ).inc()


def track_topic_mastery(grade_level: int, topic: str):
    """Track when a topic is mastered."""
    topic_mastery_count.labels(
        grade_level=str(grade_level),
        topic=topic
    ).inc()


def track_llm_request(provider: str, duration: float, success: bool):
    """Track LLM feedback requests."""
    llm_requests_total.labels(
        provider=provider,
        status='success' if success else 'error'
    ).inc()
    if success:
        llm_request_duration_seconds.labels(provider=provider).observe(duration)

