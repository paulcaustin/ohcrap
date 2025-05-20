#!/usr/bin/env node

// I think this is generally useful in defining a strategy
// But the values COULD change for different strategies
const roll_value = {
  //   %bust  value
  6: [0.024, 490],
  5: [0.078, 300],
  4: [0.157, 210],
  3: [0.278, 170],
  2: [0.443, 160],
  1: [0.666, 180],
};

const parser = require('argparse').ArgumentParser({
  description: 'Analyze the dice game',
});
parser.add_argument('--loops', '-l', {
  metavar: 'N',
  defaultValue: 1000 * 1000,
  help: 'How many loops',
});
parser.add_argument('--test', '-t', {
  action: 'store_true',
  help: 'Test #1',
});
parser.add_argument('--rolls', '-r', {
  action: 'store_true',
  help: 'Calc data for individual rolls',
});
parser.add_argument('--full', '-f', {
  action: 'store_true',
  help: 'Full sim with strategy',
});
parser.add_argument('--dice', '-d', {
  metavar: 'numdice',
  defaultValue: 6,
  help: 'Start with N dice',
});
parser.add_argument('--strategy', '-s', {
  metavar: 'name',
  defaultValue: 'trivial',
  help: 'Run with specified strategy',
});
parser.add_argument('--caution', '-c', {
  metavar: 'fudge',
  defaultValue: 1.0,
  help: 'fudge factor for extra caution, def 1.0',
});
const args = parser.parse_args();

function roll_dice(num_dice) {
  /**
   * Rolls `num_dice` number of dice and returns the results as a list.
   * Each element in the list represents the result of one die roll (1-6).
   */
  return Array.from({ length: num_dice }, () => Math.floor(Math.random() * 6) + 1);
}

function score_dice(dice) {
  // Count occurrences of each face value
  const counts = Array.from({ length: 6 }, (_, i) => dice.filter((d) => d === i + 1).length);

  // Special cases
  if (counts.filter((c) => c === 2).length === 3) {
    return [500, 6]; // 3 pairs
  }
  if (JSON.stringify(dice.slice().sort((a, b) => a - b)) === JSON.stringify([1, 2, 3, 4, 5, 6])) {
    return [1500, 6]; // 1,2,3,4,5,6
  }

  // Initialize total score
  let total_score = 0;
  let used = 0;

  // Add points for individual dice
  if (counts[0] < 3) {
    total_score += counts[0] * 100; // Aces
    used += counts[0];
  }

  if (counts[4] < 3) {
    total_score += counts[4] * 50; // Fives
    used += counts[4];
  }

  // Add points for sets (aces are like "10" here)
  for (let die = 1; die <= 6; die++) {
    const count = counts[die - 1];
    const val = die === 1 ? 10 : die;
    if (count >= 3) {
      // 3 of a kind, 4 of a kind, 5 of a kind, 6 of a kind
      total_score += (count - 2) * 100 * val;
      used += count;
    }
  }

  return [total_score, used];
}

