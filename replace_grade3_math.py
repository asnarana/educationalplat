"""
Script to replace Grade 3 Math questions with NC EOG Released Form questions.
Run this script to:
1. Delete existing Grade 3 Math questions
2. Add 40 new EOG questions with images

Usage:
    python replace_grade3_math.py
"""

import os
import sys

# Add the project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import text, inspect
from app.db import SessionLocal, engine
from app.models import Question, Base


def ensure_image_url_column():
    """Add image_url column to questions table if it doesn't exist."""
    try:
        with engine.connect() as conn:
            # Try to add the column - Oracle will error if it already exists
            conn.execute(text("ALTER TABLE questions ADD image_url VARCHAR2(500)"))
            conn.commit()
        print("[OK] Added image_url column to questions table")
    except Exception as e:
        if "ORA-01430" in str(e) or "already exists" in str(e).lower() or "name is already used" in str(e).lower():
            print("[OK] image_url column already exists")
        else:
            print(f"[WARN] Could not add image_url column: {e}")

# Images available in grade3mathimages folder
IMAGES_AVAILABLE = {1, 2, 4, 6, 7, 8, 10, 12, 13, 14, 20, 21, 22, 25, 27, 28, 29, 32, 34, 35, 38}

# Topic mapping based on NC Standard domains
# NC.3.G.1 → Geometry
# NC.3.NF.* → Fractions  
# NC.3.OA.* → Operations (Algebraic Thinking)
# NC.3.NBT.* → Number Operations (Base Ten)
# NC.3.MD.* → Measurement & Data

