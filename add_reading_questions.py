"""
Add Grade 3 Reading EOG questions to the database.
Based on North Carolina EOG Released Items 2020.
Source: https://www.dpi.nc.gov/documents/accountability/testing/eog/bog3-eog-reading-grade-3-released-form/open

Each question includes the full reading passage/excerpt so students can read it when taking the quiz.
"""
from app.db import SessionLocal
from app.models import Question

# Reading passages/excerpts
# Note: OCTOPUS_PASSAGE removed - Sample questions S1 and S2 are not released items
# Only questions 1-40 (released items) are included

GREAT_ESCAPE_PART1 = """The county was full of farms—farms here, farms there, farms everywhere. In the middle of the county fairgrounds sat the poultry tent. And in the middle of the poultry tent sat Rhode Island Red, the rooster.

2
One morning, Red pecked at the latch on his cage. No one noticed.

He opened the door to his cage. No one noticed.

He hopped to the ground. No one noticed.

He pecked open eight other cages. Eight chickens hopped out.

A water boy noticed the chickens. Hey! Stop! he cried, and suddenly the chase was on!

Chickens ran this way; chickens flapped that way. The water boy called the feed boy. The feed boy called a farmer. The farmer called his wife. His wife called a poultry judge. Water, feed, and blue ribbons flew in the wind. Everyone tried to catch the chickens.

But no one caught Rhode Island Red. He pecked at a dozen more latches. A dozen more hens flapped to freedom. He pecked at a dozen more latches! A dozen more roosters flapped away. Soon he had opened all the cages.

People were shouting! Chickens were squawking! More people came running to see.

Rhode Island Red headed straight for the goose tent. Soon one goose was loose. Then another. By the time anyone in that tent noticed, every goose was loose! They all joined the chickens and ran down the hill. Rhode Island Red ran in the lead, with the people in hot pursuit!

The birds reached the goat barn. Soon Rhode Island Red had let every goat loose! Billies, nannies, and kids all joined the party!

Red ran on to the sheep building. Rams, lambs, and ewes all joined in the spree!"""

GREAT_ESCAPE_PART2 = """Red pecked open the pigpens and the cows gate. He pecked open the pony boxes and horse stalls. Cows, pigs, and ponies joined the jamboree!

Milkmaids and goatherds, trainers and shepherds, all chased after the animals. Rhode Island Red was leading them right to the midway!

The animals ran this way and that through the rides. Chickens rode the Ferris wheel. Goats rode the roller coaster. Ponies rode the ponies on the merry-go-round! Geese ate cotton candy. Pigs ate sweet corn, and sheep bobbed for apples at the apple-bobbing booth! Cows rode the waterslide, and goats nibbled everything they could! Dust rose into the air as people chased after the animals. No one would ever be able to catch them all!

Rattle! Rattle! Rattle! The sheep stopped. What was that sound?

Clink! Tink! Tink! The cows looked. They remembered that sound.

Shake-a-shake-a-shake! The goats knew that sound. They came running to see who made it.

Walking straight down the busy midway was a boy shaking a pail full of oats. He knew just what to do! He dropped a little trail of oats behind him as he walked. Rattle! Rattle! Rattle!

The sheep, cows, and goats followed the boys trail of oats. The ponies jumped off the merry-go-round and sniffed after the sweet oats. The pigs followed, gobbling oats greedily. The chickens and geese pecked up oats, too. Rattle, rattle, shake-a-shake-a-shake!

The boy led the procession of hungry animals. And at the very end of the line, pecking up the yummy oats, was Rhode Island Red himself!

Everyone cheered! The boy led the pigs to the pig building and the ponies to their stalls. He took back the cows, sheep, and goats. He led the geese to their cages and the chickens to their tent. And finally, the boy himself put away Rhode Island Red. And this last cage, he locked.

You naughty rooster, said the boy.

But Rhode Island Red just drank a long drink, fluffed up his feathers, and crowed, R-r-r-r-roooo! Then he settled down to rest, looking very pleased with himself."""

UNDER_MY_NOSE_PART1 = """I never planned to be a writer, but something happened that changed my mind. About ten years ago I took a course to learn how to make handmade books. The books I made needed text, so I began writing words to go with my art. About the same time, I had an idea for a story about my garden.

Some friends and I shared a vegetable garden at the edge of the city of Milwaukee. I knew I could write about the vegetables and make sketches of them on the spot. They were right under my nose.

Three years later, my book Growing Vegetable Soup was published. It was the first book I illustrated and wrote.

4
Getting a good idea for a book is the hardest thing for me, but also the most fun. Watching Milwaukees annual circus parade with its flashy colors and interesting animals inspired the idea for my book Circus.

Living close to Lake Michigan, I like to take long walks. One day while I was outside, a squirrel slipped inside my house through a torn window screen. That gave me the idea for a book. In Nuts to You! I tell how I got him out.

6
When I write my books, I start with the picture first. Bucky, my sisters cat, was my model for Feathers for Lunch. Before I wrote the story I measured his legs, his head, and his tail, and painted a life-size portrait of him. The story is about a cat trying to catch a bird. Thats why I put the bell on his collar—it warns the birds. I added the words jingle, jingle to go with my art.

I began writing the story from the cats viewpoint. Later, I rewrote it from the cat owners viewpoint.

Even when I get an idea for a book, its difficult for me to get started.

Once I wanted to do a book about fish. I even had a title, Fish Eyes. To get myself in the mood, I made a list of fishy words. I wondered how it would feel to swim like a fish. Could I put those feelings into words and pictures? I went to the aquarium and made sketches as I watched beautiful fish swim by. I read so much about fish that I felt fish would swim out of my ears."""

