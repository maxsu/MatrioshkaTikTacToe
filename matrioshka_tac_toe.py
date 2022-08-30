"""
Minmax solution to matrioshka tic tac toe.

Features:
- Game state memoization
- State Canonization based on 3x3 board symmetry group

States:
- Board: 3x3 => 9 long tuple (board[i][j] = tuple[i*3 + j])
 - Squares: {-3, -2, -1, 0, 1, 2, 3} => 7 int values
  - Neutral square: 0
  - Player1 piece: 1, 2, 3
  - Player2 piece: -1, -2, -3

- Players: 6 pieces => 2x of 3 types => 3 long tuple
 - Player1 figurines: 1, 1, 2, 2, 3, 3
 - Player2 figurines: -1, -1, -2, -2, -3, -3

Symmetries:
- Rotations:
 e         r1 (90)     r2 (180)    r3 (270)
 0 1 2       6 3 0       8 7 6       2 5 8
 3 4 5   =>  7 4 1   =>  5 4 3   =>  1 4 7
 6 7 8       8 5 2       2 1 0       0 3 6

Reflections:
 Tx       T-1=Tx(r1)   Ty=Tx(r2)  T+1=Tx(r3)
 2 1 0       0 3 6       6 7 8       8 5 2
 5 4 3   =>  1 4 7   =>  3 4 5   =>  7 4 1
 8 7 6       2 5 8       0 1 2       6 3 0
"""


from collections import Counter
from typing import NamedTuple
import tqdm
import struct


TABLE_LINES = (
    (0, 1, 2),
    (3, 4, 5),
    (6, 7, 8),
    (0, 3, 6),
    (1, 4, 7),
    (2, 5, 8),
    (0, 4, 8),
    (2, 4, 6),
)

STARTING_TABLE = (0, 0, 0, 0, 0, 0, 0, 0, 0)
STARTING_HANDS = (2, 2, 2), (2, 2, 2)


class State(NamedTuple):
    table: tuple
    max_player: tuple
    min_player: tuple
    depth: int

    def score(self):
        for line in TABLE_LINES:

            vals = [self.table[i] for i in line]

            if min(vals) > 0:
                return 1

            if max(vals) < 0:
                return -1

        return None

    def moves(self):

        is_max = not self.depth % 2
        figures = self.max_player if is_max else self.min_player

        states = set()

        for figure_idx, count in enumerate(figures):
            if not count:
                continue

            figure = figure_idx + 1 if is_max else -(figure_idx + 1)

            next_figs = figures[:figure_idx] + (count - 1,) + figures[figure_idx + 1 :]
            max_figs = next_figs if is_max else self.max_player
            min_figs = self.min_player if is_max else next_figs

            for i in range(9):
                val = self.table[i]
                if abs(figure) > abs(val):
                    next_table = self.table[:i] + (figure,) + self.table[i + 1 :]

                    states.add(
                        State.canonical(
                            next_table,
                            max_figs,
                            min_figs,
                            self.depth + 1,
                        )
                    )
        return states

    @classmethod
    def canonical(cls, table, max_p, min_p, depth):
        t = table
        return cls(
            min(
                t,
                (t[6], t[3], t[0], t[7], t[4], t[1], t[8], t[5], t[2]),  # r1
                (t[8], t[7], t[6], t[5], t[4], t[3], t[2], t[1], t[0]),  # r2
                (t[2], t[5], t[8], t[1], t[4], t[7], t[0], t[3], t[6]),  # r3
                (t[2], t[1], t[0], t[5], t[4], t[3], t[8], t[7], t[6]),  # Tx
                (t[0], t[3], t[6], t[1], t[4], t[7], t[2], t[5], t[8]),  # T-1
                (t[6], t[7], t[8], t[3], t[4], t[5], t[0], t[1], t[2]),  # Ty
                (t[8], t[5], t[2], t[7], t[4], t[1], t[6], t[3], t[0]),  # T+1
            ),
            max_p,
            min_p,
            depth,
        )


STARTING_STATE = State(STARTING_TABLE, *STARTING_HANDS, depth=0)

progress = tqdm.tqdm()

depth_counter = Counter()


def minimax(state, stateDB):

    if cached_result := stateDB.get(state, None):
        return cached_result[0], state.table

    if state.depth < 7:
        depth_counter[state.depth] += 1
        progress.set_postfix({"by_depth": depth_counter})

    score = state.score()

    if score:
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


if __name__ == "__main__":
    stateDB = dict()
    print(minimax(STARTING_STATE, stateDB))

    with open("solution.dat", "wb") as fp:
        for key, value in stateDB.items():
            table, maxp, minp = key
            values = list(table) + list(maxp) + list(minp) + [value[0]] + list(value[1])
            fp.write(struct.pack(">25i", *values))
