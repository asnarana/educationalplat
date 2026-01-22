"""
Add more Reading questions for low-count topics.
- Grade 3: Main Idea (need 6+ more), Text Structure (need 3+ more)
- Grade 4: Main Idea (need 3+ more)

Uses existing passages from add_reading_questions.py and add_grade4_reading_questions.py
"""
from app.db import SessionLocal
from app.models import Question

# Import passages from existing files
from add_reading_questions import (
    GREAT_ESCAPE_PART1, GREAT_ESCAPE_PART2,
    UNDER_MY_NOSE_PART1, UNDER_MY_NOSE_PART2,
    GRANDFATHER_FROG_PART1, GRANDFATHER_FROG_PART2,
    BEAVERS_PART1, BEAVERS_PART2,
    DOG_HERO_PART1, DOG_HERO_PART2
)

from add_grade4_reading_questions import (
    LIBBY_SAVES_TEAM, AMELIA_EARHART
)

# Additional Grade 3 Main Idea Questions (using existing passages)
GRADE3_MAIN_IDEA_ADDITIONS = [
    {
        "grade_level": 3,
        "topic": "Main Idea",
        "difficulty": 2,
        "weight": 1.0,
        "prompt": f"Read both parts:\n\n{GREAT_ESCAPE_PART1}\n\n{GREAT_ESCAPE_PART2}\n\nWhat is the main idea of this story?",
        "choices": [
            "Animals at a fair cause chaos when a rooster sets them free.",
            "A water boy learns how to catch chickens at the fair.",
            "Farmers are careless about locking animal cages.",
            "A boy wants to feed all the animals at the fair."
        ],
        "correct_answer": "Animals at a fair cause chaos when a rooster sets them free.",
        "explanation": "The main idea is that Rhode Island Red the rooster frees all the animals, causing chaos at the fair until a boy leads them back with oats."
    },
    {
        "grade_level": 3,
        "topic": "Main Idea",
        "difficulty": 2,
        "weight": 1.0,
        "prompt": f"Read both parts:\n\n{GRANDFATHER_FROG_PART1}\n\n{GRANDFATHER_FROG_PART2}\n\nWhat is the main idea of this story?",
        "choices": [
            "Grandfather Frog takes a nap after eating breakfast.",
            "Billy Mink and Little Joe Otter plan to play a trick on Grandfather Frog.",
            "Jerry Muskrat warns Grandfather Frog about danger.",
            "Longlegs the Blue Heron goes fishing in the river."
        ],
        "correct_answer": "Billy Mink and Little Joe Otter plan to play a trick on Grandfather Frog.",
        "explanation": "The main idea is about Billy Mink finding Little Joe Otter so they can play a prank on the sleeping Grandfather Frog."
    },
    {
        "grade_level": 3,
        "topic": "Main Idea",
        "difficulty": 2,
        "weight": 1.0,
        "prompt": f"Read both parts:\n\n{BEAVERS_PART1}\n\n{BEAVERS_PART2}\n\nWhat is the main idea of this text?",
        "choices": [
            "Beavers have tails that look like fish scales.",
            "Beavers work together to build dams and homes.",
            "A Frenchman in Louisiana studies wild animals.",
            "Beavers sleep through cold, stormy weather."
        ],
        "correct_answer": "Beavers work together to build dams and homes.",
        "explanation": "The main idea explains how beavers cooperate to build dams and maintain their homes as a community."
    },
    {
        "grade_level": 3,
        "topic": "Main Idea",
        "difficulty": 2,
        "weight": 1.0,
        "prompt": f"Read both parts:\n\n{UNDER_MY_NOSE_PART1}\n\n{UNDER_MY_NOSE_PART2}\n\nWhat is the main idea of this text?",
        "choices": [
            "The author explains how she creates her picture books.",
            "The author describes her favorite books to read.",
            "The author talks about her pet cat named Bucky.",
            "The author explains how to grow a vegetable garden."
        ],
        "correct_answer": "The author explains how she creates her picture books.",
        "explanation": "The main idea is that author Lois Ehlert shares her creative process for writing and illustrating children's books."
    },
    {
        "grade_level": 3,
        "topic": "Main Idea",
        "difficulty": 2,
        "weight": 1.0,
        "prompt": f"Read both parts:\n\n{GREAT_ESCAPE_PART1}\n\n{GREAT_ESCAPE_PART2}\n\nWhich sentence best states the main idea of the story?",
        "choices": [
            "Rhode Island Red is a rooster who lives at a county fair.",
            "A clever rooster causes trouble but a boy solves the problem.",
            "People at the fair try to catch chickens all day.",
            "Animals like to ride on carnival rides at the fair."
        ],
        "correct_answer": "A clever rooster causes trouble but a boy solves the problem.",
        "explanation": "The main idea shows how the rooster creates chaos by freeing animals, but a boy cleverly uses oats to lead them back."
    },
    {
        "grade_level": 3,
        "topic": "Main Idea",
        "difficulty": 2,
        "weight": 1.0,
        "prompt": f"Read both parts:\n\n{DOG_HERO_PART1}\n\n{DOG_HERO_PART2}\n\nWhich detail best supports the main idea that Velvet was a hero?",
        "choices": [
            "The climbers brought a transmitter with them.",
            "During the cold night, she stretched across the three climbers like a warm blanket.",
            "The Mount Hood National Forest spans over one million acres.",
            "Trevor Liston was one of the climbers from Portland."
        ],
        "correct_answer": "During the cold night, she stretched across the three climbers like a warm blanket.",
        "explanation": "This detail shows how Velvet helped save the climbers by keeping them warm during the dangerous night."
    },
]