UNDER_MY_NOSE_PART2 = """10
I like to write out rough story ideas for my books, then make thumbnail sketches.

11
Next, I make the dummy book.*

12
I sketch in the art and hand-letter the words. I go over my dummy book with my editor. I like to read the text out loud and listen to the rhythm of the words. The text and the art should help each other tell the story. I type the text on my typewriter in my sunroom, where I'm surrounded by flowers, books, and plants. It's quiet and peaceful here, just the way I like it when I'm writing.

13
For my illustrations, I cut paper or material and glue the pieces to background paper. It's the kind of thing I liked to do when I was growing up. The art technique is called collage. I used plain colored paper for Circus, Color Zoo, and Color Farm. For Red Leaf, Yellow Leaf, and Snowballs I painted with watercolors and glued down real objects. I cut and glued forty-three pieces of paper to make the pineapple for Eating the Alphabet.

When book ideas just won't come, I stare out the window, water my plants, or go for a walk. I believe ideas need fresh air, too. I might wash my car, visit my mother, listen to the radio and sing along, find another antique charm for my vest, or just sit and read.

Then I sharpen my pencils and it's back to work I go, trying to get those words and pictures to tell a story.

16
As I go along, I continue to learn more about art and writing. If you like to write and draw, I hope you will keep learning, too. Good luck and keep your eyes open. There might be a story right under your nose."""

GRANDFATHER_FROG_PART1 = """Billy Mink ran around the edge of the Smiling Pool and turned down by the Laughing Brook. His eyes twinkled with mischief, and he hurried as only Billy can. As he passed Jerry Muskrat's house, Jerry saw him.

Hi, Billy Mink! Where are you going in such a hurry this fine morning? he called.

To find Little Joe Otter. Have you seen him? replied Billy.

No, said Jerry. He's probably down to the Big River fishing. I heard him say last night that he was going.

Thanks, said Billy Mink, and without waiting to say more he was off like a little brown flash.

Jerry watched him out of sight. Hump! exclaimed Jerry. Billy Mink is in a terrible hurry this morning. Now I wonder what he is so anxious to find Little Joe Otter for. When they get their heads together, it is usually for some mischief.

Jerry climbed to the top of his house and looked over the Smiling Pool in the direction from which Billy Mink had just come. Almost at once he saw Grandfather Frog fast asleep on his big green lily pad. The legs of a foolish green fly were sticking out of one corner of his big mouth. Jerry couldn't help laughing, for Grandfather Frog certainly did look funny.

He's had a good breakfast this morning, and his full stomach has made him sleepy, thought Jerry. But he's getting careless in his old age. He certainly is getting careless. The idea of going to sleep right out in plain sight like that!

Suddenly a new thought popped into his head. Billy Mink saw him, and that is why he is so anxious to find Little Joe Otter. He is planning to play some trick on Grandfather Frog as sure as pollywogs have tails! exclaimed Jerry. Then his eyes began to twinkle as he added: I think I'll have some fun myself."""

GRANDFATHER_FROG_PART2 = """10
Without another word Jerry slipped down into the water and swam over to the big green lily pad of Grandfather Frog. Then he pounded the water loudly with his tail. Grandfather Frog's big goggly eyes flew open, and he was just about to make a frightened plunge into the Smiling Pool when he saw Jerry.

Have a nice nap? inquired Jerry, with a broad grin.

I wasn't asleep! protested Grandfather Frog indignantly. I was just thinking.

Don't you think it a rather dangerous plan to think so long with your eyes closed? asked Jerry.

Well, maybe I did just doze off, admitted Grandfather Frog sheepishly.

Maybe you did, replied Jerry. Now listen. Then Jerry whispered in Grandfather Frog's ear, and both chuckled as if they were enjoying some joke, for they are great friends, you know. Afterward Jerry swam back to his house, and Grandfather Frog closed his eyes so as to look just as he did when he was asleep.

17
Meanwhile Billy Mink had hurried down the Laughing Brook. Halfway to the Big River he met Little Joe Otter bringing home a big fish, for you know Little Joe is a great fisherman. Billy Mink hastened to tell him how Grandfather Frog had fallen fast asleep on his big green lily pad.

It's a splendid chance to have some fun with Grandfather Frog and give him a great scare, concluded Billy.

Little Joe Otter put his fish down and grinned. He likes to play pranks almost as well as he likes to go fishing.

What can we do? said he.

I've thought of a plan, replied Billy. Do you happen to know where we can find Longlegs the Blue Heron?

Yes, said Little Joe. I saw him fishing not five minutes ago.

Then Billy told Little Joe his plan, and laughing and giggling, the two little scamps hurried off to find Longlegs the Blue Heron."""

BEAVERS_PART1 = """A beaver is a wild animal about three feet in length, and weighing forty or fifty pounds. It is covered with fine, glossy, grayish brown fur. Its tail is nearly a foot long, and has no hair at all, but only little scales, something like those of a fish. When the beaver is swimming about in the water it uses its tail as a kind of rudder.

2
A beaver cannot bear to live alone. He is never as happy as when he has a large number of friends close at hand whom he can visit every day; for beavers are the best and kindest neighbors in the world, always ready to help one another in building new houses or in repairing old ones.

Of course the first thing to be done when one is going to build a house or a village is to find a good place for it; and the spot which every beaver of sense thinks is best is either a large pond, or, if no pond is to be had, a low plain with a stream running through it. For on such a plain, a pond can be made by causing the water to cover it.

It must be a very, very long time since beavers first learned that the way to make a pond is to build a dam across a running stream. To begin with, they must know which way the stream runs, and in this they never make a mistake.

5
They first gather together a number of sticks and logs about five feet long, which they carry or roll into the stream. While some of the beavers are doing this—for the safety of the village lies in the strength of the foundation—others are gathering and piling up many green branches of trees. These branches, which they have cut from the trees with their teeth, are piled among the sticks and logs, and soon a dam is formed that reaches across the stream.

6
When the foundation of the dam has been finished, the beavers pile stones and mud upon it until they have built a wall ten or twelve feet thick at the bottom and two or three feet thick at the top. After all this has been done, the older and wiser beavers go carefully over every part to see if the dam is of the right shape and is strong and safe; for beavers do not like poor work, and they know that a weak dam is easily washed away."""

