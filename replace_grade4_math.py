"""
Replace Grade 4 Math questions with NC EOG Released Form questions.
Based on 2018-2019 NC EOG Grade 4 Mathematics Released Form.

Questions 1-20: Calculator Inactive
Questions 21-40: Calculator Active

Images are in grade4mathimages/ folder.
"""
from app.db import SessionLocal, engine
from app.models import Question
from sqlalchemy import text, inspect

def ensure_columns_exist():
    """Ensure image_url and calculator_active columns exist."""
    inspector = inspect(engine)
    columns = [col['name'].upper() for col in inspector.get_columns('questions')]
    
    if 'IMAGE_URL' not in columns:
        with engine.connect() as conn:
            conn.execute(text("ALTER TABLE questions ADD image_url VARCHAR2(500)"))
            conn.commit()
            print("[OK] Added image_url column")
    
    if 'CALCULATOR_ACTIVE' not in columns:
        with engine.connect() as conn:
            conn.execute(text("ALTER TABLE questions ADD calculator_active NUMBER(1)"))
            conn.commit()
            print("[OK] Added calculator_active column")


# Topic mapping based on NC standards:
# NC.4.NBT = Number Operations (Numbers and Operations in Base Ten)
# NC.4.NF = Fractions (Numbers - Fractions)
# NC.4.OA = Operations (Operations and Algebraic Thinking)
# NC.4.G = Geometry
# NC.4.MD = Measurement (Measurement and Data)

