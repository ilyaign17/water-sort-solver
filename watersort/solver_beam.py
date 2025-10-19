import heapq
from typing import List, Tuple, Optional
from watersort.model import State, legal_moves, is_solved, canonical_key

Step = Tuple[int, int, int]  # (src, dst, amount)


def heuristic(state: State) -> int:
    """Эвристика: меньше смешанных бутылок и полу-заполненных."""
    dirty = 0
    semi = 0
    for b in state:
        if len(b) == 0:
            continue
        if len(set(b)) == 1:
            if len(b) < 4:  # CAPACITY=4
                semi += 1
        else:
            dirty += 1
    return 3 * dirty + semi


def beam_solve(start: State,
               beam_width: int = 500,
               max_depth: int = 200) -> Optional[List[Step]]:
    """
    Beam Search: на каждой глубине оставляем beam_width лучших состояний.
    Возвращает решение (список шагов) или None.
    """
    if is_solved(start):
        return []

    # front = список кортежей (h_score, state, path)
    front: List[Tuple[int, State, List[Step]]] = [(heuristic(start), start, [])]
    visited = set([canonical_key(start)])

    for depth in range(max_depth):
        next_front: List[Tuple[int, State, List[Step]]] = []
        for _, cur, path in front:
            for nxt, src, dst, amount in legal_moves(cur):
                key = canonical_key(nxt)
                if key in visited:
                    continue
                visited.add(key)
                new_path = path + [(src, dst, amount)]
                if is_solved(nxt):
                    return new_path
                score = heuristic(nxt) + len(new_path)
                next_front.append((score, nxt, new_path))

        if not next_front:
            return None

        # оставляем только top-N
        front = heapq.nsmallest(beam_width, next_front, key=lambda x: x[0])

    return None