# Additional Grade 3 Text Structure Questions
GRADE3_TEXT_STRUCTURE_ADDITIONS = [
    {
        "grade_level": 3,
        "topic": "Text Structure",
        "difficulty": 3,
        "weight": 1.5,
        "prompt": f"Read both parts:\n\n{GREAT_ESCAPE_PART1}\n\n{GREAT_ESCAPE_PART2}\n\nHow is the story organized?",
        "choices": [
            "It compares different types of farm animals.",
            "It describes events in the order they happened.",
            "It explains the causes and effects of farming.",
            "It lists reasons why fairs are important."
        ],
        "correct_answer": "It describes events in the order they happened.",
        "explanation": "The story uses chronological order, describing events from when Red escapes to when the boy leads the animals back."
    },
    {
        "grade_level": 3,
        "topic": "Text Structure",
        "difficulty": 3,
        "weight": 1.5,
        "prompt": f"Read both parts:\n\n{GRANDFATHER_FROG_PART1}\n\n{GRANDFATHER_FROG_PART2}\n\nHow does the author organize the events in this story?",
        "choices": [
            "By comparing Billy Mink to Jerry Muskrat",
            "By explaining why frogs sleep on lily pads",
            "By telling events in the order they happen",
            "By listing all the animals in the Smiling Pool"
        ],
        "correct_answer": "By telling events in the order they happen",
        "explanation": "The story is organized chronologically, following Billy Mink as he hurries to find Little Joe Otter."
    },
    {
        "grade_level": 3,
        "topic": "Text Structure",
        "difficulty": 3,
        "weight": 1.5,
        "prompt": f"Read both parts:\n\n{DOG_HERO_PART1}\n\n{DOG_HERO_PART2}\n\nHow does the author organize this text?",
        "choices": [
            "By comparing Mount Hood to other mountains",
            "By describing the problem and how it was solved",
            "By listing the names of all the rescue workers",
            "By explaining why dogs make good pets"
        ],
        "correct_answer": "By describing the problem and how it was solved",
        "explanation": "The text presents the problem (climbers stranded in a storm) and describes how they survived with Velvet's help."
    },
]

