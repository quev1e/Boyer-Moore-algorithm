"""CLI для поиска подстрок в строке или файле."""

import argparse
import sys
from search import search, search_one

def build_parser():
    """Парсер для CLI"""
    parser = argparse.ArgumentParser(
        prog="search-cli",
        description="Поиск подстроки в строке"
    )

    src = parser.add_mutually_exclusive_group(
        required=True
    )
    src.add_argument(
        "-s", "--string",
        help="Строка для поиска",
        nargs="?",
        default=None,
        const="",
    )
    src.add_argument(
        "-f", "--file",
        help="Путь до файла",
    )

    parser.add_argument(
        "-p", "--pattern",
        help="Шаблон(ы) поиска",
        nargs="*",
        default=[],
    )
    parser.add_argument(
        "-i", "--ignore_case",
        help="Игнорировать регистр",
        action="store_true"
    )
    parser.add_argument(
        "-m", "--method",
        help="Метод поиска",
        default="first",
        choices=["first", "last"]
    )
    parser.add_argument(
        "-k", "--count",
        help="Количество выведенных результатов",
        type=int,
    )
    parser.add_argument(
        "-c", "--color",
        help="Строка с выделенными вхождениями",
        action="store_true"
    )

    return parser

def get_text(args, parser):
    """Получает текст исходной строки из ввода
    или файла, иначе выводит ошибки."""

    if args.string is not None:
        return args.string

    if args.file is not None and not args.file:
        parser.error("-f не может быть пустой строкой")

    try:
        with open(args.file, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        parser.error(f"файл не найден: {args.file}")
    except PermissionError:
        parser.error(f"нет прав на чтение файла: {args.file}")
    except IsADirectoryError:
        parser.error(f"это каталог, а не файл: {args.file}")
    except UnicodeDecodeError as e:
        parser.error(f"не удалось прочитать файл как UTF-8: {e}")
    except OSError as e:
        parser.error(f"ошибка чтения файла {args.file}: {e}")
    return None



ANSI_COLORS = [
    "\033[91m",  # красный
    "\033[92m",  # зелёный
    "\033[93m",  # жёлтый
    "\033[94m",  # синий
    "\033[95m",  # пурпурный
    "\033[96m",  # голубой
]

ANSI_RESET = "\033[0m"
MAX_OUTPUT_LINES = 10


def print_colored_matches(
    string: str,
    patterns: str | list[str] | tuple[str, ...],
    case_sensitivity: bool = True,
    method: str = 'first',
    count: int | None = None
    ) -> None:
    """Печатает до 10 строк с найденными подстроками,
    выделяя каждую подстроку своим цветом."""
    if not string or not patterns:
        return

    colors = {
        p: ANSI_COLORS[i % len(ANSI_COLORS)]
        for i, p in enumerate(patterns)
    }

    matches = sorted(
        (pos, p)
        for p in patterns
        for pos in (search_one(string, p, case_sensitivity) or ())
    )
    if method == "last":
        matches.reverse()
    if count is not None:
        matches = matches[:count]
    matches.sort()

    printed = 0
    offset = 0
    for line in string.split("\n"):
        marks = [(pos - offset, p) for pos, p in matches if offset <= pos < offset + len(line)]
        if marks:
            out, cursor = [], 0
            for rel, p in marks:
                if rel < cursor:
                    continue
                out += [
                    line[cursor:rel],
                    colors[p],
                    line[rel:rel + len(p)],
                    ANSI_RESET,
                ]
                cursor = rel + len(p)
            out.append(line[cursor:])
            print("".join(out))
            printed += 1
            if printed >= MAX_OUTPUT_LINES:
                print(
                    f"\n[Вывод ограничен {MAX_OUTPUT_LINES} строками]",
                    file=sys.stderr,
                )
                break
        offset += len(line) + 1


def main(argv=None):
    """CLI"""
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.count is not None and args.count <= 0:
        parser.error("--count должен быть положительным числом")

    string = get_text(args, parser)

    case_sensitivity = not args.ignore_case

    pattern = tuple(args.pattern)

    if not string or not pattern:
        print("Не найдено вхождений")
        return 0

    result = search(
        string,
        pattern,
        case_sensitivity,
        args.method,
        args.count
    )
    if result:
        print(result)

        if args.color:
            print_colored_matches(
                string,
                pattern,
                case_sensitivity,
                args.method,
                args.count
            )

    else:
        print("Не найдено вхождений")
    return 0

if __name__ == "__main__":
    sys.exit(main())