GRADE4_MATH_QUESTIONS = [
    # ============ CALCULATOR INACTIVE (Q1-20) ============
    # Q1 - NC.4.NBT.6 - Division - NO IMAGE
    {
        "question_num": 1,
        "topic": "Number Operations",
        "difficulty": 1,
        "prompt": "There are 594 children participating in a county science fair. They are put into groups of six children. How many groups will participate?",
        "choices": ["60", "98", "99", "150"],
        "correct_answer": "99",
        "explanation": "594 ÷ 6 = 99 groups.",
        "calculator_active": False,
        "image_url": None
    },
    # Q2 - NC.4.G.2 - Geometry - HAS IMAGE
    {
        "question_num": 2,
        "topic": "Geometry",
        "difficulty": 1,
        "prompt": "Which figure has at least one acute angle, one obtuse angle, and one right angle?",
        "choices": ["A", "B", "C", "D"],
        "correct_answer": "D",
        "explanation": "Figure D has an acute angle (less than 90°), an obtuse angle (greater than 90°), and a right angle (exactly 90°).",
        "calculator_active": False,
        "image_url": "/static/grade4mathimages/q2.png"
    },
    # Q3 - NC.4.NF.4 - Fractions - NO IMAGE
    {
        "question_num": 3,
        "topic": "Fractions",
        "difficulty": 2,
        "prompt": "Each day of the work week, Mr. Harbin uses 3/4 of a gallon of gas. Which estimate best describes the amount of gas Mr. Harbin would use in a five-day work week?",
        "choices": ["less than one gallon", "between 2 and 3 gallons", "between 3 and 4 gallons", "more than 4 gallons"],
        "correct_answer": "between 3 and 4 gallons",
        "explanation": "3/4 × 5 = 15/4 = 3.75 gallons, which is between 3 and 4 gallons.",
        "calculator_active": False,
        "image_url": None
    },
    # Q4 - NC.4.NF.3 - Fractions - NO IMAGE
    {
        "question_num": 4,
        "topic": "Fractions",
        "difficulty": 2,
        "prompt": "The body and head of a fox measure 19 and 4/5 inches, and its tail measures 10 and 4/5 inches. What is the total length of the fox?",
        "choices": ["30 and 8/10 inches", "30 and 3/5 inches", "29 and 8/10 inches", "29 and 3/5 inches"],
        "correct_answer": "30 and 3/5 inches",
        "explanation": "19 and 4/5 + 10 and 4/5 = 29 and 8/5 = 30 and 3/5 inches.",
        "calculator_active": False,
        "image_url": None
    },
    # Q5 - NC.4.NBT.6 - Division - NO IMAGE
    {
        "question_num": 5,
        "topic": "Number Operations",
        "difficulty": 1,
        "prompt": "There are 136 students in the school cafeteria. There are 8 students sitting at each table. How many tables are in the cafeteria?",
        "choices": ["12 tables", "16 tables", "17 tables", "18 tables"],
        "correct_answer": "17 tables",
        "explanation": "136 ÷ 8 = 17 tables.",
        "calculator_active": False,
        "image_url": None
    },
    # Q6 - NC.4.OA.4 - Operations (Prime/Composite) - NO IMAGE
    {
        "question_num": 6,
        "topic": "Operations",
        "difficulty": 1,
        "prompt": "Which list contains exactly 2 prime numbers and 2 composite numbers?",
        "choices": ["13, 14, 15, 16", "2, 4, 5, 6", "7, 8, 9, 10", "25, 26, 27, 29"],
        "correct_answer": "2, 4, 5, 6",
        "explanation": "2 and 5 are prime; 4 and 6 are composite.",
        "calculator_active": False,
        "image_url": None
    },
    # Q7 - NC.4.NBT.4 - Number Operations - NO IMAGE
    {
        "question_num": 7,
        "topic": "Number Operations",
        "difficulty": 2,
        "prompt": "A cafeteria manager ordered 1,251 cartons of milk on Monday.\n• He also ordered cartons of milk on Thursday.\n• He ordered 879 more cartons on Monday than on Thursday.\n\nHow many cartons did the manager order on Thursday?",
        "choices": ["372", "428", "1,628", "2,130"],
        "correct_answer": "372",
        "explanation": "1,251 - 879 = 372 cartons on Thursday.",
        "calculator_active": False,
        "image_url": None
    },
    # Q8 - NC.4.NF.6 - Fractions/Decimals - NO IMAGE
    {
        "question_num": 8,
        "topic": "Fractions",
        "difficulty": 1,
        "prompt": "Dana ran on Monday and Tuesday.\n• She ran 5 and 2/10 km on Monday.\n• She ran 4 and 6/100 km on Tuesday.\n\nHow far did Dana run altogether?",
        "choices": ["9 and 8/10 km", "9 and 8/100 km", "9 and 6/10 km", "9 and 26/100 km"],
        "correct_answer": "9 and 26/100 km",
        "explanation": "5 and 2/10 = 5 and 20/100, so 5 and 20/100 + 4 and 6/100 = 9 and 26/100 km.",
        "calculator_active": False,
        "image_url": None
    },
    # Q9 - NC.4.NF.1 - Fractions - HAS IMAGE
    {
        "question_num": 9,
        "topic": "Fractions",
        "difficulty": 2,
        "prompt": "What fraction is shaded in each of these models?",
        "choices": ["2/3", "3/4", "2/6", "4/8"],
        "correct_answer": "2/3",
        "explanation": "Both models show 2/3 shaded (equivalent fractions).",
        "calculator_active": False,
        "image_url": "/static/grade4mathimages/q9.png"
    },
    # Q10 - NC.4.NF.2 - Fractions - HAS IMAGE
    {
        "question_num": 10,
        "topic": "Fractions",
        "difficulty": 2,
        "prompt": "A group of friends were each completing a project of the same size. This table shows how much of the project each friend has completed.\n\nMichael: 2/3, James: 1/2, Leilani: 6/8, Soumi: 4/6\n\nWhich friends have completed an equal amount of their project?",
        "choices": ["Michael and Soumi", "James and Soumi", "James and Leilani", "Michael and Leilani"],
        "correct_answer": "Michael and Soumi",
        "explanation": "2/3 = 4/6, so Michael and Soumi completed the same fraction.",
        "calculator_active": False,
        "image_url": "/static/grade4mathimages/q10.png"
    },
    # Q11 - NC.4.NBT.5 - Multiplication - NO IMAGE
    {
        "question_num": 11,
        "topic": "Number Operations",
        "difficulty": 1,
        "prompt": "Pablo was getting ready for a bike race.\n• He rode his bike each day for 32 days.\n• He rode his bike for 45 minutes each day.\n\nHow many minutes did Pablo spend riding his bike to get ready for the race?",
        "choices": ["288", "1,360", "1,431", "1,440"],
        "correct_answer": "1,440",
        "explanation": "32 × 45 = 1,440 minutes.",
        "calculator_active": False,
        "image_url": None
    },
    # Q12 - NC.4.OA.1 - Operations - NO IMAGE
    {
        "question_num": 12,
        "topic": "Operations",
        "difficulty": 2,
        "prompt": "There are twice as many women on a bus as there are men. There are 24 women on the bus. What is the total number of men and women on the bus?",
        "choices": ["12", "36", "48", "72"],
        "correct_answer": "36",
        "explanation": "24 women, 24 ÷ 2 = 12 men. Total = 24 + 12 = 36.",
        "calculator_active": False,
        "image_url": None
    },
    # Q13 - NC.4.NF.1 - Fractions - NO IMAGE
    {
        "question_num": 13,
        "topic": "Fractions",
        "difficulty": 2,
        "prompt": "Patrick made 12 cookies. Patrick's sister will eat 4 of the cookies. What fraction of the cookies will be left?",
        "choices": ["1/4", "1/3", "2/3", "3/4"],
        "correct_answer": "2/3",
        "explanation": "12 - 4 = 8 cookies left. 8/12 = 2/3.",
        "calculator_active": False,
        "image_url": None
    },
    # Q14 - NC.4.NBT.5 - Multiplication - NO IMAGE
    {
        "question_num": 14,
        "topic": "Number Operations",
        "difficulty": 1,
        "prompt": "Each classroom at a school has 24 desks. There are 18 classrooms in the school. How many desks are at the school?",
        "choices": ["444 desks", "432 desks", "424 desks", "402 desks"],
        "correct_answer": "432 desks",
        "explanation": "24 × 18 = 432 desks.",
        "calculator_active": False,
        "image_url": None
    },
    # Q15 - NC.4.NF.4 - Fractions - NO IMAGE
    {
        "question_num": 15,
        "topic": "Fractions",
        "difficulty": 2,
        "prompt": "Four friends each ate 2/3 of an apple. How many apples did the four friends eat in all?",
        "choices": ["8/12 of an apple", "6/7 of an apple", "2 apples", "2 and 2/3 apples"],
        "correct_answer": "2 and 2/3 apples",
        "explanation": "4 × 2/3 = 8/3 = 2 and 2/3 apples.",
        "calculator_active": False,
        "image_url": None
    },
    # Q16 - NC.4.OA.3 - Operations (Divisibility) - NO IMAGE
    {
        "question_num": 16,
        "topic": "Operations",
        "difficulty": 3,
        "prompt": "A farmer has an equal number of cows in 3 different fields on his farm. Which choice could be the total number of cows?",
        "choices": ["112", "178", "207", "266"],
        "correct_answer": "207",
        "explanation": "207 ÷ 3 = 69, which divides evenly. The others don't divide evenly by 3.",
        "calculator_active": False,
        "image_url": None
    },
    # Q17 - NC.4.NBT.6 - Division - NO IMAGE
    {
        "question_num": 17,
        "topic": "Number Operations",
        "difficulty": 1,
        "prompt": "There are 128 pencils to be put into boxes. Each box can hold 9 pencils. How many boxes can be completely filled?",
        "choices": ["14", "15", "104", "105"],
        "correct_answer": "14",
        "explanation": "128 ÷ 9 = 14 remainder 2. So 14 boxes can be completely filled.",
        "calculator_active": False,
        "image_url": None
    },
    # Q18 - NC.4.NF.1 - Fractions - HAS IMAGE
    {
        "question_num": 18,
        "topic": "Fractions",
        "difficulty": 2,
        "prompt": "Which two of these squares have the same amount shaded?",
        "choices": ["P and Q", "P and S", "Q and R", "R and S"],
        "correct_answer": "R and S",
        "explanation": "Squares R and S both show equivalent fractions shaded.",
        "calculator_active": False,
        "image_url": "/static/grade4mathimages/q18.png"
    },
    # Q19 - NC.4.NBT.6 - Division - NO IMAGE
    {
        "question_num": 19,
        "topic": "Number Operations",
        "difficulty": 1,
        "prompt": "A farmer has 348 apples and wants to put them into baskets. He will put 6 apples into each basket. How many baskets will the farmer use?",
        "choices": ["56", "57", "58", "59"],
        "correct_answer": "58",
        "explanation": "348 ÷ 6 = 58 baskets.",
        "calculator_active": False,
        "image_url": None
    },
    # Q20 - NC.4.NF.3 - Fractions - NO IMAGE
    {
        "question_num": 20,
        "topic": "Fractions",
        "difficulty": 2,
        "prompt": "Maria is making a snack mix. For the recipe, she needs:\n• 2/4 cup peanuts\n• 1/4 cup raisins\n• 2/4 cup chocolate chips\n\nMaria will double the recipe. What is the total amount of peanuts, raisins, and chocolate chips she will need?",
        "choices": ["5/12 cup", "10/8 cups", "9/4 cups", "10/4 cups"],
        "correct_answer": "10/4 cups",
        "explanation": "Single recipe: 2/4 + 1/4 + 2/4 = 5/4. Doubled: 5/4 × 2 = 10/4 cups.",
        "calculator_active": False,
        "image_url": None
    },
    
    # ============ CALCULATOR ACTIVE (Q21-40) ============
    # Q21 - NC.4.MD.6 - Measurement (Angles) - HAS IMAGE
    {
        "question_num": 21,
        "topic": "Measurement",
        "difficulty": 2,
        "prompt": "RVU is a straight line and ∠TVU has a measure of 40° in this figure. What is the measure of ∠SVT?",
        "choices": ["40°", "45°", "50°", "90°"],
        "correct_answer": "50°",
        "explanation": "∠SVU = 90° (right angle). ∠TVU = 40°. So ∠SVT = 90° - 40° = 50°.",
        "calculator_active": True,
        "image_url": "/static/grade4mathimages/q21.png"
    },
    # Q22 - NC.4.NBT.5 - Multiplication (Array) - HAS IMAGE
    {
        "question_num": 22,
        "topic": "Number Operations",
        "difficulty": 2,
        "prompt": "Michael is solving 23 × 42 using this rectangular array. What is the missing number Michael needs to solve this problem?",
        "choices": ["12", "43", "70", "120"],
        "correct_answer": "120",
        "explanation": "The array shows partial products: 800, 40, 6, and the missing value is 3 × 40 = 120.",
        "calculator_active": True,
        "image_url": "/static/grade4mathimages/q22.png"
    },
    # Q23 - NC.4.OA.4 - Operations (Composite) - NO IMAGE
    {
        "question_num": 23,
        "topic": "Operations",
        "difficulty": 1,
        "prompt": "Which group of numbers includes only composite numbers?",
        "choices": ["3, 9, 15, 27, 31", "12, 15, 21, 28, 31", "15, 18, 21, 24, 25", "21, 28, 31, 35, 41"],
        "correct_answer": "15, 18, 21, 24, 25",
        "explanation": "All numbers in this group (15, 18, 21, 24, 25) are composite (have more than 2 factors).",
        "calculator_active": True,
        "image_url": None
    },
    # Q24 - NC.4.NBT.2 - Number Operations (Place Value) - NO IMAGE
    {
        "question_num": 24,
        "topic": "Number Operations",
        "difficulty": 1,
        "prompt": "Which choice is equal to 462?",
        "choices": ["3 hundreds, 16 tens, and 2 ones", "3 hundreds, 6 tens, and 2 ones", "4 hundreds and 62 tens", "4 hundreds, 60 tens, and 2 ones"],
        "correct_answer": "3 hundreds, 16 tens, and 2 ones",
        "explanation": "3×100 + 16×10 + 2 = 300 + 160 + 2 = 462.",
        "calculator_active": True,
        "image_url": None
    },
    # Q25 - NC.4.NF.3 - Fractions - NO IMAGE
    {
        "question_num": 25,
        "topic": "Fractions",
        "difficulty": 2,
        "prompt": "A tree was 14 and 3/8 inches tall when it was first planted. Two years later, the tree was 21 and 1/8 inches tall. How much did the tree grow in the two years?",
        "choices": ["6 and 5/8 inches", "6 and 6/8 inches", "7 and 5/8 inches", "7 and 6/8 inches"],
        "correct_answer": "6 and 6/8 inches",
        "explanation": "21 and 1/8 - 14 and 3/8 = 20 and 9/8 - 14 and 3/8 = 6 and 6/8 inches.",
        "calculator_active": True,
        "image_url": None
    },
    # Q26 - NC.4.MD.1 - Measurement - NO IMAGE
    {
        "question_num": 26,
        "topic": "Measurement",
        "difficulty": 2,
        "prompt": "Wendy filled a bucket with vegetables from her garden. The vegetables weighed 7,000 grams. She sold 4,200 grams of the vegetables. How much did the remaining vegetables weigh?",
        "choices": ["2,800 grams", "3,200 grams", "4,193 grams", "11,200 grams"],
        "correct_answer": "2,800 grams",
        "explanation": "7,000 - 4,200 = 2,800 grams remaining.",
        "calculator_active": True,
        "image_url": None
    },
    # Q27 - NC.4.MD.4 - Measurement (Data/Graph) - HAS IMAGE
    {
        "question_num": 27,
        "topic": "Measurement",
        "difficulty": 2,
        "prompt": "Fourth-grade students were surveyed about their favorite pizza topping. This graph shows the results. How many more fourth-graders chose pepperoni or sausage than chose the other toppings?",
        "choices": ["5", "10", "15", "20"],
        "correct_answer": "15",
        "explanation": "Pepperoni + Sausage vs Cheese + Mushroom. The difference is 15 students.",
        "calculator_active": True,
        "image_url": "/static/grade4mathimages/q27.png"
    },
    # Q28 - NC.4.OA.3 - Operations - NO IMAGE
    {
        "question_num": 28,
        "topic": "Operations",
        "difficulty": 2,
        "prompt": "Last week, Jeff read 8 pages of his book. This week, he has read 6 times as many pages as last week. How many pages has Jeff read altogether during the two weeks?",
        "choices": ["14", "40", "48", "56"],
        "correct_answer": "56",
        "explanation": "This week: 8 × 6 = 48 pages. Total: 8 + 48 = 56 pages.",
        "calculator_active": True,
        "image_url": None
    },
    # Q29 - NC.4.G.2 - Geometry - NO IMAGE
    {
        "question_num": 29,
        "topic": "Geometry",
        "difficulty": 2,
        "prompt": "Which polygon can have four sides of equal length, two pairs of parallel sides, and no right angles?",
        "choices": ["rectangle", "trapezoid", "rhombus", "square"],
        "correct_answer": "rhombus",
        "explanation": "A rhombus has 4 equal sides, 2 pairs of parallel sides, but doesn't require right angles.",
        "calculator_active": True,
        "image_url": None
    },
    # Q30 - NC.4.MD.2 - Measurement - NO IMAGE
    {
        "question_num": 30,
        "topic": "Measurement",
        "difficulty": 2,
        "prompt": "Maria drank 3 liters of water last week. Her friend drank twice as much water as Maria. How many milliliters of water did they both drink?",
        "choices": ["3,000 milliliters", "5,000 milliliters", "6,000 milliliters", "9,000 milliliters"],
        "correct_answer": "9,000 milliliters",
        "explanation": "Maria: 3L, Friend: 6L. Total: 9L = 9,000 mL.",
        "calculator_active": True,
        "image_url": None
    },
    # Q31 - NC.4.MD.6 - Measurement (Angles) - HAS IMAGE
    {
        "question_num": 31,
        "topic": "Measurement",
        "difficulty": 1,
        "prompt": "Rays PQ and PR are perpendicular. What is the value of x?",
        "choices": ["40", "70", "80", "110"],
        "correct_answer": "70",
        "explanation": "PQ and PR are perpendicular (90°). 20° + x° = 90°, so x = 70°.",
        "calculator_active": True,
        "image_url": "/static/grade4mathimages/q31.png"
    },
    # Q32 - NC.4.NF.7 - Decimals - NO IMAGE
    {
        "question_num": 32,
        "topic": "Fractions",
        "difficulty": 2,
        "prompt": "Thomas lives more than 0.55 km and less than 0.75 km from his school. Which choice could be the distance Thomas lives from his school?",
        "choices": ["0.06 km", "0.50 km", "0.60 km", "1.30 km"],
        "correct_answer": "0.60 km",
        "explanation": "0.60 is between 0.55 and 0.75.",
        "calculator_active": True,
        "image_url": None
    },
    # Q33 - NC.4.G.3 - Geometry (Symmetry) - HAS IMAGE
    {
        "question_num": 33,
        "topic": "Geometry",
        "difficulty": 2,
        "prompt": "Which figure has the most lines of symmetry?",
        "choices": ["A", "B", "C", "D"],
        "correct_answer": "B",
        "explanation": "Figure B (likely a circle or regular polygon) has the most lines of symmetry.",
        "calculator_active": True,
        "image_url": "/static/grade4mathimages/q33.png"
    },
    # Q34 - NC.4.OA.5 - Operations (Patterns) - NO IMAGE
    {
        "question_num": 34,
        "topic": "Operations",
        "difficulty": 2,
        "prompt": "If this pattern continues, what will the next 3 numbers be?\n\n10, 15, 25, 40, 60, ___, ___, ___",
        "choices": ["65, 70, 75", "85, 110, 135", "85, 115, 150", "90, 120, 155"],
        "correct_answer": "85, 115, 150",
        "explanation": "The differences are +5, +10, +15, +20, so next: +25=85, +30=115, +35=150.",
        "calculator_active": True,
        "image_url": None
    },
    # Q35 - NC.4.MD.8 - Measurement (Time) - NO IMAGE
    {
        "question_num": 35,
        "topic": "Measurement",
        "difficulty": 3,
        "prompt": "Every Saturday morning, Jack reads for 30 minutes, plays basketball for 60 minutes, and rides his bike. If Jack starts these activities at 10:25 a.m. and finishes them at 12:10 p.m., how long does he spend riding his bike?",
        "choices": ["5 minutes", "15 minutes", "25 minutes", "45 minutes"],
        "correct_answer": "15 minutes",
        "explanation": "Total time: 1 hour 45 min = 105 min. Reading + basketball = 90 min. Bike = 105 - 90 = 15 min.",
        "calculator_active": True,
        "image_url": None
    },
    # Q36 - NC.4.NF.3 - Fractions - NO IMAGE
    {
        "question_num": 36,
        "topic": "Fractions",
        "difficulty": 1,
        "prompt": "Which number sentence could be used to solve this problem?\n\n(3 and 1/5) - (2 and 1/5) = x",
        "choices": ["5/5 - 2/5 = x", "6/5 - 1/5 = x", "10/5 - 7/5 = x", "16/5 - 11/5 = x"],
        "correct_answer": "16/5 - 11/5 = x",
        "explanation": "3 and 1/5 = 16/5, and 2 and 1/5 = 11/5. So 16/5 - 11/5 = 5/5 = 1.",
        "calculator_active": True,
        "image_url": None
    },
    # Q37 - NC.4.MD.3 - Measurement (Area) - NO IMAGE
    {
        "question_num": 37,
        "topic": "Measurement",
        "difficulty": 2,
        "prompt": "Kathy has a garden that is 15 feet wide and 20 feet long. She will plant 1 bulb per square foot. Each bag of bulbs contains 9 bulbs. How many bags does Kathy need to buy?",
        "choices": ["34 bags", "33 bags", "12 bags", "11 bags"],
        "correct_answer": "34 bags",
        "explanation": "Area = 15 × 20 = 300 sq ft. 300 ÷ 9 = 33.33, so she needs 34 bags.",
        "calculator_active": True,
        "image_url": None
    },
    # Q38 - NC.4.NBT.7 - Number Operations - HAS IMAGE (table)
    {
        "question_num": 38,
        "topic": "Number Operations",
        "difficulty": 2,
        "prompt": "This table shows the number of students at a school in the years 2014-2016.\n\n2014: 1,030 students\n2015: ?\n2016: 1,300 students\n\nIn 2015, there were more students than in 2014 but fewer than in 2016. Which could be the number of students in 2015?",
        "choices": ["1,003 students", "1,033 students", "1,303 students", "1,330 students"],
        "correct_answer": "1,033 students",
        "explanation": "1,033 is between 1,030 and 1,300.",
        "calculator_active": True,
        "image_url": "/static/grade4mathimages/q38.png"
    },
    # Q39 - NC.4.NF.6 - Fractions (Number Line) - HAS IMAGE
    {
        "question_num": 39,
        "topic": "Fractions",
        "difficulty": 2,
        "prompt": "Marcy saw this number line in class. Which shaded section has the same value as n?",
        "choices": ["A", "B", "C", "D"],
        "correct_answer": "A",
        "explanation": "Section A represents the same fraction value as point n on the number line.",
        "calculator_active": True,
        "image_url": "/static/grade4mathimages/q39.png"
    },
    # Q40 - NC.4.NBT.4 - Number Operations - NO IMAGE
    {
        "question_num": 40,
        "topic": "Number Operations",
        "difficulty": 2,
        "prompt": "There are 1,829 students at a middle school.\n• 568 students are in 6th grade.\n• 629 students are in 7th grade.\n• The rest of the students are in 8th grade.\n\nHow many students are in 8th grade?",
        "choices": ["622 students", "632 students", "772 students", "1,197 students"],
        "correct_answer": "632 students",
        "explanation": "1,829 - 568 - 629 = 632 students in 8th grade.",
        "calculator_active": True,
        "image_url": None
    },
]


