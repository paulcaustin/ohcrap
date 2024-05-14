ohcrap

This is a simulator for a similarly named dice game.  See [the rules](the-rules.md)

At it's core, this game is entirely random.  However, there are enough decisions to be made,
that a good strategy might provide an advantage.  The point of this simulation is to help
in determining the best strategies.  There are slightly differing strategies at the
beginning and end of the game, but we are interested mostly in the middle of the game.
In the middle of the game the strategy is more or less "long term score maximization".

I think the data needed is, for 1 through 6 dice:

- The chance that throwing N dice will result in a 0 score
  - Note that this should be calculable but we'll just do monte carlo
- The likely pay off if you play good strategy going forward
  - Note that this is a recursive def, we can only approximate
  - Each level relies on the lower level and ultimately the 6-dice level
  - We can recursively approximate the 6-dice level with simulations

You always have 2 or more options.  You should optimize:

- Keeping your current score and stopping
- There may be one or more options to continue
- Diminish the current score by the chance of 0 and add the likely pay off for various options
