"""
Script to add Grade 5 Reading EOG questions to the database.
Based on the Grade 5 Reading EOG Released Items.
"""
import sys
import os
from sqlalchemy.orm import Session
from app.db import SessionLocal, engine
from app.models import Question, Base

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

# Grade 5 Reading Passages

LIFE_WITHOUT_GRAVITY = """Excerpt from "Life without Gravity"
by Robert Zimmerman

Being weightless in space seems so exciting. Astronauts bounce about from wall to wall, flying! They float, they weave, they do somersaults and acrobatics without effort. Heavy objects can be lifted like feathers, and no one ever gets tired because nothing weighs anything. In fact, everything is fun, nothing is hard.

2
NOT! Since the first manned space missions in the 1960s, scientists have discovered that being weightless in space isn't just flying around like Superman. Zero gravity is alien stuff. As space tourist Dennis Tito said when he visited the International Space Station, "Living in space is like having a different life, living in a different world."

Worse, weightlessness can sometimes be downright unpleasant. Your body gets upset and confused. Your face puffs up, your nose gets stuffy, your back hurts, your stomach gets upset. If astronauts are to survive on the moon or a one-year journey to Mars—the shortest possible trip to the Red Planet—they will have to learn how to deal with this weird environment.

Our bodies are adapted to Earth's gravity. Our muscles are strong in order to overcome gravity as we walk and run. Our inner ears use gravity to keep us upright. And because gravity wants to pull all our blood down into our legs, our hearts are designed to pump hard to get blood up to our brains.

5
In space, the much weaker gravity makes the human body change in many unexpected ways. In low gravity, your blood is rerouted, flowing from the legs, which become thin and sticklike, to the head, which swells up. The extra liquid in your head also makes you feel like you're hanging upside down or have a stuffed-up nose.

The lack of gravity causes astronauts to "grow" between one and three inches taller. Their spines straighten out. The bones in the spine and the disks between them spread apart and relax.

But their bones also get thin and spongy. The body decides that if the muscles aren't going to push and pull on the bones, it doesn't need to lay down as much bone as it normally does. Astronauts who have been in space for several months can lose 10 percent or more of their bone tissue. If their bones got much weaker, the astronauts would snap once they returned to Earth.

And their muscles get weak and flabby. Floating about in space is too easy. If astronauts don't force themselves to exercise, their muscles become so feeble that when they return to Earth they can't even walk.

Worst of all is how their stomachs feel. During the first few days in space, the inner ear—which gives people their sense of balance—gets confused. Many astronauts become nauseous. They lose their appetites.

Weightlessness isn't all bad, however. After about a week, people usually get used to it. Their stomachs settle down. Appetites return (though astronauts always say that food tastes blander in space). The heart and spine adjust.

Then, flying around like a bird becomes fun. Rooms suddenly seem much bigger. Look around you: The space above your head is pretty useless on Earth. You can't get up there to work, and anything you attach to the ceiling is simply something to bump your head on. In space, however, that area is useful. In fact, equipment can be installed on every inch of every wall. In weightlessness, you choose to move up or down and left or right simply by pointing your head. If you turn yourself upside down, the ceiling becomes the floor.

12
And you can't drop anything! As you work, you can let your tools float around you. But you'd better be organized and neat. If you don't put things back where they belong when you are finished, tying them down securely, they will float away. Air currents will then blow them into nooks and crannies, and it might take you days to find them again.

In low gravity, you have to learn new ways to eat. Don't try pouring a bowl of cornflakes. Not only will the flakes float all over the place, the milk won't pour. Instead, big balls of milk will form. You can drink these by taking big bites out of them, but you'd better finish them before they slam into a wall, splattering apart and covering everything with little tiny milk globules.

Some meals on the space station are eaten with forks and knives, but scooping food with a spoon doesn't work. If the food isn't gooey enough to stick to the spoon, it will float away.

Excerpt from "Life Without Gravity" by Robert Zimmerman. Text ©2009 by Robert Zimmerman. Reprinted by permission of the author."""

MAKING_WORLDS_RAREST_SYRUP = """Making the World's Rarest Syrup
by David Edwards

It's six in the morning and already hot. In just a few hours, the thermometer will register over a hundred degrees. My family has come to Southern Arizona's Colossal Cave Mountain Park to participate in something few tourists experience—the annual saguaro-cactus harvest. For a single day each year, Colossal Cave Mountain Park hosts a Tohono O'odham saguaro harvest. Any other time of year, it's illegal to harvest saguaro fruit here.

Mature saguaros stand fifteen feet and higher, and the fruit we'll be gathering grows on top of their spine-covered arms and trunks. The obvious question: How will we reach them?

Here to answer this question—and more—are Regina (Gina) Squieros; her sister, Angie Saraficio; and Regina's 16-year-old grandson, Gustavo Verdugo. They are Tohono O'odham. The Tohono O'odham (Desert People) were once called Papago Indians by nonnatives. They make up the second largest Native-American nation in the United States.

4
Gina begins by showing us how to make our kuipad—harvesting sticks—from saguaro ribs. The wooden ribs are straight, unlike most plants growing in the Sonoran Desert, and light, but none of them is long enough to reach the fruit. We bind the ribs together using pliers and baling wire, positioning the thickest, heaviest rib on the bottom. We attach a small creosote branch crosswise near the top of our harvesting sticks. Creosote is very strong and won't easily break when pulled or pushed, which is how we will bring down the fruit.

5
Saguaro fruit is about the size and shape of a large egg and covered with a reddish-green peel. Beneath the peel, the fruit is bright red and freckled with as many as two thousand tiny black seeds. The fruit feels like a fresh fig in your mouth, but tastes more like watermelon mixed with pear.

Gina explains that the first fruit we gather is very special . . . it will take a lot of patience to make syrup from the fruit we'll gather.

As we nudge the saguaro fruit loose, I stop and listen. The falling fruit sounds almost like rain—a soft thump when the fruit lands in the dirt or a sharp patter when it's caught in the buckets.

8
When the first fruit is taken from each saguaro, we leave the peel red-side up at the base of the saguaro, open like a flower. Gina says this will help summon the summer rains.

9
We use our thumbs to scoop the fruit into our buckets, careful to avoid the spines that occasionally cling to the bottom of the peel. Soon, my hands are sticky and flecked with crunchy black seeds.

10
Gina and Angie add a little water to the fruit we've collected and pour it into a large pot to boil for several hours. After the fruit has boiled, Gina brings out a square cloth to strain the mixture. Then she returns the hot juice to the cleaned pot to boil a second time.

It's nearly sunrise before the saguaro syrup is ready, but everyone agrees it was worth the wait. A tiny four-ounce bottle of "the world's rarest syrup" sells for $25. Now that I have experienced the hard work that goes into making it, I understand why it is so expensive.

We leave with a small jar filled with this rare syrup and lasting memories of the opportunity to learn from the Tohono O'odham.

"Making the World's Rarest Syrup" by David Edwards from Highlights for Children, July 2008. Copyright ©2008 Highlights for Children, Inc., Columbus, Ohio. All rights reserved. Used by permission."""

