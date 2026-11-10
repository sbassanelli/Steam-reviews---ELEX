# Design Brief: ELEX

Output of the review pipeline on a random sample of 1,200 Steam reviews, of 10,027 after filtering (copies bought on Steam, not received for free).

**How to read it.** The evidence is computed from the coded reviews. Quotes are verbatim. Each section gives a model draft and a version reviewed by the authors. Both are hypotheses for the design team to discuss: associations are not causal, no change has been tested, and the coding has not yet been validated by a human coder.

## Summary

| ID | Group | Issue | Type | Reviews | Negative | OR | Requirement |
|---|---|---|---|---:|---:|---:|---|
| R1 | Repair first | Combat Dynamics | Design | 536 | 68% | 0.62 | Attacks must respond promptly to input, and hits must match what the animations show. |
| R2 | Repair first | Movement and Evasion | Design | 163 | 49% | 0.56 | Moving and dodging must feel responsive and must be affordable during combat. |
| R3 | Repair first | Enemy Strength and Balance | Design | 132 | 89% | 0.47 | Players must be able to tell how dangerous an enemy is before engaging it. |
| R4 | Repair first | Performance and Technical Implementation | System | 55 | 69% | 0.50 | The game must run correctly on current hardware. |
| R5 | Repair first | Control and Customization | Design | 39 | 90% | 0.29 | All keys must be rebindable, and different actions must not share a key when they collide. |
| R6 | Repair first | Crash and Stability | System | 36 | 75% | 0.42 | The game must start and run without crashing to desktop or freezing. |
| A1 | Accepted friction | Early Game Difficulty | Design | 177 | 94% | 1.60 | Keep the weak start, and make clear that it is a stage of growth. |
| A2 | Accepted friction | Overall Difficulty and Mastery | Design | 165 | 55% | 1.68 | Keep the high challenge for the established audience, and make it manageable for players new to the studio. |
| P1 | Protect | Story Engagement | Design | 250 | 21% | 2.17 | Quest outcomes must keep depending on the player's decisions. |
| P2 | Protect | World Building | Design | 162 | 15% | 1.78 | The setting must remain distinctive and worth exploring. |
| P3 | Protect | Factions and Lore | Design | 144 | 22% | 1.88 | Factions must stay distinct in their history, their world view and the way they play. |
| P4 | Protect | Exploration and Resource Management | Design | 140 | 30% | 2.62 | Exploration must stay rewarding and not led by the hand. |
| P5 | Protect | Character Growth and Replayability | Design | 85 | 10% | 5.69 | The character's growth must stay long and perceptible, and different builds and factions must stay worth replaying. |
| P6 | Protect | Gameplay Duration and Engagement | Design | 69 | 27% | 2.27 | Length must come from content and must not feel stretched. |

## Repair first

Players criticize these aspects, and criticism goes with not recommending the game.

### R1. Combat Dynamics (Design)

**Requirement (reviewed by the authors).** Attacks must respond promptly to input, and hits must match what the animations show.

**Evidence.**
- Mentioned in 536 reviews; 67.8% of its extracts are negative and 21.3% positive.
- Odds ratio of recommending the game: 0.62 (95% CI 0.48-0.79; corrected p = 0.001).
- Of the 398 reviews criticizing it, 53.0% recommend the game (70.0% of all reviews do).
- Those critics recommend at 64.4% among reviews naming the studio's earlier games (n = 177; group average 80.9%) and at 43.9% among the others (n = 221; group average 62.1%).

**What players say.**
> your guy just stands there and doesn't swing his weapon

> enemy animations that will hit even when you are not in there 'shown' hit zone

> stamina on NORMAL needs to be like 20% less use per hit

**Proposed change.** Review input response on attacks; align hit zones with animations; retune stamina cost per hit by difficulty.

**Check in later reviews.** Track codes on response, hit detection and stamina separately; negative extracts should fall in each.

