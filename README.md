ohcrap

This is a simulator for a similarly named dice game.  See [the rules](the-rules.md)

At it's core, this game is entirely random.  However, there are enough decisions to be made,
that a good strategy might provide an advantage.  The point of this simulation is to help
in determining the best strategies.

I think the data needed is, for 1 through 6 dice:

- The chance that your next throw will result in a 0 score
- The likely pay off if you play good strategy going forward

You always have 2 or more options.  You should optimize:

- Keeping your current score
- Diminish the current score by the chance of 0 and add the likely pay off for various options
