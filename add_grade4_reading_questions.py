"""
Script to add Grade 4 Reading EOG questions to the database.
Based on the Grade 4 Reading EOG Released Items.
"""
import sys
import os
from sqlalchemy.orm import Session
from app.db import SessionLocal, engine
from app.models import Question, Base

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

# Grade 4 Reading Passages (single passages, no parts)

LIBBY_SAVES_TEAM = """Libby Saves the Team
by Kristine Nielsen

Libby wiggled with excitement as she watched her dad hook up their six Alaskan huskies to the red and black canvas sled. Her brown eyes peeked out of the fur-lined hood which outlined her round, full face.

Libby paced around the sled, impatiently waiting for her father as he hooked each dog to the gang-line. "Dad," she shouted in her self-assured voice, "let's go! I want to go! The dogs have ants in their pants. Let's go!"

"Yeah, just a minute, Libby. I've got one more dog to harness, and we're out of here," her dad said.

The dogs, sensing the excitement in Libby's voice, began a chorus of their own, joining in one at a time with howls and cries.

Just minutes later, Libby hopped into the sled and wiggled down to get comfortable on a bed of washed-out throw pillows.

Libby's dad took a position standing on the sled behind her. He shouted out to the team, "Ready, girls? Yip!"

7
The dogs' ears stood erect as the team lunged forward.

8
Libby felt the power of the dogs as the sled jolted across the packed-snow trail. She held tightly to the sides of the sled with her oversized gloves while steadying herself against the cold canvas. "Whee . . . we're finally off. I can hardly believe it," Libby giggled.

Her father yelled, "Gee!" and the dogs obediently turned into the woods.

The sled stirred the snow up around them, and the wind threw the snow into Libby's smiling face. "How far are we running the dogs today?" Libby called to her dad.

"About twenty miles, Libby. If they make it that far," he answered.

Libby reached out toward the pine trees and grabbed one of the snow-covered branches. Clenching the twig, she snapped it off and swung it between Timber and Tucker, the two dogs closest to the sled. "Go, girls, go!" Libby called.

Just as Libby shouted, the dogs darted, with a bump, through the woods faster than ever, and Libby giggled in excitement.

Seconds passed, then Libby heard her father shouting in the distance behind her. She turned around and brushed her hair back and tried to see through the back of the sled.

"Dad? Dad, where are you?" she yelled.

There was no response. She realized her father must have been bumped off the sled on the last turn. What was she going to do? The sled bounced along the trail.

Libby steadied her shaky legs and stood. It seemed the sled was moving faster than ever. Grabbing the canvas with one hand and the top of the sled with the other, she pulled herself over the bar and planted her feet where her father's had been just minutes before. She felt her heart beating faster and faster.

She reached down for the metal anchor and pushed it over the edge of the sled. Nothing happened. The dogs still raced out of control, not feeling the weight of the anchor dragging in the snow.

Libby then leaned back, dug her right boot deep into the snow and commanded the dogs to stop. "Whoa, girls, WHOA!" she shouted at the top of her lungs.

The sled slowed to a halt, and the dogs stood motionless, waiting for her next command.

Libby let out a sigh and wiped her wet nose with her gloves, which were now dirty and torn.

Soon her father came running through the snow. He grabbed Libby and hugged her.

"You saved the team, Libby! You really did it. I'm so proud of you."

Libby spread her cheeks into a wide, proud smile for her dad and squeezed him even tighter. Libby and her father stood at the edge of the sled until the dogs gently nudged them on, and then they headed for home."""

AMELIA_EARHART = """Excerpt from Amelia Earhart
by Marilyn Rosenthal and Daniel Freeman

Friendly Flight

In 1928, Amelia met with book publisher George Palmer Putnam. He was arranging an airplane flight across the Atlantic Ocean. The airplane Friendship belonged to Amy Guest. She wanted to show that women could fly in airplanes like men could.

George wanted Amelia to be a passenger on the flight. She would be the first woman to travel across the Atlantic Ocean in an airplane. On June 17, 1928, Amelia, pilot Wilmer Stultz, and a mechanic took off from Newfoundland, Canada. They landed safely near England 20 hours and 40 minutes later. Amelia instantly became famous. But she did not feel she had earned the fame. She had not been the pilot.

George became Amelia's manager after the flight. He arranged for her to write books and give talks about flying. Amelia and George became friends. They married in 1931.

New Records

Amelia was famous because of the Friendship's flight across the Atlantic Ocean. But she wanted to set a record by herself. She wanted to fly across the Atlantic Ocean alone. No woman had done this.

By 1932, she was ready to make the flight. Amelia would fly a Lockheed Vega. The airplane could carry enough fuel to fly 3,200 miles (5,150 kilometers) without stopping.

On May 20, 1932, Amelia took off from Newfoundland, Canada. Her airplane's altimeter quit. Amelia could not tell how high she was flying. She also had to fly through heavy rain and strong winds. But she landed safely in Ireland 13 hours later.

Amelia wanted to become the first person to fly nonstop across the Pacific Ocean. Ten pilots had died attempting this flight. In 1935, Amelia took off from Hawaii and landed safely in Oakland, California.

Women's Rights

8
Amelia used her fame to help women. She started The Ninety-Nines in 1929. This group of women pilots originally had 99 members. Today, The Ninety-Nines continues to encourage women to become pilots.

Amelia knew U.S. President Franklin Delano Roosevelt and his wife, Eleanor. Amelia and Eleanor gave speeches in favor of women's rights.

10
The president of Purdue University, Edwin C. Elliot, was impressed with Amelia's efforts. Edwin asked Amelia to become a career counselor at Purdue. Amelia advised almost 1,000 women students.

At Purdue, Amelia began planning a flight around the world. She wanted to be the first person to fly around the Earth near the equator. Purdue helped pay for an airplane that could fly 4,500 miles (7,242 kilometers) without refueling.

Final Flight

12
On June 1, 1937, Amelia and her navigator, Fred Noonan, took off from Miami, Florida. They made stops in South America, Africa, Asia, and Australia.

On July 1, Amelia and Fred took off from Lae, New Guinea. Their last stop before arriving back in the United States was Howland Island. This tiny island in the Pacific Ocean was 2,500 miles (4,023 kilometers) northeast of Lae.

But Amelia and Fred never made it to Howland Island. Amelia lost radio contact with the U.S. Navy at around 8:45 a.m. on July 2. She had told the navy they were near the island. She said the airplane was almost out of gas. Amelia and Fred had disappeared.

Ships and airplanes searched 250,000 square miles (647,500 kilometers) of ocean for 15 days. Amelia and Fred were never found. No one knows why Amelia's airplane disappeared."""

