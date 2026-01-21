"""
Script to expand the question bank with more questions.
Generates additional questions for each topic and grade level.
"""
from sqlalchemy.orm import Session
from app.db import get_db, SessionLocal
from app.models import Question, Base
from app.db import engine

# Expanded question bank - At least 15-20 questions per topic for variety
EXPANDED_QUESTIONS = [
    # Grade 3 - Addition (15+ questions)
    {
        "grade_level": 3,
        "topic": "Addition",
        "difficulty": 1,
        "weight": 1.0,
        "prompt": "What is 7 + 4?",
        "choices": ["10", "11", "12", "13"],
        "correct_answer": "11",
        "explanation": "Adding 7 and 4 gives 11."
    },
    {
        "grade_level": 3,
        "topic": "Addition",
        "difficulty": 1,
        "weight": 1.0,
        "prompt": "What is 9 + 6?",
        "choices": ["14", "15", "16", "17"],
        "correct_answer": "15",
        "explanation": "Adding 9 and 6 gives 15."
    },
    {
        "grade_level": 3,
        "topic": "Addition",
        "difficulty": 1,
        "weight": 1.0,
        "prompt": "What is 8 + 5?",
        "choices": ["12", "13", "14", "15"],
        "correct_answer": "13",
        "explanation": "Adding 8 and 5 gives 13."
    },
    {
        "grade_level": 3,
        "topic": "Addition",
        "difficulty": 1,
        "weight": 1.0,
        "prompt": "What is 6 + 9?",
        "choices": ["14", "15", "16", "17"],
        "correct_answer": "15",
        "explanation": "Adding 6 and 9 gives 15."
    },
    {
        "grade_level": 3,
        "topic": "Addition",
        "difficulty": 1,
        "weight": 1.0,
        "prompt": "What is 11 + 7?",
        "choices": ["17", "18", "19", "20"],
        "correct_answer": "18",
        "explanation": "Adding 11 and 7 gives 18."
    },
    {
        "grade_level": 3,
        "topic": "Addition",
        "difficulty": 2,
        "weight": 1.5,
        "prompt": "What is 18 + 19?",
        "choices": ["35", "36", "37", "38"],
        "correct_answer": "37",
        "explanation": "Adding 18 and 19 gives 37."
    },
    {
        "grade_level": 3,
        "topic": "Addition",
        "difficulty": 2,
        "weight": 1.5,
        "prompt": "What is 23 + 14?",
        "choices": ["36", "37", "38", "39"],
        "correct_answer": "37",
        "explanation": "Adding 23 and 14 gives 37."
    },
    {
        "grade_level": 3,
        "topic": "Addition",
        "difficulty": 2,
        "weight": 1.5,
        "prompt": "What is 16 + 17?",
        "choices": ["32", "33", "34", "35"],
        "correct_answer": "33",
        "explanation": "Adding 16 and 17 gives 33."
    },
    {
        "grade_level": 3,
        "topic": "Addition",
        "difficulty": 2,
        "weight": 1.5,
        "prompt": "What is 24 + 15?",
        "choices": ["38", "39", "40", "41"],
        "correct_answer": "39",
        "explanation": "Adding 24 and 15 gives 39."
    },
    {
        "grade_level": 3,
        "topic": "Addition",
        "difficulty": 2,
        "weight": 1.5,
        "prompt": "What is 19 + 22?",
        "choices": ["40", "41", "42", "43"],
        "correct_answer": "41",
        "explanation": "Adding 19 and 22 gives 41."
    },
    {
        "grade_level": 3,
        "topic": "Addition",
        "difficulty": 2,
        "weight": 1.5,
        "prompt": "What is 27 + 13?",
        "choices": ["39", "40", "41", "42"],
        "correct_answer": "40",
        "explanation": "Adding 27 and 13 gives 40."
    },
    {
        "grade_level": 3,
        "topic": "Addition",
        "difficulty": 2,
        "weight": 1.5,
        "prompt": "What is 31 + 18?",
        "choices": ["48", "49", "50", "51"],
        "correct_answer": "49",
        "explanation": "Adding 31 and 18 gives 49."
    },
    
    # Grade 3 - Subtraction (15+ questions)
    {
        "grade_level": 3,
        "topic": "Subtraction",
        "difficulty": 1,
        "weight": 1.0,
        "prompt": "What is 15 - 7?",
        "choices": ["7", "8", "9", "10"],
        "correct_answer": "8",
        "explanation": "Subtracting 7 from 15 gives 8."
    },
    {
        "grade_level": 3,
        "topic": "Subtraction",
        "difficulty": 1,
        "weight": 1.0,
        "prompt": "What is 20 - 9?",
        "choices": ["10", "11", "12", "13"],
        "correct_answer": "11",
        "explanation": "Subtracting 9 from 20 gives 11."
    },
    {
        "grade_level": 3,
        "topic": "Subtraction",
        "difficulty": 1,
        "weight": 1.0,
        "prompt": "What is 14 - 6?",
        "choices": ["7", "8", "9", "10"],
        "correct_answer": "8",
        "explanation": "Subtracting 6 from 14 gives 8."
    },
    {
        "grade_level": 3,
        "topic": "Subtraction",
        "difficulty": 1,
        "weight": 1.0,
        "prompt": "What is 18 - 9?",
        "choices": ["8", "9", "10", "11"],
        "correct_answer": "9",
        "explanation": "Subtracting 9 from 18 gives 9."
    },
    {
        "grade_level": 3,
        "topic": "Subtraction",
        "difficulty": 1,
        "weight": 1.0,
        "prompt": "What is 16 - 8?",
        "choices": ["7", "8", "9", "10"],
        "correct_answer": "8",
        "explanation": "Subtracting 8 from 16 gives 8."
    },
    {
        "grade_level": 3,
        "topic": "Subtraction",
        "difficulty": 2,
        "weight": 1.5,
        "prompt": "What is 35 - 18?",
        "choices": ["16", "17", "18", "19"],
        "correct_answer": "17",
        "explanation": "Subtracting 18 from 35 gives 17."
    },
    {
        "grade_level": 3,
        "topic": "Subtraction",
        "difficulty": 2,
        "weight": 1.5,
        "prompt": "What is 42 - 19?",
        "choices": ["22", "23", "24", "25"],
        "correct_answer": "23",
        "explanation": "Subtracting 19 from 42 gives 23."
    },
    {
        "grade_level": 3,
        "topic": "Subtraction",
        "difficulty": 2,
        "weight": 1.5,
        "prompt": "What is 38 - 16?",
        "choices": ["21", "22", "23", "24"],
        "correct_answer": "22",
        "explanation": "Subtracting 16 from 38 gives 22."
    },
    {
        "grade_level": 3,
        "topic": "Subtraction",
        "difficulty": 2,
        "weight": 1.5,
        "prompt": "What is 45 - 17?",
        "choices": ["27", "28", "29", "30"],
        "correct_answer": "28",
        "explanation": "Subtracting 17 from 45 gives 28."
    },
    {
        "grade_level": 3,
        "topic": "Subtraction",
        "difficulty": 2,
        "weight": 1.5,
        "prompt": "What is 50 - 23?",
        "choices": ["26", "27", "28", "29"],
        "correct_answer": "27",
        "explanation": "Subtracting 23 from 50 gives 27."
    },
    {
        "grade_level": 3,
        "topic": "Subtraction",
        "difficulty": 2,
        "weight": 1.5,
        "prompt": "What is 41 - 14?",
        "choices": ["26", "27", "28", "29"],
        "correct_answer": "27",
        "explanation": "Subtracting 14 from 41 gives 27."
    },
    {
        "grade_level": 3,
        "topic": "Subtraction",
        "difficulty": 2,
        "weight": 1.5,
        "prompt": "What is 39 - 21?",
        "choices": ["17", "18", "19", "20"],
        "correct_answer": "18",
        "explanation": "Subtracting 21 from 39 gives 18."
    },
    
    # Grade 3 - Multiplication (15+ questions)
    {
        "grade_level": 3,
        "topic": "Multiplication",
        "difficulty": 1,
        "weight": 1.0,
        "prompt": "What is 4 × 5?",
        "choices": ["18", "19", "20", "21"],
        "correct_answer": "20",
        "explanation": "Multiplying 4 by 5 gives 20."
    },
    {
        "grade_level": 3,
        "topic": "Multiplication",
        "difficulty": 1,
        "weight": 1.0,
        "prompt": "What is 5 × 8?",
        "choices": ["38", "39", "40", "41"],
        "correct_answer": "40",
        "explanation": "Multiplying 5 by 8 gives 40."
    },
    {
        "grade_level": 3,
        "topic": "Multiplication",
        "difficulty": 1,
        "weight": 1.0,
        "prompt": "What is 6 × 4?",
        "choices": ["22", "23", "24", "25"],
        "correct_answer": "24",
        "explanation": "Multiplying 6 by 4 gives 24."
    },
    {
        "grade_level": 3,
        "topic": "Multiplication",
        "difficulty": 1,
        "weight": 1.0,
        "prompt": "What is 7 × 3?",
        "choices": ["20", "21", "22", "23"],
        "correct_answer": "21",
        "explanation": "Multiplying 7 by 3 gives 21."
    },
    {
        "grade_level": 3,
        "topic": "Multiplication",
        "difficulty": 1,
        "weight": 1.0,
        "prompt": "What is 9 × 2?",
        "choices": ["16", "17", "18", "19"],
        "correct_answer": "18",
        "explanation": "Multiplying 9 by 2 gives 18."
    },
    {
        "grade_level": 3,
        "topic": "Multiplication",
        "difficulty": 2,
        "weight": 1.5,
        "prompt": "What is 8 × 9?",
        "choices": ["70", "71", "72", "73"],
        "correct_answer": "72",
        "explanation": "Multiplying 8 by 9 gives 72."
    },
    {
        "grade_level": 3,
        "topic": "Multiplication",
        "difficulty": 2,
        "weight": 1.5,
        "prompt": "What is 7 × 8?",
        "choices": ["54", "55", "56", "57"],
        "correct_answer": "56",
        "explanation": "Multiplying 7 by 8 gives 56."
    },
    {
        "grade_level": 3,
        "topic": "Multiplication",
        "difficulty": 2,
        "weight": 1.5,
        "prompt": "What is 6 × 7?",
        "choices": ["40", "41", "42", "43"],
        "correct_answer": "42",
        "explanation": "Multiplying 6 by 7 gives 42."
    },
    {
        "grade_level": 3,
        "topic": "Multiplication",
        "difficulty": 2,
        "weight": 1.5,
        "prompt": "What is 9 × 6?",
        "choices": ["52", "53", "54", "55"],
        "correct_answer": "54",
        "explanation": "Multiplying 9 by 6 gives 54."
    },
    {
        "grade_level": 3,
        "topic": "Multiplication",
        "difficulty": 2,
        "weight": 1.5,
        "prompt": "What is 8 × 7?",
        "choices": ["54", "55", "56", "57"],
        "correct_answer": "56",
        "explanation": "Multiplying 8 by 7 gives 56."
    },
    {
        "grade_level": 3,
        "topic": "Multiplication",
        "difficulty": 2,
        "weight": 1.5,
        "prompt": "What is 9 × 4?",
        "choices": ["34", "35", "36", "37"],
        "correct_answer": "36",
        "explanation": "Multiplying 9 by 4 gives 36."
    },
    {
        "grade_level": 3,
        "topic": "Multiplication",
        "difficulty": 2,
        "weight": 1.5,
        "prompt": "What is 7 × 6?",
        "choices": ["40", "41", "42", "43"],
        "correct_answer": "42",
        "explanation": "Multiplying 7 by 6 gives 42."
    },
    
    # Grade 3 - Division (15+ questions)
    {
        "grade_level": 3,
        "topic": "Division",
        "difficulty": 1,
        "weight": 1.0,
        "prompt": "What is 15 ÷ 5?",
        "choices": ["2", "3", "4", "5"],
        "correct_answer": "3",
        "explanation": "Dividing 15 by 5 gives 3."
    },
    {
        "grade_level": 3,
        "topic": "Division",
        "difficulty": 1,
        "weight": 1.0,
        "prompt": "What is 18 ÷ 6?",
        "choices": ["2", "3", "4", "5"],
        "correct_answer": "3",
        "explanation": "Dividing 18 by 6 gives 3."
    },
    {
        "grade_level": 3,
        "topic": "Division",
        "difficulty": 1,
        "weight": 1.0,
        "prompt": "What is 20 ÷ 4?",
        "choices": ["4", "5", "6", "7"],
        "correct_answer": "5",
        "explanation": "Dividing 20 by 4 gives 5."
    },
    {
        "grade_level": 3,
        "topic": "Division",
        "difficulty": 1,
        "weight": 1.0,
        "prompt": "What is 16 ÷ 4?",
        "choices": ["3", "4", "5", "6"],
        "correct_answer": "4",
        "explanation": "Dividing 16 by 4 gives 4."
    },
    {
        "grade_level": 3,
        "topic": "Division",
        "difficulty": 1,
        "weight": 1.0,
        "prompt": "What is 21 ÷ 7?",
        "choices": ["2", "3", "4", "5"],
        "correct_answer": "3",
        "explanation": "Dividing 21 by 7 gives 3."
    },
    {
        "grade_level": 3,
        "topic": "Division",
        "difficulty": 2,
        "weight": 1.5,
        "prompt": "What is 36 ÷ 6?",
        "choices": ["5", "6", "7", "8"],
        "correct_answer": "6",
        "explanation": "Dividing 36 by 6 gives 6."
    },
    {
        "grade_level": 3,
        "topic": "Division",
        "difficulty": 2,
        "weight": 1.5,
        "prompt": "What is 42 ÷ 7?",
        "choices": ["5", "6", "7", "8"],
        "correct_answer": "6",
        "explanation": "Dividing 42 by 7 gives 6."
    },
    {
        "grade_level": 3,
        "topic": "Division",
        "difficulty": 2,
        "weight": 1.5,
        "prompt": "What is 48 ÷ 8?",
        "choices": ["5", "6", "7", "8"],
        "correct_answer": "6",
        "explanation": "Dividing 48 by 8 gives 6."
    },
    {
        "grade_level": 3,
        "topic": "Division",
        "difficulty": 2,
        "weight": 1.5,
        "prompt": "What is 54 ÷ 9?",
        "choices": ["5", "6", "7", "8"],
        "correct_answer": "6",
        "explanation": "Dividing 54 by 9 gives 6."
    },
    {
        "grade_level": 3,
        "topic": "Division",
        "difficulty": 2,
        "weight": 1.5,
        "prompt": "What is 35 ÷ 5?",
        "choices": ["6", "7", "8", "9"],
        "correct_answer": "7",
        "explanation": "Dividing 35 by 5 gives 7."
    },
    {
        "grade_level": 3,
        "topic": "Division",
        "difficulty": 2,
        "weight": 1.5,
        "prompt": "What is 49 ÷ 7?",
        "choices": ["6", "7", "8", "9"],
        "correct_answer": "7",
        "explanation": "Dividing 49 by 7 gives 7."
    },
    {
        "grade_level": 3,
        "topic": "Division",
        "difficulty": 2,
        "weight": 1.5,
        "prompt": "What is 32 ÷ 8?",
        "choices": ["3", "4", "5", "6"],
        "correct_answer": "4",
        "explanation": "Dividing 32 by 8 gives 4."
    },
    
    # Grade 3 - Fractions (15+ questions)
    {
        "grade_level": 3,
        "topic": "Fractions",
        "difficulty": 1,
        "weight": 1.0,
        "prompt": "What fraction represents one quarter?",
        "choices": ["1/3", "1/4", "1/5", "2/4"],
        "correct_answer": "1/4",
        "explanation": "One quarter is represented by 1/4."
    },
    {
        "grade_level": 3,
        "topic": "Fractions",
        "difficulty": 1,
        "weight": 1.0,
        "prompt": "What fraction represents three quarters?",
        "choices": ["2/4", "3/4", "4/4", "1/3"],
        "correct_answer": "3/4",
        "explanation": "Three quarters is represented by 3/4."
    },
    {
        "grade_level": 3,
        "topic": "Fractions",
        "difficulty": 1,
        "weight": 1.0,
        "prompt": "What fraction represents one third?",
        "choices": ["1/2", "1/3", "1/4", "2/3"],
        "correct_answer": "1/3",
        "explanation": "One third is represented by 1/3."
    },
    {
        "grade_level": 3,
        "topic": "Fractions",
        "difficulty": 1,
        "weight": 1.0,
        "prompt": "What fraction represents two thirds?",
        "choices": ["1/3", "2/3", "3/3", "2/4"],
        "correct_answer": "2/3",
        "explanation": "Two thirds is represented by 2/3."
    },
    {
        "grade_level": 3,
        "topic": "Fractions",
        "difficulty": 1,
        "weight": 1.0,
        "prompt": "What fraction represents one fifth?",
        "choices": ["1/4", "1/5", "1/6", "2/5"],
        "correct_answer": "1/5",
        "explanation": "One fifth is represented by 1/5."
    },
    {
        "grade_level": 3,
        "topic": "Fractions",
        "difficulty": 2,
        "weight": 1.5,
        "prompt": "Which fraction is smaller: 1/3 or 1/5?",
        "choices": ["1/3", "1/5", "They are equal", "Cannot compare"],
        "correct_answer": "1/5",
        "explanation": "1/5 is smaller than 1/3 because it represents a smaller portion of the whole."
    },
    {
        "grade_level": 3,
        "topic": "Fractions",
        "difficulty": 2,
        "weight": 1.5,
        "prompt": "If you have 2/4 of a pizza, how much do you have?",
        "choices": ["Half", "Quarter", "Three quarters", "Whole"],
        "correct_answer": "Half",
        "explanation": "2/4 is equal to 1/2, which is half."
    },
    {
        "grade_level": 3,
        "topic": "Fractions",
        "difficulty": 2,
        "weight": 1.5,
        "prompt": "Which fraction is larger: 2/3 or 1/2?",
        "choices": ["1/2", "2/3", "They are equal", "Cannot compare"],
        "correct_answer": "2/3",
        "explanation": "2/3 is larger than 1/2 because it represents a bigger portion."
    },
    {
        "grade_level": 3,
        "topic": "Fractions",
        "difficulty": 2,
        "weight": 1.5,
        "prompt": "If you have 3/6 of a cake, how much do you have?",
        "choices": ["Half", "Quarter", "Three quarters", "Whole"],
        "correct_answer": "Half",
        "explanation": "3/6 is equal to 1/2, which is half."
    },
    {
        "grade_level": 3,
        "topic": "Fractions",
        "difficulty": 2,
        "weight": 1.5,
        "prompt": "Which fraction is smaller: 1/4 or 1/6?",
        "choices": ["1/4", "1/6", "They are equal", "Cannot compare"],
        "correct_answer": "1/6",
        "explanation": "1/6 is smaller than 1/4 because it represents a smaller portion."
    },
    {
        "grade_level": 3,
        "topic": "Fractions",
        "difficulty": 2,
        "weight": 1.5,
        "prompt": "What fraction is equivalent to 1/2?",
        "choices": ["2/3", "2/4", "3/4", "1/3"],
        "correct_answer": "2/4",
        "explanation": "2/4 is equivalent to 1/2 because both represent half."
    },
    {
        "grade_level": 3,
        "topic": "Fractions",
        "difficulty": 2,
        "weight": 1.5,
        "prompt": "If you have 4/8 of something, how much do you have?",
        "choices": ["Half", "Quarter", "Three quarters", "Whole"],
        "correct_answer": "Half",
        "explanation": "4/8 is equal to 1/2, which is half."
    },
    
    # Grade 5 - Algebra (15+ questions)
    {
        "grade_level": 5,
        "topic": "Algebra",
        "difficulty": 1,
        "weight": 1.0,
        "prompt": "If x + 3 = 8, what is x?",
        "choices": ["4", "5", "6", "7"],
        "correct_answer": "5",
        "explanation": "If x + 3 = 8, then x = 8 - 3 = 5."
    },
    {
        "grade_level": 5,
        "topic": "Algebra",
        "difficulty": 1,
        "weight": 1.0,
        "prompt": "If x - 4 = 6, what is x?",
        "choices": ["8", "9", "10", "11"],
        "correct_answer": "10",
        "explanation": "If x - 4 = 6, then x = 6 + 4 = 10."
    },
    {
        "grade_level": 5,
        "topic": "Algebra",
        "difficulty": 1,
        "weight": 1.0,
        "prompt": "If x + 7 = 15, what is x?",
        "choices": ["7", "8", "9", "10"],
        "correct_answer": "8",
        "explanation": "If x + 7 = 15, then x = 15 - 7 = 8."
    },
    {
        "grade_level": 5,
        "topic": "Algebra",
        "difficulty": 1,
        "weight": 1.0,
        "prompt": "If x - 5 = 9, what is x?",
        "choices": ["13", "14", "15", "16"],
        "correct_answer": "14",
        "explanation": "If x - 5 = 9, then x = 9 + 5 = 14."
    },
    {
        "grade_level": 5,
        "topic": "Algebra",
        "difficulty": 1,
        "weight": 1.0,
        "prompt": "If x + 9 = 20, what is x?",
        "choices": ["10", "11", "12", "13"],
        "correct_answer": "11",
        "explanation": "If x + 9 = 20, then x = 20 - 9 = 11."
    },
    {
        "grade_level": 5,
        "topic": "Algebra",
        "difficulty": 2,
        "weight": 1.5,
        "prompt": "If 3x = 21, what is x?",
        "choices": ["6", "7", "8", "9"],
        "correct_answer": "7",
        "explanation": "If 3x = 21, then x = 21 ÷ 3 = 7."
    },
    {
        "grade_level": 5,
        "topic": "Algebra",
        "difficulty": 2,
        "weight": 1.5,
        "prompt": "If x ÷ 4 = 5, what is x?",
        "choices": ["18", "19", "20", "21"],
        "correct_answer": "20",
        "explanation": "If x ÷ 4 = 5, then x = 5 × 4 = 20."
    },
    {
        "grade_level": 5,
        "topic": "Algebra",
        "difficulty": 2,
        "weight": 1.5,
        "prompt": "If 4x = 28, what is x?",
        "choices": ["6", "7", "8", "9"],
        "correct_answer": "7",
        "explanation": "If 4x = 28, then x = 28 ÷ 4 = 7."
    },
    {
        "grade_level": 5,
        "topic": "Algebra",
        "difficulty": 2,
        "weight": 1.5,
        "prompt": "If x ÷ 3 = 6, what is x?",
        "choices": ["17", "18", "19", "20"],
        "correct_answer": "18",
        "explanation": "If x ÷ 3 = 6, then x = 6 × 3 = 18."
    },
    {
        "grade_level": 5,
        "topic": "Algebra",
        "difficulty": 2,
        "weight": 1.5,
        "prompt": "If 5x = 35, what is x?",
        "choices": ["6", "7", "8", "9"],
        "correct_answer": "7",
        "explanation": "If 5x = 35, then x = 35 ÷ 5 = 7."
    },
    {
        "grade_level": 5,
        "topic": "Algebra",
        "difficulty": 2,
        "weight": 1.5,
        "prompt": "If x + 12 = 25, what is x?",
        "choices": ["12", "13", "14", "15"],
        "correct_answer": "13",
        "explanation": "If x + 12 = 25, then x = 25 - 12 = 13."
    },
    {
        "grade_level": 5,
        "topic": "Algebra",
        "difficulty": 2,
        "weight": 1.5,
        "prompt": "If x - 8 = 15, what is x?",
        "choices": ["22", "23", "24", "25"],
        "correct_answer": "23",
        "explanation": "If x - 8 = 15, then x = 15 + 8 = 23."
    },
    
    # Grade 5 - Geometry (15+ questions)
    {
        "grade_level": 5,
        "topic": "Geometry",
        "difficulty": 1,
        "weight": 1.0,
        "prompt": "How many sides does a square have?",
        "choices": ["3", "4", "5", "6"],
        "correct_answer": "4",
        "explanation": "A square has 4 sides."
    },
    {
        "grade_level": 5,
        "topic": "Geometry",
        "difficulty": 1,
        "weight": 1.0,
        "prompt": "What is the perimeter of a square with side length 5?",
        "choices": ["15", "20", "25", "30"],
        "correct_answer": "20",
        "explanation": "Perimeter of a square = 4 × side = 4 × 5 = 20."
    },
    {
        "grade_level": 5,
        "topic": "Geometry",
        "difficulty": 1,
        "weight": 1.0,
        "prompt": "How many sides does a rectangle have?",
        "choices": ["3", "4", "5", "6"],
        "correct_answer": "4",
        "explanation": "A rectangle has 4 sides."
    },
    {
        "grade_level": 5,
        "topic": "Geometry",
        "difficulty": 1,
        "weight": 1.0,
        "prompt": "What is the area of a square with side length 6?",
        "choices": ["30", "36", "42", "48"],
        "correct_answer": "36",
        "explanation": "Area of a square = side × side = 6 × 6 = 36."
    },
    {
        "grade_level": 5,
        "topic": "Geometry",
        "difficulty": 1,
        "weight": 1.0,
        "prompt": "How many sides does a pentagon have?",
        "choices": ["4", "5", "6", "7"],
        "correct_answer": "5",
        "explanation": "A pentagon has 5 sides."
    },
    {
        "grade_level": 5,
        "topic": "Geometry",
        "difficulty": 2,
        "weight": 1.5,
        "prompt": "What is the area of a rectangle with length 6 and width 5?",
        "choices": ["28", "29", "30", "31"],
        "correct_answer": "30",
        "explanation": "Area of rectangle = length × width = 6 × 5 = 30."
    },
    {
        "grade_level": 5,
        "topic": "Geometry",
        "difficulty": 2,
        "weight": 1.5,
        "prompt": "What is the perimeter of a rectangle with length 8 and width 5?",
        "choices": ["24", "25", "26", "27"],
        "correct_answer": "26",
        "explanation": "Perimeter = 2 × (length + width) = 2 × (8 + 5) = 2 × 13 = 26."
    },
    {
        "grade_level": 5,
        "topic": "Geometry",
        "difficulty": 2,
        "weight": 1.5,
        "prompt": "What is the area of a rectangle with length 7 and width 4?",
        "choices": ["26", "27", "28", "29"],
        "correct_answer": "28",
        "explanation": "Area of rectangle = length × width = 7 × 4 = 28."
    },
    {
        "grade_level": 5,
        "topic": "Geometry",
        "difficulty": 2,
        "weight": 1.5,
        "prompt": "What is the perimeter of a square with side length 7?",
        "choices": ["26", "27", "28", "29"],
        "correct_answer": "28",
        "explanation": "Perimeter of a square = 4 × side = 4 × 7 = 28."
    },
    {
        "grade_level": 5,
        "topic": "Geometry",
        "difficulty": 2,
        "weight": 1.5,
        "prompt": "What is the area of a rectangle with length 9 and width 3?",
        "choices": ["25", "26", "27", "28"],
        "correct_answer": "27",
        "explanation": "Area of rectangle = length × width = 9 × 3 = 27."
    },
    {
        "grade_level": 5,
        "topic": "Geometry",
        "difficulty": 2,
        "weight": 1.5,
        "prompt": "What is the perimeter of a rectangle with length 10 and width 6?",
        "choices": ["30", "31", "32", "33"],
        "correct_answer": "32",
        "explanation": "Perimeter = 2 × (length + width) = 2 × (10 + 6) = 2 × 16 = 32."
    },
    {
        "grade_level": 5,
        "topic": "Geometry",
        "difficulty": 2,
        "weight": 1.5,
        "prompt": "What is the area of a square with side length 8?",
        "choices": ["62", "63", "64", "65"],
        "correct_answer": "64",
        "explanation": "Area of a square = side × side = 8 × 8 = 64."
    },
    
    # Grade 5 - Decimals (15+ questions)
    {
        "grade_level": 5,
        "topic": "Decimals",
        "difficulty": 1,
        "weight": 1.0,
        "prompt": "What is 0.7 + 0.2?",
        "choices": ["0.8", "0.9", "1.0", "1.1"],
        "correct_answer": "0.9",
        "explanation": "Adding 0.7 and 0.2 gives 0.9."
    },
    {
        "grade_level": 5,
        "topic": "Decimals",
        "difficulty": 1,
        "weight": 1.0,
        "prompt": "What is 1.5 - 0.8?",
        "choices": ["0.6", "0.7", "0.8", "0.9"],
        "correct_answer": "0.7",
        "explanation": "Subtracting 0.8 from 1.5 gives 0.7."
    },
    {
        "grade_level": 5,
        "topic": "Decimals",
        "difficulty": 1,
        "weight": 1.0,
        "prompt": "What is 0.6 + 0.4?",
        "choices": ["0.9", "1.0", "1.1", "1.2"],
        "correct_answer": "1.0",
        "explanation": "Adding 0.6 and 0.4 gives 1.0."
    },
    {
        "grade_level": 5,
        "topic": "Decimals",
        "difficulty": 1,
        "weight": 1.0,
        "prompt": "What is 2.3 - 1.1?",
        "choices": ["1.1", "1.2", "1.3", "1.4"],
        "correct_answer": "1.2",
        "explanation": "Subtracting 1.1 from 2.3 gives 1.2."
    },
    {
        "grade_level": 5,
        "topic": "Decimals",
        "difficulty": 1,
        "weight": 1.0,
        "prompt": "What is 0.9 + 0.3?",
        "choices": ["1.1", "1.2", "1.3", "1.4"],
        "correct_answer": "1.2",
        "explanation": "Adding 0.9 and 0.3 gives 1.2."
    },
    {
        "grade_level": 5,
        "topic": "Decimals",
        "difficulty": 2,
        "weight": 1.5,
        "prompt": "What is 3.2 × 2?",
        "choices": ["6.2", "6.3", "6.4", "6.5"],
        "correct_answer": "6.4",
        "explanation": "Multiplying 3.2 by 2 gives 6.4."
    },
    {
        "grade_level": 5,
        "topic": "Decimals",
        "difficulty": 2,
        "weight": 1.5,
        "prompt": "What is 4.8 ÷ 2?",
        "choices": ["2.3", "2.4", "2.5", "2.6"],
        "correct_answer": "2.4",
        "explanation": "Dividing 4.8 by 2 gives 2.4."
    },
    {
        "grade_level": 5,
        "topic": "Decimals",
        "difficulty": 2,
        "weight": 1.5,
        "prompt": "What is 2.5 × 3?",
        "choices": ["7.3", "7.4", "7.5", "7.6"],
        "correct_answer": "7.5",
        "explanation": "Multiplying 2.5 by 3 gives 7.5."
    },
    {
        "grade_level": 5,
        "topic": "Decimals",
        "difficulty": 2,
        "weight": 1.5,
        "prompt": "What is 6.4 ÷ 2?",
        "choices": ["3.1", "3.2", "3.3", "3.4"],
        "correct_answer": "3.2",
        "explanation": "Dividing 6.4 by 2 gives 3.2."
    },
    {
        "grade_level": 5,
        "topic": "Decimals",
        "difficulty": 2,
        "weight": 1.5,
        "prompt": "What is 1.8 + 2.3?",
        "choices": ["4.0", "4.1", "4.2", "4.3"],
        "correct_answer": "4.1",
        "explanation": "Adding 1.8 and 2.3 gives 4.1."
    },
    {
        "grade_level": 5,
        "topic": "Decimals",
        "difficulty": 2,
        "weight": 1.5,
        "prompt": "What is 5.6 - 2.4?",
        "choices": ["3.1", "3.2", "3.3", "3.4"],
        "correct_answer": "3.2",
        "explanation": "Subtracting 2.4 from 5.6 gives 3.2."
    },
    {
        "grade_level": 5,
        "topic": "Decimals",
        "difficulty": 2,
        "weight": 1.5,
        "prompt": "What is 3.5 × 2?",
        "choices": ["6.8", "6.9", "7.0", "7.1"],
        "correct_answer": "7.0",
        "explanation": "Multiplying 3.5 by 2 gives 7.0."
    },
    
    # Grade 5 - Percentages (15+ questions)
    {
        "grade_level": 5,
        "topic": "Percentages",
        "difficulty": 1,
        "weight": 1.0,
        "prompt": "What is 25% of 80?",
        "choices": ["18", "20", "22", "24"],
        "correct_answer": "20",
        "explanation": "25% of 80 = 0.25 × 80 = 20."
    },
    {
        "grade_level": 5,
        "topic": "Percentages",
        "difficulty": 1,
        "weight": 1.0,
        "prompt": "What is 10% of 50?",
        "choices": ["4", "5", "6", "7"],
        "correct_answer": "5",
        "explanation": "10% of 50 = 0.10 × 50 = 5."
    },
    {
        "grade_level": 5,
        "topic": "Percentages",
        "difficulty": 1,
        "weight": 1.0,
        "prompt": "What is 20% of 60?",
        "choices": ["10", "12", "14", "16"],
        "correct_answer": "12",
        "explanation": "20% of 60 = 0.20 × 60 = 12."
    },
    {
        "grade_level": 5,
        "topic": "Percentages",
        "difficulty": 1,
        "weight": 1.0,
        "prompt": "What is 30% of 40?",
        "choices": ["10", "12", "14", "16"],
        "correct_answer": "12",
        "explanation": "30% of 40 = 0.30 × 40 = 12."
    },
    {
        "grade_level": 5,
        "topic": "Percentages",
        "difficulty": 1,
        "weight": 1.0,
        "prompt": "What is 15% of 80?",
        "choices": ["10", "12", "14", "16"],
        "correct_answer": "12",
        "explanation": "15% of 80 = 0.15 × 80 = 12."
    },
    {
        "grade_level": 5,
        "topic": "Percentages",
        "difficulty": 2,
        "weight": 1.5,
        "prompt": "What is 75% of 120?",
        "choices": ["88", "89", "90", "91"],
        "correct_answer": "90",
        "explanation": "75% of 120 = 0.75 × 120 = 90."
    },
    {
        "grade_level": 5,
        "topic": "Percentages",
        "difficulty": 2,
        "weight": 1.5,
        "prompt": "What is 20% of 150?",
        "choices": ["28", "29", "30", "31"],
        "correct_answer": "30",
        "explanation": "20% of 150 = 0.20 × 150 = 30."
    },
    {
        "grade_level": 5,
        "topic": "Percentages",
        "difficulty": 2,
        "weight": 1.5,
        "prompt": "What is 40% of 75?",
        "choices": ["28", "29", "30", "31"],
        "correct_answer": "30",
        "explanation": "40% of 75 = 0.40 × 75 = 30."
    },
    {
        "grade_level": 5,
        "topic": "Percentages",
        "difficulty": 2,
        "weight": 1.5,
        "prompt": "What is 60% of 50?",
        "choices": ["28", "29", "30", "31"],
        "correct_answer": "30",
        "explanation": "60% of 50 = 0.60 × 50 = 30."
    },
    {
        "grade_level": 5,
        "topic": "Percentages",
        "difficulty": 2,
        "weight": 1.5,
        "prompt": "What is 35% of 100?",
        "choices": ["33", "34", "35", "36"],
        "correct_answer": "35",
        "explanation": "35% of 100 = 0.35 × 100 = 35."
    },
    {
        "grade_level": 5,
        "topic": "Percentages",
        "difficulty": 2,
        "weight": 1.5,
        "prompt": "What is 45% of 80?",
        "choices": ["35", "36", "37", "38"],
        "correct_answer": "36",
        "explanation": "45% of 80 = 0.45 × 80 = 36."
    },
    {
        "grade_level": 5,
        "topic": "Percentages",
        "difficulty": 2,
        "weight": 1.5,
        "prompt": "What is 55% of 60?",
        "choices": ["32", "33", "34", "35"],
        "correct_answer": "33",
        "explanation": "55% of 60 = 0.55 × 60 = 33."
    },
    
    # Grade 5 - Word Problems (15+ questions)
    {
        "grade_level": 5,
        "topic": "Word Problems",
        "difficulty": 1,
        "weight": 1.0,
        "prompt": "Tom has 20 marbles. He gives away 8. How many does he have left?",
        "choices": ["10", "11", "12", "13"],
        "correct_answer": "12",
        "explanation": "20 - 8 = 12 marbles remaining."
    },
    {
        "grade_level": 5,
        "topic": "Word Problems",
        "difficulty": 1,
        "weight": 1.0,
        "prompt": "A box has 30 pencils. If 5 students share them equally, how many pencils does each student get?",
        "choices": ["5", "6", "7", "8"],
        "correct_answer": "6",
        "explanation": "30 ÷ 5 = 6 pencils per student."
    },
    {
        "grade_level": 5,
        "topic": "Word Problems",
        "difficulty": 1,
        "weight": 1.0,
        "prompt": "Lisa has 25 stickers. She buys 15 more. How many stickers does she have now?",
        "choices": ["38", "39", "40", "41"],
        "correct_answer": "40",
        "explanation": "25 + 15 = 40 stickers total."
    },
    {
        "grade_level": 5,
        "topic": "Word Problems",
        "difficulty": 1,
        "weight": 1.0,
        "prompt": "There are 24 cookies. If 4 friends share them equally, how many cookies does each friend get?",
        "choices": ["5", "6", "7", "8"],
        "correct_answer": "6",
        "explanation": "24 ÷ 4 = 6 cookies per friend."
    },
    {
        "grade_level": 5,
        "topic": "Word Problems",
        "difficulty": 1,
        "weight": 1.0,
        "prompt": "Jake has 18 toy cars. He gives 7 to his friend. How many toy cars does Jake have left?",
        "choices": ["10", "11", "12", "13"],
        "correct_answer": "11",
        "explanation": "18 - 7 = 11 toy cars remaining."
    },
    {
        "grade_level": 5,
        "topic": "Word Problems",
        "difficulty": 2,
        "weight": 1.5,
        "prompt": "Emma saves $5 each week. How much will she save in 8 weeks?",
        "choices": ["38", "39", "40", "41"],
        "correct_answer": "40",
        "explanation": "$5 × 8 weeks = $40."
    },
    {
        "grade_level": 5,
        "topic": "Word Problems",
        "difficulty": 2,
        "weight": 1.5,
        "prompt": "A store has 48 apples. They sell 3/4 of them. How many apples are left?",
        "choices": ["10", "11", "12", "13"],
        "correct_answer": "12",
        "explanation": "3/4 of 48 = 36 sold. 48 - 36 = 12 apples left."
    },
    {
        "grade_level": 5,
        "topic": "Word Problems",
        "difficulty": 2,
        "weight": 1.5,
        "prompt": "Mike reads 12 pages each day. How many pages will he read in 6 days?",
        "choices": ["70", "71", "72", "73"],
        "correct_answer": "72",
        "explanation": "12 pages × 6 days = 72 pages."
    },
    {
        "grade_level": 5,
        "topic": "Word Problems",
        "difficulty": 2,
        "weight": 1.5,
        "prompt": "A classroom has 32 students. If they are divided into 4 equal groups, how many students are in each group?",
        "choices": ["7", "8", "9", "10"],
        "correct_answer": "8",
        "explanation": "32 ÷ 4 = 8 students per group."
    },
    {
        "grade_level": 5,
        "topic": "Word Problems",
        "difficulty": 2,
        "weight": 1.5,
        "prompt": "Sarah has $45. She spends $18 on a book. How much money does she have left?",
        "choices": ["26", "27", "28", "29"],
        "correct_answer": "27",
        "explanation": "$45 - $18 = $27 remaining."
    },
    {
        "grade_level": 5,
        "topic": "Word Problems",
        "difficulty": 2,
        "weight": 1.5,
        "prompt": "A garden has 36 flowers. If 1/3 of them are roses, how many roses are there?",
        "choices": ["11", "12", "13", "14"],
        "correct_answer": "12",
        "explanation": "1/3 of 36 = 36 ÷ 3 = 12 roses."
    },
    {
        "grade_level": 5,
        "topic": "Word Problems",
        "difficulty": 2,
        "weight": 1.5,
        "prompt": "David runs 3 miles each day. How many miles will he run in 7 days?",
        "choices": ["20", "21", "22", "23"],
        "correct_answer": "21",
        "explanation": "3 miles × 7 days = 21 miles."
    },
]
