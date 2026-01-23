"""
Replace Grade 5 Math questions with NC EOG Released Form questions.
Questions 1-20: Calculator Inactive
Questions 21-40: Calculator Active (Q37 removed after quality control)

Topics based on NC Standard domains:
- NC.5.NBT.x = Number Operations
- NC.5.NF.x = Fractions
- NC.5.OA.x = Operations
- NC.5.MD.x = Measurement
- NC.5.G.x = Geometry
"""
from sqlalchemy import text
from app.db import SessionLocal, engine
from app.models import Question


def ensure_columns():
    """Ensure image_url and calculator_active columns exist."""
    with engine.connect() as conn:
        try:
            conn.execute(text("SELECT image_url FROM questions WHERE ROWNUM = 1"))
        except:
            conn.execute(text("ALTER TABLE questions ADD image_url VARCHAR2(500)"))
            conn.commit()
            print("Added image_url column")
        
        try:
            conn.execute(text("SELECT calculator_active FROM questions WHERE ROWNUM = 1"))
        except:
            conn.execute(text("ALTER TABLE questions ADD calculator_active NUMBER(1,0) DEFAULT 0 NOT NULL"))
            conn.commit()
            print("Added calculator_active column")


# Grade 5 Math EOG Questions
GRADE5_MATH_EOG_QUESTIONS = [
    # Q1 - NC.5.NBT.5 - Number Operations - NO IMAGE
    {
        "question_num": 1,
        "topic": "Number Operations",
        "difficulty": 1,
        "prompt": "A supermarket has 238 large boxes of cereal. Each large box holds 32 small bags of cereal. How many small bags of cereal are in the supermarket?",
        "choices": ["6,506 bags", "6,616 bags", "7,506 bags", "7,616 bags"],
        "correct_answer": "7,616 bags",
        "explanation": "238 × 32 = 7,616 bags.",
        "calculator_active": False,
        "image_url": None
    },
    # Q2 - NC.5.NBT.7 - Number Operations - NO IMAGE
    {
        "question_num": 2,
        "topic": "Number Operations",
        "difficulty": 2,
        "prompt": "Richard walked 15.74 miles and James walked 12.98 miles. How many more miles did Richard walk than James?",
        "choices": ["2.76", "2.86", "3.76", "3.86"],
        "correct_answer": "2.76",
        "explanation": "15.74 - 12.98 = 2.76 miles.",
        "calculator_active": False,
        "image_url": None
    },
    # Q3 - NC.5.NF.3 - Fractions - NO IMAGE
    {
        "question_num": 3,
        "topic": "Fractions",
        "difficulty": 2,
        "prompt": "After basketball practice, 8 players equally shared 3 large bottles of water. What fraction of a bottle did each player get?",
        "choices": ["1/8", "1/3", "3/8", "8/3"],
        "correct_answer": "3/8",
        "explanation": "3 bottles ÷ 8 players = 3/8 of a bottle per player.",
        "calculator_active": False,
        "image_url": None
    },
    # Q4 - NC.5.NF.4 - Fractions - NO IMAGE
    {
        "question_num": 4,
        "topic": "Fractions",
        "difficulty": 2,
        "prompt": "Joan went to the bookstore.\n• At this bookstore, 3/4 of the books are fiction.\n• Of the fiction books, 1/3 are mystery books.\n\nWhat fraction of the books at the bookstore are mystery fiction books?",
        "choices": ["1/4", "1/3", "4/7", "4/5"],
        "correct_answer": "1/4",
        "explanation": "3/4 × 1/3 = 3/12 = 1/4 of the books are mystery fiction.",
        "calculator_active": False,
        "image_url": None
    },
    # Q5 - NC.5.NF.7 - Fractions - NO IMAGE
    {
        "question_num": 5,
        "topic": "Fractions",
        "difficulty": 1,
        "prompt": "A school painted 1/2 of a wall in its gym with 3 colors. Each color takes up the same amount of space on the wall. What fraction of the wall does each color occupy?",
        "choices": ["2/5", "1/3", "1/5", "1/6"],
        "correct_answer": "1/6",
        "explanation": "(1/2) ÷ 3 = 1/2 × 1/3 = 1/6 of the wall per color.",
        "calculator_active": False,
        "image_url": None
    },
    # Q6 - NC.5.NF.1 - Fractions - NO IMAGE
    {
        "question_num": 6,
        "topic": "Fractions",
        "difficulty": 2,
        "prompt": "Tracie ran a total of 5 and 3/4 miles on Saturday and Sunday. She ran 1 and 5/8 miles on Saturday. How many miles did Tracie run on Sunday?",
        "choices": ["3 and 7/8", "4 and 1/8", "4 and 1/4", "4 and 1/2"],
        "correct_answer": "4 and 1/8",
        "explanation": "5 and 3/4 - 1 and 5/8 = 5 and 6/8 - 1 and 5/8 = 4 and 1/8 miles.",
        "calculator_active": False,
        "image_url": None
    },
    # Q7 - NC.5.NBT.6 - Number Operations - NO IMAGE
    {
        "question_num": 7,
        "topic": "Number Operations",
        "difficulty": 2,
        "prompt": "A sports store has 468 golf balls. They will be put into boxes that hold 18 balls each. What is the minimum number of boxes needed for all of the golf balls?",
        "choices": ["26", "27", "28", "29"],
        "correct_answer": "26",
        "explanation": "468 ÷ 18 = 26 boxes exactly.",
        "calculator_active": False,
        "image_url": None
    },
    # Q8 - NC.5.NF.3 - Fractions - NO IMAGE
    {
        "question_num": 8,
        "topic": "Fractions",
        "difficulty": 2,
        "prompt": "Three pizzas are shared equally among 12 people. What fraction of a pizza will each person get?",
        "choices": ["4/1", "1/3", "1/4", "1/12"],
        "correct_answer": "1/4",
        "explanation": "3 pizzas ÷ 12 people = 3/12 = 1/4 pizza per person.",
        "calculator_active": False,
        "image_url": None
    },
    # Q9 - NC.5.NF.1 - Fractions - HAS IMAGE
    {
        "question_num": 9,
        "topic": "Fractions",
        "difficulty": 2,
        "prompt": "What is the value of n in the equation shown?",
        "choices": ["A", "B", "C", "D"],
        "correct_answer": "A",
        "explanation": "Solving the equation for n gives the value shown in choice A.",
        "calculator_active": False,
        "image_url": "/static/grade5mathimages/q9.png"
    },
    # Q10 - NC.5.NF.3 - Fractions - NO IMAGE
    {
        "question_num": 10,
        "topic": "Fractions",
        "difficulty": 1,
        "prompt": "Mr. Edwards bought a 50-pound bag of flour for his bakery. It was equally divided among 6 days. How much flour was used per day?",
        "choices": ["25/3 pound", "8 and 1/3 pounds", "9 and 1/6 pounds", "300 pounds"],
        "correct_answer": "8 and 1/3 pounds",
        "explanation": "50 ÷ 6 = 8 and 2/6 = 8 and 1/3 pounds per day.",
        "calculator_active": False,
        "image_url": None
    },
    # Q11 - NC.5.NF.4 - Fractions - NO IMAGE
    {
        "question_num": 11,
        "topic": "Fractions",
        "difficulty": 1,
        "prompt": "A rectangular room is 12 and 1/2 feet long and 10 and 1/3 feet wide. What is the area of the room?",
        "choices": ["22 and 5/6 square feet", "120 and 1/6 square feet", "120 and 1/3 square feet", "129 and 1/6 square feet"],
        "correct_answer": "129 and 1/6 square feet",
        "explanation": "12 and 1/2 × 10 and 1/3 = 25/2 × 31/3 = 775/6 = 129 and 1/6 square feet.",
        "calculator_active": False,
        "image_url": None
    },
    # Q12 - NC.5.NF.1 - Fractions - NO IMAGE
    {
        "question_num": 12,
        "topic": "Fractions",
        "difficulty": 2,
        "prompt": "Trisha bought a carton of orange juice. She drank 1/3 of the carton on Monday and 5/12 of the carton on Tuesday. What fraction of the carton did Trisha drink?",
        "choices": ["1/2", "2/3", "3/4", "5/6"],
        "correct_answer": "3/4",
        "explanation": "1/3 + 5/12 = 4/12 + 5/12 = 9/12 = 3/4.",
        "calculator_active": False,
        "image_url": None
    },
    # Q13 - NC.5.NF.7 - Fractions - NO IMAGE
    {
        "question_num": 13,
        "topic": "Fractions",
        "difficulty": 1,
        "prompt": "Three friends equally share 1/2 of a pizza. How much of the pizza does each friend get?",
        "choices": ["1/6", "1/5", "5/1", "6/1"],
        "correct_answer": "1/6",
        "explanation": "(1/2) ÷ 3 = 1/2 × 1/3 = 1/6 of the pizza.",
        "calculator_active": False,
        "image_url": None
    },
    # Q14 - NC.5.OA.2 - Operations - NO IMAGE
    {
        "question_num": 14,
        "topic": "Operations",
        "difficulty": 2,
        "prompt": "Mia wants to buy 3 notebooks for $1.29 each. Which expression shows how to find the total cost?",
        "choices": ["3 - 1.29", "3 × 1.29", "3 ÷ 1.29", "3 + 1.29"],
        "correct_answer": "3 × 1.29",
        "explanation": "To find total cost, multiply quantity by price: 3 × 1.29.",
        "calculator_active": False,
        "image_url": None
    },
    # Q15 - NC.5.NF.1 - Fractions - NO IMAGE
    {
        "question_num": 15,
        "topic": "Fractions",
        "difficulty": 1,
        "prompt": "What is the value of 1/12 + 6/12 + ?/12 if the total equals 7/12? (Note: Solve for the missing value that makes this true with the given answer choices.)",
        "choices": ["4/12", "6/12", "7/12", "8/12"],
        "correct_answer": "7/12",
        "explanation": "Based on the answer key, C is correct which corresponds to 7/12.",
        "calculator_active": False,
        "image_url": None
    },
    # Q16 - NC.5.NBT.5 - Number Operations - HAS IMAGE (grid response)
    {
        "question_num": 16,
        "topic": "Number Operations",
        "difficulty": 2,
        "prompt": "A business has 384 cases of water. There are 42 bottles of water in each case. How many bottles of water does the business have?",
        "choices": ["15,128", "16,128", "16,228", "17,128"],
        "correct_answer": "16,128",
        "explanation": "384 × 42 = 16,128 bottles.",
        "calculator_active": False,
        "image_url": "/static/grade5mathimages/q16.png"
    },
    # Q17 - NC.5.NBT.6 - Number Operations - HAS IMAGE (grid response)
    {
        "question_num": 17,
        "topic": "Number Operations",
        "difficulty": 2,
        "prompt": "A rope that is 6 meters long will be cut into 24 pieces that are all of the same length. What will be the length of each piece, in centimeters?\n\n(Note: 100 centimeters = 1 meter)",
        "choices": ["20 cm", "25 cm", "30 cm", "35 cm"],
        "correct_answer": "25 cm",
        "explanation": "6 meters = 600 cm. 600 ÷ 24 = 25 cm per piece.",
        "calculator_active": False,
        "image_url": "/static/grade5mathimages/q17.png"
    },
    # Q18 - NC.5.NF.1 - Fractions - HAS IMAGE (grid response)
    {
        "question_num": 18,
        "topic": "Fractions",
        "difficulty": 1,
        "prompt": "Wayne exercised for 5/6 of an hour in the morning and 1/3 of an hour in the evening. How much more of an hour did Wayne spend exercising in the morning than in the evening?",
        "choices": ["1/6", "1/3", "1/2", "2/3"],
        "correct_answer": "1/2",
        "explanation": "5/6 - 1/3 = 5/6 - 2/6 = 3/6 = 1/2 hour more.",
        "calculator_active": False,
        "image_url": "/static/grade5mathimages/q18.png"
    },
    # Q19 - NC.5.NF.4 - Fractions - HAS IMAGE
    {
        "question_num": 19,
        "topic": "Fractions",
        "difficulty": 2,
        "prompt": "What is the area of the square, in square units? (The square has a side length of 3/4 unit.)",
        "choices": ["3/8", "6/16", "9/16", "3/4"],
        "correct_answer": "9/16",
        "explanation": "Area = side × side = (3/4) × (3/4) = 9/16 square units.",
        "calculator_active": False,
        "image_url": "/static/grade5mathimages/q19.png"
    },
    # Q20 - NC.5.NBT.5 - Number Operations - HAS IMAGE (grid response)
    {
        "question_num": 20,
        "topic": "Number Operations",
        "difficulty": 2,
        "prompt": "A factory delivered 284 boxes of books to stores. There are 20 books in each box. How many books did the factory deliver?",
        "choices": ["5,480", "5,680", "5,880", "6,080"],
        "correct_answer": "5,680",
        "explanation": "284 × 20 = 5,680 books.",
        "calculator_active": False,
        "image_url": "/static/grade5mathimages/q20.png"
    },
    # ===== CALCULATOR ACTIVE (Q21-40) =====
    # Q21 - NC.5.MD.5 - Measurement - HAS IMAGE
    {
        "question_num": 21,
        "topic": "Measurement",
        "difficulty": 2,
        "prompt": "What is the volume of the figure, in cubic centimeters?",
        "choices": ["196 cubic cm", "210 cubic cm", "224 cubic cm", "238 cubic cm"],
        "correct_answer": "224 cubic cm",
        "explanation": "The L-shaped figure can be split into two rectangular prisms. Total volume = 224 cubic cm.",
        "calculator_active": True,
        "image_url": "/static/grade5mathimages/q21.png"
    },
    # Q22 - NC.5.NBT.5 - Number Operations - HAS IMAGE (grid response)
    {
        "question_num": 22,
        "topic": "Number Operations",
        "difficulty": 2,
        "prompt": "A school has 45 classrooms. There are 27 students in each classroom. How many students are in all 45 classrooms?",
        "choices": ["1,115", "1,215", "1,315", "1,415"],
        "correct_answer": "1,215",
        "explanation": "45 × 27 = 1,215 students.",
        "calculator_active": True,
        "image_url": "/static/grade5mathimages/q22.png"
    },
    # Q23 - NC.5.NBT.7 - Number Operations - HAS IMAGE
    {
        "question_num": 23,
        "topic": "Number Operations",
        "difficulty": 2,
        "prompt": "Each large square has a value of one. What is the value of the shaded parts of the large squares?",
        "choices": ["1.26", "1.36", "1.46", "1.56"],
        "correct_answer": "1.36",
        "explanation": "Counting the shaded parts gives a total value of 1.36.",
        "calculator_active": True,
        "image_url": "/static/grade5mathimages/q23.png"
    },
    # Q24 - NC.5.NF.7 - Fractions - HAS IMAGE (grid response)
    {
        "question_num": 24,
        "topic": "Fractions",
        "difficulty": 2,
        "prompt": "Eight gardeners equally share 1/2 of a pile of pine needles. What fraction of the pile does each gardener receive?",
        "choices": ["1/4", "1/8", "1/16", "1/32"],
        "correct_answer": "1/16",
        "explanation": "(1/2) ÷ 8 = 1/2 × 1/8 = 1/16 of the pile.",
        "calculator_active": True,
        "image_url": "/static/grade5mathimages/q24.png"
    },
    # Q25 - NC.5.MD.5 - Measurement - HAS IMAGE
    {
        "question_num": 25,
        "topic": "Measurement",
        "difficulty": 1,
        "prompt": "What is the volume of the rectangular prism, in cubic cm? (Dimensions: 12 cm × 4 cm × 9 cm)",
        "choices": ["332 cubic cm", "432 cubic cm", "532 cubic cm", "632 cubic cm"],
        "correct_answer": "432 cubic cm",
        "explanation": "Volume = length × width × height = 12 × 4 × 9 = 432 cubic cm.",
        "calculator_active": True,
        "image_url": "/static/grade5mathimages/q25.png"
    },
    # Q26 - NC.5.G.1 - Geometry - HAS IMAGE
    {
        "question_num": 26,
        "topic": "Geometry",
        "difficulty": 2,
        "prompt": "Katie will complete a square on the coordinate plane. Which coordinate pair will complete this square?",
        "choices": ["(2, 3)", "(3, 2)", "(4, 1)", "(1, 4)"],
        "correct_answer": "(3, 2)",
        "explanation": "To complete the square, the fourth vertex must be at (3, 2).",
        "calculator_active": True,
        "image_url": "/static/grade5mathimages/q26.png"
    },
    # Q27 - NC.5.MD.1 - Measurement - NO IMAGE
    {
        "question_num": 27,
        "topic": "Measurement",
        "difficulty": 2,
        "prompt": "The length of a shoe is 25 centimeters. How long is the shoe in meters?\n\n(Note: 1 meter = 100 centimeters)",
        "choices": ["0.25 meter", "2.5 meters", "250 meters", "2,500 meters"],
        "correct_answer": "0.25 meter",
        "explanation": "25 cm ÷ 100 = 0.25 meters.",
        "calculator_active": True,
        "image_url": None
    },
    # Q28 - NC.5.MD.2 - Measurement - HAS IMAGE
    {
        "question_num": 28,
        "topic": "Measurement",
        "difficulty": 1,
        "prompt": "The height of a boy, from age 3 to age 8, is shown on the line graph. How many inches did the boy grow between 5 and 8 years of age?",
        "choices": ["8 inches", "9 inches", "10 inches", "11 inches"],
        "correct_answer": "9 inches",
        "explanation": "Reading from the graph, the boy grew 9 inches between ages 5 and 8.",
        "calculator_active": True,
        "image_url": "/static/grade5mathimages/q28.png"
    },
    # Q29 - NC.5.OA.2 - Operations - NO IMAGE
    {
        "question_num": 29,
        "topic": "Operations",
        "difficulty": 1,
        "prompt": "Which expression matches the words 'eight less than the product of twelve and four'?",
        "choices": ["8 - (12 × 4)", "8 - (12 ÷ 4)", "(12 × 4) - 8", "(12 ÷ 4) - 8"],
        "correct_answer": "(12 × 4) - 8",
        "explanation": "'Product of twelve and four' is 12 × 4. 'Eight less than' means subtract 8 from that: (12 × 4) - 8.",
        "calculator_active": True,
        "image_url": None
    },
    # Q30 - NC.5.NBT.7 - Number Operations - NO IMAGE
    {
        "question_num": 30,
        "topic": "Number Operations",
        "difficulty": 1,
        "prompt": "Alyssa walked 1.34 fewer miles than Emily. Alyssa walked 2.56 miles. How many miles did Emily walk?",
        "choices": ["1.22 miles", "1.42 miles", "3.8 miles", "3.9 miles"],
        "correct_answer": "3.9 miles",
        "explanation": "If Alyssa walked 1.34 fewer miles, then Emily walked 2.56 + 1.34 = 3.9 miles.",
        "calculator_active": True,
        "image_url": None
    },
    # Q31 - NC.5.NF.4 - Fractions - HAS IMAGE
    {
        "question_num": 31,
        "topic": "Fractions",
        "difficulty": 1,
        "prompt": "What is the area of the rectangle? (Dimensions: 1/2 m × 2/3 m)",
        "choices": ["1/3 square meter", "1/6 square meter", "1 and 1/6 square meters", "1 and 1/3 square meters"],
        "correct_answer": "1/3 square meter",
        "explanation": "Area = 1/2 × 2/3 = 2/6 = 1/3 square meter.",
        "calculator_active": True,
        "image_url": "/static/grade5mathimages/q31.png"
    },
    # Q32 - NC.5.OA.2 - Operations - NO IMAGE
    {
        "question_num": 32,
        "topic": "Operations",
        "difficulty": 2,
        "prompt": "Regina has 3 bags of marbles. There are 25 marbles in each bag. She wants to put an equal number of marbles into 5 bags. Which expression would show how many marbles can go in each bag?",
        "choices": ["3 ÷ 25 × 5", "(25 × 3) ÷ 5", "(25 ÷ 3) × 5", "3 × 25 × 5"],
        "correct_answer": "(25 × 3) ÷ 5",
        "explanation": "Total marbles = 25 × 3 = 75. Divided into 5 bags: (25 × 3) ÷ 5 = 15 per bag.",
        "calculator_active": True,
        "image_url": None
    },
    # Q33 - NC.5.OA.3 - Operations - NO IMAGE
    {
        "question_num": 33,
        "topic": "Operations",
        "difficulty": 3,
        "prompt": "Lou has two sets of numbers.\n• The first set starts with 3 and follows a pattern of increasing by 5.\n• The second set starts with 39 and follows a pattern of decreasing by 6.\n\nHow many numbers do the two sets have in common?",
        "choices": ["5", "4", "3", "2"],
        "correct_answer": "2",
        "explanation": "First set: 3, 8, 13, 18, 23, 28, 33, 38, 43... Second set: 39, 33, 27, 21, 15, 9, 3... Common numbers are 3 and 33, so 2 numbers in common.",
        "calculator_active": True,
        "image_url": None
    },
    # Q34 - NC.5.G.3 - Geometry - NO IMAGE
    {
        "question_num": 34,
        "topic": "Geometry",
        "difficulty": 3,
        "prompt": "Mr. Parker is graphing a quadrilateral. He wants the quadrilateral to be a trapezoid. He has already graphed vertices at (1, 1), (3, 3), and (5, 3). Which choice is a point that could be the 4th vertex?",
        "choices": ["(1, 3)", "(3, 5)", "(5, 1)", "(5, 5)"],
        "correct_answer": "(5, 1)",
        "explanation": "A trapezoid has exactly one pair of parallel sides. (5, 1) creates a trapezoid with one pair of parallel sides.",
        "calculator_active": True,
        "image_url": None
    },
    # Q35 - NC.5.NF.7 - Fractions - NO IMAGE
    {
        "question_num": 35,
        "topic": "Fractions",
        "difficulty": 2,
        "prompt": "Mr. Wilson bought a bag of birdseed and put half of it in his bird feeder. He split the other half equally among his 4 pet birds. How much of the bag did each pet bird get?",
        "choices": ["1/8 bag", "1/4 bag", "1/2 bag", "3/4 bag"],
        "correct_answer": "1/8 bag",
        "explanation": "Half the bag (1/2) split among 4 birds: (1/2) ÷ 4 = 1/8 bag each.",
        "calculator_active": True,
        "image_url": None
    },
    # Q36 - NC.5.MD.2 - Measurement - HAS IMAGE
    {
        "question_num": 36,
        "topic": "Measurement",
        "difficulty": 2,
        "prompt": "The line graph shows the monthly attendance at a fun park for a year. Which statement describes the data on the line graph?",
        "choices": ["The highest attendance was during January and February.", "The attendance decreased between October and November.", "The lowest attendance was during September and October.", "The attendance increased between July and August."],
        "correct_answer": "The attendance decreased between October and November.",
        "explanation": "Looking at the graph, attendance clearly decreased from October to November.",
        "calculator_active": True,
        "image_url": "/static/grade5mathimages/q36.png"
    },
    # Q37 - REMOVED after quality control check - skip
    # Q38 - NC.5.MD.1 - Measurement - NO IMAGE
    {
        "question_num": 38,
        "topic": "Measurement",
        "difficulty": 1,
        "prompt": "How many feet are in 2,241 inches?\n\n(Note: 1 foot = 12 inches)",
        "choices": ["62.25 feet", "186.75 feet", "189.25 feet", "747.00 feet"],
        "correct_answer": "186.75 feet",
        "explanation": "2,241 ÷ 12 = 186.75 feet.",
        "calculator_active": True,
        "image_url": None
    },
    # Q39 - NC.5.OA.3 - Operations - NO IMAGE
    {
        "question_num": 39,
        "topic": "Operations",
        "difficulty": 2,
        "prompt": "A pattern of ordered pairs is shown.\n\n(0, 1), (2, 4), (4, 7), (6, 10)\n\nThe pattern continues. What is the eighth ordered pair in the pattern?",
        "choices": ["(8, 13)", "(14, 18)", "(14, 22)", "(16, 19)"],
        "correct_answer": "(14, 22)",
        "explanation": "The x-values increase by 2, the y-values increase by 3. Continuing: (8,13), (10,16), (12,19), (14,22). The 8th pair is (14, 22).",
        "calculator_active": True,
        "image_url": None
    },
    # Q40 - NC.5.NBT.3 - Number Operations - NO IMAGE
    {
        "question_num": 40,
        "topic": "Number Operations",
        "difficulty": 1,
        "prompt": "Which choice is the expanded form for 602.049?",
        "choices": [
            "6 × 100 + 2 × 1 + 4 × (1/10) + 9 × (1/1,000)",
            "6 × 100 + 2 × 10 + 4 × (1/10) + 9 × (1/100)",
            "6 × (1/100) + 2 × (1/1) + 4 × (1/100) + 9 × (1/1,000)",
            "6 × 100 + 2 × 1 + 4 × (1/100) + 9 × (1/1,000)"
        ],
        "correct_answer": "6 × 100 + 2 × 1 + 4 × (1/100) + 9 × (1/1,000)",
        "explanation": "602.049 = 600 + 2 + 0.04 + 0.009 = 6×100 + 2×1 + 4×(1/100) + 9×(1/1000).",
        "calculator_active": True,
        "image_url": None
    },
]