WORLD_IN_A_BOTTLE = """The World in a Bottle
by Janeen R. Adil

If you want a garden full of plants, you need to grow them outdoors. Or do you? What if you could bring the world indoors—on a smaller scale, of course! What if you could have your own collection of living plants right inside your home? All you have to do is create a world in a bottle by making a terrarium.

A terrarium is a clear glass or plastic container holding natural materials such as dirt, sand, and rocks. It gets its name from the Latin word for earth, which is terra. Terrariums are typically used for growing small plants.

A terrarium is actually a little ecosystem. Because the container is usually closed, it acts like a tiny greenhouse. Plants take up water from the soil and release it into the air. As the water vapor cools, it condenses on the sides of the glass and trickles back into the soil. Then the process starts all over again.

During the day, plants use carbon dioxide inside the terrarium for photosynthesis, providing energy for their growth. Oxygen and water vapor are released into the air. Then, at night, the plants use the oxygen and give off carbon dioxide, and the cycle starts all over again.

5
While ancient Greeks are credited with being the first to grow plants in transparent containers, a nineteenth-century London physician was the creator of the modern-day terrarium. Dr. Nathaniel Ward was conducting an experiment that led to the terrarium's accidental discovery.

Dr. Ward wanted to study how a sphinx moth developed, so he buried a pupa in some moist earth in a closed glass container. As time passed, he was surprised to see that a fern seedling and some grass had sprouted in the jar. Dr. Ward decided to continue the experiment, this time focusing on the plants. He kept the jar sealed, never adding even a drop of water, and for four years the plants grew and thrived.

Dr. Ward called his tiny greenhouse a fern case. After experimenting with other plants as well, he wrote up his findings in the book On the Growth of Plants in Closely Glazed Cases, published in 1842. His work led to the creation of more spacious, enclosed glass containers called Wardian cases, which were larger versions of today's terrariums.

8
Wardian cases became extremely popular during the Victorian era. The Victorians loved exotic plants as well as fancy decorations. Wardian cases let them grow tropical plants right in their homes. And the cases could be as ornamental and expensive as a family's budget would allow.

But Wardian cases weren't just important as a home-decorating item. During the Victorian era, plant collectors traveled around the world in search of rare and exotic specimens, and thanks to these cases, collectors could now transport delicate tropical plants back to England. During long voyages at sea, the cases protected the plants both from salt air and from changes in climate. A great number of specimens were introduced into England and other parts of Europe this way.

Today it's still possible to buy terrariums labeled as Wardian cases. It's much less expensive, though—and a lot of fun—to create your own terrarium. Choices for a container can include a goldfish bowl, a big pickle jar from the deli, or a one- to three-gallon water bottle. Even an empty soft drink bottle can be used to make a terrarium!"""

ANTONIO_CANOVA = """Antonio Canova
by James Baldwin

A good many years ago, there lived in Italy a little boy whose name was Antonio Canova. He lived with his grandfather. . . . His grandfather was a stonecutter, and he was very poor.

Antonio was a puny lad and not strong enough to work. He did not care to play with the other boys of the town. But he liked to go with his grandfather to the stoneyard. While the old man was busy, cutting and trimming the great blocks of stone, the lad would play among the chips. Sometimes he would make a little statue of soft clay; sometimes he would take hammer and chisel and try to cut a statue from a piece of rock. He showed so much skill that his grandfather was delighted.

"The boy will be a sculptor someday," he said.

Then when they went home in the evening, the grandmother would say, "What have you been doing today, my little sculptor?"

And she would take him upon her lap and sing to him or tell him stories that filled his mind with pictures of wonderful and beautiful things. And the next day, when he went back to the stoneyard, he would try to make some of those pictures in stone or clay.

There lived in the same town a rich man who was called the Count. Sometimes the Count would have a grand dinner, and his rich friends from other towns would come to visit him. Then Antonio's grandfather would go up to the Count's house to help with the work in the kitchen, for he was a fine cook as well as a good stonecutter.

It happened one day that Antonio went with his grandfather to the Count's great house. Some people from the city were coming, and there was to be a grand feast. The boy could not cook, and he was not old enough to wait on the table; but he could wash the pans and kettles, and as he was smart and quick, he could help in many other ways.

8
All went well until it was time to spread the table for dinner. Then there was a crash in the dining room, and a man rushed into the kitchen with some pieces of marble in his hands. He was pale, and trembling with fright.

"What shall I do? What shall I do?" he cried. "I have broken the statue that was to stand at the center of the table. I cannot make the table look pretty without the statue. What will the Count say?"

And now all the other servants were in trouble. Was the dinner to be a failure after all? For everything depended on having the table nicely arranged. The Count would be very angry.

"Ah, what shall we do?" they all asked.

Then little Antonio Canova left his pans and kettles and went up to the man who had caused the trouble.

"If you had another statue, could you arrange the table?" he asked.

"Certainly," said the man, "that is, if the statue were of the right length and height."

"Will you let me try to make one?" asked Antonio. "Perhaps I can make something that will do."

The man laughed.

"Nonsense!" he cried. "Who are you, that you talk of making statues on an hour's notice?"

"I am Antonio Canova," said the lad.

"Let the boy try what he can do," said the servants, who knew him.

And so, since nothing else could be done, the man allowed him to try.

On the kitchen table there was a large square lump of yellow butter. Two hundred pounds the lump weighed, and it had just come in, fresh and clean, from the dairy on the mountain. With a kitchen knife in his hand, Antonio began to cut and carve this butter. In a few minutes, he had molded it into the shape of a crouching lion; and all the servants crowded around to see it.

"How beautiful!" they cried. "It is a great deal prettier than the statue that was broken."

When it was finished, the man carried it to its place.

"The table will be handsomer by half than I ever hoped to make it," he said.

When the Count and his friends came in to dinner, the first thing they saw was the yellow lion.

"What a beautiful work of art!" they cried. "None but a very great artist could ever carve such a figure; and how odd that he should choose to make it of butter!" And then they asked the Count to tell them the name of the artist.

"Truly, my friends," he said, "this is as much of a surprise to me as to you." And then he called to his head servant and asked him where he had found so wonderful a statue.

"It was carved only an hour ago by a little boy in the kitchen," said the servant.

This made the Count's friends wonder still more; and the Count bade the servant call the boy into the room.

"My lad," he said, "you have done a piece of work of which the greatest artists would be proud. What is your name, and who is your teacher?"

"My name is Antonio Canova," said the boy, "and I have had no teacher but my grandfather the stonecutter."

By this time, all the guests had crowded around Antonio. There were famous artists among them, and they knew that the lad was a genius. They could not say enough in praise of his work; and when at last they sat down at the table, nothing would please them but that Antonio should have a seat with them; and the dinner was made a feast in his honor.

The very next day, the Count sent for Antonio to come and live with him. The best artists in the land were employed to teach him the art in which he had shown so much skill; but now, instead of carving butter, he chiseled marble. In a few years, Antonio Canova became known as one of the greatest sculptors in the world."""