**Model draft (Phi-4, to be reviewed).**
- Requirement: The game must refine combat mechanics to ensure responsive and fluid interactions, reducing clunkiness and improving player satisfaction.
- Change: Enhance the responsiveness of combat actions, such as dodging and blocking, to ensure they feel intuitive and effective. Adjust enemy AI to provide a balanced challenge without feeling like 'bullet sponges'.
- Check: Reviews should indicate that combat feels more responsive and engaging, with players noting improved fluidity and satisfaction in combat interactions.

**Status.** Proposed

### R2. Movement and Evasion (Design)

**Requirement (reviewed by the authors).** Moving and dodging must feel responsive and must be affordable during combat.

**Evidence.**
- Mentioned in 163 reviews; 48.9% of its extracts are negative and 37.2% positive.
- Odds ratio of recommending the game: 0.56 (95% CI 0.40-0.79; corrected p = 0.008).
- Of the 88 reviews criticizing it, 33.0% recommend the game (70.0% of all reviews do).
- Those critics recommend at 46.7% among reviews naming the studio's earlier games (n = 30; group average 80.9%) and at 25.9% among the others (n = 58; group average 62.1%).

**What players say.**
> even rolling around is a waste of stamina during combat

> character's movement feels like pushing a bag of rice

**Proposed change.** Lower the stamina cost of dodging; shorten acceleration and stopping.

**Check in later reviews.** The share of critics who still recommend the game should rise.

**Model draft (Phi-4, to be reviewed).**
- Requirement: The game must improve the responsiveness and fluidity of movement controls, including dodging, jetpacking, and enemy engagement, to ensure smooth and intuitive player interactions.
- Change: Refine the movement mechanics to eliminate jankiness and improve responsiveness, allowing for more precise dodging and jetpacking. This could involve optimizing animations and control inputs to reduce delays and increase fluidity.
- Check: Reviews should indicate that players experience smoother and more responsive movement, with fewer complaints about control lag and animation issues.

**Status.** Proposed

### R3. Enemy Strength and Balance (Design)

**Requirement (reviewed by the authors).** Players must be able to tell how dangerous an enemy is before engaging it.

**Evidence.**
- Mentioned in 132 reviews; 88.8% of its extracts are negative and 5.9% positive.
- Odds ratio of recommending the game: 0.47 (95% CI 0.32-0.68; corrected p = 0.001).
- Of the 117 reviews criticizing it, 50.4% recommend the game (70.0% of all reviews do).
- Those critics recommend at 66.7% among reviews naming the studio's earlier games (n = 48; group average 80.9%) and at 39.1% among the others (n = 69; group average 62.1%).

**What players say.**
> Strong NPCs are randomly distributed and they can one-shot you

> you'll often encounter enemies that are way above your level and will kill you quickly

**Proposed change.** Keep dangerous enemies, but signal their strength before contact and review where they are placed.

**Check in later reviews.** Complaints about surprise deaths should fall, even if complaints about strength remain.

**Model draft (Phi-4, to be reviewed).**
- Requirement: The game must adjust enemy damage output and health scaling to ensure that players can effectively engage and defeat enemies without being one-shot or requiring excessive time to defeat.
- Change: Implement a rebalancing of enemy health and damage values to create a more gradual difficulty curve, allowing players to feel progression and mastery over time.
- Check: Reviews should indicate that players experience a more balanced challenge, with enemies being neither too easy nor overwhelmingly difficult, and that players feel their character's progression is meaningful.

**Status.** Proposed

### R4. Performance and Technical Implementation (System)

**Requirement (reviewed by the authors).** The game must run correctly on current hardware.

**Evidence.**
- Mentioned in 55 reviews; 68.9% of its extracts are negative and 29.5% positive.
- Odds ratio of recommending the game: 0.50 (95% CI 0.29-0.85; corrected p = 0.047).
- Of the 38 reviews criticizing it, 39.5% recommend the game (70.0% of all reviews do).
- Those critics recommend at 64.3% among reviews naming the studio's earlier games (n = 14; group average 80.9%) and at 25.0% among the others (n = 24; group average 62.1%).

