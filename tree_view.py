#!/usr/bin/env python3
"""
tree_view.py — универсальный скрипт для печати структуры проекта.
Запуск:
    python tree_view.py [PATH] [-e PATTERN ...] [-d MAX_DEPTH]
"""
from __future__ import annotations
import argparse
import fnmatch
import os
from pathlib import Path
from typing import Iterable, List

# ================== НАСТРОЙКИ ==================
# Список папок и файлов для исключения (можно добавлять свои)
DEFAULT_EXCLUDE_PATTERNS = [
    "__pycache__",      # Кеш Python
    "*.pyc",            # Скомпилированные Python файлы
    "*.pyo",            # Оптимизированные Python файлы
    ".git",             # Git репозиторий
    ".gitignore",       # Git игнор файл
    "node_modules",     # Node.js зависимости
    ".env",             # Файлы окружения
    "*.log",            # Лог файлы
    ".vscode",          # VS Code настройки
    ".idea",            # PyCharm/IntelliJ настройки
    "*.tmp",            # Временные файлы
    "*.cache",          # Файлы кеша
    ".DS_Store",        # macOS системные файлы
    "LOGS",          # Логи приложения
    "tests",            # Тестовые директории
    "DOCS",             # Документация
    "dejavu-sans"
]

# Максимальная глубина по умолчанию (-1 = без ограничений)
DEFAULT_MAX_DEPTH = 3
# ===============================================


def parse_args() -> argparse.Namespace:
    """Парсит аргументы командной строки."""
    parser = argparse.ArgumentParser(description="Print directory tree")
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Корень проекта (default: текущая директория)",
    )
    parser.add_argument(
        "-e",
        "--exclude",
        action="append",
        default=[],
        metavar="PATTERN",
        help="Дополнительная glob-маска для исключения",
    )
    parser.add_argument(
        "-d",
        "--max-depth",
        type=int,
        default=DEFAULT_MAX_DEPTH,
        metavar="N",
        help=f"Максимальная глубина (default: {DEFAULT_MAX_DEPTH}, -1 = без ограничений)",
    )
    return parser.parse_args()


def should_exclude(name: str, patterns: Iterable[str]) -> bool:
    """Проверяет, подходит ли имя под одну из масок исключения."""
    return any(fnmatch.fnmatch(name, p) for p in patterns)


def build_tree(
    root: Path,
    prefix: str,
    exclude: List[str],
    level: int,
    max_depth: int,
) -> None:
    """Рекурсивно печатает дерево, соблюдая ограничения."""
    if max_depth >= 0 and level > max_depth:
        return
    
    # Отфильтровываем и сортируем: папки сначала, затем файлы (алфавитно)
    children = [
        child
        for child in sorted(root.iterdir(), key=lambda p: (p.is_file(), p.name.lower()))
        if not should_exclude(child.name, exclude)
    ]
    
    for index, child in enumerate(children):
        connector = "└── " if index == len(children) - 1 else "├── "
        print(f"{prefix}{connector}{child.name}")
        
        if child.is_dir():
            extension = "    " if index == len(children) - 1 else "│   "
            build_tree(child, prefix + extension, exclude, level + 1, max_depth)


def main() -> None:
    """Главная функция программы."""
    args = parse_args()
    root_path = Path(args.path).resolve()
    
    if not root_path.exists():
        raise FileNotFoundError(f"Путь '{root_path}' не существует")
    
    # Объединяем настройки по умолчанию с аргументами командной строки
    all_exclude_patterns = DEFAULT_EXCLUDE_PATTERNS + args.exclude
    
    print(f"{root_path.name}/")
    build_tree(
        root=root_path,
        prefix="",
        exclude=all_exclude_patterns,
        level=0,
        max_depth=args.max_depth,
    )


if __name__ == "__main__":
    main()