ANNABEL_LEE_PI = """Annabel Lee, P.I.
by Judy Cox

It's eight-twenty in the morning. Another school day. Dad's in the kitchen grinding coffee beans. Mom's in the bedroom drying her hair. John's in the laundry room looking for clean socks. In the living room, the television is on, screaming a song about hunky-chunky cat food.

And me? I'm working the day shift out of headquarters. Annabel Lee. Private Investigator.

Call me Al. It's my initials, get it? A.L. Annabel Lee. But only my parents call me that. My friends call me Al.

"Mom!" A piercing yell from the laundry room. My superbrain identifies it at once as belonging to my older brother, John. "Mom, where's my gray sock?" Mom comes to the top of the stairs.

"Look in the dryer!" she calls.

"I did already. It's gone," John wails. "I need that sock!"

"Did you try under your bed?"

"It's not there," John complains.

"Well, if you'd only remember to put your dirty clothes in the hamper in the first place . . ." Dad pokes his head around the kitchen door. Mornings always make him grouchy.

I hear John banging around the laundry room. "This is the third pair of socks I've lost this month! We need a new dryer. I think this dryer eats socks!" he says.

Sounds like a case for Annabel Lee, P.I. I pull on my battered old slouch hat and grab my notebook. Flip it open to a clean page. Pull my new fine-point marker from over my ear. Leap downstairs, taking the steps two by two, to the laundry room. I'll interview possible witnesses.

12
John first. "Just the facts, sir," I tell him. "When was the last time you saw the alleged gray sock?" I lick the tip of my pen, like they do on cop shows. It tastes real funny.

13
John gives me a dirty look. "Last time I wore it, birdbrain." He thinks for a minute, then says, "Let's see. I wore my gray shirt to the game on Friday. Must have been then."

14
"Can you describe the AMS?"

15
"The what?"

16
"Alleged Missing Sock. It's what we call them," I explain patiently.

17
Another look from John. He dangles a long, gray, woolly object in front of me. "It's a sock, see. What do you think it looks like? An elephant?"

18
Honestly, big brothers are a pain. I take the object from him. "Just the facts, sir. The missing sock matches this one?"

19
He nods. I take the sock and write "Exhibit A" in my notebook. Next I head up the stairs to interview Mom, following the roar of the blow dryer. I show her Exhibit A. "Excuse me, ma'am. Can you identify this sock?"

"Oh, you found it? John was looking for it. Get dressed for school, dear, or you'll miss the bus."

"This isn't the missing sock, ma'am. This is its mate." I lay the sock neatly on the bed to show her. "Have you seen this sock before?"

Mom sighs. "Listen. I do laundry ten billion times a week, and if you expect me to be able to tell you where one little sock is . . ." She switches the hair dryer off. "If you and your brother would offer to help once in a while . . ." She looks in the mirror and fluffs her hair, then catches sight of me. Her eyes narrow in The Mom Look. "Annabel, I thought I told you to go get dressed."

I head downstairs to interview the head of the household. I find him at the kitchen table, reading the paper and sipping coffee.

"Sir, have you seen a sock like this? Inquiring minds want to know." I hold out the gray sock.

Dad takes it, absentmindedly. "Isn't this the sock I lost last week? Where did you find it?"

I take Exhibit A back. "Sorry sir, this is John's sock. I'm looking into the alleged disappearance of its mate."

He goes back to his paper. "While you're at it, look into the disappearance of mine. We've only got ten minutes."

"What's that?" Mom comes downstairs—every hair in place—and pours herself a cup of coffee.

"Nothing, dear," says Dad. They both look at me. "Annabel! Go get dressed!"

If I were a sock, where would I hide? I pace through the living room, looking for clues. What kind of clue could a sock leave? Footprints? A bit of unraveled wool? A sticker that says "Inspected by No. 13"?

In the corner, the television howls about sugar-coated cereal. The sound makes it hard to concentrate. I head over to switch it off. Suddenly, there on the screen is a clue! Some man is walking down the hall, his pants all twisted up, a sock stuck to his back. The screen switches to a lady with her dress sticking to her slip and then shows a can of spray gunk for your dryer. I've got it! I click off the TV and race to the laundry room.

23
The gray sock is there, inside the dryer with the last load, clinging to Mom's new silk blouse. "I found it!" I yell. John comes pounding down the stairs. Mom and Dad poke their noses in from the kitchen. "Look here!" I wave the sock triumphantly.

"Solid detective work, Sis," admits John, taking the sock. He puts it on. "Now, let's have it."

25
"Have what?"

"My other sock. The one I gave you. Exhibit A." He holds out his hand, balancing on one foot, one sock on, one sock off. "Give it here. I need it."

I look at my hands. Notebook, check. Pen, check. No sock. "Now let's see. I had it just a minute ago . . ." """