**What players say.**
> Game needs updating for 5000 series gpu’s

**Proposed change.** Run a compatibility pass on current graphics cards.

**Check in later reviews.** Read reviews by date: complaints should no longer follow new hardware.

**Model draft (Phi-4, to be reviewed).**
- Requirement: The game must be optimized to ensure stable performance across a wide range of hardware configurations, including modern GPUs and platforms like the Steam Deck.
- Change: Implement comprehensive performance optimization and testing, focusing on reducing lag, improving frame rates, and fixing known glitches and bugs. This includes optimizing code for better resource management and conducting extensive QA and playtesting to identify and resolve technical issues.
- Check: Reviews should indicate improved stability, reduced lag, and fewer technical issues, with players noting a smoother and more responsive gameplay experience.

**Status.** Proposed

### R5. Control and Customization (Design)

**Requirement (reviewed by the authors).** All keys must be rebindable, and different actions must not share a key when they collide.

**Evidence.**
- Mentioned in 39 reviews; 90.5% of its extracts are negative and 4.8% positive.
- Odds ratio of recommending the game: 0.29 (95% CI 0.15-0.55; corrected p = 0.001).
- Of the 35 reviews criticizing it, 34.3% recommend the game (70.0% of all reviews do).
- Those critics recommend at 42.9% among reviews naming the studio's earlier games (n = 7; group average 80.9%) and at 32.1% among the others (n = 28; group average 62.1%).

**What players say.**
> Keybinds are NOT fully customizable

> make it a different key to sit in chairs and lay in beds then it is to loot

> the very badly designed weapons mode switching

**Proposed change.** Add full key rebinding; separate the interaction keys that collide; speed up weapon switching.

**Check in later reviews.** Negative extracts on bindings, context keys and weapon switching should fall.

**Model draft (Phi-4, to be reviewed).**
- Requirement: The game must allow full customization of keybindings, including the ability to remap all keys and hotbar slots, and provide intuitive control schemes for both keyboard and gamepad users.
- Change: Implement a comprehensive keybinding menu that allows players to remap all controls, including weapon switching, camera control, and interaction keys. Ensure that the control schemes are intuitive and responsive for both keyboard and gamepad users.
- Check: Reviews should indicate that players find the controls more intuitive and customizable, with fewer complaints about clunky or unresponsive controls.

**Status.** Proposed

### R6. Crash and Stability (System)

**Requirement (reviewed by the authors).** The game must start and run without crashing to desktop or freezing.

**Evidence.**
- Mentioned in 36 reviews; 75.0% of its extracts are negative and 20.0% positive.
- Odds ratio of recommending the game: 0.42 (95% CI 0.22-0.80; corrected p = 0.047).
- Of the 26 reviews criticizing it, 34.6% recommend the game (70.0% of all reviews do).
- Those critics recommend at 55.6% among reviews naming the studio's earlier games (n = 9; group average 80.9%) and at 23.5% among the others (n = 17; group average 62.1%).

**What players say.**
> the game black screens at the 5 hour mark

> this game continues to crash to desktop upon starting

**Proposed change.** Use the moments players name (start-up, first city, final cutscene) as reproduction cases.

**Check in later reviews.** Crash codes should fall at each moment reported.

**Model draft (Phi-4, to be reviewed).**
- Requirement: The game must ensure stability by preventing crashes and freezes during gameplay, including during key sequences and dialogues.
- Change: Implement comprehensive stability testing and debugging to identify and fix crash-inducing bugs, particularly those occurring during critical game moments such as dialogues with Thorald and final cutscenes.
- Check: Reviews should indicate a significant reduction in crash frequency and improved game stability, with players noting fewer instances of game freezes and crashes to desktop.

**Status.** Proposed

## Accepted friction

Players complain, yet those who complain tend to recommend the game. Do not remove these without checking what they give to players.

### A1. Early Game Difficulty (Design)

**Requirement (reviewed by the authors).** Keep the weak start, and make clear that it is a stage of growth.