# Additional Grade 4 Main Idea Questions
GRADE4_MAIN_IDEA_ADDITIONS = [
    {
        "grade_level": 4,
        "topic": "Main Idea",
        "difficulty": 2,
        "weight": 1.0,
        "prompt": f"Read the passage:\n\n{LIBBY_SAVES_TEAM}\n\nWhat is the main idea of this story?",
        "choices": [
            "A girl learns how to train sled dogs.",
            "A girl shows courage when she must control a runaway sled.",
            "A father teaches his daughter about winter sports.",
            "Dogs are faster than people in the snow."
        ],
        "correct_answer": "A girl shows courage when she must control a runaway sled.",
        "explanation": "The main idea is that Libby bravely takes control of the sled when her father falls off and successfully stops the dogs."
    },
    {
        "grade_level": 4,
        "topic": "Main Idea",
        "difficulty": 2,
        "weight": 1.0,
        "prompt": f"Read the passage:\n\n{AMELIA_EARHART}\n\nWhat is the main idea of this text?",
        "choices": [
            "Amelia Earhart was a famous pilot who set records and helped women.",
            "George Putnam was a book publisher in the 1920s.",
            "Flying across the Pacific Ocean is very dangerous.",
            "Purdue University has many women students."
        ],
        "correct_answer": "Amelia Earhart was a famous pilot who set records and helped women.",
        "explanation": "The main idea is that Amelia Earhart was a pioneering female pilot who broke records and advocated for women's rights."
    },
    {
        "grade_level": 4,
        "topic": "Main Idea",
        "difficulty": 2,
        "weight": 1.0,
        "prompt": f"Read the passage:\n\n{LIBBY_SAVES_TEAM}\n\nWhich sentence best supports the main idea of the story?",
        "choices": [
            "Libby wiggled with excitement as she watched her dad hook up their six Alaskan huskies.",
            "You saved the team, Libby! You really did it. I'm so proud of you.",
            "The dogs, sensing the excitement in Libby's voice, began a chorus of their own.",
            "About twenty miles, Libby. If they make it that far."
        ],
        "correct_answer": "You saved the team, Libby! You really did it. I'm so proud of you.",
        "explanation": "This sentence directly states that Libby saved the team, which is the central message of the story."
    },
    {
        "grade_level": 4,
        "topic": "Main Idea",
        "difficulty": 2,
        "weight": 1.0,
        "prompt": f"Read the passage:\n\n{AMELIA_EARHART}\n\nWhich detail best supports the main idea that Amelia worked to help women?",
        "choices": [
            "Amelia's airplane could fly 3,200 miles without stopping.",
            "She started The Ninety-Nines, a group of women pilots.",
            "Amelia took off from Newfoundland, Canada.",
            "George became Amelia's manager after the flight."
        ],
        "correct_answer": "She started The Ninety-Nines, a group of women pilots.",
        "explanation": "Starting The Ninety-Nines shows Amelia's dedication to supporting and encouraging women pilots."
    },
]


def add_questions():
    """Add the additional reading questions to the database."""
    db = SessionLocal()
    
    try:
        all_questions = (
            GRADE3_MAIN_IDEA_ADDITIONS + 
            GRADE3_TEXT_STRUCTURE_ADDITIONS + 
            GRADE4_MAIN_IDEA_ADDITIONS
        )
        
        added = 0
        for q_data in all_questions:
            question = Question(**q_data)
            db.add(question)
            added += 1
        
        db.commit()
        
        print(f"Successfully added {added} questions:")
        print(f"  - Grade 3 Main Idea: {len(GRADE3_MAIN_IDEA_ADDITIONS)}")
        print(f"  - Grade 3 Text Structure: {len(GRADE3_TEXT_STRUCTURE_ADDITIONS)}")
        print(f"  - Grade 4 Main Idea: {len(GRADE4_MAIN_IDEA_ADDITIONS)}")
        
        return {"added": added}
        
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("Adding additional Reading questions for low-count topics...")
    result = add_questions()
    print(f"\nDone! Added {result['added']} questions.")
