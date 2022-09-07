"""
Minmax solution to matrioshka tic tac toe.

Features:
- Transposition table (game state memoization)
- Non-canonical state pruning (based on board symmetries)
"""

from State import TicTacToe
from minimax import minimax


if __name__ == "__main__":
    TicTacToeValue = minimax(
        TicTacToe.starting(),
    )

    print(TicTacToeValue)

    
