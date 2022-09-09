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
from typing import Iterable, Iterator, Protocol

DRAW = 0
WIN = 1
LOSS = -1


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
