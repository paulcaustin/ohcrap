#!/usr/bin/env python3

import sys
import re
import argparse
import random

# I think this is generally useful in defining a strategy
# But the values COULD change for different strategies
roll_value = {
    #   %bust  value
    6: (0.024, 490),
    5: (0.078, 300),
    4: (0.157, 210),
    3: (0.278, 170),
    2: (0.443, 160),
    1: (0.666, 180)
}

parser = argparse.ArgumentParser(description='Analyze the dice game')
parser.add_argument('--loops', '-l', metavar='N', default=1000*1000, help='How many loops')
parser.add_argument('--test', '-t', action='store_true', help='Test #1')
parser.add_argument('--rolls', '-r', action='store_true', help='Calc data for individual rolls')
parser.add_argument('--full', '-f', action='store_true', help='Full sim with strategy')
parser.add_argument('--dice', '-d', metavar='numdice', default=6, help='Start with N dice')
parser.add_argument('--strategy', '-s', metavar='name', default='trivial', help='Run with specified strategy')
parser.add_argument('--caution', '-c', metavar='fudge', default=1.0, help='fudge factor for extra caution, def 1.0')
args = parser.parse_args()

def roll_dice(num_dice):
    """
    Rolls `num_dice` number of dice and returns the results as a list.
    Each element in the list represents the result of one die roll (1-6).
    """
    return [random.randint(1, 6) for _ in range(num_dice)]


def score_dice(dice):
    # Count occurrences of each face value
    counts = [dice.count(i) for i in range(1, 7)]

    # Special cases
    if counts.count(2) == 3:
        return (500, 6)           # 3 pairs
    if sorted(dice) == [1, 2, 3, 4, 5, 6]:
        return (1500, 6)          # 1,2,3,4,5,6

    # Initialize total score
    total_score = 0
    used = 0

    # Add points for individual dice
    if counts[0] < 3:
        total_score += counts[0] * 100  # Aces
        used += counts[0]

    if counts[4] < 3:
        total_score += counts[4] * 50   # Fives
        used += counts[4]

    # Add points for sets (aces are like "10" here)
    for die in range(1, 7):
        count = counts[die-1]
        val = 10 if die == 1 else die
        if count >= 3:
            # 3 of a kind, 4 of a kind, 5 of a kind, 6 of a kind
            total_score += (count-2) * 100 * val
            used += count

    return (total_score, used)

def strategize(current_score, dice):
    '''
        Implement a strategy based on current score and the current roll.
        The interface is to return the score and the number of dice to roll next.
        A score of 0 means we busted (no strategy is needed).
        Rolling 0 dice next means the strategy says to stop rolling.
    '''
    (score, used) = score_dice(dice)
    # print(f"Rolled {num_dice}: {','.join((str(x) for x in dice))} - {score}")

    # Handle a bust
    if score == 0:
        return (0, 0)

    if args.strategy == 'smart':
        # To be implemented
        pass
    elif args.strategy == 'keepall':
        # Use all scorable dice
        # Decide if we should continue rolling by using roll_values * caution
        keep_all_score = current_score + score
        remaining_dice = len(dice) - used if used < len(dice) else 6
        (chance_of_bust, value_to_proceed) = roll_value[remaining_dice]

        if roll_score * chance_of_bust < value_to_proceed * float(args.caution):
            return (keep_all_score, remaining_dice)
        else:
            # Quit while you're ahead
            return (keep_all_score, 0)
    elif args.strategy == 'trivial':
        # Decide if we should continue rolling
        keep_all_score = current_score + score
        remaining_dice = len(dice) - used if used < len(dice) else 6

        # Continue if you have 4, 5, or 6 dice
        if remaining_dice > 3:
            return (keep_all_score, remaining_dice)
        else:
            # Quit while you're ahead
            return (keep_all_score, 0)
    elif args.strategy == 'hardcoded':
        # Decide if we should continue rolling
        keep_all_score = current_score + score
        remaining_dice = len(dice) - used if used < len(dice) else 6

        if remaining_dice == 6 and keep_all_score < 20000:   # Worth 500 ?
            pass
        elif remaining_dice == 5 and keep_all_score < 5000:  # Worth 400 ?
            pass
        elif remaining_dice == 4 and keep_all_score < 2000:  # Worth 300 ?
            pass
        elif remaining_dice == 3 and keep_all_score < 700:   # Worth 200 ?
            pass
        elif remaining_dice == 2 and keep_all_score < 200:   # Worth 100 ?
            pass
        elif remaining_dice == 1 and keep_all_score < 75:    # Worth 50 ?
            pass
        else:
            return (keep_all_score, 0)

        return (keep_all_score, remaining_dice)
    else:
        throw(f"Unknown strategy: {args.strategy}")

def iterate_dice_combinations(*dice):
    '''
        Iterate over all subsets of the given dice.
        Example:
            for combination in iterate_dice_combinations(5, 4, 3):
                print(combination)
    '''
    if dice:
        for i, d in enumerate(dice):
            for c in iterate_dice_combinations(*dice[:i] + dice[i+1:]):
                yield (d,) + c

# Example usage:
# dice = [1, 2, 3, 4, 5, 6]
# print("Maximum score for", dice, ":", calculate_max_score(dice))


if args.test:
    for i in range(0, 30):
        num_dice = random.randint(1, 6)
        dice = roll_dice(num_dice)
        (max_score, used) = score_dice(dice)
        print(f"{max_score}, {used}: {','.join((str(x) for x in dice))}")
    sys.exit(0)

if args.rolls:
    for num_dice in range(1,7):
        bust = 0
        total = 0
        for i in range(1, int(args.loops)):
            dice = roll_dice(num_dice)
            (max_score, used) = score_dice(dice)
            total += max_score
            if max_score == 0:
                bust += 1
        avg = total / (int(args.loops) - bust)
        print(f"Dice={num_dice}, Bust={(100*bust/int(args.loops)):.1f}, Avg={int(avg)}")

if args.full:
    bust = 0
    total = 0
    lost_score = 0
    for i in range(1, int(args.loops)):
        num_dice = int(args.dice)
        roll_score = 0
        rolls = 0
        while True:
            rolls += 1
            dice = roll_dice(num_dice)
            (new_score, dice_to_roll) = strategize(roll_score, dice)

            # print(f"Rolled {num_dice}: {','.join((str(x) for x in dice))} - {score}")

            # Handle a bust
            if new_score == 0:
                bust += 1
                lost_score += roll_score
                roll_score = 0
                break

            roll_score = new_score
            if dice_to_roll == 0:
                break   # Quit while you're ahead

            num_dice = dice_to_roll

        total += roll_score
        # print(f"Turn {i}: Score={roll_score}, Rolls={rolls}")

    avg_lost = lost_score / bust if bust > 0 else 0
    # If you think we should exclude busts from the avg
    # avg_score = total / (int(args.loops) - bust)
    avg_score = total / int(args.loops)
    print(f"Avg={avg_score:.1f}, Bust={(100*bust/int(args.loops)):.1f}, AvgLost={avg_lost:.1f}")