WHATS_IT_LIKE_TO_BE_A_CHEF = """What's It Like to Be a Chef?
This article was written in 2006.

November is one of my favorite times of the year. It seems that everyone spends a lot more time in the kitchen getting ready for Thanksgiving! Pumpkin pie, turkey, sweet potatoes—yum! Have you ever wondered what it's like to be a chef and to cook for lots and lots of people? Bill Justus is the Executive Chef at Hershey Lodge^1 in Hershey, Pennsylvania. He comes up with recipes to go on the menus of the resort's restaurants, and he loves to cook with chocolate. And not just desserts! At Hershey, the home of the famous Hershey chocolate bar, they use chocolate in all different types of recipes! I was lucky to meet with Chef Justus and get his story about what it's like to be a chef.

TRUMAN: What does it take to become a chef?

CHEF JUSTUS: First of all, it takes a little bit of schooling. Whether you go through an apprenticeship,^2 or there's a lot of really good culinary^3 schools in the United States now. If you are in an area that is fortunate to have a good vocational technical school,^4 that's a good way for you to get in and see if it's really something you'd like to pursue as a profession.

TRUMAN: When did you know that this was something you wanted to do for a living?

5
CHEF JUSTUS: Well, I'd always kind of kicked the idea around a little bit, helping my aunt and uncle who had some restaurants. Probably when I went into vocational school is when I really started taking it seriously as a profession. I went to vocational school during my junior and senior years of high school.

TRUMAN: Did you always like to help out in the kitchen when you were young?

CHEF JUSTUS: I always helped out somewhat. My mother is a really, really good cook, and she can make pretty much anything. My grandmother was a really good baker, and she liked to make candies. I have two brothers, so when my mom was at work, I would help her out a little bit in the kitchen.

TRUMAN: What exactly do you do as an executive chef?

CHEF JUSTUS: As an executive chef, you have a lot of responsibilities, not only with cooking, but with scheduling, menu planning, organizing, hiring, training. Budgets and numbers, things of that nature. Not only is it being a good cook, but you also have to communicate with people—like we're doing here today. With the Food Network and things like that, people are a little more aware of what's going on and a little more educated about cooking.

TRUMAN: What is a typical day like?

CHEF JUSTUS: A typical day is coming in, going over financial reports from the previous day, meeting with your staff and going over menu development. We have menu tastings, too. The property is pretty big, so we have really big groups that come in. We have one coming up soon for 1,300 people. It's a lot of planning—planning ahead. You have to figure out how much lettuce to order, how many vegetables to order, things of that nature. We try to use seasonal products on the menu and change them for spring, fall, and special holidays.

TRUMAN: So when do you actually cook?

13
CHEF JUSTUS: I cook as much as I can. I'm fortunate enough that when we do the specialty functions, I try to get a hand in that. A lot of times, my sous chefs—the assistants—they are the ones that are on the floor throughout the day supervising the line-level staff^5 and making sure that everything is going according to plan.

TRUMAN: So, what's the best part of your job?

CHEF JUSTUS: I think the creativity. It changes daily. Dealing with different groups and the diversity of what we do—one day you might be doing a basic box lunch, and the next day you're doing a seven-course dinner. It changes—every day it's something different. It's exciting.

TRUMAN: What's the worst part of your job?

CHEF JUSTUS: I don't consider anything bad. I think the one thing people would have to realize is that the hours are different than most people have. You work the weekends, the holidays; it's not a bad thing, just something you should be aware of. My first chef told me, "Always remember, when everybody is playing, you're working."

TRUMAN: I hear you do some interesting things with chocolate. What's your favorite kind of chocolate?

CHEF JUSTUS: My favorite is the Hershey Special Dark. They've also come out with some new products, the extra dark. I like the dark chocolates. We use the chocolates as much as we can. Not only for desserts, but we try to use it in the center-of-plate items. We use the Hershey cocoas, spice it up with different spices and seasonings and use it as a rub for meats, fish, and chicken. We try to use chocolate not only for dessert, but other applications. We do a chocolate-barbecued chicken wing that is pretty good.

TRUMAN: What's your favorite dessert?

CHEF JUSTUS: My favorite dessert—hmm, I like desserts! My favorite dessert is probably pumpkin pie.

TRUMAN: And what's your favorite meal?

CHEF JUSTUS: I like to make soups when I'm at home. I like a nice homemade soup or stew. I like the one-dish meals.

TRUMAN: What are you serving for Thanksgiving dinner at Hershey Lodge?

CHEF JUSTUS: We're going to have a wide variety of things, a little bit of an international flair this year. We'll be using local ingredients as well as recipes and items from around the world. We're calling it a world of thanks.

TRUMAN: What kind of advice would you give to kids who are interested in becoming a chef?

CHEF JUSTUS: Be open-minded. Study. Math, science, all the classes, take all that to heart and make sure to get a good education. The opportunities are wide open in the culinary and hospitality^6 field. You can be adventurous and travel. Be open-minded.

TRUMAN: Thanks for talking to me! And these cookies are delicious—this really is the sweetest place on Earth!

Footnotes
^1 lodge: a hotel
^2 apprenticeship: a training period when a person learns on the job
^3 culinary: concerning cooking
^4 vocational technical school: a school that trains people for a particular job
^5 line-level staff: beginning jobs
^6 hospitality: concerning housing and entertaining visitors"""