**Evidence.**
- Mentioned in 177 reviews; 94.1% of its extracts are negative and 3.4% positive.
- Odds ratio of recommending the game: 1.60 (95% CI 1.10-2.34; corrected p = 0.046).
- Of the 167 reviews criticizing it, 76.6% recommend the game (70.0% of all reviews do).
- Those critics recommend at 82.6% among reviews naming the studio's earlier games (n = 69; group average 80.9%) and at 72.4% among the others (n = 98; group average 62.1%).

**What players say.**
> Combat is tough until you reach level 15 or so and then it becomes pretty easy

> It is hard, and you are laughable weak at the start

**Proposed change.** State the difficulty early as a promise of growth; look at the later drop in challenge instead of softening the start.

**Check in later reviews.** Critics who recommend the game should stay above the average of their group.

**Model draft (Phi-4, to be reviewed).**
- Requirement: Keep the early game difficulty as a core challenge, but clearly communicate its role in the game's design and player progression.
- Change: Introduce an in-game tutorial or narrative element that frames the early game difficulty as a deliberate design choice to enhance player skill development and immersion. This could be achieved through character dialogue or a prologue that sets expectations about the challenge.
- Check: Reviews should indicate that players understand and appreciate the early game difficulty as a meaningful part of the game's challenge, without feeling unfairly punished or misled.

**Status.** Proposed

### A2. Overall Difficulty and Mastery (Design)

**Requirement (reviewed by the authors).** Keep the high challenge for the established audience, and make it manageable for players new to the studio.

**Evidence.**
- Mentioned in 165 reviews; 54.6% of its extracts are negative and 31.7% positive.
- Odds ratio of recommending the game: 1.68 (95% CI 1.14-2.50; corrected p = 0.034).
- Of the 92 reviews criticizing it, 67.4% recommend the game (70.0% of all reviews do).
- Those critics recommend at 86.0% among reviews naming the studio's earlier games (n = 43; group average 80.9%) and at 51.0% among the others (n = 49; group average 62.1%).

**What players say.**
> You will die A LOT and sometimes you may even get frustrated with it

> challenging difficulty which makes you truly think about your actions

**Proposed change.** State the level of challenge on the store page and in the first hour; test an entry option for new players.

**Check in later reviews.** Critics who do not name earlier games should reach the average of their group.

**Model draft (Phi-4, to be reviewed).**
- Requirement: Keep the overall difficulty and mastery as a core challenge of the game, ensuring it is communicated as a deliberate design choice that enhances the player's sense of achievement.
- Change: Introduce a narrative or tutorial element early in the game that frames the difficulty as a key part of the game's identity, emphasizing the rewarding nature of overcoming challenges. This could include dialogue or lore that highlights the game's world as one where only the most skilled and persistent can thrive.
- Check: Reviews should reflect an understanding and appreciation of the game's difficulty as a core feature, with fewer mentions of frustration and more emphasis on the satisfaction derived from mastering the game.

**Status.** Proposed

## Protect

Players praise these aspects, and they go with recommending the game. Later changes should not damage them.

### P1. Story Engagement (Design)

**Requirement (reviewed by the authors).** Quest outcomes must keep depending on the player's decisions.

**Evidence.**
- Mentioned in 250 reviews; 20.7% of its extracts are negative and 72.4% positive.
- Odds ratio of recommending the game: 2.17 (95% CI 1.54-3.07; corrected p = 0.000).
- Of the 54 reviews criticizing it, 53.7% recommend the game (70.0% of all reviews do).
- Those critics recommend at 54.5% among reviews naming the studio's earlier games (n = 33; group average 80.9%) and at 52.4% among the others (n = 21; group average 62.1%).

**What players say.**
> where decisions you make and things you do matter

> multiple solutions and multiple endings

**Proposed change.** Check any change to quests against the choices and outcomes they offer.

**Check in later reviews.** Positive extracts on choices and consequences should not fall.

