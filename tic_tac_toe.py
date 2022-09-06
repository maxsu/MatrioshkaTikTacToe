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
import minimax

if __name__ == "__main__":
    stateDB = dict()
    starting_state = State.TicTacToe.starting()
    print(
        minimax.minimax(
            starting_state,
            # stateDB,
        )
    )

    # with open("solution.dat", "wb") as fp:
    #     for key, value in stateDB.items():
    #         table, maxp, minp = key
    #         values = list(table) + list(maxp) + list(minp) + [value[0]] + list(value[1])
    #         fp.write(struct.pack(">25i", *values))
