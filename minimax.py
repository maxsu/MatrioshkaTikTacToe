"""
Minmax solution to matrioshka tic tac toe.

Features:
- Transposition table (game state memoization)
- Non-canonical state pruning (based on board symmetries)
"""

from collections import Counter
from typing import NamedTuple
import tqdm
import struct

import State
from State import DRAW

progress = tqdm.tqdm()
DEPTH_COUNTER = Counter()


def depth_counter(level):
    def wrapper(fn):
        def wrapped_fn(state):
            if state.depth <= level:
                DEPTH_COUNTER[state.depth] += 1
                progress.set_postfix({"by_depth": DEPTH_COUNTER})
            return fn(state)

        return wrapped_fn

    return wrapper


def _progress(fn):
    def wrapped_fn(state):
        result = fn(state)
        progress.update(1)
        return result

    return wrapped_fn


@_progress
@depth_counter(level=4)
def minimax(state):

    if win_or_loss := state.score():
        return win_or_loss

    next_states = state.moves()

    if not next_states:
        return DRAW

    return max((minimax(s) for s in next_states), key=lambda x: -x)


def transposition_table(fn):
    def wrapped_fn(state, stateDB):

        if cached_result := stateDB.get(state, None):
            return cached_result[0], state.table

        score = fn(state)


def minimax2(state, stateDB):

    if cached_result := stateDB.get(state, None):
        return cached_result[0], state.table

    if state.depth < 5:
        DEPTH_COUNTER[state.depth] += 1
        progress.set_postfix({"by_depth": DEPTH_COUNTER})

    if score := state.score():
        progress.update(1)
        return score, state.table

    next_states = state.moves()

    if not next_states:
        progress.update(1)
        return 0, state.table

    score, next_table = max(
        (minimax(next_state, stateDB) for next_state in next_states),
        key=lambda x: -x[0],
    )

    stateDB[state] = score, next_table
    return score, state.table