def get_math_topics():
    """Get list of math topic keywords."""
    return ['geometry', 'fractions', 'operations', 'number operations', 'measurement',
            'addition', 'subtraction', 'multiplication', 'division', 'algebra', 'decimals']


def replace_grade4_math_questions():
    """Replace all Grade 4 Math questions with EOG questions."""
    ensure_columns_exist()
    
    db = SessionLocal()
    
    try:
        # Delete existing Grade 4 Math questions
        math_keywords = get_math_topics()
        
        existing_questions = db.query(Question).filter(
            Question.grade_level == 4
        ).all()
        
        # Filter for math questions
        math_questions_to_delete = []
        for q in existing_questions:
            topic_lower = q.topic.lower()
            if any(keyword in topic_lower for keyword in math_keywords):
                math_questions_to_delete.append(q)
        
        deleted_count = len(math_questions_to_delete)
        for q in math_questions_to_delete:
            db.delete(q)
        
        db.commit()
        print(f"[OK] Deleted {deleted_count} existing Grade 4 Math questions")
        
        # Add new EOG questions
        added_count = 0
        with_images = 0
        calc_active = 0
        calc_inactive = 0
        
        for q_data in GRADE4_MATH_QUESTIONS:
            question = Question(
                grade_level=4,
                topic=q_data["topic"],
                difficulty=q_data["difficulty"],
                weight=1.0 + (q_data["difficulty"] - 1) * 0.5,  # 1.0, 1.5, 2.0 based on difficulty
                prompt=q_data["prompt"],
                choices=q_data["choices"],
                correct_answer=q_data["correct_answer"],
                explanation=q_data["explanation"],
                image_url=q_data["image_url"],
                calculator_active=q_data["calculator_active"]
            )
            db.add(question)
            added_count += 1
            
            if q_data["image_url"]:
                with_images += 1
            if q_data["calculator_active"]:
                calc_active += 1
            else:
                calc_inactive += 1
        
        db.commit()
        
        print(f"[OK] Added {added_count} Grade 4 Math EOG questions")
        print(f"   - {with_images} questions have images")
        print(f"   - {calc_inactive} questions are Calculator Inactive")
        print(f"   - {calc_active} questions are Calculator Active")
        
        # Show topic breakdown
        topic_counts = {}
        for q in GRADE4_MATH_QUESTIONS:
            topic = q["topic"]
            topic_counts[topic] = topic_counts.get(topic, 0) + 1
        
        print("\nTopic breakdown:")
        for topic, count in sorted(topic_counts.items(), key=lambda x: -x[1]):
            print(f"   - {topic}: {count} questions")
        
        return {
            "deleted": deleted_count,
            "added": added_count,
            "with_images": with_images
        }
        
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("=" * 60)
    print("Grade 4 Math Question Replacement Script")
    print("=" * 60)
    print()
    
    result = replace_grade4_math_questions()
    
    print()
    print("=" * 60)
    print("Complete!")
    print(f"Deleted: {result['deleted']} questions")
    print(f"Added: {result['added']} questions")
    print(f"With images: {result['with_images']} questions")
    print("=" * 60)
