from dataclasses import dataclass
from typing import Iterable

from State import IState, ITable, IFigures, Figures, ILines, Table, WIN, LOSS

@dataclass(eq=True, frozen=True)
class MatrioshkaState(IState, ILines):
    table: ITable
    max_player: IFigures
    min_player: IFigures
    depth: int

    def score(self):
        for line in self.LINES:

            vals = [self.table[i] for i in line]

            if min(vals) > 0:
                return WIN

            if max(vals) < 0:
                return LOSS

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