# Grade 5 Reading Questions
GRADE_5_READING_QUESTIONS = [
    # Life without Gravity questions (1-8)
    {
        "grade_level": 5,
        "topic": "Reading Comprehension",
        "difficulty": 2,
        "weight": 1.0,
        "prompt": f"Read the passage:\n\n{LIFE_WITHOUT_GRAVITY}\n\nWhat are two main ideas about weightlessness in the text?",
        "choices": [
            "It is easy to handle and makes the room seem bigger.",
            "It makes bones heavy and causes the head to swell.",
            "It is uncomfortable for the body and upsets the stomach.",
            "It reroutes the flow of blood and puts the heart in danger."
        ],
        "correct_answer": "It is uncomfortable for the body and upsets the stomach.",
        "explanation": "The text explains that weightlessness causes physical discomfort: face puffs up, nose gets stuffy, back hurts, stomach gets upset."
    },
    {
        "grade_level": 5,
        "topic": "Reading Comprehension",
        "difficulty": 2,
        "weight": 1.0,
        "prompt": f"Read the passage:\n\n{LIFE_WITHOUT_GRAVITY}\n\nWhy does the author use the word NOT in paragraph 2?",
        "choices": [
            "The author is trying to make sure the reader understands the point.",
            "The author is showing that some information is untrue.",
            "The author is using quotes from a space tourist.",
            "The author is disagreeing with the reader."
        ],
        "correct_answer": "The author is showing that some information is untrue.",
        "explanation": "The author uses 'NOT!' to contradict the opening paragraph's positive view of weightlessness, showing that the initial description is misleading."
    },
    {
        "grade_level": 5,
        "topic": "Reading Comprehension",
        "difficulty": 2,
        "weight": 1.0,
        "prompt": f"Read the passage:\n\n{LIFE_WITHOUT_GRAVITY}\n\nWhich statement summarizes the author's view on weightlessness?",
        "choices": [
            "\"In fact, everything is fun, nothing is hard.\"",
            "\"'Living in space is like having a different life, living in a different world.'\"",
            "\"If you turn yourself upside down, the ceiling becomes the floor.\"",
            "\"In low gravity, you have to learn new ways to eat.\""
        ],
        "correct_answer": "\"'Living in space is like having a different life, living in a different world.'\"",
        "explanation": "This quote from Dennis Tito captures the author's main point that weightlessness creates a fundamentally different experience."
    },
    {
        "grade_level": 5,
        "topic": "Vocabulary",
        "difficulty": 2,
        "weight": 1.0,
        "prompt": f"Read the passage:\n\n{LIFE_WITHOUT_GRAVITY}\n\nWhat is the meaning of the word rerouted in paragraph 5?",
        "choices": [
            "pumping extra blood",
            "going the same way",
            "changing the direction",
            "hanging upside down"
        ],
        "correct_answer": "changing the direction",
        "explanation": "Rerouted means to change the direction or path. In space, blood flows differently, changing direction from legs to head."
    },
    {
        "grade_level": 5,
        "topic": "Reading Comprehension",
        "difficulty": 1,
        "weight": 1.0,
        "prompt": f"Read the passage:\n\n{LIFE_WITHOUT_GRAVITY}\n\nHow does the lack of gravity in space affect the bones?",
        "choices": [
            "The bones stretch and bend easier.",
            "The bones break while in space.",
            "The bones become stronger.",
            "The bones become thin and spongy."
        ],
        "correct_answer": "The bones become thin and spongy.",
        "explanation": "The text states that without gravity, bones get thin and spongy, and astronauts can lose 10 percent or more of their bone tissue."
    },
    {
        "grade_level": 5,
        "topic": "Reading Comprehension",
        "difficulty": 1,
        "weight": 1.0,
        "prompt": f"Read the passage:\n\n{LIFE_WITHOUT_GRAVITY}\n\nHow might astronauts in space prepare for the return to Earth?",
        "choices": [
            "by performing somersaults and flying around",
            "by learning how to care for themselves when feeling sick",
            "by doing exercises to strengthen bones and muscles",
            "by growing taller and getting flabby"
        ],
        "correct_answer": "by doing exercises to strengthen bones and muscles",
        "explanation": "The text explains that if astronauts don't exercise, their muscles become feeble and bones weaken, so they must exercise to prepare for Earth's gravity."
    },
    {
        "grade_level": 5,
        "topic": "Vocabulary",
        "difficulty": 2,
        "weight": 1.0,
        "prompt": f"Read the passage:\n\n{LIFE_WITHOUT_GRAVITY}\n\nWhat is meant by the phrase \"nooks and crannies\" in paragraph 12?",
        "choices": [
            "outer space",
            "small places",
            "on the ceiling",
            "out in the open"
        ],
        "correct_answer": "small places",
        "explanation": "Nooks and crannies refers to small, hidden places where objects can get stuck or lost."
    },
    {
        "grade_level": 5,
        "topic": "Reading Comprehension",
        "difficulty": 2,
        "weight": 1.0,
        "prompt": f"Read the passage:\n\n{LIFE_WITHOUT_GRAVITY}\n\nWhich statement summarizes the text?",
        "choices": [
            "After adjusting, the astronauts enjoy some of the benefits of weightlessness.",
            "At first, many astronauts find weightlessness to be fun and easy.",
            "Usually, astronauts take a one-year trip to Mars.",
            "In space, astronauts' bodies have to adapt to Earth's gravity."
        ],
        "correct_answer": "After adjusting, the astronauts enjoy some of the benefits of weightlessness.",
        "explanation": "The text explains that after about a week, people adjust and can enjoy benefits like flying around and using all wall space."
    },
    # Making the World's Rarest Syrup questions (9-16)
    {
        "grade_level": 5,
        "topic": "Reading Comprehension",
        "difficulty": 2,
        "weight": 1.0,
        "prompt": f"Read the passage:\n\n{MAKING_WORLDS_RAREST_SYRUP}\n\nWhich statement explains why saguaro ribs and creosote branches are important for creating saguaro syrup?",
        "choices": [
            "Saguaro fruit are peeled using saguaro ribs and creosote branches.",
            "Kukuipads are created with saguaro ribs and creosote branches.",
            "Fruit from creosote branches and saguaro ribs are used to make the syrup.",
            "Saguaro ribs and creosote branches are ingredients needed to create the syrup."
        ],
        "correct_answer": "Kukuipads are created with saguaro ribs and creosote branches.",
        "explanation": "Kukuipads (harvesting sticks) are made from saguaro ribs and creosote branches, which are needed to reach and harvest the fruit."
    },
    {
        "grade_level": 5,
        "topic": "Reading Comprehension",
        "difficulty": 2,
        "weight": 1.0,
        "prompt": f"Read the passage:\n\n{MAKING_WORLDS_RAREST_SYRUP}\n\nBased on paragraphs 4 and 5, why are creosote branches used at the top of a kukuipad?",
        "choices": [
            "Creosote branches are straight and light, making it easy to spear fruit at the top of a saguaro cactus.",
            "Creosote branches are thick and heavy, making it easy to push fruit from the top of a saguaro cactus.",
            "Creosote branches are bright red and freckled, making it easy to see them at the top of a saguaro cactus.",
            "Creosote branches are sturdy and durable, making it easy to prod fruit from the top of a saguaro cactus."
        ],
        "correct_answer": "Creosote branches are sturdy and durable, making it easy to prod fruit from the top of a saguaro cactus.",
        "explanation": "The text states that creosote is very strong and won't easily break when pulled or pushed, which is how the fruit is brought down."
    },
    {
        "grade_level": 5,
        "topic": "Reading Comprehension",
        "difficulty": 2,
        "weight": 1.0,
        "prompt": f"Read the passage:\n\n{MAKING_WORLDS_RAREST_SYRUP}\n\nWhich detail reveals how the Tohono O'odham feel about the land?",
        "choices": [
            "Gina shows the harvesters how to make kukuipad.",
            "Gina and Angie add water to the saguaro fruit and boil it.",
            "Gina tells the harvesters to leave the first fruit at the base of the saguaro.",
            "Gina brings a square cloth to strain the syrup before boiling it again."
        ],
        "correct_answer": "Gina tells the harvesters to leave the first fruit at the base of the saguaro.",
        "explanation": "Leaving the peel red-side up at the base to 'summon the summer rains' shows respect and connection to the land."
    },
    {
        "grade_level": 5,
        "topic": "Vocabulary",
        "difficulty": 2,
        "weight": 1.0,
        "prompt": f"Read the passage:\n\n{MAKING_WORLDS_RAREST_SYRUP}\n\nWhat does the word summon mean in paragraph 8?",
        "choices": [
            "bring forth",
            "send away",
            "catch",
            "stop"
        ],
        "correct_answer": "bring forth",
        "explanation": "Summon means to call forth or bring about. The peel is left to help bring forth the summer rains."
    },
    {
        "grade_level": 5,
        "topic": "Reading Comprehension",
        "difficulty": 2,
        "weight": 1.0,
        "prompt": f"Read the passage:\n\n{MAKING_WORLDS_RAREST_SYRUP}\n\nWhich step comes after placing the peel at the base of the saguaro?",
        "choices": [
            "Bring out a square cloth to strain the mixture.",
            "Return the hot juice to the cleaned pot to boil a second time.",
            "Scoop the fruit into buckets and avoid the spines that cling to the peel.",
            "Nudge the saguaro fruit loose and put into buckets."
        ],
        "correct_answer": "Scoop the fruit into buckets and avoid the spines that cling to the peel.",
        "explanation": "After leaving the peel at the base (paragraph 8), the next step is scooping fruit into buckets (paragraph 9)."
    },
    {
        "grade_level": 5,
        "topic": "Vocabulary",
        "difficulty": 2,
        "weight": 1.0,
        "prompt": f"Read the passage:\n\n{MAKING_WORLDS_RAREST_SYRUP}\n\nWhat does the word flecked mean in paragraph 9?",
        "choices": [
            "striped",
            "dotted",
            "disguised",
            "wrapped"
        ],
        "correct_answer": "dotted",
        "explanation": "Flecked means marked with small spots or dots, like the hands being marked with black seeds."
    },
    {
        "grade_level": 5,
        "topic": "Vocabulary",
        "difficulty": 2,
        "weight": 1.0,
        "prompt": f"Read the passage:\n\n{MAKING_WORLDS_RAREST_SYRUP}\n\nWhat is the meaning of strain as it is used in paragraph 10?",
        "choices": [
            "pass through a filter",
            "injure a body part",
            "painful effort",
            "make great demands"
        ],
        "correct_answer": "pass through a filter",
        "explanation": "In this context, strain means to pass liquid through a filter or cloth to separate solids from liquids."
    },
    {
        "grade_level": 5,
        "topic": "Reading Comprehension",
        "difficulty": 2,
        "weight": 1.0,
        "prompt": f"Read the passage:\n\n{MAKING_WORLDS_RAREST_SYRUP}\n\nHow are the harvesting of saguaro fruit and the creation of saguaro syrup similar?",
        "choices": [
            "Both require creosote branches and boiling water to reach the desired result.",
            "Both require inexperience and good fortune to reach the desired result.",
            "Both require kukuipads and large pots to reach the desired result.",
            "Both require patience and persistence to reach the desired result."
        ],
        "correct_answer": "Both require patience and persistence to reach the desired result.",
        "explanation": "Gina explains that making syrup requires 'a lot of patience,' and harvesting also requires careful, persistent work."
    },
    # The World in a Bottle questions (17-24)
    {
        "grade_level": 5,
        "topic": "Reading Comprehension",
        "difficulty": 2,
        "weight": 1.0,
        "prompt": f"Read the passage:\n\n{WORLD_IN_A_BOTTLE}\n\nWhich two details from the text support the main ideas?",
        "choices": [
            "A terrarium is easy to create, and terrariums were first named Wardian cases.",
            "A terrarium gets its name from the Greek word terra, and a terrarium is in a clear glass or plastic container.",
            "A terrarium is used as a home-decorating item, and Wardian cases replaced greenhouses in the Victorian era.",
            "A terrarium is a tiny ecosystem inside a container, and Dr. Ward accidentally discovered the terrarium."
        ],
        "correct_answer": "A terrarium is a tiny ecosystem inside a container, and Dr. Ward accidentally discovered the terrarium.",
        "explanation": "These two details support the main ideas: that terrariums are self-contained ecosystems and that they were discovered accidentally."
    },
    {
        "grade_level": 5,
        "topic": "Reading Comprehension",
        "difficulty": 2,
        "weight": 1.0,
        "prompt": f"Read the passage:\n\n{WORLD_IN_A_BOTTLE}\n\nWhich describes a good terrarium?",
        "choices": [
            "a new, clean container",
            "a large, clear container",
            "a recycled, used container",
            "an expensive, fancy container"
        ],
        "correct_answer": "a large, clear container",
        "explanation": "The text mentions Wardian cases were 'more spacious' versions, and the passage emphasizes clear containers for visibility."
    },
    {
        "grade_level": 5,
        "topic": "Vocabulary",
        "difficulty": 2,
        "weight": 1.0,
        "prompt": f"Read the passage:\n\n{WORLD_IN_A_BOTTLE}\n\nWhat is the meaning of transparent in paragraph 5?",
        "choices": [
            "unbreakable",
            "gigantic",
            "clear",
            "open"
        ],
        "correct_answer": "clear",
        "explanation": "Transparent means see-through or clear, allowing light to pass through so you can see inside."
    },
    {
        "grade_level": 5,
        "topic": "Reading Comprehension",
        "difficulty": 2,
        "weight": 1.0,
        "prompt": f"Read the passage:\n\n{WORLD_IN_A_BOTTLE}\n\nHow did Dr. Ward's study of the sphinx moth affect his decision to write a book?",
        "choices": [
            "His studies of the sphinx moth caused his accidental discovery of the terrarium.",
            "His studies of the sphinx moth became popular during the Victorian era.",
            "His studies of the sphinx moth were published in the book.",
            "His studies of the sphinx moth were performed inside Wardian cases."
        ],
        "correct_answer": "His studies of the sphinx moth caused his accidental discovery of the terrarium.",
        "explanation": "While studying the sphinx moth, Dr. Ward accidentally discovered plants growing in his sealed container, which led to his book about terrariums."
    },
    {
        "grade_level": 5,
        "topic": "Reading Comprehension",
        "difficulty": 1,
        "weight": 1.0,
        "prompt": f"Read the passage:\n\n{WORLD_IN_A_BOTTLE}\n\nWhat happened to Dr. Ward's experimental terrarium?",
        "choices": [
            "It became too dry.",
            "It required much care.",
            "It lasted for years.",
            "It bloomed too often."
        ],
        "correct_answer": "It lasted for years.",
        "explanation": "The text states that Dr. Ward kept the jar sealed for four years and the plants grew and thrived."
    },
    {
        "grade_level": 5,
        "topic": "Reading Comprehension",
        "difficulty": 2,
        "weight": 1.0,
        "prompt": f"Read the passage:\n\n{WORLD_IN_A_BOTTLE}\n\nFor what reason does the author include information on the origin of the terrarium in the text?",
        "choices": [
            "to help the reader understand its history",
            "to provide directions about how to create it",
            "to show its importance in home decorating",
            "to tell the background of its inventor"
        ],
        "correct_answer": "to help the reader understand its history",
        "explanation": "The author includes the historical background to help readers understand how terrariums came to be."
    },
    {
        "grade_level": 5,
        "topic": "Vocabulary",
        "difficulty": 2,
        "weight": 1.0,
        "prompt": f"Read the passage:\n\n{WORLD_IN_A_BOTTLE}\n\nWhat is the meaning of the word exotic in paragraph 8?",
        "choices": [
            "familiar",
            "unusual",
            "local",
            "unsteady"
        ],
        "correct_answer": "unusual",
        "explanation": "Exotic means foreign, unusual, or from another place, referring to plants from distant locations."
    },
    {
        "grade_level": 5,
        "topic": "Reading Comprehension",
        "difficulty": 2,
        "weight": 1.0,
        "prompt": f"Read the passage:\n\n{WORLD_IN_A_BOTTLE}\n\nHow did terrariums help plant collectors?",
        "choices": [
            "Plant collectors could learn to build greenhouses.",
            "Terrariums allowed plant collectors to grow gardens.",
            "Plant collectors could experiment with saltwater and freshwater.",
            "Terrariums allowed plant collectors to safely travel with plants."
        ],
        "correct_answer": "Terrariums allowed plant collectors to safely travel with plants.",
        "explanation": "Wardian cases protected delicate tropical plants during long voyages at sea from salt air and climate changes."
    },
    # Annabel Lee, P.I. questions (25-32)
    {
        "grade_level": 5,
        "topic": "Reading Comprehension",
        "difficulty": 3,
        "weight": 1.5,
        "prompt": f"Read the passage:\n\n{ANNABEL_LEE_PI}\n\nWhich quote supports Annabel Lee's point of view that life in her house is like a case waiting to be solved?",
        "choices": [
            "\"I'm working the day shift out of headquarters.\"",
            "\"Leap downstairs, taking the steps two by two, to the laundry room.\"",
            "\"I lick the tip of my pen, like they do on cop shows.\"",
            "\"I find him at the kitchen table, reading the paper and sipping coffee.\""
        ],
        "correct_answer": "\"I'm working the day shift out of headquarters.\"",
        "explanation": "This quote shows Annabel views her home as her workplace/headquarters, treating everyday situations as cases to solve."
    },
    {
        "grade_level": 5,
        "topic": "Reading Comprehension",
        "difficulty": 2,
        "weight": 1.0,
        "prompt": f"Read the passage:\n\n{ANNABEL_LEE_PI}\n\nHow does the dialogue in paragraphs 12–19 compare Annabel Lee and her brother, John?",
        "choices": [
            "It underlines the fact that Annabel Lee deeply admires her brother, John.",
            "It creates a sense of their relationship and shows that John and Annabel Lee think alike.",
            "It underlines the fact that Annabel Lee and John are incapable of getting along.",
            "It creates a sense of their relationship and implies that John often tolerates Annabel Lee's behavior."
        ],
        "correct_answer": "It creates a sense of their relationship and implies that John often tolerates Annabel Lee's behavior.",
        "explanation": "John's responses show annoyance but tolerance, calling her 'birdbrain' but still answering her questions."
    },
    {
        "grade_level": 5,
        "topic": "Reading Comprehension",
        "difficulty": 2,
        "weight": 1.0,
        "prompt": f"Read the passage:\n\n{ANNABEL_LEE_PI}\n\nWhat can be inferred from the quote below in paragraph 17?\n\n\"'It's a sock, see. What do you think it looks like? An elephant?'\"",
        "choices": [
            "John appreciates his sister's help.",
            "John thinks his sister has the sock.",
            "John is bothered by his sister's help.",
            "John does not think he will find his sock."
        ],
        "correct_answer": "John is bothered by his sister's help.",
        "explanation": "John's sarcastic tone and rhetorical question show he's annoyed by Annabel's detective routine."
    },
    {
        "grade_level": 5,
        "topic": "Reading Comprehension",
        "difficulty": 2,
        "weight": 1.0,
        "prompt": f"Read the passage:\n\n{ANNABEL_LEE_PI}\n\nWhich statement describes how Mom feels when Annabel asks her about the missing sock?",
        "choices": [
            "She is upset that the children do not help with the chores.",
            "She is grateful that Annabel likes to solve mysteries.",
            "She is dismayed that Jack is not dressed yet.",
            "She is worried that it will never be found."
        ],
        "correct_answer": "She is upset that the children do not help with the chores.",
        "explanation": "Mom sighs and says 'If you and your brother would offer to help once in a while,' showing her frustration."
    },
    {
        "grade_level": 5,
        "topic": "Reading Comprehension",
        "difficulty": 2,
        "weight": 1.0,
        "prompt": f"Read the passage:\n\n{ANNABEL_LEE_PI}\n\nWhich quote suggests that the mother feels resentment?",
        "choices": [
            "\"'Oh, you found it? John was looking for it. Get dressed for school, dear, or you'll miss the bus.'\"",
            "\"'If you and your brother would offer to help once in a while . . .'\"",
            "\"Her eyes narrow in The Mom Look.\"",
            "\"'What's that?' Mom comes downstairs—every hair in place—and pours herself a cup of coffee.\""
        ],
        "correct_answer": "\"'If you and your brother would offer to help once in a while . . .'\"",
        "explanation": "This quote directly expresses Mom's frustration that the children don't help with household chores."
    },
    {
        "grade_level": 5,
        "topic": "Vocabulary",
        "difficulty": 2,
        "weight": 1.0,
        "prompt": f"Read the passage:\n\n{ANNABEL_LEE_PI}\n\nWhat is the meaning of the word triumphantly in paragraph 32?",
        "choices": [
            "mysteriously",
            "successfully",
            "pleasantly",
            "harshly"
        ],
        "correct_answer": "successfully",
        "explanation": "Triumphantly means in a way that shows success or victory, as Annabel feels she solved the case."
    },
    {
        "grade_level": 5,
        "topic": "Reading Comprehension",
        "difficulty": 2,
        "weight": 1.0,
        "prompt": f"Read the passage:\n\n{ANNABEL_LEE_PI}\n\nWhat inference can be made from the question \"Have what?\" in paragraph 34?",
        "choices": [
            "Annabel's brother lost the other sock.",
            "Annabel's mom lost the other sock.",
            "Annabel's dad lost the other sock.",
            "Annabel lost the other sock."
        ],
        "correct_answer": "Annabel lost the other sock.",
        "explanation": "John asks for 'Exhibit A' back, and Annabel realizes she doesn't have it, meaning she lost it."
    },
    {
        "grade_level": 5,
        "topic": "Reading Comprehension",
        "difficulty": 3,
        "weight": 1.5,
        "prompt": f"Read the passage:\n\n{ANNABEL_LEE_PI}\n\nHow does Annabel Lee's detective approach influence how the events in the story are told?",
        "choices": [
            "It creates a methodical and orderly structure for the plot.",
            "It adds a sense of surprise and disappointment to the plot.",
            "It provides a framework of frustration for the family.",
            "It offers an inside look at the disorganization in the family."
        ],
        "correct_answer": "It creates a methodical and orderly structure for the plot.",
        "explanation": "Annabel's detective approach structures the story as she interviews witnesses, collects evidence, and solves the case systematically."
    },
    # Antonio Canova questions (33-40)
    {
        "grade_level": 5,
        "topic": "Reading Comprehension",
        "difficulty": 2,
        "weight": 1.0,
        "prompt": f"Read the passage:\n\n{ANTONIO_CANOVA}\n\nWhich theme do key details in the selection support?",
        "choices": [
            "Generosity is rewarded.",
            "Do not judge a book by its cover.",
            "People should overcome their fear.",
            "Family is most important."
        ],
        "correct_answer": "Do not judge a book by its cover.",
        "explanation": "The story shows that Antonio, a poor boy working in the kitchen, had hidden talent that no one expected, teaching not to judge by appearance."
    },
    {
        "grade_level": 5,
        "topic": "Reading Comprehension",
        "difficulty": 2,
        "weight": 1.0,
        "prompt": f"Read the passage:\n\n{ANTONIO_CANOVA}\n\nWhere did Antonio get ideas for his \"pictures\" as a little boy?",
        "choices": [
            "from rich people",
            "from other famous artists",
            "from stories his grandmother told him",
            "from what he saw his grandfather doing"
        ],
        "correct_answer": "from stories his grandmother told him",
        "explanation": "The text states that the grandmother would tell him stories that 'filled his mind with pictures of wonderful and beautiful things.'"
    },
    {
        "grade_level": 5,
        "topic": "Vocabulary",
        "difficulty": 2,
        "weight": 1.0,
        "prompt": f"Read the passage:\n\n{ANTONIO_CANOVA}\n\nWhat does the phrase \"spread the table\" mean in paragraph 8?",
        "choices": [
            "to separate the table",
            "to make the table cleaner",
            "to make the table larger",
            "to decorate the table"
        ],
        "correct_answer": "to decorate the table",
        "explanation": "To spread the table means to set it up or decorate it for a meal, arranging items on it."
    },
    {
        "grade_level": 5,
        "topic": "Reading Comprehension",
        "difficulty": 2,
        "weight": 1.0,
        "prompt": f"Read the passage:\n\n{ANTONIO_CANOVA}\n\nWhich event caused Antonio to create the sculpture?",
        "choices": [
            "The stonecutter could not fix the sculpture.",
            "The servants dared him to make the sculpture.",
            "The Count paid him to make the sculpture.",
            "The servant broke the original sculpture."
        ],
        "correct_answer": "The servant broke the original sculpture.",
        "explanation": "A servant broke the statue meant for the center of the table, which created the need for Antonio to make a replacement."
    },
    {
        "grade_level": 5,
        "topic": "Reading Comprehension",
        "difficulty": 2,
        "weight": 1.0,
        "prompt": f"Read the passage:\n\n{ANTONIO_CANOVA}\n\nWhich event allowed Antonio to sit at the Count's table?",
        "choices": [
            "The statue on the center of the table was stolen.",
            "Antonio's grandfather was friends with the Count.",
            "The statue to be used for the table centerpiece was broken.",
            "Antonio won a contest and sitting with the Count was the prize."
        ],
        "correct_answer": "The statue to be used for the table centerpiece was broken.",
        "explanation": "When the original statue broke, Antonio created a replacement that impressed everyone, leading to him being invited to sit at the table."
    },
    {
        "grade_level": 5,
        "topic": "Reading Comprehension",
        "difficulty": 2,
        "weight": 1.0,
        "prompt": f"Read the passage:\n\n{ANTONIO_CANOVA}\n\nWhat is the reason why \"the Count sent for Antonio to come and live with him\" the very next day?",
        "choices": [
            "He needed to protect Antonio from other artists who were jealous of his skills.",
            "He wanted to provide Antonio with great art teachers to develop his talent.",
            "He hoped to guarantee that Antonio would create sculptures only for him.",
            "He wanted to raise Antonio to be a stonecutter like his grandfather."
        ],
        "correct_answer": "He wanted to provide Antonio with great art teachers to develop his talent.",
        "explanation": "The text states that 'The best artists in the land were employed to teach him the art in which he had shown so much skill.'"
    },
    {
        "grade_level": 5,
        "topic": "Reading Comprehension",
        "difficulty": 2,
        "weight": 1.0,
        "prompt": f"Read the passage:\n\n{ANTONIO_CANOVA}\n\nWhich sentence supports the idea that Antonio achieved success?",
        "choices": [
            "\"'What a beautiful work of art!' they cried.\"",
            "\"'Truly, my friends,' he said, 'this is as much of a surprise to me as to you.'\"",
            "\"'My name is Antonio Canova,' said the boy, 'and I have had no teacher but my grandfather the stonecutter.'\"",
            "\"In a few years, Antonio Canova became known as one of the greatest sculptors in the world.\""
        ],
        "correct_answer": "\"In a few years, Antonio Canova became known as one of the greatest sculptors in the world.\"",
        "explanation": "This sentence directly states that Antonio achieved great success and recognition as a sculptor."
    },
    {
        "grade_level": 5,
        "topic": "Reading Comprehension",
        "difficulty": 3,
        "weight": 1.5,
        "prompt": f"Read the passage:\n\n{ANTONIO_CANOVA}\n\nWhat is the narrator's point of view on the servant breaking the sculpture before the Count's dinner?",
        "choices": [
            "It caused Antonio to show his great talent.",
            "It caused Antonio's grandfather to lose his job.",
            "It caused the Count to cancel the dinner.",
            "It caused the head servant to get fired."
        ],
        "correct_answer": "It caused Antonio to show his great talent.",
        "explanation": "The breaking of the sculpture created an opportunity for Antonio to demonstrate his artistic ability, which changed his life."
    }
]