BEAVERS_PART2 = """Beavers are always quite clear in their minds as to what they want, and how to get it, and they like to keep things separate. When they are in the water, they are as happy as they can be; but when they are out of it, they like to be dry. It is sometimes two or three months before the village is finished. But the little round huts are to be used only for winter homes; for during the summer no beaver would think of sleeping indoors or, indeed, of staying very long in the same place.

9
Everything that a beaver does is well done. The walls of his house are thick and strong, and when he has a large family or many friends to stay with him the house has several rooms in it. No beaver ever thinks of living alone. Sometimes he will have one companion, and sometimes a dozen or more. But however full the house may be, everything is kept in good order. Each beaver has his fixed place on the floor, which is covered with dry leaves and grass. A door is always kept open into the place where their food is kept, and so they never go hungry. There they stay all through the winter eating the bark and tender shoots of young trees which they have carefully stored away, sleeping through the cold stormy weather, and at last getting very fat.

10
At one time there were many beavers in the West and the South, but now there are very few to be found there. Many years ago a Frenchman who was traveling in Louisiana spent a good deal of time watching beavers and learning about their ways. He hid himself close to a dam which the little creatures had built, and in the night he cut a hole about a foot wide right through it.

11
He had made no noise while cutting through the dam, but the rush of the water awakened one beaver who was not sleeping as soundly as the others. This beaver left his hut quickly, and swam to the dam to see what was wrong. As soon as he saw the stream that had been dug, he struck four loud blows with his tail, and every beaver in the village left his bed and rushed out in answer to the call. When they reached the dam and saw the large hole in it, they held a meeting as to what they should do. Then the head beaver gave orders to the rest, and all went to the bank to get sticks and mud.

When they had gathered together as much as they could carry, they formed in line and marched with their loads to the dam. The sticks were thrown into the hole and mud and stones were packed upon them. The beavers worked hard and wisely, and in a short time the dam was as good as ever. Then one of the older beavers struck two blows with his tail, and in a few minutes all were in bed and asleep again."""

DOG_HERO_PART1 = """It's been said that a dog is a man's best friend. This proved to be true when three friends set out to climb to the summit of Mount Hood in Oregon. They had no idea they would be turning around. They had no idea a German shepherd named Velvet would help save their lives.

2
Two of the climbers were school teachers. Matty Bryant and Kate Hanlon were teachers in schools in the suburbs of Portland, Oregon. Bryant, Hanlon, and six others began the hike to climb Mount Hood on a Saturday morning. They were all experienced rock climbers. They had brought the right gear to camp overnight on the 11,239 foot (3,425.6 meter)-high mountain, which towers over the Mount Hood National Forest. They also brought a transmitter with them. This is a small device that sends and/or receives signals. If the climbers ran into trouble, rangers might be able to track their location with the transmitter.

The Weather Factor

On Sunday, the weather took a turn for the worse. Now the climbers faced strong winds and blowing snow. So they chose to play it safe; they turned around to go back down the mountain. They decided it was not worth risking their lives to climb to the summit of Mount Hood.

5
The storm picked up strength. Matty and Kate roped themselves together with another friend, Christina Ridl. They also fastened the rope to Velvet. This is so they could all stay together in the high winds and blowing snow. Plus if anyone slipped, they would still be connected to others who still had their feet on solid ground.

6
At about 8,300 feet (2,529.8 meters) above sea level, Matty, Kate, and Christina reached a slippery edge. First one climber, then another, then the other fell at nearly the same time! The three climbers and Velvet tumbled down nearly five hundred feet. This is like jumping off the roof of a forty- to fifty-story apartment building.

When the climbers finally hit the ground, they knew they were lucky to be alive. Velvet, too, had survived the fall. But Ridl had injured her head. She put on a tight-fitting hat to stop the bleeding.

Meanwhile, the other climbers were doing their best to make it safely down the side of Mount Hood in the storm. Trevor Liston from Portland was one of them. He saw the three people fall who had been roped together. He and the others tried to throw a rope down to them. But this was not successful. Trevor and the other climbers called park rangers for help.

8
The three fallen climbers were wet and cold. But they had to keep moving to stay warm. They hiked for miles to try to make it down the mountainside. Soon it became dark. They had to face the fact they would be spending the night outdoors on the mountain—this time in bad weather.

The three did their best to stay calm. They wrapped themselves in sleeping bags to stay warm. They knew it might take some time for rescuers to find them in the dense forest. The Mount Hood National Forest spans over one million acres! The three also huddled around Velvet, who kept them warm with her fur and body heat. Velvet also helped the climbers keep their spirits up. This is important when lost in the wilderness. A person must make up his or her mind to survive."""

