from typing import Optional, List, Tuple, Set
from watersort.model import State, legal_moves, is_solved

Step = Tuple[int, int, int]  # (src, dst, amount)


def dfs_solve(start: State, max_depth: int = 50_000) -> Optional[List[Step]]:
    """
    Поиск в глубину (DFS с возвратом).
    Возвращает список шагов или None.
    max_depth — ограничение по глубине, чтобы не зациклиться.
    """

    visited: Set[State] = set()

    def backtrack(state: State, path: List[Step], depth: int) -> Optional[List[Step]]:
        if is_solved(state):
            return path
        if depth >= max_depth:
            return None
        visited.add(state)

        for nxt, src, dst, amount in legal_moves(state):
            if nxt in visited:
                continue
            res = backtrack(nxt, path + [(src, dst, amount)], depth + 1)
            if res is not None:
                return res
        return None

    return backtrack(start, [], 0)