def add_grade5_reading_questions():
    """Add Grade 5 Reading questions to the database."""
    db: Session = SessionLocal()
    try:
        added_count = 0
        skipped_count = 0
        
        for question_data in GRADE_5_READING_QUESTIONS:
            # Check for duplicates based on grade_level, topic, difficulty, and weight
            # (Cannot compare CLOB fields like prompt and correct_answer directly)
            existing = db.query(Question).filter(
                Question.grade_level == question_data["grade_level"],
                Question.topic == question_data["topic"],
                Question.difficulty == question_data["difficulty"],
                Question.weight == question_data["weight"]
            ).first()
            
            if existing:
                print(f"Skipping duplicate question: Grade {question_data['grade_level']}, {question_data['topic']}, Difficulty {question_data['difficulty']}")
                skipped_count += 1
                continue
            
            question = Question(
                grade_level=question_data["grade_level"],
                topic=question_data["topic"],
                difficulty=question_data["difficulty"],
                weight=question_data["weight"],
                prompt=question_data["prompt"],
                choices=question_data["choices"],
                correct_answer=question_data["correct_answer"],
                explanation=question_data.get("explanation", "")
            )
            
            db.add(question)
            added_count += 1
        
        db.commit()
        print(f"\n✅ Successfully added {added_count} Grade 5 Reading questions")
        if skipped_count > 0:
            print(f"⏭️  Skipped {skipped_count} duplicate questions")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error adding questions: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    print("Adding Grade 5 Reading EOG questions to the database...")
    add_grade5_reading_questions()
    print("Done!")
