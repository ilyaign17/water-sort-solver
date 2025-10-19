# cli.py
from __future__ import annotations
import argparse
from pathlib import Path
from typing import List, Tuple
import json
import sys

from watersort.model import make_state, pretty_state, is_solved
from watersort.solver_dfs import dfs_solve
from watersort.solver_beam import beam_solve
from watersort.replay import replay_solution, print_replay, ascii_replay

Step = Tuple[int, int, int]

LEVELS_DIR = Path("levels")
DEFAULT_LEVEL = LEVELS_DIR / "level1.json"
DEFAULT_BEAM_WIDTH = 500
DEFAULT_MAX_DEPTH = 300


def find_level(path_like: str | Path) -> Path:
    """Умно резолвит имя уровня:
    1) ровно указанный путь;
    2) файл в ./levels/;
    3) добавляет .json, если забыли.
    """
    cand = Path(path_like)
    exts = ["", ".json"] if cand.suffix == "" else [""]

    for ext in exts:
        p = Path(str(cand) + ext)
        if p.exists():
            return p
        p2 = LEVELS_DIR / (p.name)
        if p2.exists():
            return p2
    raise FileNotFoundError(f"Не нашёл файл уровня: {path_like}")


def load_level(path: Path):
    data = json.loads(path.read_text(encoding="utf-8"))
    return make_state(data["bottles"])


def solve(level_path: Path, use_dfs: bool, steps_only: bool, ascii_view: bool):
    state = load_level(level_path)
    print(f"Уровень: {level_path}")
    print(pretty_state(state))
    print("is_solved? ->", is_solved(state))

    if use_dfs:
        solution: List[Step] | None = dfs_solve(state, max_depth=DEFAULT_MAX_DEPTH)
        method = "dfs"
    else:
        solution = beam_solve(state, beam_width=DEFAULT_BEAM_WIDTH, max_depth=DEFAULT_MAX_DEPTH)
        method = "beam"

    if solution is None:
        print("\n❌ Решение не найдено.")
        return
    if not solution:
        print("\n✅ Уровень уже решён.")
        return

    print(f"\n✅ Нашли решение из {len(solution)} шагов ({method}):")
    for i, (src, dst, amount) in enumerate(solution, 1):
        print(f"{i:>2}. {src+1} → {dst+1} (перелить {amount})")

    if steps_only:
        return

    states = replay_solution(state, solution)
    print("\n===== Пошаговый разбор =====")
    if ascii_view:
        ascii_replay(states)
    else:
        print_replay(states)


def list_levels() -> None:
    if not LEVELS_DIR.exists():
        print("Папка levels/ не найдена.")
        return
    files = sorted(p for p in LEVELS_DIR.iterdir() if p.suffix == ".json")
    if not files:
        print("В levels/ нет .json уровней.")
        return
    print("Доступные уровни в levels/:")
    for p in files:
        print(" -", p.name)


def main():
    ap = argparse.ArgumentParser(
        description="Water Sort — простой солвер. Можно передать имя уровня (напр., level3.json)."
    )
    ap.add_argument(
        "level",
        nargs="?",
        help="Путь или имя файла уровня (ищется также в ./levels). Примеры: level3.json, levels/level3.json"
    )
    ap.add_argument("--dfs", action="store_true", help="Использовать DFS вместо beam.")
    ap.add_argument("--steps-only", action="store_true", help="Только список ходов без покадрового разбора.")
    ap.add_argument("--no-ascii", dest="ascii", action="store_false", help="Отключить ASCII-визуализацию.")
    ap.add_argument("--list", action="store_true", help="Показать уровни в папке levels и выйти.")
    ap.set_defaults(ascii=True)

    args = ap.parse_args()

    if args.list:
        list_levels()
        return

    # Если уровень не указан — спросим интерактивно.
    if not args.level:
        try:
            user = input(f"Файл уровня (Enter для {DEFAULT_LEVEL}): ").strip()
        except KeyboardInterrupt:
            print("\nОтменено.")
            sys.exit(1)
        level_arg = user or str(DEFAULT_LEVEL)
    else:
        level_arg = args.level

    try:
        level_path = find_level(level_arg)
    except FileNotFoundError as e:
        print(e)
        print("Подсказка: используйте --list, чтобы посмотреть доступные уровни.")
        sys.exit(2)

    solve(level_path, use_dfs=args.dfs, steps_only=args.steps_only, ascii_view=args.ascii)


if __name__ == "__main__":
    main()