GRADE3_MATH_QUESTIONS = [
    # Q1 - NC.3.G.1 - Geometry - HAS IMAGE
    {
        "question_num": 1,
        "topic": "Geometry",
        "difficulty": 1,
        "prompt": "Which group of figures contains only quadrilaterals?",
        "choices": ["A", "B", "C", "D"],
        "correct_answer": "B",
        "explanation": "Quadrilaterals are polygons with exactly 4 sides. Group B contains only 4-sided shapes."
    },
    # Q2 - NC.3.NF.3 - Fractions - HAS IMAGE
    {
        "question_num": 2,
        "topic": "Fractions",
        "difficulty": 1,
        "prompt": "Which figure shows a shaded amount that is equivalent to the fraction 2/6?",
        "choices": ["A", "B", "C", "D"],
        "correct_answer": "A",
        "explanation": "2/6 simplifies to 1/3. Figure A shows 1/3 shaded, which is equivalent to 2/6."
    },
    # Q3 - NC.3.OA.3 - Operations - NO IMAGE
    {
        "question_num": 3,
        "topic": "Operations",
        "difficulty": 1,
        "prompt": "Which equation is true when r = 7?\n\nA) 6 = 30 ÷ r\nB) 7 = 54 ÷ r\nC) 7 = 49 ÷ r\nD) 9 = 72 ÷ r",
        "choices": ["A", "B", "C", "D"],
        "correct_answer": "C",
        "explanation": "When r = 7: 49 ÷ 7 = 7, so C is correct. Check: A) 30÷7≈4.3, B) 54÷7≈7.7, D) 72÷7≈10.3"
    },
    # Q4 - NC.3.MD.1 - Measurement - HAS IMAGE
    {
        "question_num": 4,
        "topic": "Measurement",
        "difficulty": 2,
        "prompt": "Vanessa spent 15 minutes in the library. She left the library at 11:30 a.m. What letter on the number line represents the time Vanessa arrived at the library?",
        "choices": ["M", "N", "O", "P"],
        "correct_answer": "M",
        "explanation": "If she left at 11:30 and spent 15 minutes, she arrived at 11:15. Point M is at 11:15 on the number line."
    },
    # Q5 - NC.3.NBT.2 - Number Operations - NO IMAGE
    {
        "question_num": 5,
        "topic": "Number Operations",
        "difficulty": 2,
        "prompt": "Jacquelyn's mom drove 265 miles on Thursday and 478 miles on Friday. She has 143 miles more to drive on Saturday. About how many miles will she drive in all?",
        "choices": ["700", "800", "900", "1,000"],
        "correct_answer": "900",
        "explanation": "265 + 478 + 143 = 886 miles. Rounded to the nearest hundred, this is about 900 miles."
    },
    # Q6 - NC.3.NF.3 - Fractions - HAS IMAGE
    {
        "question_num": 6,
        "topic": "Fractions",
        "difficulty": 1,
        "prompt": "What fraction of this figure is shaded?",
        "choices": ["1/4", "1/5", "3/4", "2/5"],
        "correct_answer": "1/4",
        "explanation": "The figure is divided into 4 equal parts, and 1 part is shaded. So 1/4 is shaded."
    },
    # Q7 - NC.3.MD.7 - Measurement - HAS IMAGE
    {
        "question_num": 7,
        "topic": "Measurement",
        "difficulty": 1,
        "prompt": "This figure is 4 units long and 4 units wide. Which measurements describe a rectangle that has the same area as the figure?",
        "choices": ["5 units long and 3 units wide", "8 units long and 2 units wide", "10 units long and 6 units wide", "12 units long and 4 units wide"],
        "correct_answer": "8 units long and 2 units wide",
        "explanation": "Area of original = 4 × 4 = 16 square units. Choice B: 8 × 2 = 16 square units. Same area!"
    },
    # Q8 - NC.3.NF.1 - Fractions - HAS IMAGE
    {
        "question_num": 8,
        "topic": "Fractions",
        "difficulty": 1,
        "prompt": "Each of the triangles below has three sides of equal length. In which choice does the triangle have 1/6 of its area shaded?",
        "choices": ["A", "B", "C", "D"],
        "correct_answer": "D",
        "explanation": "Triangle D is divided into 6 equal parts with 1 part shaded, representing 1/6."
    },
    # Q9 - NC.3.NBT.2 - Number Operations - NO IMAGE
    {
        "question_num": 9,
        "topic": "Number Operations",
        "difficulty": 1,
        "prompt": "There are 500 seats in a movie theater. There are 362 people sitting in the seats. How many seats are empty?",
        "choices": ["262 seats", "152 seats", "148 seats", "138 seats"],
        "correct_answer": "138 seats",
        "explanation": "500 - 362 = 138 empty seats."
    },
    # Q10 - NC.3.NF.4 - Fractions - HAS IMAGE
    {
        "question_num": 10,
        "topic": "Fractions",
        "difficulty": 1,
        "prompt": "Which figure could be added to the diagram to make it true?",
        "choices": ["A", "B", "C", "D"],
        "correct_answer": "A",
        "explanation": "Figure A completes the fraction comparison correctly."
    },
    # Q11 - NC.3.OA.8 - Operations - NO IMAGE
    {
        "question_num": 11,
        "topic": "Operations",
        "difficulty": 2,
        "prompt": "Sam's goal is to walk 36 miles.\n• He walks 4 miles each day.\n• He has walked for 6 days.\n\nWhich equation can be used to find how many more miles, n, Sam still needs to walk to reach his goal?",
        "choices": ["3 × 5 + n = 36", "4 × 6 + n = 36", "4 × 6 × n = 36", "9 × 4 + n = 36"],
        "correct_answer": "4 × 6 + n = 36",
        "explanation": "Sam walked 4 miles × 6 days = 24 miles. So 24 + n = 36, which is 4 × 6 + n = 36."
    },
    # Q12 - NC.3.NF.1 - Fractions - HAS IMAGE
    {
        "question_num": 12,
        "topic": "Fractions",
        "difficulty": 2,
        "prompt": "Amy shaded some parts of this poster. What fraction of the area of the poster is shaded?",
        "choices": ["2/3", "3/8", "5/3", "5/8"],
        "correct_answer": "5/8",
        "explanation": "The poster is divided into 8 equal parts, and 5 parts are shaded. So 5/8 is shaded."
    },
    # Q13 - NC.3.MD.1 - Measurement - HAS IMAGE
    {
        "question_num": 13,
        "topic": "Measurement",
        "difficulty": 1,
        "prompt": "Eric leaves school at the time shown. He arrives home 25 minutes later. At what time does Eric get home?",
        "choices": ["2:50", "3:15", "3:40", "4:05"],
        "correct_answer": "3:40",
        "explanation": "The clock shows 3:15. Adding 25 minutes: 3:15 + 25 = 3:40."
    },
    # Q14 - NC.3.NF.2 - Fractions - HAS IMAGE
    {
        "question_num": 14,
        "topic": "Fractions",
        "difficulty": 2,
        "prompt": "Which number line shows point M at 3/8?",
        "choices": ["A", "B", "C", "D"],
        "correct_answer": "B",
        "explanation": "Number line B correctly shows point M positioned at 3/8 between 0 and 1."
    },
    # Q15 - NC.3.OA.3 - Operations - NO IMAGE
    {
        "question_num": 15,
        "topic": "Operations",
        "difficulty": 2,
        "prompt": "Chantelle has 56 stickers. She will give all of the stickers to 8 friends. Each friend will receive the same number of stickers. Which equation will help Chantelle decide how many stickers, n, to give to each friend?",
        "choices": ["n ÷ 8 = 56", "8 × n = 56", "56 – n = 48", "56 – 8 = n"],
        "correct_answer": "8 × n = 56",
        "explanation": "If each of 8 friends gets n stickers, then 8 × n = 56 total stickers."
    },
    # Q16 - NC.3.NBT.3 - Number Operations - NO IMAGE
    {
        "question_num": 16,
        "topic": "Number Operations",
        "difficulty": 2,
        "prompt": "A farmer planted 5 different types of tomatoes. He planted 40 of each type. How many tomatoes did the farmer plant?",
        "choices": ["20", "45", "200", "250"],
        "correct_answer": "200",
        "explanation": "5 types × 40 of each = 200 tomatoes total."
    },
    # Q17 - NC.3.OA.8 - Operations - NO IMAGE
    {
        "question_num": 17,
        "topic": "Operations",
        "difficulty": 2,
        "prompt": "Daniel's goal is to walk 100 miles.\n• He walks 5 miles every day.\n• He has walked for 7 days.\n• Daniel still needs to walk k more miles for his goal.\n\nWhich equation could be used to find how many more miles, k, Daniel will have to walk to meet his goal?",
        "choices": ["100 = 5 × 7 + k", "100 = 5 × 7 × k", "100 = 5 × 7 – k", "100 = 5 + 7 + k"],
        "correct_answer": "100 = 5 × 7 + k",
        "explanation": "Daniel walked 5 × 7 = 35 miles. So 35 + k = 100, which is 100 = 5 × 7 + k."
    },
    # Q18 - NC.3.NBT.2 - Number Operations - NO IMAGE
    {
        "question_num": 18,
        "topic": "Number Operations",
        "difficulty": 1,
        "prompt": "There were 823 people attending a baseball game after 37 people left. How many people were at the game before the people left?",
        "choices": ["786", "850", "860", "896"],
        "correct_answer": "860",
        "explanation": "If 823 people remain after 37 left, then 823 + 37 = 860 people were there before."
    },
    # Q19 - NC.3.OA.3 - Operations - NO IMAGE
    {
        "question_num": 19,
        "topic": "Operations",
        "difficulty": 1,
        "prompt": "What value for M makes this equation true?\n\nM ÷ 7 = 7",
        "choices": ["1", "14", "42", "49"],
        "correct_answer": "49",
        "explanation": "If M ÷ 7 = 7, then M = 7 × 7 = 49."
    },
    # Q20 - NC.3.MD.8 - Measurement - HAS IMAGE
    {
        "question_num": 20,
        "topic": "Measurement",
        "difficulty": 1,
        "prompt": "The perimeter of this pentagon is 52 cm. What is the missing length?",
        "choices": ["6 cm", "8 cm", "9 cm", "10 cm"],
        "correct_answer": "8 cm",
        "explanation": "Perimeter = 52 cm. Given sides: 10 + 10 + 12 + 12 = 44 cm. Missing side = 52 - 44 = 8 cm."
    },
    # Q21 - NC.3.NF.3 - Fractions - HAS IMAGE
    {
        "question_num": 21,
        "topic": "Fractions",
        "difficulty": 2,
        "prompt": "A fraction of this circle is shaded. Which circle has an equal fraction shaded?",
        "choices": ["A", "B", "C", "D"],
        "correct_answer": "A",
        "explanation": "Circle A has the same fraction shaded as the original circle."
    },
    # Q22 - NC.3.NF.2 - Fractions - HAS IMAGE
    {
        "question_num": 22,
        "topic": "Fractions",
        "difficulty": 1,
        "prompt": "What fraction is represented by point L on this number line?",
        "choices": ["1/2", "2/3", "2/4", "3/4"],
        "correct_answer": "3/4",
        "explanation": "Point L is positioned at 3/4 on the number line between 0 and 1."
    },
    # Q23 - NC.3.OA.2 - Operations - NO IMAGE
    {
        "question_num": 23,
        "topic": "Operations",
        "difficulty": 2,
        "prompt": "Carlos and his friends collected 72 rocks. Each person collected 9 rocks. How many people collected rocks?",
        "choices": ["8", "9", "63", "81"],
        "correct_answer": "8",
        "explanation": "72 rocks ÷ 9 rocks per person = 8 people."
    },
    # Q24 - NC.3.OA.8 - Operations - NO IMAGE
    {
        "question_num": 24,
        "topic": "Operations",
        "difficulty": 2,
        "prompt": "Jasmine wrote 2 pages in her journal every day for 7 days. Her journal has 32 total pages. How many pages does Jasmine have left to write before her journal will be full?",
        "choices": ["14 pages", "18 pages", "25 pages", "30 pages"],
        "correct_answer": "18 pages",
        "explanation": "Jasmine wrote 2 × 7 = 14 pages. Pages left = 32 - 14 = 18 pages."
    },
    # Q25 - NC.3.NF.1 - Fractions - HAS IMAGE
    {
        "question_num": 25,
        "topic": "Fractions",
        "difficulty": 2,
        "prompt": "What fraction of the area of this figure is shaded?",
        "choices": ["1/4", "1/6", "1/8", "1/10"],
        "correct_answer": "1/8",
        "explanation": "The figure is divided into 8 equal parts, and 1 part is shaded. So 1/8 is shaded."
    },
    # Q26 - NC.3.OA.8 - Operations - NO IMAGE
    {
        "question_num": 26,
        "topic": "Operations",
        "difficulty": 2,
        "prompt": "A truck rental company charges $20 per day plus a onetime fee of $40 to rent a truck. A person needs to rent a truck for 9 days. How much will the person pay to rent the truck?",
        "choices": ["$540", "$380", "$220", "$180"],
        "correct_answer": "$220",
        "explanation": "Cost = $40 (one-time) + ($20 × 9 days) = $40 + $180 = $220."
    },
    # Q27 - NC.3.NF.3 - Fractions - HAS IMAGE
    {
        "question_num": 27,
        "topic": "Fractions",
        "difficulty": 1,
        "prompt": "Which circle is 3/4 shaded?",
        "choices": ["A", "B", "C", "D"],
        "correct_answer": "D",
        "explanation": "Circle D is divided into 4 equal parts with 3 parts shaded, representing 3/4."
    },
    # Q28 - NC.3.MD.3 - Measurement - HAS IMAGE
    {
        "question_num": 28,
        "topic": "Measurement",
        "difficulty": 2,
        "prompt": "A third-grade class voted for their favorite subject, as shown. How many more students voted for math than science?",
        "choices": ["7", "6", "4", "3"],
        "correct_answer": "6",
        "explanation": "Count the pictograph symbols. Math has 6 more votes than Science."
    },
    # Q29 - NC.3.NF.2 - Fractions - HAS IMAGE
    {
        "question_num": 29,
        "topic": "Fractions",
        "difficulty": 2,
        "prompt": "Which letter has a value of 3/4 on this number line?",
        "choices": ["W", "X", "Y", "Z"],
        "correct_answer": "Z",
        "explanation": "Letter Z is positioned at 3/4 on the number line between 0 and 1."
    },
    # Q30 - NC.3.G.1 - Geometry - NO IMAGE
    {
        "question_num": 30,
        "topic": "Geometry",
        "difficulty": 1,
        "prompt": "Sarah drew a shape. It was a quadrilateral, and all the sides were the same length. Which shape did Sarah draw?",
        "choices": ["pentagon", "rhombus", "trapezoid", "triangle"],
        "correct_answer": "rhombus",
        "explanation": "A rhombus is a quadrilateral (4 sides) with all sides equal length."
    },
    # Q31 - NC.3.OA.3 - Operations - NO IMAGE
    {
        "question_num": 31,
        "topic": "Operations",
        "difficulty": 1,
        "prompt": "A train makes 9 stops each day. How many days will it take for the train to make 63 stops?",
        "choices": ["7", "9", "54", "72"],
        "correct_answer": "7",
        "explanation": "63 stops ÷ 9 stops per day = 7 days."
    },
    # Q32 - NC.3.MD.3 - Measurement - HAS IMAGE
    {
        "question_num": 32,
        "topic": "Measurement",
        "difficulty": 2,
        "prompt": "Four friends were playing a game. John and Bill were on Team 1. Susie and Amy were on Team 2. They made a graph to show how many points each person scored. How many more points did Team 2 score than Team 1?",
        "choices": ["5", "6", "11", "16"],
        "correct_answer": "6",
        "explanation": "Add points for each team from the graph. Team 2 scored 6 more points than Team 1."
    },
    # Q33 - NC.3.NBT.2 - Number Operations - NO IMAGE
    {
        "question_num": 33,
        "topic": "Number Operations",
        "difficulty": 2,
        "prompt": "A school collects canned food for charity.\n• Third-graders collected 327 cans.\n• Third-graders collected 138 more cans than fourth-graders.\n\nHow many cans did the fourth grade collect?",
        "choices": ["289", "211", "189", "111"],
        "correct_answer": "189",
        "explanation": "Third-graders collected 138 MORE than fourth-graders. So 327 - 138 = 189 cans for fourth grade."
    },
    # Q34 - NC.3.OA.9 - Operations - HAS IMAGE
    {
        "question_num": 34,
        "topic": "Operations",
        "difficulty": 2,
        "prompt": "Which expression can be used to find the missing number in this multiplication table?",
        "choices": ["63 + 9", "45 – 9", "63 – 15", "45 + 9"],
        "correct_answer": "45 + 9",
        "explanation": "Looking at the pattern in the multiplication table, 45 + 9 = 54, which is the missing number."
    },
    # Q35 - NC.3.NF.4 - Fractions - HAS IMAGE
    {
        "question_num": 35,
        "topic": "Fractions",
        "difficulty": 1,
        "prompt": "Donna shaded this rectangle. Michael's rectangle is the same size. He shaded less than Donna. Which choice could be the shaded fraction of Michael's rectangle?",
        "choices": ["1/3", "2/3", "3/3", "4/3"],
        "correct_answer": "1/3",
        "explanation": "If Michael shaded less than Donna, he must have shaded a smaller fraction. 1/3 is less than Donna's shaded amount."
    },
    # Q36 - NC.3.MD.8 - Measurement - NO IMAGE
    {
        "question_num": 36,
        "topic": "Measurement",
        "difficulty": 2,
        "prompt": "Ellen is comparing two rectangles.\n• Rectangle P is 5 inches long and 1 inch wide.\n• Rectangle Q is 4 inches long and 2 inches wide.\n\nWhich statement correctly compares the areas and perimeters of the rectangles?",
        "choices": ["The rectangles have equal areas, and rectangle P has a greater perimeter.", "The rectangles have equal areas, and rectangle Q has a greater perimeter.", "The rectangles have equal perimeters, and rectangle P has a greater area.", "The rectangles have equal perimeters, and rectangle Q has a greater area."],
        "correct_answer": "The rectangles have equal perimeters, and rectangle Q has a greater area.",
        "explanation": "P: Area=5, Perimeter=12. Q: Area=8, Perimeter=12. Equal perimeters, Q has greater area."
    },
    # Q37 - NC.3.OA.1 - Operations - NO IMAGE
    {
        "question_num": 37,
        "topic": "Operations",
        "difficulty": 2,
        "prompt": "Lacey has a bookcase with 6 shelves.\n• She used only 4 of the shelves.\n• She put 6 books on each shelf.\n\nWhich choice shows another way Lacey could put the same number of books in the bookcase, but this time, using all of the shelves?",
        "choices": ["2 books on each shelf", "4 books on each shelf", "10 books on each shelf", "24 books on each shelf"],
        "correct_answer": "4 books on each shelf",
        "explanation": "Lacey has 4 × 6 = 24 books. To use all 6 shelves: 24 ÷ 6 = 4 books per shelf."
    },
    # Q38 - NC.3.MD.2 - Measurement - HAS IMAGE
    {
        "question_num": 38,
        "topic": "Measurement",
        "difficulty": 1,
        "prompt": "This shows a pencil and a ruler. What is the length of the pencil?",
        "choices": ["5 1/2 inches", "6 inches", "6 1/4 inches", "6 1/2 inches"],
        "correct_answer": "6 1/4 inches",
        "explanation": "Reading the ruler, the pencil measures 6 and 1/4 inches."
    },
    # Q39 - NC.3.OA.8 - Operations - NO IMAGE
    {
        "question_num": 39,
        "topic": "Operations",
        "difficulty": 2,
        "prompt": "Tanya baked 125 cookies for a bake sale. Mark baked 67 fewer cookies than Tanya. How many cookies did they bake in all?",
        "choices": ["183", "192", "250", "267"],
        "correct_answer": "183",
        "explanation": "Mark baked 125 - 67 = 58 cookies. Total = 125 + 58 = 183 cookies."
    },
    # Q40 - NC.3.OA.1 - Operations - NO IMAGE
    {
        "question_num": 40,
        "topic": "Operations",
        "difficulty": 1,
        "prompt": "Which answer choice shows two correct ways to arrange 21 pennies in equal rows?",
        "choices": ["2 rows of 1, or 1 row of 2", "7 rows of 3, or 3 rows of 7", "8 rows of 3, or 3 rows of 8", "20 rows of 1, or 1 row of 20"],
        "correct_answer": "7 rows of 3, or 3 rows of 7",
        "explanation": "21 = 7 × 3 = 3 × 7. Both arrangements give 21 pennies in equal rows."
    },
    # ADDITIONAL GEOMETRY QUESTIONS (Q41-Q48)
    # Q41 - NC.3.G.1 - Geometry - NO IMAGE
    {
        "question_num": 41,
        "topic": "Geometry",
        "difficulty": 1,
        "prompt": "Which shape has exactly 6 sides?",
        "choices": ["pentagon", "hexagon", "octagon", "quadrilateral"],
        "correct_answer": "hexagon",
        "explanation": "A hexagon has exactly 6 sides. Pentagon has 5, octagon has 8, and quadrilateral has 4."
    },
    # Q42 - NC.3.G.1 - Geometry - NO IMAGE
    {
        "question_num": 42,
        "topic": "Geometry",
        "difficulty": 1,
        "prompt": "A rectangle has 4 right angles. Which other shape also has 4 right angles?",
        "choices": ["triangle", "square", "pentagon", "hexagon"],
        "correct_answer": "square",
        "explanation": "A square has 4 right angles (90 degrees each), just like a rectangle."
    },
    # Q43 - NC.3.G.1 - Geometry - NO IMAGE
    {
        "question_num": 43,
        "topic": "Geometry",
        "difficulty": 1,
        "prompt": "Which shape is NOT a quadrilateral?",
        "choices": ["rectangle", "square", "triangle", "trapezoid"],
        "correct_answer": "triangle",
        "explanation": "A triangle has 3 sides. Quadrilaterals have 4 sides. Rectangle, square, and trapezoid are all quadrilaterals."
    },
    # Q44 - NC.3.G.1 - Geometry - NO IMAGE
    {
        "question_num": 44,
        "topic": "Geometry",
        "difficulty": 2,
        "prompt": "Marcus drew a shape with 4 sides. Two sides are parallel, but the other two sides are not parallel. What shape did Marcus draw?",
        "choices": ["rectangle", "rhombus", "trapezoid", "square"],
        "correct_answer": "trapezoid",
        "explanation": "A trapezoid has exactly one pair of parallel sides. Rectangles, rhombuses, and squares have two pairs of parallel sides."
    },
    # Q45 - NC.3.G.1 - Geometry - NO IMAGE
    {
        "question_num": 45,
        "topic": "Geometry",
        "difficulty": 1,
        "prompt": "How many sides does an octagon have?",
        "choices": ["5", "6", "7", "8"],
        "correct_answer": "8",
        "explanation": "An octagon has 8 sides. The prefix 'octa' means 8."
    },
    # Q46 - NC.3.G.1 - Geometry - NO IMAGE
    {
        "question_num": 46,
        "topic": "Geometry",
        "difficulty": 2,
        "prompt": "Which statement is true about all rectangles?",
        "choices": ["All sides are the same length", "They have exactly 3 sides", "They have 4 right angles", "They have no parallel sides"],
        "correct_answer": "They have 4 right angles",
        "explanation": "All rectangles have 4 right angles (90 degrees each). Not all rectangles have equal sides - that's a square."
    },
    # Q47 - NC.3.G.1 - Geometry - NO IMAGE
    {
        "question_num": 47,
        "topic": "Geometry",
        "difficulty": 1,
        "prompt": "Which shape has exactly 5 sides?",
        "choices": ["quadrilateral", "pentagon", "hexagon", "triangle"],
        "correct_answer": "pentagon",
        "explanation": "A pentagon has exactly 5 sides. The prefix 'penta' means 5."
    },
    # Q48 - NC.3.G.1 - Geometry - NO IMAGE
    {
        "question_num": 48,
        "topic": "Geometry",
        "difficulty": 2,
        "prompt": "Emma says that a square is also a rectangle. Is Emma correct?",
        "choices": ["No, squares and rectangles are completely different", "No, rectangles have longer sides", "Yes, a square has 4 right angles like a rectangle", "Yes, but only if the square is very large"],
        "correct_answer": "Yes, a square has 4 right angles like a rectangle",
        "explanation": "A square is a special type of rectangle. It has 4 right angles and 4 sides, with all sides equal length."
    },
]


