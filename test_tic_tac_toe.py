from TicTacToeState import X, O, TicTacToe
from State import DRAW, Table
from minimax import minimax


"""
PREDICATES
"""


def drawn(state):
    return minimax(state) == DRAW


"""
TESTS
"""


def test_draw_depth_0():
    state = TicTacToe.start()
    assert drawn(state)


def test_draw_depth_1():
    state = TicTacToe(Table.start().update(4, X), 1)
    assert drawn(state)


def test_draw_progression():
    states = [
        TicTacToe(Table((O, O, X, X, X, O, O, X, X)), 9),
        TicTacToe(Table((O, O, X, X, X, O, O, X, 0)), 8),
        TicTacToe(Table((O, O, X, X, X, 0, O, X, 0)), 7),
        TicTacToe(Table((O, O, X, 0, X, 0, O, X, 0)), 6),
        TicTacToe(Table((O, O, X, 0, X, 0, 0, X, 0)), 5),
        TicTacToe(Table((O, O, 0, 0, X, 0, 0, X, 0)), 4),
        TicTacToe(Table((O, 0, 0, 0, X, 0, 0, X, 0)), 3),
        TicTacToe(Table((O, 0, 0, 0, X, 0, 0, 0, 0)), 2),
        TicTacToe(Table((0, 0, 0, 0, X, 0, 0, 0, 0)), 1),
    ]

    for i, state in enumerate(states):

        assert drawn(state)


def test_draw_depth_2():
    state = TicTacToe(Table((O, 0, 0, 0, X, 0, 0, 0, 0)), 2)
    assert drawn(state)


def test_draw_depth_9():
    state = TicTacToe(Table((X, O, X, X, X, O, O, X, O)), 9)
    assert drawn(state)


def test_draw_depth_8():
    state = TicTacToe(Table((O, X, O, O, X, 0, X, O, X)), 8)
    assert drawn(state)


if __name__ == "__main__":

    test_draw_depth_9()
    test_draw_depth_8()
    test_draw_progression()

    test_draw_depth_4()
    
    
    # test_draw_depth_2()
    # test_draw_depth_1()
    # test_draw_depth_0()
