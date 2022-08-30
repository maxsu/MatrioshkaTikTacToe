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

        is_max = self.depth % 2
        figures = self.max_player if is_max else self.min_player

        states = []

        for figure_idx, count in enumerate(figures):
            if count == 0:
                continue
            visited_tables = set()
            figure = figure_idx + 1 if is_max else -(figure_idx + 1)
            for idx in range(9):
                if abs(figure) > abs(self.table[idx]):
                    next_table = canonical_table(
                        tuple(
                            t if i != idx else figure for i, t in enumerate(self.table)
                        )
                    )
                    if next_table not in visited_tables:
                        visited_tables.add(next_table)
                        remaining_figures = tuple(
                            fc if f_idx != figure_idx else fc - 1
                            for f_idx, fc in enumerate(figures)
                        )
                        if is_max:
                            states.append(
                                State(
                                    next_table,
                                    remaining_figures,
                                    self.min_player,
                                    self.depth + 1,
                                )
                            )
                        else:
                            states.append(
                                State(
                                    next_table,
                                    self.max_player,
                                    remaining_figures,
                                    self.depth + 1,
                                )
                            )
        return states

    def canonical_state(self):
        t = self
        return State(
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
            t.max_player,
            t.min_player,
            t.depth,
        )


STARTING_STATE = State(STARTING_TABLE, *STARTING_HANDS, depth=0)


progress = tqdm.tqdm()


def canonical_table(e):
    return min(
        e,
        (e[6], e[3], e[0], e[7], e[4], e[1], e[8], e[5], e[2]),  # r1
        (e[8], e[7], e[6], e[5], e[4], e[3], e[2], e[1], e[0]),  # r2
        (e[2], e[5], e[8], e[1], e[4], e[7], e[0], e[3], e[6]),  # r3
        (e[2], e[1], e[0], e[5], e[4], e[3], e[8], e[7], e[6]),  # Tx
        (e[0], e[3], e[6], e[1], e[4], e[7], e[2], e[5], e[8]),  # T-1
        (e[6], e[7], e[8], e[3], e[4], e[5], e[0], e[1], e[2]),  # Ty
        (e[8], e[5], e[2], e[7], e[4], e[1], e[6], e[3], e[0]),  # T+1
    )


depth_counter = Counter()


def minimax(state, resolved_states):
    res = resolved_states.get(state, None)
    if res is not None:
        return res[0], state.table
    is_max = state.depth % 2 == 0

    if state.depth < 7:
        depth_counter[state.depth] += 1
        progress.set_postfix({"by_depth": depth_counter})

    sc = state.score()

    if sc:
        progress.update(1)
        return sc, state.table

    next_states = state.moves()

    if not next_states:
        progress.update(1)
        return 0, state.table

    if is_max:
        sc, next_table = max(
            (
                minimax(
                    State(next_t, next_f, state.min_player, state.depth + 1),
                    resolved_states,
                )
                for next_t, next_f in next_states
            ),
            key=lambda x: x[0],
        )

    else:
        sc, next_table = min(
            (
                minimax(
                    State(next_t, state.max_player, next_f, state.depth + 1),
                    resolved_states,
                )
                for next_t, next_f in next_states
            ),
            key=lambda x: x[0],
        )

    resolved_states[state] = sc, next_table
    return sc, state.table


if __name__ == "__main__":
    states = dict()
    print(minimax(STARTING_STATE, states))

    with open("solution.dat", "wb") as fp:
        for key, value in states.items():
            table, maxp, minp = key
            values = list(table) + list(maxp) + list(minp) + [value[0]] + list(value[1])
            fp.write(struct.pack(">25i", *values))
