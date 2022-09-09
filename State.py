"""
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

from __future__ import annotations
from typing import Iterable, Iterator, NamedTuple, Protocol
from dataclasses import dataclass

DRAW = 0
WIN = 1
LOSS = -1

X = 1
O = -1

class IFigures(Protocol):
    def get(self) -> Iterable[tuple[int, IFigures]]:
        """Iterate through available figures"""
        ...

    @classmethod
    def start(cls):
        """A starting set of figures"""
        ...


class Figures(tuple, IFigures):
    def get(self):
        def decrement(figure):
            return self.__class__(
                self[:figure] + (self[figure] - 1,) + self[figure + 1 :]
            )

        for figure, count in enumerate(self):
            if count:
                yield figure, decrement(figure)

    @classmethod
    def start(cls):
        return cls((2, 2, 2))


class ITable(Protocol):
    def update(self, i: int, fig: int) -> ITable:
        """Place a figure on the board

        Args:
            i (int): board square
            fig (int): figure to place
        """
        ...

    def __getitem__(self, index: int) -> int:
        ...

    def __iter__(self) -> Iterator[int]:
        """Board iterator"""
        ...

    @classmethod
    def start(cls) -> ITable:
        """An empty board"""
        ...


class Table(tuple, ITable):
    def update(self, i, fig):
        return Table(self[:i] + (fig,) + self[i + 1 :])

    @classmethod
    def start(cls):
        return cls((0, 0, 0, 0, 0, 0, 0, 0, 0))


class IState(Protocol):
    def score(self) -> int | None:
        """Compute the score for the state"""
        ...

    def moves(self) -> Iterable[IState]:
        """Generate the next moves"""
        ...

    @classmethod
    def start(cls) -> IState:
        """The starting state"""
        ...


class ILines(Protocol):
    LINES = (
        (0, 1, 2),
        (3, 4, 5),
        (6, 7, 8),
        (0, 3, 6),
        (1, 4, 7),
        (2, 5, 8),
        (0, 4, 8),
        (2, 4, 6),
    )


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


@dataclass(eq=True, frozen=True)
class MatrioshkaState(IState):
    table: ITable
    max_player: IFigures
    min_player: IFigures
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

        for figure_idx, next_figs in figures.get():

            figure = figure_idx + 1 if is_max else -(figure_idx + 1)
            max_figs = next_figs if is_max else self.max_player
            min_figs = self.min_player if is_max else next_figs

            for i, val in enumerate(self.table):
                square_empty = not val
                enemy_fig = figure * val < 0
                enemy_is_lesser = abs(figure) > abs(val)

                if square_empty or enemy_fig and enemy_is_lesser:
                    next_table = self.table.update(i, figure)

                    states.add(
                        self.__class__(next_table, max_figs, min_figs, self.depth + 1)
                    )
        return states

    @classmethod
    def start(cls):
        return cls(Table.start(), Figures.start(), Figures.start(), 0)


class CanonicalMatrioshkaState(MatrioshkaState, IState):
    def __init__(self, table, max_player, min_player, depth):
        t = table
        t = Table(
            min(
                t,
                (t[6], t[3], t[0], t[7], t[4], t[1], t[8], t[5], t[2]),  # r1
                (t[8], t[7], t[6], t[5], t[4], t[3], t[2], t[1], t[0]),  # r2
                (t[2], t[5], t[8], t[1], t[4], t[7], t[0], t[3], t[6]),  # r3
                (t[2], t[1], t[0], t[5], t[4], t[3], t[8], t[7], t[6]),  # Tx
                (t[0], t[3], t[6], t[1], t[4], t[7], t[2], t[5], t[8]),  # T-1
                (t[6], t[7], t[8], t[3], t[4], t[5], t[0], t[1], t[2]),  # Ty
                (t[8], t[5], t[2], t[7], t[4], t[1], t[6], t[3], t[0]),  # T+1
            )
        )

        super().__init__(
            t,
            max_player,
            min_player,
            depth,
        )