REGULAR_RAILROAD_DOG = """Adapted from "A Regular Railroad Dog"
by Avis J. Kirsch

Trigger was a railroad dog right from the start. Charlie, the station agent, found the black-and-white cocker spaniel in a deserted boxcar.

Before he adopted Trigger, Charlie was frequently lonesome. He worked at a small railroad station high up in the Rocky Mountains of Colorado. He was the flagman, switchman, and yardmaster. He was everything, because there was no one else.

One of Charlie's duties was to turn the switch, and Trigger went with him. It was an important task. At the switch, the trains could go on the right track fork to the gold fields or on the left track fork to the silver mines. Charlie knew which way to turn the switch by the number of toots signaled to him by the engineer.

Hearing those engine whistles all the time, Trigger learned to tell them apart. Whenever they sounded, he ran to the switch. With his little head cocked to one side and his black-and-white tail straight up, he'd watch Charlie open the correct switch.

Trigger took such an interest in the switching that Charlie made a decision. "I'm going to teach you how to lift the handle with your nose and move it with your paws."

Before long, Trigger could do it alone.

Charlie discovered a section of track that needed repair. When the men came out to work on the rails, Charlie showed them how Trigger could turn the switch.

They took off their caps and scratched their heads. It was hard for them to believe what they were seeing.

"Charlie, you got yourself a regular railroad dog," one of the men said.

While the men were working, Charlie had to stop the train, so he'd stand in the middle of the tracks and wave a red flag.

11
Trigger went with Charlie each time and stood beside him. Soon Charlie let Trigger carry the flag. Then the dog learned to fetch it. By the time the repairs were almost finished, Trigger would get the flag, sit up between the rails holding the flag in his teeth, and wait for the big iron locomotive to stop. Sometimes the big monster of an engine, bellowing steam, would come very close to the little dog before it stopped, but Trigger never faltered. He'd hold still until the iron wheels came to a screeching halt. Then he'd wag his tail and go back to the station.

"A regular railroad dog," the men said, over and over.

One bitter-cold winter day when the wind blew with an icy breath, Charlie's knees began to hurt. When he heard the train coming up the mountain, he started out for the switch. It was very painful for Charlie to walk.

Trigger scampered along, his curly black ears flopping in the biting wind. But when they reached the switch, Trigger could not move it.

"What's the matter, Trigger?" Charlie asked.

Then he saw. The switch was frozen in the middle. The train coming could not go on the left or the right fork. It would wreck. Charlie tugged with all his might, but the switch did not move.

"Old 49 will be here before I can get the red flag," Charlie said.

The engineer was signaling for the left fork. Expecting to go to the silver mines, he would instead shoot straight ahead and down the mountain.

"Trigger, Mr. Sears, the superintendent of the railroad, is on Old 49. And all the others will go down, too! Quick, Trigger, fetch the flag!"

The little dog started running back to the station.

"Hurry!" shouted Charlie above the howling wind.

Trigger ran faster.

In spite of the weather, little beads of sweat formed on Charlie's forehead. He had never been so scared. Could Trigger save the train? He closed his eyes and said a prayer. The sound of the train pounding on the rails thundered in Charlie's head.

Tugging its load of passengers, the engine labored upward. "Now it's at the bend," Charlie said aloud. "It'll come roaring by me on the downgrade and hit that spot where the track divides, and over they'll go—people, boxcars, engine, strewn all over the mountainside."

Charlie hated to open his eyes, but when he did . . . there was Trigger in the center of the track, sitting proudly on his hind legs, his two little paws showing like white mittens, the red flag secure in his mouth.

Closer and closer the engine came, its great iron point aimed like an arrow at the brave little dog. Sparks flew from the wheels as the engineer tried to apply the brakes.

Inches from Trigger, the train stopped.

Charlie was a man who never let his feelings show, but this time they overwhelmed him. He hobbled over to Trigger, picked up the little dog, flag and all, and hugged him. "You did it, Trigger. You did it!"

Mr. Sears hopped off the train, wanting to know why it had stopped. When he heard about Trigger, Mr. Sears petted the dog and said, "This little dog saved all our lives. I'm going to send him a big, juicy steak every day for as long as he lives."

Some say this is a true story. They say it happened at Forks Creek, Colorado, in 1900, and the real Trigger stopped the train. "A regular railroad dog," they say."""