**Model draft (Phi-4, to be reviewed).**
- Requirement: Preserve the impact of player choices on the storyline and quest outcomes to maintain player engagement and satisfaction.
- Change: When modifying quest structures or dialogue options, ensure that changes do not reduce the number of meaningful choices available to players.
- Check: Reviews should continue to highlight the significance of player choices and their consequences on the game's narrative and world.

**Status.** Proposed

### P2. World Building (Design)

**Requirement (reviewed by the authors).** The setting must remain distinctive and worth exploring.

**Evidence.**
- Mentioned in 162 reviews; 15.4% of its extracts are negative and 69.8% positive.
- Odds ratio of recommending the game: 1.78 (95% CI 1.19-2.66; corrected p = 0.020).
- Of the 27 reviews criticizing it, 48.1% recommend the game (70.0% of all reviews do).
- Those critics recommend at 52.4% among reviews naming the studio's earlier games (n = 21; group average 80.9%) and at 33.3% among the others (n = 6; group average 62.1%).

**What players say.**
> The World in itself is what got me hooked in the first place

**Proposed change.** Treat the world as a core asset in expansions and sequels.

**Check in later reviews.** Positive extracts on the world should not fall.

**Model draft (Phi-4, to be reviewed).**
- Requirement: Preserve the immersive and unique blend of science fiction, fantasy, and post-apocalyptic elements in the game world to maintain player engagement and satisfaction.
- Change: When modifying the game world, ensure that any changes do not disrupt the established balance between high technology and magic, or the diversity of locations and cultures.
- Check: Reviews should continue to highlight the world's creativity, diversity, and the seamless integration of different thematic elements without noting a loss of immersion or uniqueness.

**Status.** Proposed

### P3. Factions and Lore (Design)

**Requirement (reviewed by the authors).** Factions must stay distinct in their history, their world view and the way they play.

**Evidence.**
- Mentioned in 144 reviews; 21.9% of its extracts are negative and 49.8% positive.
- Odds ratio of recommending the game: 1.88 (95% CI 1.22-2.88; corrected p = 0.014).
- Of the 34 reviews criticizing it, 61.8% recommend the game (70.0% of all reviews do).
- Those critics recommend at 65.2% among reviews naming the studio's earlier games (n = 23; group average 80.9%) and at 54.5% among the others (n = 11; group average 62.1%).

**What players say.**
> Each of the factions is well explained, has it's specific history and the way they see the world differs drastically

> 3 different factions that play quite differently

**Proposed change.** Keep the differences between factions when rebalancing them.

**Check in later reviews.** Positive extracts on faction identity should not fall.

**Model draft (Phi-4, to be reviewed).**
- Requirement: Preserve the distinctiveness and moral ambiguity of the factions to maintain player immersion and engagement.
- Change: When modifying faction-related content, ensure that each faction retains its unique characteristics and worldview, such as the Berserkers' focus on healing the planet, the Outlaws' reliance on modern weapons, and the Clerics' futuristic technology.
- Check: Reviews should continue to highlight the immersive and engaging nature of the factions, without any indication of diminished distinctiveness or moral complexity.

**Status.** Proposed

### P4. Exploration and Resource Management (Design)

**Requirement (reviewed by the authors).** Exploration must stay rewarding and not led by the hand.

**Evidence.**
- Mentioned in 140 reviews; 29.7% of its extracts are negative and 48.5% positive.
- Odds ratio of recommending the game: 2.62 (95% CI 1.62-4.21; corrected p = 0.000).
- Of the 47 reviews criticizing it, 68.1% recommend the game (70.0% of all reviews do).
- Those critics recommend at 76.7% among reviews naming the studio's earlier games (n = 30; group average 80.9%) and at 52.9% among the others (n = 17; group average 62.1%).

**What players say.**
> Exploration that actually rewards in multiple ways instead of just money and experience points

> Not being spoon fed and led between encounters and quests

**Proposed change.** Improve guidance only where it does not replace discovery; Guidance and Direction is criticized, so treat this as a trade-off.