def get_math_topics():
    """Get list of math topic keywords to identify math questions."""
    return ['geometry', 'fractions', 'operations', 'number operations', 'measurement',
            'addition', 'subtraction', 'multiplication', 'division']


def replace_grade3_math_questions():
    """Replace all Grade 3 Math questions with EOG questions."""
    # Ensure image_url column exists
    ensure_image_url_column()
    
    db = SessionLocal()
    
    try:
        # First, delete existing Grade 3 Math questions
        # Identify math topics
        math_keywords = get_math_topics()
        
        existing_questions = db.query(Question).filter(
            Question.grade_level == 3
        ).all()
        
        # Filter for math questions
        math_questions_to_delete = []
        for q in existing_questions:
            topic_lower = q.topic.lower()
            if any(keyword in topic_lower for keyword in math_keywords):
                math_questions_to_delete.append(q)
        
        deleted_count = len(math_questions_to_delete)
        
        if deleted_count > 0:
            for q in math_questions_to_delete:
                db.delete(q)
            db.commit()
            print(f"[OK] Deleted {deleted_count} existing Grade 3 Math questions")
        else:
            print("[INFO] No existing Grade 3 Math questions to delete")
        
        # Now add the 40 new EOG questions
        added_count = 0
        for q_data in GRADE3_MATH_QUESTIONS:
            question_num = q_data["question_num"]
            
            # Determine image URL
            image_url = None
            if question_num in IMAGES_AVAILABLE:
                image_url = f"/static/grade3mathimages/q{question_num}.png"
            
            question = Question(
                grade_level=3,
                topic=q_data["topic"],
                difficulty=q_data["difficulty"],
                weight=1.5 if q_data["difficulty"] == 2 else 1.0,
                prompt=q_data["prompt"],
                choices=q_data["choices"],
                correct_answer=q_data["correct_answer"],
                explanation=q_data["explanation"],
                image_url=image_url
            )
            db.add(question)
            added_count += 1
        
        db.commit()
        print(f"[OK] Added {added_count} Grade 3 Math EOG questions")
        
        # Count questions with images
        with_images = len([q for q in GRADE3_MATH_QUESTIONS if q["question_num"] in IMAGES_AVAILABLE])
        print(f"   - {with_images} questions have images")
        print(f"   - {added_count - with_images} questions have no images")
        
        # Print topic breakdown
        topic_counts = {}
        for q in GRADE3_MATH_QUESTIONS:
            topic = q["topic"]
            topic_counts[topic] = topic_counts.get(topic, 0) + 1
        
        print("\nTopic breakdown:")
        for topic, count in sorted(topic_counts.items()):
            print(f"   - {topic}: {count} questions")
        
        return {
            "deleted": deleted_count,
            "added": added_count,
            "with_images": with_images
        }
        
    except Exception as e:
        db.rollback()
        print(f"[ERROR] {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("=" * 60)
    print("Grade 3 Math Question Replacement Script")
    print("=" * 60)
    print()
    
    # Check for --force flag to skip confirmation
    force = "--force" in sys.argv or "-f" in sys.argv
    
    if not force:
        print("This script will:")
        print("1. Delete ALL existing Grade 3 Math questions")
        print("2. Add 40 NC EOG Released Form questions")
        print("3. Link images from grade3mathimages folder")
        print()
        print("Use --force or -f to skip this prompt.")
        print()
        
        try:
            response = input("Continue? (y/n): ").strip().lower()
            if response != 'y':
                print("Cancelled.")
                sys.exit(0)
        except EOFError:
            # Handle piped input
            pass
    
    print()
    result = replace_grade3_math_questions()
    print()
    print("=" * 60)
    print("Complete!")
    print(f"Deleted: {result['deleted']} questions")
    print(f"Added: {result['added']} questions")
    print(f"With images: {result['with_images']} questions")
    print("=" * 60)
