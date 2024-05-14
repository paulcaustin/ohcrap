#!/usr/bin/env python3

import sys
import re
import argparse
import random

# I think this is how to specify a strategy
strategy = {
    #   %bust  value
    6: (0.024, 490),
    5: (0.078, 300),
    4: (0.157, 210),
    3: (0.278, 170),
    2: (0.443, 160),
    1: (0.666, 180)
}

parser = argparse.ArgumentParser(description='Analyze the dice game')
parser.add_argument('--test', '-t', action='store_true', help='Test #1')
parser.add_argument('--zero', '-z', metavar='loops', help='Use Monte-Carlo to get probabilities of 0')
parser.add_argument('--rolls', '-r', metavar='loops', help='Use Monte-Carlo to get data for rolls')
parser.add_argument('--full', '-f', metavar='loops', help='Run full sim')
parser.add_argument('--dice', '-d', metavar='numdice', default=6, help='Start with N dice')
parser.add_argument('--simple', '-s', metavar='loops', help='Run with simple strategy')
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

if args.zero:
    for num_dice in range(1,7):
        bust = 0
        total = 0
        for i in range(1, int(args.zero)):
            dice = roll_dice(num_dice)
            (max_score, used) = score_dice(dice)
            total += max_score
            if max_score == 0:
                bust += 1
        avg = total / (int(args.zero) - bust)
        print(f"Dice={num_dice}, Bust={(100*bust/int(args.zero)):.1f}")

if args.rolls:
    for num_dice in range(1,7):
        bust = 0
        total = 0
        for i in range(1, int(args.rolls)):
            dice = roll_dice(num_dice)
            (max_score, used) = score_dice(dice)
            total += max_score
            if max_score == 0:
                bust += 1
        avg = total / (int(args.rolls) - bust)
        print(f"Dice={num_dice}, Bust={(100*bust/int(args.rolls)):.1f}, Avg={int(avg)}")

if args.full:
    bust = 0
    total = 0
    lost_score = 0
    for i in range(1, int(args.full)):
        num_dice = int(args.dice)
        roll_score = 0
        rolls = 0
        while True:
            rolls += 1
            dice = roll_dice(num_dice)

            # Simple strategy, use all scorable dice
            (score, used) = score_dice(dice)
            # print(f"Rolled {num_dice}: {','.join((str(x) for x in dice))} - {score}")

            # Handle a bust
            if score == 0:
                bust += 1
                lost_score += roll_score
                roll_score = 0
                break

            # Simple strategy
            roll_score += score
            remaining = num_dice - used if used < num_dice else 6
            (chance_of_bust, value_to_proceed) = strategy[remaining]

            if roll_score * chance_of_bust < value_to_proceed * float(args.caution):
                pass
            else:
                break   # Quit while you're ahead
            num_dice = remaining
        total += roll_score
        # print(f"Turn {i}: Score={roll_score}, Rolls={rolls}")
    avg_lost = lost_score / bust if bust > 0 else 0
    avg_score = total / (int(args.full) - bust)
    avg_score = total / (int(args.full))
    print(f"Avg={avg_score:.1f}, Bust={(100*bust/int(args.full)):.1f}, AvgLost={avg_lost:.1f}")

if args.simple:
    bust = 0
    total = 0
    lost_score = 0
    for i in range(1, int(args.simple)):
        num_dice = int(args.dice)
        roll_score = 0
        rolls = 0
        while True:
            rolls += 1
            dice = roll_dice(num_dice)

            # Simple strategy, use all scorable dice
            (score, used) = score_dice(dice)
            # print(f"Rolled {num_dice}: {','.join((str(x) for x in dice))} - {score}")

            # Handle a bust
            if score == 0:
                bust += 1
                lost_score += roll_score
                roll_score = 0
                break

            # Simple strategy
            roll_score += score
            remaining = num_dice - used if used < num_dice else 6
            if remaining == 6 and roll_score < 20000:   # Worth 500 ?
                pass
            elif remaining == 5 and roll_score < 5000:  # Worth 400 ?
                pass
            elif remaining == 4 and roll_score < 2000:  # Worth 300 ?
                pass
            elif remaining == 3 and roll_score < 700:   # Worth 200 ?
                pass
            elif remaining == 2 and roll_score < 200:   # Worth 100 ?
                pass
            elif remaining == 1 and roll_score < 75:    # Worth 50 ?
                pass
            else:
                break   # Quit while you're ahead
            num_dice = remaining
        total += roll_score
        # print(f"Turn {i}: Score={roll_score}, Rolls={rolls}")
    avg_lost = lost_score / bust if bust > 0 else 0
    avg_score = total / (int(args.simple) - bust)
    print(f"Avg={avg_score:.1f}, Bust={(100*bust/int(args.simple)):.1f}, AvgLost={avg_lost:.1f}")
