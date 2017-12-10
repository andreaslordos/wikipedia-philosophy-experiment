# wikipedia-philosophy-experiment
Allows you to run tests that yield data on what happens if you keep clicking the first link on a Wikipedia page

If you're confused, that's fine. 

Essentially, you input three things:

Initial Target
Times the program should hit on the initial target before moving onto the next target (let this be x)
Number of targets the program should complete (let this be y)

After inputting these 3 parameters, the program will start on a completely random Wikipiedia page and start hopping from page to page by clicking the first link on each page. It will continue to do this until

a) It reaches a dead end page with no links
b) It ends up in a loop (e.g. Biology -> Organisms -> Biology -> Organisms etc.)
c) It finds the target page

Once it finds the target page x times, it will then pick another target based on the pages it has seen - it will usually pick the page it ran onto most often.

It will then repeat the process y times with a new target each time

At the end, it will output data about how many hops it needed for each target, and how many times it needed to start at a random page to reach a target x times - you will see that the more specific the target, the more times it will run into loops or dead end pages, but the hops needed to get to the target on successful trials will be less.