DINOS_IN_THE_DARK = """Dinos in the Dark
by Stephen Whitt

When you think of dinosaurs and where they lived, what do you picture? Do you see hot, steamy swamps, thick jungles, or sunny plains? Dinosaurs lived in those places, yes. But did you know that some dinosaurs lived in the cold and the darkness near the North and South Poles?

This surprised scientists, too. Paleontologists¹ used to believe that dinosaurs lived only in the warmest parts of the world. They thought that dinosaurs could only have lived in places where turtles, crocodiles, and snakes live today. Later, these dinosaur scientists began finding bones in surprising places.

One of those surprising fossil beds is a place called Dinosaur Cove, Australia. One hundred million years ago, Australia was connected to Antarctica. Both continents were located near the South Pole. Today, paleontologists dig dinosaur fossils out of the ground. They think about what those ancient bones must mean.

What was the climate like at Dinosaur Cove then? It was cold! The average temperature was probably around 30 degrees F. The weather would have been like the weather in southern Alaska. How could dinosaurs have lived in such cold temperatures?

5
And that's not all. Dinosaur Cove was located near the South Pole. This means that for several months each year, the sun never rose. Instead, Dinosaur Cove was plunged into a dark, cold winter night that didn't end until the spring or summer.

Go or Stay?

In other parts of the world, dinosaurs probably migrated away from the winter's darkness. But the animals at Dinosaur Cove lived on a peninsula of land. They were blocked to the north by a huge lake. To the south and east was the ocean. The only way out was to the west, but it was too far for most of the animals at Dinosaur Cove to migrate. So they couldn't travel each year when the long night came.

To survive, these dinosaurs had to adapt.² How did they change over time? Imagine you are a dinosaur at Dinosaur Cove. If you happen to have larger eyes, you will have a better chance of surviving than will a dinosaur with small eyes because you can see in the dark. Your children will probably have big eyes, too. As time goes by, there will be more and more dinosaurs with bigger eyes.

Big eyes helped the dinosaurs see evergreen trees in the darkness. Since these trees didn't lose their needles in the winter, they were food for the plant-eating dinosaurs. Big eyes also helped the dinosaurs watch out for predators that would have hunted them.

Dino Blood?

Even with big eyes, though, the dinosaurs at Dinosaur Cove faced another problem—the cold. Turtles, snakes, and crocodiles are all reptiles. Almost all of them live in the warmer parts of the world, and for good reason. Their bodies don't produce their own heat, so they stay the same temperature as their surroundings. We say these animals are "cold-blooded," but their blood doesn't have to be cold. It's just as warm as the air or water around them.

If reptiles get too cold, they become sluggish and slow. Some paleontologists wonder if maybe dinosaurs were more like birds than reptiles. If dinosaurs were "warm-blooded" like birds, then they could have made their own heat. That would explain how dinosaurs might have survived through the cold, dark winters at Dinosaur Cove.

The Last Dinosaurs?

But that brings up another mystery. Most paleontologists think the dinosaurs died out because the world got very cold very quickly. Maybe a giant rock from space (an asteroid) slammed into Earth and threw up a cloud of dust. Or maybe ash from volcanoes blocked out the sun. Either way, the world became too cold for the dinosaurs to survive.

12
But what if some dinosaurs could survive cold polar winters? Could they also survive on a colder planet? What if the descendents³ of the animals at Dinosaur Cove survived the extinction?⁴ Could they have been the last dinosaurs on Earth?

The wonderful thing about science is that each new answer creates more questions. Maybe one day you will become a paleontologist and travel to the coldest parts of the world to search for the bones of Earth's last dinosaurs. Be sure to pack a sweater!"""

