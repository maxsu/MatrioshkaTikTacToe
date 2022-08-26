import tqdm
import json

# states:
# neutral: 0
# player1: 1, 2, 3 (have 2 of each)
# player2: -1, -2, -3 (have 2 of each)
# board: 3x3 => 9 long tuple (board[i][j] = tuple[i*3 + j])

# Rotations
# e         r1 (90)     r2 (180)    r3 (270)
# 0 1 2       6 3 0       8 7 6       2 5 8
# 3 4 5   =>  7 4 1   =>  5 4 3   =>  1 4 7
# 6 7 8       8 5 2       2 1 0       0 3 6
# Reflections
# Tx       T-1=Tx(r1)   Ty=Tx(r2)  T+1=Tx(r3)
# 2 1 0       0 3 6       6 7 8       8 5 2
# 5 4 3   =>  1 4 7   =>  3 4 5   =>  7 4 1
# 8 7 6       2 5 8       0 1 2       6 3 0
def symmetries(e):
    return {
        e,
        (e[6], e[3], e[0], e[7], e[4], e[1], e[8], e[5], e[2]),  # r1
        (e[8], e[7], e[6], e[5], e[4], e[3], e[2], e[1], e[0]),  # r2
        (e[2], e[5], e[8], e[1], e[4], e[7], e[0], e[3], e[6]),  # r3
        (e[2], e[1], e[0], e[5], e[4], e[3], e[8], e[7], e[6]),  # Tx
        (e[0], e[3], e[6], e[1], e[4], e[7], e[2], e[5], e[8]),  # T-1
        (e[6], e[7], e[8], e[3], e[4], e[5], e[0], e[1], e[2]),  # Ty
        (e[8], e[5], e[2], e[7], e[4], e[1], e[6], e[3], e[0]),  # T+1
    }


def score(table):
    for line_idxs in (
        (0, 1, 2),
        (3, 4, 5),
        (6, 7, 8),
        (0, 3, 6),
        (1, 4, 7),
        (2, 5, 8),
        (0, 4, 8),
        (2, 4, 6),
    ):
        if all(table[li] > 0 for li in line_idxs):
            return 1
        if all(table[li] < 0 for li in line_idxs):
            return -1
    return None


def canonical_table(table):
    return sorted(symmetries(table))[0]


def moves(table, figures):
    for figure, count in figures:
        if count == 0:
            continue
        visited_tables = set()
        for idx in range(9):
            if abs(figure) > abs(table[idx]):
                next_table = canonical_table(
                    tuple(t if i != idx else figure for i, t in enumerate(table))
                )
                if next_table not in visited_tables:
                    visited_tables.add(next_table)
                    remaining_figures = tuple(
                        (f, c) if f != figure else (f, count - 1) for f, c in figures
                    )
                    yield next_table, remaining_figures


progress = tqdm.tqdm()


def minimax(table, max_player, min_player, depth, resolved_states):
    is_max = depth % 2 == 0
    sc = score(table)
    if sc is not None:
        progress.update(1)
        progress.set_postfix({"size": len(resolved_states)})
        return sc, table
    next_states = list(moves(table, max_player if is_max else min_player))
    if len(next_states) == 0:
        progress.update(1)
        progress.set_postfix({"size": len(resolved_states)})
        return 0, table
    if is_max:
        sc, next_table = max(
            (
                minimax(next_t, next_f, min_player, depth + 1, resolved_states)
                for next_t, next_f in next_states
            ),
            key=lambda x: x[0],
        )
    else:
        sc, next_table = min(
            (
                minimax(next_t, max_player, next_f, depth + 1, resolved_states)
                for next_t, next_f in next_states
            ),
            key=lambda x: x[0],
        )

    resolved_states.append([depth, sc, list(table), list(next_table)])
    return sc, table


if __name__ == "__main__":
    states = list()
    print(
        minimax(
            (0, 0, 0, 0, 0, 0, 0, 0, 0),
            ((1, 2), (2, 2), (3, 2)),
            ((-1, 2), (-2, 2), (-3, 2)),
            0,
            states,
        )
    )

    with open("solution.json", "w") as fp:
        json.dump(states, fp)
