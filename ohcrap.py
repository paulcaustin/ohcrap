#!/usr/bin/env python3

import sys
import re
import argparse
import random

parser = argparse.ArgumentParser(description='Analyze the dice game')
parser.add_argument('--test', '-t', action='store_true', help='Test #1')
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
    for die in range(1, 6):
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