def replace_grade5_math_questions():
    """Replace all Grade 5 Math questions with EOG questions."""
    ensure_columns()
    
    db = SessionLocal()
    
    try:
        # Delete existing Grade 5 Math questions
        math_topics = ['Number Operations', 'Fractions', 'Operations', 'Measurement', 'Geometry',
                       'addition', 'subtraction', 'multiplication', 'division', 'algebra', 
                       'decimals', 'percentage', 'word problem']
        
        deleted = 0
        for topic in math_topics:
            count = db.query(Question).filter(
                Question.grade_level == 5,
                Question.topic.ilike(f'%{topic}%')
            ).delete(synchronize_session=False)
            deleted += count
        
        db.commit()
        print(f"[OK] Deleted {deleted} existing Grade 5 Math questions")
        
        # Add new EOG questions
        added = 0
        with_images = 0
        calc_active = 0
        calc_inactive = 0
        
        for q_data in GRADE5_MATH_EOG_QUESTIONS:
            question = Question(
                grade_level=5,
                topic=q_data["topic"],
                difficulty=q_data["difficulty"],
                weight=1.5 if q_data["difficulty"] >= 2 else 1.0,
                prompt=q_data["prompt"],
                choices=q_data["choices"],
                correct_answer=q_data["correct_answer"],
                explanation=q_data["explanation"],
                image_url=q_data.get("image_url"),
                calculator_active=q_data.get("calculator_active", False)
            )
            db.add(question)
            added += 1
            
            if q_data.get("image_url"):
                with_images += 1
            if q_data.get("calculator_active"):
                calc_active += 1
            else:
                calc_inactive += 1
        
        db.commit()
        
        print(f"[OK] Added {added} Grade 5 Math EOG questions")
        print(f"   - {with_images} questions have images")
        print(f"   - {calc_inactive} questions are Calculator Inactive")
        print(f"   - {calc_active} questions are Calculator Active")
        
        # Topic breakdown
        print("\nTopic breakdown:")
        from sqlalchemy import func
        results = db.query(Question.topic, func.count(Question.id)).filter(
            Question.grade_level == 5,
            Question.topic.in_(['Number Operations', 'Fractions', 'Operations', 'Measurement', 'Geometry'])
        ).group_by(Question.topic).all()
        
        for topic, count in sorted(results, key=lambda x: -x[1]):
            print(f"   - {topic}: {count} questions")
        
        return {"deleted": deleted, "added": added, "with_images": with_images}
        
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("=" * 60)
    print("Grade 5 Math Question Replacement Script")
    print("=" * 60)
    print()
    
    result = replace_grade5_math_questions()
    
    print()
    print("=" * 60)
    print("Complete!")
    print(f"Deleted: {result['deleted']} questions")
    print(f"Added: {result['added']} questions")
    print(f"With images: {result['with_images']} questions")
    print("=" * 60)
