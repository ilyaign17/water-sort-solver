from typing import Iterable, Tuple, List
from watersort.model import State, pretty_state, pour

Step = Tuple[int, int, int]  # (src, dst, amount)

def replay_solution(start: State, steps: Iterable[Step]) -> List[State]:
    """
    Применяет шаги по очереди и возвращает список состояний:
    [state0(start), state1, state2, ...]
    Проверяет, что фактически перелилось ровно 'amount' слоёв.
    """
    states = [start]
    cur = start
    for idx, (src, dst, amount) in enumerate(steps, 1):
        res = pour(cur, src, dst)
        if res is None:
            raise RuntimeError(f"[шаг {idx}] Ход невозможен: {src+1} → {dst+1}")
        new_state, actual_amount = res
        if actual_amount != amount:
            raise RuntimeError(
                f"[шаг {idx}] Ожидали перелить {amount}, а перелилось {actual_amount} "
                f"при ходе {src+1} → {dst+1}"
            )
        states.append(new_state)
        cur = new_state
    return states


def print_replay(states: List[State]) -> None:
    """
    Печатает все состояния с шагами.
    """
    for i, st in enumerate(states):
        if i == 0:
            print("Стартовое состояние:")
        else:
            print(f"\nПосле шага {i}:")
        print(pretty_state(st))


def ascii_state(state: State) -> str:
    """
    Рисует бутылки вертикально. Верх — справа в списке бутылки.
    Пример одной бутылки на 4 слоя:
    |   |
    | r |
    | r |
    | b |
    └───┘
    """
    CAP = 4  # у нас фиксировано
    cols = []
    for b in state:
        col = []
        # рисуем сверху вниз (пустоты сверху)
        pad = CAP - len(b)
        for _ in range(pad):
            col.append("   ")
        for c in b:
            col.append(f"{str(c)[:3]:>3}")
        cols.append(col)

    lines = []
    # строки по уровням
    for row in range(CAP):
        line = []
        for col in cols:
            line.append(f"|{col[row]}|")
        lines.append(" ".join(line))
    # нижняя окантовка
    base = " ".join(["└───┘" for _ in cols])
    lines.append(base)
    return "\n".join(lines)


def ascii_replay(states: list[State]) -> None:
    for i, st in enumerate(states):
        if i == 0:
            print("\n[Старт]")
        else:
            print(f"\n[После шага {i}]")
        print(ascii_state(st))