function strategize(current_score, dice) {
  /**
   * Implement a strategy based on the current score and the current roll.
   * The interface is to return the score and the number of dice to roll next.
   * A score of 0 means we busted (no strategy is needed).
   * Rolling 0 dice next means the strategy says to stop rolling.
   */
  const [score, used] = score_dice(dice);

  // Handle a bust
  if (score === 0) {
    return [0, 0];
  }

  if (args.strategy === 'smart') {
    // To be implemented
    return [current_score + score, 0]; // Default return to avoid infinite loop
  } else if (args.strategy === 'keepall') {
    // Use all scorable dice
    // Decide if we should continue rolling by using roll_values * caution
    const keep_all_score = current_score + score;
    const remaining_dice = used < dice.length ? dice.length - used : 6;
    const [chance_of_bust, value_to_proceed] = roll_value[remaining_dice];

    // Note: The original python code used `roll_score` here, which is not defined in this scope.
    // Assuming it should be `keep_all_score` or `score`. Using `score` based on context.
    if (score * chance_of_bust < value_to_proceed * parseFloat(args.caution)) {
      return [keep_all_score, remaining_dice];
    } else {
      // Quit while you're ahead
      return [keep_all_score, 0];
    }
  } else if (args.strategy === 'trivial') {
    // Decide if we should continue rolling
    const keep_all_score = current_score + score;
    const remaining_dice = used < dice.length ? dice.length - used : 6;

    // Continue if you have 4, 5, or 6 dice
    if (remaining_dice > 3) {
      return [keep_all_score, remaining_dice];
    } else {
      // Quit while you're ahead
      return [keep_all_score, 0];
    }
  } else if (args.strategy === 'hardcoded') {
    // Decide if we should continue rolling
    const keep_all_score = current_score + score;
    const remaining_dice = used < dice.length ? dice.length - used : 6;

    if (remaining_dice === 6 && keep_all_score < 20000) { 
       return [keep_all_score, remaining_dice];
    } else if (remaining_dice === 5 && keep_all_score < 5000) { 
       return [keep_all_score, remaining_dice];
    } else if (remaining_dice === 4 && keep_all_score < 2000) { 
       return [keep_all_score, remaining_dice];
    } else if (remaining_dice === 3 && keep_all_score < 700) { 
       return [keep_all_score, remaining_dice];
    } else if (remaining_dice === 2 && keep_all_score < 200) { 
       return [keep_all_score, remaining_dice];
    } else if (remaining_dice === 1 && keep_all_score < 75) { 
       return [keep_all_score, remaining_dice];
    } else {
      return [keep_all_score, 0];
    }

  } else {
    throw new Error(`Unknown strategy: ${args.strategy}`);
  }
  // Default return to avoid infinite loop if strategy is not 'smart'
  return [current_score + score, 0];
}

function iterate_dice_combinations(dice) {
  /**
   * Iterate over all subsets of the given dice.
   */
  const combinations = [];
  function generateCombinations(currentIndex, currentCombination) {
    combinations.push(currentCombination);

    for (let i = currentIndex; i < dice.length; i++) {
      generateCombinations(i + 1, currentCombination.concat(dice[i]));
    }
  }

  generateCombinations(0, []);
  // Remove the empty combination at the beginning
  combinations.shift();
  return combinations;
}

// Example usage:
// const dice = [1, 2, 3, 4, 5, 6];
// console.log("Maximum score for", dice, ":", calculate_max_score(dice));


if (args.test) {
  for (let i = 0; i < 30; i++) {
    const num_dice = Math.floor(Math.random() * 6) + 1;
    const dice = roll_dice(num_dice);
    const [max_score, used] = score_dice(dice);
    console.log(`${max_score}, ${used}: ${dice.join(',')}`);
  }
  process.exit(0);
}

if (args.rolls) {
  for (let num_dice = 1; num_dice <= 6; num_dice++) {
    let bust = 0;
    let total = 0;
    for (let i = 1; i < parseInt(args.loops); i++) {
      const dice = roll_dice(num_dice);
      const [max_score, used] = score_dice(dice);
      total += max_score;
      if (max_score === 0) {
        bust++;
      }
    }
    const avg = total / (parseInt(args.loops) - bust);
    console.log(`Dice=${num_dice}, Bust=${(100 * bust / parseInt(args.loops)).toFixed(1)}, Avg=${Math.floor(avg)}`);
  }
}

if (args.full) {
  let bust = 0;
  let total = 0;
  let lost_score = 0;
  for (let i = 1; i < parseInt(args.loops); i++) {
    let num_dice = parseInt(args.dice);
    let roll_score = 0;
    let rolls = 0;
    while (true) {
      rolls++;
      const dice = roll_dice(num_dice);
      const [new_score, dice_to_roll] = strategize(roll_score, dice);

      // Handle a bust
      if (new_score === 0) {
        bust++;
        lost_score += roll_score;
        roll_score = 0;
        break;
      }

      roll_score = new_score;
      if (dice_to_roll === 0) {
        break; // Quit while you're ahead
      }

      num_dice = dice_to_roll;
    }

    total += roll_score;
  }

  const avg_lost = bust > 0 ? lost_score / bust : 0;
  // If you think we should exclude busts from the avg
  // avg_score = total / (parseInt(args.loops) - bust);
  const avg_score = total / parseInt(args.loops);
  console.log(`Avg=${avg_score.toFixed(1)}, Bust=${(100 * bust / parseInt(args.loops)).toFixed(1)}, AvgLost=${avg_lost.toFixed(1)}`);
}
