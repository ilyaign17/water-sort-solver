from typing import Tuple, List, Optional, Dict

# ---- Константы ----
CAPACITY = 4  # фиксированная вместимость каждой бутылки

# ---- Типы ----
Color = str
Bottle = Tuple[Color, ...]   # сверху последний элемент
State = Tuple[Bottle, ...]


# ---- Конструкторы/утилиты ----
def make_state(bottles: List[List[Color]]) -> State:
    """
    Превращает список списков в неизменяемое состояние (кортежи).
    Проверяет, что ни одна бутылка не переполнена (> CAPACITY).
    """
    norm: List[Bottle] = []
    for i, b in enumerate(bottles, 1):
        if len(b) > CAPACITY:
            raise ValueError(f"Бутылка {i} длиннее CAPACITY={CAPACITY}: len={len(b)}")
        norm.append(tuple(b))
    return tuple(norm)


def pretty_state(state: State) -> str:
    """Красиво печатает состояние по бутылкам."""
    lines = []
    for i, b in enumerate(state, 1):
        lines.append(f"{i:>2}: {list(b)}")
    return "\n".join(lines)


# ---- Правила игры ----
def is_uniform(bottle: Bottle) -> bool:
    """
    Бутылка считается правильной, если:
    - она пустая, или
    - в ней CAPACITY слоёв одного цвета.
    """
    if len(bottle) == 0:
        return True
    if len(bottle) == CAPACITY and len(set(bottle)) == 1:
        return True
    return False


def is_solved(state: State) -> bool:
    """Уровень решён, если каждая бутылка либо пустая, либо заполнена одним цветом на CAPACITY."""
    return all(is_uniform(b) for b in state)


def pour(state: State, src: int, dst: int) -> Optional[Tuple[State, int]]:
    """
    Переливает за одно действие подряд все верхние одинаковые слои из src в dst,
    но не больше свободного места. Возвращает (new_state, amount) или None.
    """
    if src == dst:
        return None

    bottles = [list(b) for b in state]
    donor = bottles[src]
    receiver = bottles[dst]

    if not donor:
        return None                 # донор пуст
    if len(receiver) >= CAPACITY:
        return None                 # приёмник полон

    color = donor[-1]

    # приёмник не пуст и верхний цвет другой — нельзя
    if receiver and receiver[-1] != color:
        return None

    # длина одноцветной "шапки" у донора
    run = 1
    for i in range(len(donor) - 2, -1, -1):
        if donor[i] == color:
            run += 1
        else:
            break

    free_space = CAPACITY - len(receiver)
    amount = min(run, free_space)
    if amount <= 0:
        return None

    for _ in range(amount):
        receiver.append(donor.pop())

    new_state: State = tuple(tuple(b) for b in bottles)
    return new_state, amount

def legal_moves(state: State) -> List[Tuple[State, int, int, int]]:
    """
    Возвращает список всех допустимых ходов из состояния.
    Применяем простые правила pruning:
    - не льём из пустой;
    - не льём в ту же самую бутылку;
    - не льём обратно в ту, откуда только что взяли (из-за visited всё равно не зациклится, но экономим);
    - не льём из уже одноцветной полной бутылки.
    """
    n = len(state)
    moves: List[Tuple[State, int, int, int]] = []
    for src in range(n):
        bottle_src = state[src]
        if not bottle_src:
            continue  # из пустой нечего лить
        if len(bottle_src) == CAPACITY and len(set(bottle_src)) == 1:
            continue  # полная одноцветная — её трогать не надо
        for dst in range(n):
            if src == dst:
                continue
            res = pour(state, src, dst)
            if res is None:
                continue
            new_state, amount = res
            moves.append((new_state, src, dst, amount))
    return moves


def canonical_key(state: State) -> tuple:
    """
    Канонический ключ состояния:
    - нормируем цвета: присваиваем новые id 0..k-1 в порядке первого появления сверху-вниз, слева-направо;
    - каждую бутылку представляем кортежем новых id;
    - сортируем список бутылок лексикографически.
    Возвращаем хэшируемый ключ (tuple of tuples).
    """
    color_map: Dict[Color, int] = {}
    next_id = 0

    def remap_color(c: Color) -> int:
        nonlocal next_id
        if c not in color_map:
            color_map[c] = next_id
            next_id += 1
        return color_map[c]

    remapped_bottles = []
    # Важна стабильность обхода: идём по бутылкам и по слоям снизу->верх/верх->низ — не критично,
    # главное последовательно. Возьмём слева-направо и снизу-вверх для детерминизма.
    for b in state:
        remapped = tuple(remap_color(c) for c in b)
        remapped_bottles.append(remapped)

    # сортируем бутылки лексикографически
    remapped_bottles.sort()
    return tuple(remapped_bottles)