DOG_HERO_PART2 = """Dogs can be helpful because they can smell the scent of another animal. A dog may start barking to let people know danger is near. Dogs can also hear sounds that people might not hear. But perhaps their most important role is to keep people warm and comfort them. It is likely petting Velvet's black fur comforted Matty, Kate, and Christina. The same was probably true whenever the friendly dog licked their chins!

Even though they could not yet reach the stranded climbers, rescuers did their part to help them keep calm. They were able to call the climbers on their cell phones to guide them.

The three spent the night in blinding snow and 70 mile-per-hour winds. The forest was dense and dark. Snowflakes swirled around and around. The wind howled all night long; at times, it sounded like the cries of wolves! It was a long night for everyone, including Velvet. During the cold night, she stretched across the three climbers like a warm blanket.

No Place Like Home!

As soon as the sun rose over the glaciers, Erik Brom and other members of the Portland Mountain Rescue Team began their search. The rescue team found the climbers with Velvet in White River Canyon at about 7,400 feet.

We're soaking wet and freezing! the three told reporters who shouted questions at them. Upon her return, Christina got into an ambulance to go to the hospital. She had black rings on the skin around her eyes from her injury. Still she was willing to have her picture taken by news reporters. Everybody, Velvet included, was happy to be back at the forest ranger station in the park.

Rescuers said Velvet probably saved the climbers' lives by huddling with them during the cold night.

Russel Gubele was one of the rescue operations leaders. He warned reporters that just knowing how to rock climb does not always mean that a person is ready to climb a mountain that rises out of a deep forest. Still, Matty, Kate, and Christina had been prepared with the right gear, cell phones, the transmitter, and Velvet. They had helped to ensure their own rescue by being prepared.

Even though she is just a pet, Velvet turned out to be one of the operation's rescue heroes. But in the end, Velvet was probably just happy to go home.

She'll be getting extra treats when we go home, Matty joked."""