# Grade 4 Reading EOG Questions - Released Items Only (Questions 1-40)
# Note: Sample questions S1 and S2 are excluded - these are not released items
GRADE_4_READING_QUESTIONS = [
    # Topic: Vocabulary/Word Meaning
    {
        "grade_level": 4,
        "topic": "Vocabulary/Word Meaning",
        "difficulty": 2,
        "weight": 1.0,
        "prompt": f"Read the passage:\n\n{LIBBY_SAVES_TEAM}\n\nWhat is the meaning of lunged in this sentence from paragraph 7?\n\"The dogs' ears stood erect as the team lunged forward.\"",
        "choices": ["jumped", "served", "forced", "stepped"],
        "correct_answer": "jumped",
        "explanation": "Lunged means to make a sudden forward movement or leap, which is what the dogs did."
    },
    {
        "grade_level": 4,
        "topic": "Vocabulary/Word Meaning",
        "difficulty": 2,
        "weight": 1.0,
        "prompt": f"Read the passage:\n\n{LIBBY_SAVES_TEAM}\n\nWhat does the word jolted mean in paragraph 8?",
        "choices": ["circled", "bounced", "reached", "stopped"],
        "correct_answer": "bounced",
        "explanation": "Jolted means to move suddenly and roughly, like bouncing or shaking."
    },
    {
        "grade_level": 4,
        "topic": "Vocabulary/Word Meaning",
        "difficulty": 2,
        "weight": 1.0,
        "prompt": f"Read the passage:\n\n{AMELIA_EARHART}\n\nIn paragraph 8, what is the meaning of the word originally?",
        "choices": ["in the middle", "at the end", "in the beginning", "at a slow rate"],
        "correct_answer": "in the beginning",
        "explanation": "Originally means at first or in the beginning."
    },
    {
        "grade_level": 4,
        "topic": "Vocabulary/Word Meaning",
        "difficulty": 2,
        "weight": 1.0,
        "prompt": f"Read the passage:\n\n{AMELIA_EARHART}\n\nIn paragraph 10, what is the meaning of the word impressed?",
        "choices": ["admired", "disliked", "forced", "imitated"],
        "correct_answer": "admired",
        "explanation": "Impressed means to have a strong positive effect on someone, similar to being admired."
    },
    {
        "grade_level": 4,
        "topic": "Vocabulary/Word Meaning",
        "difficulty": 1,
        "weight": 1.0,
        "prompt": f"Read the passage:\n\n{AMELIA_EARHART}\n\nIn paragraph 12, what is another name for navigator?",
        "choices": ["fighter", "target", "customer", "guide"],
        "correct_answer": "guide",
        "explanation": "A navigator is someone who guides or directs the course of a ship or aircraft."
    },
    {
        "grade_level": 4,
        "topic": "Vocabulary/Word Meaning",
        "difficulty": 3,
        "weight": 1.5,
        "prompt": f"Read the passage:\n\n{WHATS_IT_LIKE_TO_BE_A_CHEF}\n\nWhat is the meaning of \"always kind of kicked the idea around a little bit\" in paragraph 5?",
        "choices": ["thought about the idea from time to time", "wanted to be a professional soccer player", "did not like making a decision", "did not like the idea of cooking"],
        "correct_answer": "thought about the idea from time to time",
        "explanation": "To 'kick an idea around' means to think about or consider something casually over time."
    },
    {
        "grade_level": 4,
        "topic": "Vocabulary/Word Meaning",
        "difficulty": 1,
        "weight": 1.0,
        "prompt": f"Read the passage:\n\n{WHATS_IT_LIKE_TO_BE_A_CHEF}\n\nWhat does \"sous chef\" mean in paragraph 13?",
        "choices": ["planner", "manager", "pastry chef", "assistant chef"],
        "correct_answer": "assistant chef",
        "explanation": "A sous chef is an assistant chef who helps the head chef."
    },
    {
        "grade_level": 4,
        "topic": "Vocabulary/Word Meaning",
        "difficulty": 2,
        "weight": 1.0,
        "prompt": f"Read the passage:\n\n{REGULAR_RAILROAD_DOG}\n\nWhat is the meaning of fetch in paragraph 11?",
        "choices": ["set up", "run toward", "give away", "bring back"],
        "correct_answer": "bring back",
        "explanation": "Fetch means to go get something and bring it back."
    },
    {
        "grade_level": 4,
        "topic": "Vocabulary/Word Meaning",
        "difficulty": 2,
        "weight": 1.0,
        "prompt": f"Read the passage:\n\n{DINOS_IN_THE_DARK}\n\nWhat does the word plunged mean in paragraph 5?",
        "choices": ["ran toward", "pushed away", "fell suddenly", "walked slowly"],
        "correct_answer": "fell suddenly",
        "explanation": "Plunged means to fall or drop suddenly and quickly."
    },
    
    # Topic: Character Analysis / Reading Comprehension
    {
        "grade_level": 4,
        "topic": "Character Analysis",
        "difficulty": 2,
        "weight": 1.0,
        "prompt": f"Read the passage:\n\n{LIBBY_SAVES_TEAM}\n\nWhich quote from the text describes the setting?",
        "choices": ["\"Her brown eyes peeked out of the fur-lined hood which outlined her round, full face.\"", "\"She held tightly to the sides of the sled with her oversized gloves.\"", "\"Libby reached out toward the pine trees and grabbed one of the now-covered branches.\"", "\"She reached down for the metal anchor and pushed it over the edge of the sled.\""],
        "correct_answer": "\"Libby reached out toward the pine trees and grabbed one of the now-covered branches.\"",
        "explanation": "This quote describes the setting by mentioning pine trees and covered branches, which shows the outdoor winter environment."
    },
    {
        "grade_level": 4,
        "topic": "Character Analysis",
        "difficulty": 2,
        "weight": 1.0,
        "prompt": f"Read the passage:\n\n{LIBBY_SAVES_TEAM}\n\nWhich event changes how Libby feels about the sled ride?",
        "choices": ["Snow gets stirred up all around them.", "Her dad is bumped off the sled in the last turn.", "The wind throws snow in her face.", "The dogs run through the woods faster than ever."],
        "correct_answer": "Her dad is bumped off the sled in the last turn.",
        "explanation": "This event changes everything - Libby goes from being a passenger to being in control of the sled."
    },
    {
        "grade_level": 4,
        "topic": "Character Analysis",
        "difficulty": 1,
        "weight": 1.0,
        "prompt": f"Read the passage:\n\n{LIBBY_SAVES_TEAM}\n\nWhy does Libby snap off a pine twig and swing it between Timber and Tucker?",
        "choices": ["to make the dogs start walking", "to make the dogs go into the woods", "to make the dogs stop running", "to make the dogs go faster"],
        "correct_answer": "to make the dogs stop running",
        "explanation": "Libby remembers her dad's instructions to stop the dogs by snapping a pine twig and swinging it between Timber and Tucker."
    },
    {
        "grade_level": 4,
        "topic": "Character Analysis",
        "difficulty": 2,
        "weight": 1.0,
        "prompt": f"Read the passage:\n\n{LIBBY_SAVES_TEAM}\n\nWhat does the action that Libby took to save the team show about her character?",
        "choices": ["She is brave.", "She is frightened.", "She is excited.", "She is comfortable."],
        "correct_answer": "She is brave.",
        "explanation": "Libby's actions show bravery - she took control of a dangerous situation and successfully stopped the dogs."
    },
    {
        "grade_level": 4,
        "topic": "Character Analysis",
        "difficulty": 2,
        "weight": 1.0,
        "prompt": f"Read the passage:\n\n{LIBBY_SAVES_TEAM}\n\nWhy is Libby's father proud of her at the end of the text?",
        "choices": ["Libby wanted to go on a sled ride.", "Libby saved the dogs and the sled.", "Libby commanded the dogs to go faster.", "Libby turned the team around to look for her dad."],
        "correct_answer": "Libby saved the dogs and the sled.",
        "explanation": "Libby's father is proud because she successfully saved the team by stopping the dogs when he fell off."
    },
    {
        "grade_level": 4,
        "topic": "Character Analysis",
        "difficulty": 2,
        "weight": 1.0,
        "prompt": f"Read the passage:\n\n{REGULAR_RAILROAD_DOG}\n\nWhich statement from the text shows that Trigger was a smart dog?",
        "choices": ["\"Trigger was a railroad dog right from the start.\"", "\"One of Charlie's duties was to turn the switch, and Trigger went with him.\"", "\"Hearing those engine whistles all the time, Trigger learned to tell them apart.\"", "\"Trigger went with Charlie each time and stood beside him.\""],
        "correct_answer": "\"Hearing those engine whistles all the time, Trigger learned to tell them apart.\"",
        "explanation": "This shows Trigger's intelligence - he learned to distinguish between different train whistles."
    },
    {
        "grade_level": 4,
        "topic": "Character Analysis",
        "difficulty": 1,
        "weight": 1.0,
        "prompt": f"Read the passage:\n\n{REGULAR_RAILROAD_DOG}\n\nWhat does Charlie's reaction to the frozen switch show about him?",
        "choices": ["He is worried.", "He is surprised.", "He is frustrated.", "He is disappointed."],
        "correct_answer": "He is worried.",
        "explanation": "Charlie realizes the danger of the situation - the train will crash if the switch isn't changed, showing his worry."
    },
    {
        "grade_level": 4,
        "topic": "Character Analysis",
        "difficulty": 2,
        "weight": 1.0,
        "prompt": f"Read the passage:\n\n{REGULAR_RAILROAD_DOG}\n\nWhich quote from the text supports the theme of bravery?",
        "choices": ["\"Trigger took such an interest in the switching that Charlie made a decision.\"", "\"Charlie discovered a section of track that needed repair.\"", "\"Trigger scampered along, his curly black ears flopping in the biting wind.\"", "\"There was Trigger in the center of the track, sitting proudly on his hind legs.\""],
        "correct_answer": "\"There was Trigger in the center of the track, sitting proudly on his hind legs.\"",
        "explanation": "This quote shows Trigger's bravery - he sits in the center of the track facing an oncoming train to stop it."
    },
    
    # Topic: Main Idea / Summary
    {
        "grade_level": 4,
        "topic": "Main Idea",
        "difficulty": 2,
        "weight": 1.0,
        "prompt": f"Read the passage:\n\n{LIBBY_SAVES_TEAM}\n\nWhich statement summarizes the text?",
        "choices": ["Libby and her dad take turns driving the sled.", "Libby learns how to control a sled pulled by dogs.", "Libby takes control of the sled when her dad falls off.", "Libby learns how to lead the sled through the trees."],
        "correct_answer": "Libby takes control of the sled when her dad falls off.",
        "explanation": "The main event of the story is Libby taking control when her dad falls off and successfully stopping the team."
    },
    {
        "grade_level": 4,
        "topic": "Main Idea",
        "difficulty": 2,
        "weight": 1.0,
        "prompt": f"Read the passage:\n\n{AMELIA_EARHART}\n\nWhat is the main idea of the selection?",
        "choices": ["Amelia Earhart and Eleanor Roosevelt gave speeches to support women's rights.", "Amelia Earhart was the first woman to cross the Atlantic Ocean in an airplane.", "Amelia Earhart was a determined female pilot who disappeared on a flight around the world.", "Amelia Earhart became a career counselor at Purdue and advised women students."],
        "correct_answer": "Amelia Earhart was a determined female pilot who disappeared on a flight around the world.",
        "explanation": "The main idea covers Amelia's achievements as a pilot and her final, mysterious disappearance."
    },
    {
        "grade_level": 4,
        "topic": "Main Idea",
        "difficulty": 2,
        "weight": 1.0,
        "prompt": f"Read the passage:\n\n{WHATS_IT_LIKE_TO_BE_A_CHEF}\n\nWhat is the main idea of this text?",
        "choices": ["Recipes have to be creative and fun.", "Chefs do many things besides cooking.", "Working different hours is part of being a chef.", "Chocolate can be used in many different recipes."],
        "correct_answer": "Chefs do many things besides cooking.",
        "explanation": "The text emphasizes that being a chef involves many responsibilities beyond just cooking, such as scheduling, menu planning, and managing staff."
    },
    {
        "grade_level": 4,
        "topic": "Main Idea",
        "difficulty": 2,
        "weight": 1.0,
        "prompt": f"Read the passage:\n\n{REGULAR_RAILROAD_DOG}\n\nWhich statement summarizes the text?",
        "choices": ["A dog loves to ride a train.", "A dog stops a train wreck.", "A man adopts a dog.", "A man hurts his knee."],
        "correct_answer": "A dog stops a train wreck.",
        "explanation": "The main event of the story is Trigger stopping the train from crashing by sitting on the tracks with a red flag."
    },
    {
        "grade_level": 4,
        "topic": "Main Idea",
        "difficulty": 2,
        "weight": 1.0,
        "prompt": f"Read the passage:\n\n{DINOS_IN_THE_DARK}\n\nWhich detail supports the main idea?",
        "choices": ["that dinosaurs could see in the dark", "that dinosaurs could not swim", "that dinosaurs survived in cold places", "that dinosaurs migrated to warmer places"],
        "correct_answer": "that dinosaurs survived in cold places",
        "explanation": "The main idea is that some dinosaurs lived in cold, dark polar regions, which challenges the traditional view."
    },
    
    # Topic: Reading Comprehension / Inference
    {
        "grade_level": 4,
        "topic": "Reading Comprehension",
        "difficulty": 2,
        "weight": 1.0,
        "prompt": f"Read the passage:\n\n{AMELIA_EARHART}\n\nAccording to the selection, why was Amelia unhappy with her flight on Friendship?",
        "choices": ["Her landing was not smooth.", "She did not fly across the Pacific.", "Her plane disappeared.", "She was not the pilot."],
        "correct_answer": "She was not the pilot.",
        "explanation": "The text states that Amelia was unhappy because she was a passenger, not the pilot, on the Friendship flight."
    },
    {
        "grade_level": 4,
        "topic": "Reading Comprehension",
        "difficulty": 3,
        "weight": 1.5,
        "prompt": f"Read the passage:\n\n{AMELIA_EARHART}\n\nWhat evidence from the selection shows how Amelia supported other women who wanted to become pilots?",
        "choices": ["Amelia wrote books and gave talks about flying.", "Amelia accepted a job at Purdue University.", "Amelia gave speeches with Franklin D. Roosevelt.", "Amelia started the group The Ninety-Nines in 1929."],
        "correct_answer": "Amelia started the group The Ninety-Nines in 1929.",
        "explanation": "The Ninety-Nines was a group specifically for women pilots, showing Amelia's support for other women in aviation."
    },
    {
        "grade_level": 4,
        "topic": "Reading Comprehension",
        "difficulty": 1,
        "weight": 1.0,
        "prompt": f"Read the passage:\n\n{AMELIA_EARHART}\n\nWhose wife made speeches with Amelia Earhart?",
        "choices": ["Franklin Roosevelt's", "Wilmer Stultz's", "Edwin Elliot's", "Fred Noonan's"],
        "correct_answer": "Franklin Roosevelt's",
        "explanation": "The text states that Amelia worked with U.S. President Franklin Delano Roosevelt and his wife, Eleanor."
    },
    {
        "grade_level": 4,
        "topic": "Reading Comprehension",
        "difficulty": 3,
        "weight": 1.5,
        "prompt": f"Read the passage:\n\n{AMELIA_EARHART}\n\nWhy was Amelia Earhart asked to be a career counselor?",
        "choices": ["She planned a flight around the world.", "She encouraged women's rights.", "She knew the president and his wife.", "She advised women students at Purdue."],
        "correct_answer": "She encouraged women's rights.",
        "explanation": "Amelia was asked to be a career counselor because of her work supporting women's rights and encouraging women."
    },
    {
        "grade_level": 4,
        "topic": "Reading Comprehension",
        "difficulty": 2,
        "weight": 1.0,
        "prompt": f"Read the passage:\n\n{WHATS_IT_LIKE_TO_BE_A_CHEF}\n\nWhich statement from the text supports the idea that being a chef is more than just cooking?",
        "choices": ["\"First of all, it takes a little bit of schooling.\"", "\"With the Food Network and things like that, people are a little more aware of what's going on and a little more educated about cooking.\"", "\"A typical day is coming in, going over financial reports from the previous day, meeting with your staff and going over menu development.\"", "\"It changes—every day it's something different.\""],
        "correct_answer": "\"A typical day is coming in, going over financial reports from the previous day, meeting with your staff and going over menu development.\"",
        "explanation": "This statement shows that a chef's day involves financial reports and staff management, not just cooking."
    },
    {
        "grade_level": 4,
        "topic": "Reading Comprehension",
        "difficulty": 2,
        "weight": 1.0,
        "prompt": f"Read the passage:\n\n{WHATS_IT_LIKE_TO_BE_A_CHEF}\n\nWhy is it important for a chef to have creativity?",
        "choices": ["The chef has to be willing to find enjoyment when working on the weekends and holidays.", "The chef has to be able to change the menu for each group being served.", "The chef has to be able to plan ahead to prepare for large groups of customers.", "The chef has to be able to communicate directly with all those involved with preparing the food."],
        "correct_answer": "The chef has to be able to change the menu for each group being served.",
        "explanation": "Chef Justus mentions that creativity is important because they deal with different groups and diverse events, requiring menu changes."
    },
    {
        "grade_level": 4,
        "topic": "Reading Comprehension",
        "difficulty": 2,
        "weight": 1.0,
        "prompt": f"Read the passage:\n\n{WHATS_IT_LIKE_TO_BE_A_CHEF}\n\nWhich statement from the text supports the idea that chefs have unusual hours?",
        "choices": ["\"It's a lot of planning.\"", "\"Every day it's something different.\"", "\"When everybody is playing, you're working.\"", "\"We're going to have a wide variety of things.\""],
        "correct_answer": "\"When everybody is playing, you're working.\"",
        "explanation": "This quote directly supports that chefs work during times when others are off, like weekends and holidays."
    },
    {
        "grade_level": 4,
        "topic": "Reading Comprehension",
        "difficulty": 2,
        "weight": 1.0,
        "prompt": f"Read the passage:\n\n{WHATS_IT_LIKE_TO_BE_A_CHEF}\n\nWhich statement from the text supports that chocolate is an important ingredient for Chef Justus?",
        "choices": ["\"He comes up with recipes to go on the menus.\"", "\"I like the dark chocolates.\"", "\"We use the chocolates as much as we can.\"", "\"We do a chocolate-barbecued chicken wing.\""],
        "correct_answer": "\"We use the chocolates as much as we can.\"",
        "explanation": "This statement directly shows that chocolate is used extensively and is important to Chef Justus."
    },
    {
        "grade_level": 4,
        "topic": "Reading Comprehension",
        "difficulty": 3,
        "weight": 1.5,
        "prompt": f"Read the passage:\n\n{WHATS_IT_LIKE_TO_BE_A_CHEF}\n\nHow does the author show that being an executive chef is hard work?",
        "choices": ["by showing the many different duties of an executive chef every day", "by describing the many recipes that an executive chef can make each season", "by explaining the different classes that an executive chef must complete", "by talking about the people who have eaten in his restaurant recently"],
        "correct_answer": "by showing the many different duties of an executive chef every day",
        "explanation": "The author shows hard work by listing all the responsibilities: scheduling, menu planning, organizing, hiring, training, budgets, etc."
    },
    {
        "grade_level": 4,
        "topic": "Reading Comprehension",
        "difficulty": 1,
        "weight": 1.0,
        "prompt": f"Read the passage:\n\n{REGULAR_RAILROAD_DOG}\n\nHow did the dog stop the train from crashing?",
        "choices": ["He barked at the train driver.", "He moved the switch.", "He ran to get the red flag.", "He ran beside the train."],
        "correct_answer": "He ran to get the red flag.",
        "explanation": "Trigger ran back to the station to get the red flag, then sat on the tracks holding it, which caused the engineer to stop the train."
    },
    {
        "grade_level": 4,
        "topic": "Reading Comprehension",
        "difficulty": 1,
        "weight": 1.0,
        "prompt": f"Read the passage:\n\n{REGULAR_RAILROAD_DOG}\n\nWhy does the train almost fall off the mountain?",
        "choices": ["The switch is frozen.", "The brakes stop working.", "The driver is asleep.", "The station agent is injured."],
        "correct_answer": "The switch is frozen.",
        "explanation": "The switch is frozen and can't be moved, which means the train will be directed onto the wrong track and derailed."
    },
    {
        "grade_level": 4,
        "topic": "Reading Comprehension",
        "difficulty": 2,
        "weight": 1.0,
        "prompt": f"Read the passage:\n\n{REGULAR_RAILROAD_DOG}\n\nHow does Trigger learning how to stop a train contribute to the end of the text?",
        "choices": ["He learns how to turn the switch.", "He is able to save many people's lives.", "He makes the people on the train angry.", "He is unable to move the switch."],
        "correct_answer": "He is able to save many people's lives.",
        "explanation": "Trigger's ability to stop trains by carrying the red flag allows him to save the train and all its passengers from crashing."
    },
    {
        "grade_level": 4,
        "topic": "Reading Comprehension",
        "difficulty": 2,
        "weight": 1.0,
        "prompt": f"Read the passage:\n\n{DINOS_IN_THE_DARK}\n\nWhy were scientists surprised to find dinosaur bones near Antarctica?",
        "choices": ["They believed dinosaurs could only have survived in warm climates.", "They believed Australia and Antarctica would have had different temperatures.", "They believed dinosaurs migrated away from cold climates.", "They believed all dinosaurs became extinct because of cold weather."],
        "correct_answer": "They believed dinosaurs could only have survived in warm climates.",
        "explanation": "Scientists were surprised because they originally believed dinosaurs lived only in warm places, like where turtles and crocodiles live today."
    },
    {
        "grade_level": 4,
        "topic": "Reading Comprehension",
        "difficulty": 3,
        "weight": 1.5,
        "prompt": f"Read the passage:\n\n{DINOS_IN_THE_DARK}\n\nHow does the author show in paragraph 12 that scientists may not have all the information they need?",
        "choices": ["by asking a lot of questions", "by talking about the extinction of dinosaurs", "by telling the reader that information is hard to find", "by using a timeline of events"],
        "correct_answer": "by asking a lot of questions",
        "explanation": "The author asks multiple questions about what might have happened, showing that scientists don't have all the answers."
    },
    {
        "grade_level": 4,
        "topic": "Reading Comprehension",
        "difficulty": 2,
        "weight": 1.0,
        "prompt": f"Read the passage:\n\n{DINOS_IN_THE_DARK}\n\nHow does the author explain the effect of living at Dinosaur Cove on the dinosaurs?",
        "choices": ["by showing that dinosaur fossils were found there by paleontologists", "by showing that dinosaurs of Dinosaur Cove lived on a peninsula and could not migrate", "by describing that dinosaurs were like turtles, snakes, and crocodiles", "by describing that dinosaurs of Dinosaur Cove were the last dinosaurs on Earth"],
        "correct_answer": "by showing that dinosaurs of Dinosaur Cove lived on a peninsula and could not migrate",
        "explanation": "The author explains that the dinosaurs were trapped on a peninsula and couldn't migrate away from the cold, dark winters."
    },
    {
        "grade_level": 4,
        "topic": "Reading Comprehension",
        "difficulty": 2,
        "weight": 1.0,
        "prompt": f"Read the passage:\n\n{DINOS_IN_THE_DARK}\n\nWhich statement from the text explains what helped dinosaurs stay alive in the darkness?",
        "choices": ["\"In other parts of the world, dinosaurs probably migrated away from the winter's darkness.\"", "\"Since these trees didn't lose their needles in the winter, they were food for the plant-eating dinosaurs.\"", "\"Big eyes also helped the dinosaurs watch out for predators that would have hunted them.\"", "\"If dinosaurs were 'warm-blooded' like birds, then they could have made their own heat.\""],
        "correct_answer": "\"Big eyes also helped the dinosaurs watch out for predators that would have hunted them.\"",
        "explanation": "Big eyes helped dinosaurs survive in the darkness by allowing them to see food and watch for predators."
    },
    {
        "grade_level": 4,
        "topic": "Reading Comprehension",
        "difficulty": 2,
        "weight": 1.0,
        "prompt": f"Read the passage:\n\n{DINOS_IN_THE_DARK}\n\nAccording to the text, why were the dinosaurs in Dinosaur Cove unable to move to a warmer place?",
        "choices": ["They lived on an island and could not travel.", "It was too dangerous to migrate.", "They did not know about warmer places.", "Warmer places were too far away."],
        "correct_answer": "Warmer places were too far away.",
        "explanation": "The text states that the only way out was to the west, but it was too far for most animals to migrate."
    },
    {
        "grade_level": 4,
        "topic": "Reading Comprehension",
        "difficulty": 3,
        "weight": 1.5,
        "prompt": f"Read the passage:\n\n{DINOS_IN_THE_DARK}\n\nHow does the author show in paragraph 12 that scientists may not have all the information they need?",
        "choices": ["by asking a lot of questions", "by talking about the extinction of dinosaurs", "by telling the reader that information is hard to find", "by using a timeline of events"],
        "correct_answer": "by asking a lot of questions",
        "explanation": "The author asks multiple questions about what might have happened, showing that scientists don't have all the answers."
    },
]


