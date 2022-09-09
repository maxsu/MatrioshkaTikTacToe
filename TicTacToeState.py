"""
State class for Tic Tac Toe
"""

from dataclasses import dataclass
from typing import Iterable

from State import IState, ILines, Table, WIN, LOSS

X = 1
O = -1

@dataclass(eq=True, frozen=True)
class TicTacToe(IState, ILines):

    table: Table
    depth: int

    def score(self) -> int | None:
        is_max = self.depth % 2 == 0

        for line in self.LINES:

            a, b, c = (self.table[i] for i in line)
            
            if is_max:
                if a == b == c == X:
                    return WIN
                if a == b == c == O:
                    return LOSS
            else:
                if a == b == c == X:
                    return LOSS
                if a == b == c == O:
                    return WIN

        return None

    def moves(self) -> Iterable[IState]:

        is_max = self.depth % 2 == 0
        figure = 1 if is_max else -1

        states = []

        for square, square_occupied in enumerate(self.table):
            if square_occupied:
                continue

            next_table = self.table.update(square, figure)

            states.append(self.__class__(next_table, self.depth + 1))

        return states

    @classmethod
    def start(cls) -> IState:
        return cls(Table.start(), 0)

    def __repr__(self) -> str:
        result = ""

        for row in range(0, 9, 3):

            vm = {-1: "O", 1: "X", 0: " "}
            _row = self.table[row : row + 3]
            _row = [vm[x] for x in _row]
            result += "".join(_row) + "\n"
        return result