# Grade 3 Reading EOG Questions - Released Items Only (Questions 1-40)
# Note: Sample questions S1 and S2 (octopus) are excluded - these are not released items
GRADE_3_READING_QUESTIONS = [
    # Topic: Vocabulary/Word Meaning
    {
        "grade_level": 3,
        "topic": "Vocabulary/Word Meaning",
        "difficulty": 2,
        "weight": 1.0,
        "prompt": f"Read the passage:\n\n{GREAT_ESCAPE_PART1}\n\nWhat is the meaning of pecked in paragraph 2?",
        "choices": ["poked", "ran from", "marched to", "tossed"],
        "correct_answer": "poked",
        "explanation": "Pecked means to strike or poke with a beak, which is what a rooster would do."
    },
    {
        "grade_level": 3,
        "topic": "Vocabulary/Word Meaning",
        "difficulty": 2,
        "weight": 1.0,
        "prompt": f"Read the passage:\n\n{GREAT_ESCAPE_PART1}\n\nWhat is the meaning of latch in paragraph 2?",
        "choices": ["side", "fence", "lock", "bottom"],
        "correct_answer": "lock",
        "explanation": "A latch is a type of lock or fastening device used to secure a door or gate."
    },
    {
        "grade_level": 3,
        "topic": "Vocabulary/Word Meaning",
        "difficulty": 2,
        "weight": 1.0,
        "prompt": f"Read the passage:\n\n{UNDER_MY_NOSE_PART1}\n\nWhat is the meaning of inspired in paragraph 4?",
        "choices": ["changed", "started", "finished", "used"],
        "correct_answer": "started",
        "explanation": "Inspired means to be motivated or encouraged to begin something new, like starting a creative project."
    },
    {
        "grade_level": 3,
        "topic": "Vocabulary/Word Meaning",
        "difficulty": 2,
        "weight": 1.0,
        "prompt": f"Read the passage:\n\n{UNDER_MY_NOSE_PART1}\n\nWhat is the meaning of portrait in paragraph 6?",
        "choices": ["lesson", "picture", "report", "story"],
        "correct_answer": "picture",
        "explanation": "A portrait is a picture or painting of a person, especially one showing the face."
    },
    {
        "grade_level": 3,
        "topic": "Vocabulary/Word Meaning",
        "difficulty": 2,
        "weight": 1.0,
        "prompt": f"Read the passage:\n\n{GRANDFATHER_FROG_PART2}\n\nWhat is the meaning of the word slipped in paragraph 10?",
        "choices": ["crashed", "floated", "attacked", "entered"],
        "correct_answer": "entered",
        "explanation": "Slipped means to move quietly or smoothly into something, like entering the water."
    },
    {
        "grade_level": 3,
        "topic": "Vocabulary/Word Meaning",
        "difficulty": 2,
        "weight": 1.0,
        "prompt": f"Read the passage:\n\n{GRANDFATHER_FROG_PART2}\n\nWhat is the meaning of splendid in paragraph 17?",
        "choices": ["fast", "great", "safe", "usual"],
        "correct_answer": "great",
        "explanation": "Splendid means excellent or very good, which is what Billy thinks about the opportunity."
    },
    {
        "grade_level": 3,
        "topic": "Vocabulary/Word Meaning",
        "difficulty": 2,
        "weight": 1.0,
        "prompt": f"Read the passage:\n\n{BEAVERS_PART1}\n\nWhat is the meaning of the word bear in paragraph 2?",
        "choices": ["accept", "carry", "uncover", "earn"],
        "correct_answer": "accept",
        "explanation": "In this context, 'bear' means to tolerate or accept something unpleasant."
    },
    {
        "grade_level": 3,
        "topic": "Vocabulary/Word Meaning",
        "difficulty": 2,
        "weight": 1.0,
        "prompt": f"Read the passage:\n\n{BEAVERS_PART2}\n\nWhat does the word companion mean in paragraph 9?",
        "choices": ["sister", "enemy", "worker", "friend"],
        "correct_answer": "friend",
        "explanation": "A companion is a friend or partner who accompanies someone."
    },
    {
        "grade_level": 3,
        "topic": "Vocabulary/Word Meaning",
        "difficulty": 2,
        "weight": 1.0,
        "prompt": f"Read the passage:\n\n{DOG_HERO_PART1}\n\nWhat is the meaning of experienced in paragraph 2?",
        "choices": ["eager", "important", "practiced", "expected"],
        "correct_answer": "practiced",
        "explanation": "Experienced means having knowledge or skill from doing something many times before."
    },
    {
        "grade_level": 3,
        "topic": "Vocabulary/Word Meaning",
        "difficulty": 2,
        "weight": 1.0,
        "prompt": f"Read the passage:\n\n{DOG_HERO_PART1}\n\nWhat is the meaning of face the fact in paragraph 8?",
        "choices": ["to look at an idea one believes in", "to admit that something is true", "to escape from danger", "to learn something new"],
        "correct_answer": "to admit that something is true",
        "explanation": "To 'face the fact' means to accept or admit that something is true, even if it's difficult."
    },
    
    # Topic: Reading Comprehension
    {
        "grade_level": 3,
        "topic": "Reading Comprehension",
        "difficulty": 2,
        "weight": 1.0,
        "prompt": f"Read the passage:\n\n{GREAT_ESCAPE_PART1}\n\nWhat did Rhode Island Red do after he got out of his cage?",
        "choices": ["He rode with the animals on the roller coaster.", "He put all of the animals in their cages.", "He chased the animals to the midway.", "He let the other animals out of their cages."],
        "correct_answer": "He let the other animals out of their cages.",
        "explanation": "After Rhode Island Red escaped, he went around and let all the other animals out of their cages."
    },
    {
        "grade_level": 3,
        "topic": "Reading Comprehension",
        "difficulty": 1,
        "weight": 1.0,
        "prompt": f"Read both parts of the story:\n\n{GREAT_ESCAPE_PART1}\n\n{GREAT_ESCAPE_PART2}\n\nHow did the boy get all the animals back in their cages?",
        "choices": ["He chased after each one to get them to run into their cages.", "He shook a pail of oats while yelling at the animals to get back in their cages.", "He dropped a trail of oats behind him so the animals would follow him to their cages.", "He grabbed Rhode Island Red first and then scared all the other animals to their cages."],
        "correct_answer": "He dropped a trail of oats behind him so the animals would follow him to their cages.",
        "explanation": "The boy cleverly used a trail of oats to lead the animals back to their cages."
    },
    {
        "grade_level": 3,
        "topic": "Reading Comprehension",
        "difficulty": 2,
        "weight": 1.0,
        "prompt": f"Read the passage:\n\n{UNDER_MY_NOSE_PART1}\n\nAccording to the text, what is often difficult for the author?",
        "choices": ["drawing pictures", "creating a title", "getting started", "reading a book"],
        "correct_answer": "getting started",
        "explanation": "The author mentions that getting a good idea for a book is the hardest thing, which means getting started is difficult."
    },
    {
        "grade_level": 3,
        "topic": "Reading Comprehension",
        "difficulty": 1,
        "weight": 1.0,
        "prompt": f"Read the passage:\n\n{UNDER_MY_NOSE_PART1}\n\nAccording to the text, why does the cat have a bell on its collar?",
        "choices": ["The bell warns the birds.", "The bell makes a nice sound.", "The bell is pretty.", "The bell is interesting."],
        "correct_answer": "The bell warns the birds.",
        "explanation": "The bell on the cat's collar warns birds that the cat is nearby, giving them a chance to fly away."
    },
    {
        "grade_level": 3,
        "topic": "Reading Comprehension",
        "difficulty": 1,
        "weight": 1.0,
        "prompt": f"Read the passage:\n\n{GRANDFATHER_FROG_PART1}\n\nWhy was Billy in a hurry?",
        "choices": ["He was looking for Grandfather Frog.", "He was getting careless in his old age.", "He was going to eat breakfast.", "He was looking for Little Joe Otter."],
        "correct_answer": "He was looking for Little Joe Otter.",
        "explanation": "The text states that Billy Mink was hurrying to find Little Joe Otter."
    },
    {
        "grade_level": 3,
        "topic": "Reading Comprehension",
        "difficulty": 2,
        "weight": 1.0,
        "prompt": f"Read the passage:\n\n{GRANDFATHER_FROG_PART1}\n\nWhy was Grandfather Frog sleeping?",
        "choices": ["He was hot.", "He is old.", "He had just eaten.", "He had been sick."],
        "correct_answer": "He had just eaten.",
        "explanation": "Jerry thinks that Grandfather Frog's full stomach from breakfast made him sleepy."
    },
    {
        "grade_level": 3,
        "topic": "Reading Comprehension",
        "difficulty": 1,
        "weight": 1.0,
        "prompt": f"Read the passage:\n\n{GRANDFATHER_FROG_PART1}\n\nWhy does Jerry laugh when he sees Grandfather Frog?",
        "choices": ["Grandfather Frog is jumping on the lily pads.", "Grandfather Frog has part of a fly sticking out of his mouth.", "Grandfather Frog has singing lessons after breakfast with his friends.", "Grandfather Frog is dancing because he is happy to see Jerry."],
        "correct_answer": "Grandfather Frog has part of a fly sticking out of his mouth.",
        "explanation": "The text describes the legs of a fly sticking out of Grandfather Frog's mouth, which looks funny."
    },
    {
        "grade_level": 3,
        "topic": "Reading Comprehension",
        "difficulty": 1,
        "weight": 1.0,
        "prompt": f"Read the passage:\n\n{BEAVERS_PART1}\n\nAccording to the text, which choice describes a beaver's tail?",
        "choices": ["It is three feet long and weighs forty or fifty pounds.", "It has small scales similar to those of a fish.", "It is covered with shiny, brown fur.", "It looks like a hairy rudder on a boat."],
        "correct_answer": "It has small scales similar to those of a fish.",
        "explanation": "The text states that a beaver's tail has little scales, something like those of a fish."
    },
    {
        "grade_level": 3,
        "topic": "Reading Comprehension",
        "difficulty": 2,
        "weight": 1.0,
        "prompt": f"Read the passage:\n\n{BEAVERS_PART1}\n\nAccording to the text, what step follows finishing the foundation when building a beaver dam?",
        "choices": ["gathering sticks and logs", "piling stones and mud on top", "watching which way the stream runs", "checking to see if it is strong and safe"],
        "correct_answer": "piling stones and mud on top",
        "explanation": "After finishing the foundation, beavers pile stones and mud upon it to build the wall."
    },
    {
        "grade_level": 3,
        "topic": "Reading Comprehension",
        "difficulty": 1,
        "weight": 1.0,
        "prompt": f"Read the passage:\n\n{BEAVERS_PART1}\n\nWhy do beavers carefully inspect a dam after building it?",
        "choices": ["Beavers need to build a bridge to get across the stream.", "Beavers know that water will wash away a weak dam.", "Beavers want to find the best place to build a house or village.", "Beavers make the walls of their houses with big sticks."],
        "correct_answer": "Beavers know that water will wash away a weak dam.",
        "explanation": "Beavers inspect the dam to make sure it is strong because they know a weak dam can be easily washed away."
    },
    {
        "grade_level": 3,
        "topic": "Reading Comprehension",
        "difficulty": 2,
        "weight": 1.0,
        "prompt": f"Read the passage:\n\n{DOG_HERO_PART1}\n\nWhy did the rock climbers end their climb early?",
        "choices": ["The weather was bad.", "The group was bored.", "The dog was tired.", "The dog was sick."],
        "correct_answer": "The weather was bad.",
        "explanation": "The text states that the weather took a turn for the worse, causing them to end their climb early."
    },
    {
        "grade_level": 3,
        "topic": "Reading Comprehension",
        "difficulty": 1,
        "weight": 1.0,
        "prompt": f"Read the passage:\n\n{DOG_HERO_PART1}\n\nAccording to the text, what caused the climbers to fall down the mountain?",
        "choices": ["They were very tired.", "The mountain was rocky.", "It was getting dark.", "The mountain was slippery."],
        "correct_answer": "The mountain was slippery.",
        "explanation": "The text explains that the mountain became slippery, which caused the climbers to fall."
    },
    {
        "grade_level": 3,
        "topic": "Reading Comprehension",
        "difficulty": 2,
        "weight": 1.0,
        "prompt": f"Read both parts:\n\n{DOG_HERO_PART1}\n\n{DOG_HERO_PART2}\n\nAccording to the text, what is the relationship between the climbers petting Velvet's fur and Velvet licking them?",
        "choices": ["Both dried the climbers.", "Both scared the climbers.", "Both calmed the climbers.", "Both warmed the climbers."],
        "correct_answer": "Both warmed the climbers.",
        "explanation": "Both actions helped keep the climbers warm during the cold, dangerous situation on the mountain."
    },
    
    # Topic: Character Analysis
    {
        "grade_level": 3,
        "topic": "Character Analysis",
        "difficulty": 2,
        "weight": 1.0,
        "prompt": f"Read both parts:\n\n{GREAT_ESCAPE_PART1}\n\n{GREAT_ESCAPE_PART2}\n\nWhich word describes the boy in the text?",
        "choices": ["clever", "scared", "unusual", "useless"],
        "correct_answer": "clever",
        "explanation": "The boy shows cleverness by using a trail of oats to lead the animals back to their cages."
    },
    {
        "grade_level": 3,
        "topic": "Character Analysis",
        "difficulty": 2,
        "weight": 1.0,
        "prompt": f"Read both parts:\n\n{GREAT_ESCAPE_PART1}\n\n{GREAT_ESCAPE_PART2}\n\nWhy is Rhode Island Red so pleased with himself at the end of the text?",
        "choices": ["He gets the boy to feed all the animals and let them out of their cages.", "He gets all the animals back into their cages without anyone else's help.", "He is happy to be in his cage with a long drink and some food.", "He is happy that he let the animals out of their cages so they could have some fun."],
        "correct_answer": "He is happy that he let the animals out of their cages so they could have some fun.",
        "explanation": "Rhode Island Red is pleased because he successfully freed all the animals so they could have fun."
    },
    {
        "grade_level": 3,
        "topic": "Character Analysis",
        "difficulty": 2,
        "weight": 1.0,
        "prompt": f"Read both parts:\n\n{GREAT_ESCAPE_PART1}\n\n{GREAT_ESCAPE_PART2}\n\nWhat is one way that Rhode Island Red and the boy are alike?",
        "choices": ["They both lead the animals.", "They both chase the animals.", "They both feed the animals.", "They both catch the animals."],
        "correct_answer": "They both lead the animals.",
        "explanation": "Both Rhode Island Red and the boy lead the animals - Red leads them out, and the boy leads them back."
    },
    {
        "grade_level": 3,
        "topic": "Character Analysis",
        "difficulty": 2,
        "weight": 1.0,
        "prompt": f"Read both parts:\n\n{GREAT_ESCAPE_PART1}\n\n{GREAT_ESCAPE_PART2}\n\nWhich statement from the text shows that Rhode Island Red is proud?",
        "choices": ["And in the middle of the poultry tent sat Rhode Island Red, the rooster.", "One morning, Red pecked at the latch on his cage.", "Rhode Island Red headed straight for the goose tent.", "But Rhode Island Red just drank a long drink, fluffed up his feathers, and crowed, R-r-r-r-roooo!"],
        "correct_answer": "But Rhode Island Red just drank a long drink, fluffed up his feathers, and crowed, R-r-r-r-roooo!",
        "explanation": "Fluffing up feathers and crowing are actions that show pride and satisfaction."
    },
    {
        "grade_level": 3,
        "topic": "Character Analysis",
        "difficulty": 2,
        "weight": 1.0,
        "prompt": f"Read both parts:\n\n{GRANDFATHER_FROG_PART1}\n\n{GRANDFATHER_FROG_PART2}\n\nWhy did Grandfather Frog close his eyes to look just as he did when he was asleep?",
        "choices": ["to play a joke on Billy", "to get back to his nap", "to be a friend to Jerry", "to finish eating the fly"],
        "correct_answer": "to play a joke on Billy",
        "explanation": "Grandfather Frog closed his eyes to pretend he was still asleep so he could help play a trick on Billy Mink."
    },
    {
        "grade_level": 3,
        "topic": "Character Analysis",
        "difficulty": 2,
        "weight": 1.0,
        "prompt": f"Read both parts:\n\n{GRANDFATHER_FROG_PART1}\n\n{GRANDFATHER_FROG_PART2}\n\nWhich detail from the text supports that Grandfather Frog was scared when Jerry pounded the water with his tail?",
        "choices": ["The idea of going to sleep right out in plain sight like that!", "He was just about to make a frightened plunge into the Smiling Pool when he saw Jerry.", "I wasn't asleep! protested Grandfather Frog indignantly.", "Don't you think it a rather dangerous plan to think so long with your eyes closed? asked Jerry."],
        "correct_answer": "He was just about to make a frightened plunge into the Smiling Pool when he saw Jerry.",
        "explanation": "The phrase 'frightened plunge' clearly shows that Grandfather Frog was scared."
    },
    {
        "grade_level": 3,
        "topic": "Character Analysis",
        "difficulty": 2,
        "weight": 1.0,
        "prompt": f"Read both parts:\n\n{GRANDFATHER_FROG_PART1}\n\n{GRANDFATHER_FROG_PART2}\n\nHow does Jerry's climb to the top of his house contribute to the rest of the text?",
        "choices": ["He realizes that he wants to take a nap.", "He knows that he wants to go fishing.", "He knows where to find Longlegs the Blue Heron.", "He realizes why Billy Mink is in such a hurry."],
        "correct_answer": "He realizes why Billy Mink is in such a hurry.",
        "explanation": "By climbing to the top of his house, Jerry can see Grandfather Frog sleeping, which helps him understand why Billy is hurrying to find Little Joe Otter."
    },
    
    # Topic: Main Idea
    {
        "grade_level": 3,
        "topic": "Main Idea",
        "difficulty": 2,
        "weight": 1.0,
        "prompt": f"Read both parts:\n\n{UNDER_MY_NOSE_PART1}\n\n{UNDER_MY_NOSE_PART2}\n\nWhich statement by the author supports the main idea?",
        "choices": ["The books I made needed text, so I began writing words to go with my art.", "Getting a good idea for a book is the hardest thing for me, but also the most fun.", "I like to write out rough story ideas for my books, then make thumbnail sketches.", "I like to read the text out loud and listen to the rhythm of the words."],
        "correct_answer": "Getting a good idea for a book is the hardest thing for me, but also the most fun.",
        "explanation": "This statement supports the main idea that the creative process of writing books involves challenges and enjoyment."
    },
    {
        "grade_level": 3,
        "topic": "Main Idea",
        "difficulty": 2,
        "weight": 1.0,
        "prompt": f"Read both parts:\n\n{DOG_HERO_PART1}\n\n{DOG_HERO_PART2}\n\nWhat is the main idea of the text?",
        "choices": ["Mount Hood can be a dangerous place.", "Mount Hood is popular for rock climbing.", "A dog helps a group of rock climbers.", "A group of teachers goes rock climbing."],
        "correct_answer": "A dog helps a group of rock climbers.",
        "explanation": "The main idea focuses on how Velvet the dog helped save the climbers during their dangerous situation."
    },
    {
        "grade_level": 3,
        "topic": "Main Idea",
        "difficulty": 2,
        "weight": 1.0,
        "prompt": f"Read both parts:\n\n{DOG_HERO_PART1}\n\n{DOG_HERO_PART2}\n\nWhich statement from the text supports the main idea?",
        "choices": ["They had no idea a German shepherd named Velvet would help save their lives.", "On Sunday, the weather took a turn for the worse.", "They hiked for miles to try to make it down the mountainside.", "The rescue team found the climbers with Velvet in White River Canyon at about 7,400 feet."],
        "correct_answer": "They had no idea a German shepherd named Velvet would help save their lives.",
        "explanation": "This statement directly supports the main idea that Velvet the dog was instrumental in helping the climbers."
    },
    {
        "grade_level": 3,
        "topic": "Main Idea",
        "difficulty": 2,
        "weight": 1.0,
        "prompt": f"Read both parts:\n\n{BEAVERS_PART1}\n\n{BEAVERS_PART2}\n\nWhich detail from the text supports the main idea?",
        "choices": ["A beaver is a wild animal about three feet in length.", "They first gather together a number of sticks and logs.", "No beaver ever thinks of living alone.", "Each beaver has his fixed place on the floor."],
        "correct_answer": "They first gather together a number of sticks and logs.",
        "explanation": "This detail supports the main idea about how beavers work together to build dams."
    },
    
    # Topic: Text Structure
    {
        "grade_level": 3,
        "topic": "Text Structure",
        "difficulty": 3,
        "weight": 1.5,
        "prompt": f"Read both parts:\n\n{UNDER_MY_NOSE_PART1}\n\n{UNDER_MY_NOSE_PART2}\n\nHow does the author connect the writing steps in paragraphs 10 and 11?",
        "choices": ["by contrasting two different styles for writing books", "by giving a step-by-step process for publishing a book", "by comparing the writing steps for two kinds of books", "by giving a chronological order for beginning a book"],
        "correct_answer": "by giving a chronological order for beginning a book",
        "explanation": "The author presents the steps in time order, showing the sequence of how to begin writing a book."
    },
    {
        "grade_level": 3,
        "topic": "Text Structure",
        "difficulty": 3,
        "weight": 1.5,
        "prompt": f"Read both parts:\n\n{UNDER_MY_NOSE_PART1}\n\n{UNDER_MY_NOSE_PART2}\n\nHow does the author connect the ideas in paragraphs 12 and 13?",
        "choices": ["by listing important events that have occurred in the author's life", "by explaining the different parts of the book that have to be made", "by describing how the author gets ideas when they just will not come", "by comparing the rhythm of the text when read aloud to how it looks on paper"],
        "correct_answer": "by explaining the different parts of the book that have to be made",
        "explanation": "The paragraphs explain the various components that go into creating a complete book."
    },
    {
        "grade_level": 3,
        "topic": "Text Structure",
        "difficulty": 3,
        "weight": 1.5,
        "prompt": f"Read the passage:\n\n{BEAVERS_PART1}\n\nWhat is the connection between paragraphs 5 and 6?",
        "choices": ["They present a problem and offer a solution.", "They explain a cause-effect relationship.", "They present a sequence for building.", "They compare habits of wise beavers."],
        "correct_answer": "They present a sequence for building.",
        "explanation": "Paragraphs 5 and 6 describe the step-by-step process of how beavers build their dams."
    },
    {
        "grade_level": 3,
        "topic": "Text Structure",
        "difficulty": 3,
        "weight": 1.5,
        "prompt": f"Read both parts:\n\n{BEAVERS_PART1}\n\n{BEAVERS_PART2}\n\nHow are paragraphs 10 and 11 connected?",
        "choices": ["Both compare the two ways that beavers build dams.", "Both describe the differences between a dam and a pond.", "Paragraph 10 presents a problem, and paragraph 11 describes a solution.", "Paragraph 10 shows a result of the unusual situation in paragraph 11."],
        "correct_answer": "Paragraph 10 presents a problem, and paragraph 11 describes a solution.",
        "explanation": "Paragraph 10 shows the problem (hole in the dam), and paragraph 11 describes how the beavers solve it."
    },
    {
        "grade_level": 3,
        "topic": "Text Structure",
        "difficulty": 3,
        "weight": 1.5,
        "prompt": f"Read both parts:\n\n{DOG_HERO_PART1}\n\n{DOG_HERO_PART2}\n\nHow does the author connect the point that the climb was very dangerous in paragraphs 5 and 6?",
        "choices": ["The information in paragraph 6 is a result of the action in paragraph 5.", "The ideas in paragraphs 5 and 6 compare the different climbers.", "Paragraphs 5 and 6 describe the path the climbers took.", "Paragraph 5 lists the steps needed for paragraph 6."],
        "correct_answer": "The information in paragraph 6 is a result of the action in paragraph 5.",
        "explanation": "Paragraph 5 describes dangerous conditions, and paragraph 6 shows the consequences (the climbers falling)."
    },
    
    # Topic: Inference
    {
        "grade_level": 3,
        "topic": "Inference",
        "difficulty": 2,
        "weight": 1.0,
        "prompt": f"Read both parts:\n\n{UNDER_MY_NOSE_PART1}\n\n{UNDER_MY_NOSE_PART2}\n\nWhat is the meaning of the phrase 'right under your nose' in paragraph 16?",
        "choices": ["inside a person", "on a person's face", "read by a person", "in front of a person"],
        "correct_answer": "in front of a person",
        "explanation": "The phrase 'right under your nose' means something is very close or obvious, right in front of you."
    },
]