def add_grade4_reading_questions():
    """Add Grade 4 Reading EOG questions to the database."""
    db: Session = SessionLocal()
    try:
        print("Database connection:", os.getenv('ORACLE_HOST', 'localhost') + ":" + os.getenv('ORACLE_PORT', '1522') + "/" + os.getenv('ORACLE_SERVICE', 'FREEPDB1'))
        print("Adding Grade 4 Reading EOG questions to database...")
        
        added_count = 0
        skipped_count = 0
        
        for question_data in GRADE_4_READING_QUESTIONS:
            # Check for duplicates using non-CLOB fields (Oracle doesn't allow CLOB comparison)
            existing = db.query(Question).filter(
                Question.grade_level == question_data["grade_level"],
                Question.topic == question_data["topic"],
                Question.difficulty == question_data["difficulty"],
                Question.weight == question_data["weight"]
            ).first()
            
            if existing:
                skipped_count += 1
                continue
            
            question = Question(**question_data)
            db.add(question)
            added_count += 1
        
        db.commit()
        print(f"Added {added_count} Grade 4 Reading questions")
        print(f"Summary: {added_count} added, {skipped_count} skipped, {len(GRADE_4_READING_QUESTIONS)} total")
        
    except Exception as e:
        db.rollback()
        print(f"Error adding questions: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    add_grade4_reading_questions()