**Check in later reviews.** Criticism of guidance should fall without losing positive extracts on exploration.

**Model draft (Phi-4, to be reviewed).**
- Requirement: Preserve the rewarding nature of exploration by ensuring that exploration consistently leads to discovering new items, weapons, and events.
- Change: Verify that any modifications to the game's exploration mechanics do not reduce the frequency or variety of discoveries made during exploration.
- Check: Reviews should continue to highlight the rewarding and enjoyable aspects of exploration, without indicating a decrease in the discovery of new items, weapons, or events.

**Status.** Proposed

### P5. Character Growth and Replayability (Design)

**Requirement (reviewed by the authors).** The character's growth must stay long and perceptible, and different builds and factions must stay worth replaying.

**Evidence.**
- Mentioned in 85 reviews; 9.6% of its extracts are negative and 85.1% positive.
- Odds ratio of recommending the game: 5.69 (95% CI 2.53-12.79; corrected p = 0.000).
- Of the 8 reviews criticizing it, 50.0% recommend the game (70.0% of all reviews do).
- Those critics recommend at 60.0% among reviews naming the studio's earlier games (n = 5; group average 80.9%) and at 33.3% among the others (n = 3; group average 62.1%).

**What players say.**
> rewarding progress, with actual zero to hero

> replay value with 3 different factions and different play styles

**Proposed change.** Check every balance change against the length of the growth arc.

**Check in later reviews.** Positive extracts should not fall after a rebalance.

**Model draft (Phi-4, to be reviewed).**
- Requirement: Preserve the sense of character progression and replayability by ensuring that character growth remains noticeable and satisfying across multiple playthroughs.
- Change: When modifying character progression mechanics, ensure that the sense of growth and the variety of progression paths remain intact.
- Check: Reviews should continue to highlight the noticeable and satisfying character growth and the game's replayability without any decline in these aspects.

**Status.** Proposed

### P6. Gameplay Duration and Engagement (Design)

**Requirement (reviewed by the authors).** Length must come from content and must not feel stretched.

**Evidence.**
- Mentioned in 69 reviews; 27.4% of its extracts are negative and 61.6% positive.
- Odds ratio of recommending the game: 2.27 (95% CI 1.19-4.33; corrected p = 0.037).
- Of the 19 reviews criticizing it, 57.9% recommend the game (70.0% of all reviews do).
- Those critics recommend at 69.2% among reviews naming the studio's earlier games (n = 13; group average 80.9%) and at 33.3% among the others (n = 6; group average 62.1%).

**What players say.**
> A solid 40+ hour adventure awaits you if you want to do pretty much everything and every quest

> This makes the game longer but doesn't feel stretched by any means like in other RPGs

**Proposed change.** When adding content, avoid repeating what already exists.

**Check in later reviews.** Positive extracts on length should not fall, and complaints about padding should not appear.

**Model draft (Phi-4, to be reviewed).**
- Requirement: Preserve the game's ability to engage players for extended periods by ensuring that progression and exploration remain rewarding and challenging.
- Change: Consider adjusting the pacing of skill progression and exploration rewards to maintain player interest over long play sessions.
- Check: Reviews should indicate that players continue to find the game engaging and rewarding over extended play sessions without feeling repetitive or overly difficult.

**Status.** Proposed

## Watch list

More criticized than praised, but with no significant association with the recommendation. The reviews give no reason to put these first.

| Issue | Reviews | Negative | OR (95% CI) |
|---|---:|---:|---|
| Graphics Quality | 184 | 46% | 1.00 (0.71-1.41) |
| Progression Speed and Reward Balance | 157 | 64% | 0.69 (0.49-0.98) |
| Character Progression | 128 | 52% | 0.93 (0.63-1.38) |
| Difficulty Curve and Scaling | 117 | 71% | 0.71 (0.48-1.05) |
| Bug Impact Spectrum | 113 | 91% | 0.90 (0.60-1.37) |
| Combat Challenge | 79 | 83% | 0.57 (0.36-0.91) |