def add_reading_questions():
    """Add Grade 3 Reading questions to the database."""
    db = SessionLocal()
    try:
        added_count = 0
        skipped_count = 0
        
        for q_data in GRADE_3_READING_QUESTIONS:
            # Check if question already exists (by grade_level, topic, and difficulty only)
            # Oracle doesn't allow direct CLOB comparison (prompt and correct_answer are CLOB)
            # We'll just add all questions - duplicates will be handled by unique constraints if any
            # For now, skip duplicate check and just add all questions
            # If you run this multiple times, you may get duplicates, but that's okay for now
            question = Question(**q_data)
            db.add(question)
            added_count += 1
            
            question = Question(**q_data)
            db.add(question)
            added_count += 1
        
        db.commit()
        print(f"Added {added_count} Grade 3 Reading questions")
        if skipped_count > 0:
            print(f"Skipped {skipped_count} questions (already exist)")
        
        return {
            "added": added_count,
            "skipped": skipped_count,
            "total": len(GRADE_3_READING_QUESTIONS)
        }
    except Exception as e:
        db.rollback()
        print(f"Error adding questions: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("Adding Grade 3 Reading EOG questions to database...")
    print(f"Total questions to add: {len(GRADE_3_READING_QUESTIONS)}")
    result = add_reading_questions()
    print(f"\nSummary: {result['added']} added, {result['skipped']} skipped, {result['total']} total")
