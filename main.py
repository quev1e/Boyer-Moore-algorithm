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


def print_colored_matches(string, patterns, case_sensitivity, method, count):
    """Печатает до 10 строк с найденными подстроками,
    выделяя каждую подстроку своим цветом."""

    if not string or not patterns:
        return

    pattern_colors = {
        pattern: ANSI_COLORS[index % len(ANSI_COLORS)]
        for index, pattern in enumerate(patterns)
    }

    # Собираем все позиции для каждого шаблона
    all_matches = []
    for pattern in patterns:
        positions = search_one(string, pattern, case_sensitivity)

        if positions:
            for position in positions:
                all_matches.append((position, pattern))

    if not all_matches:
        return

    # Сортируем по позиции, чтобы корректно собирать строки
    all_matches.sort(key=lambda item: item[0])

    if method == "last" and count is not None:
        all_matches.sort(key=lambda x: x[0], reverse=True)
        all_matches = all_matches[:count]
        all_matches.sort(key=lambda x: x[0])

    if method == "first" and count is not None:
        all_matches = all_matches[:count]

    printed_lines = 0
    line_start = 0

    while line_start < len(string) and printed_lines < MAX_OUTPUT_LINES:
        line_end = string.find("\n", line_start)
        if line_end == -1:
            line_end = len(string)

        line = string[line_start:line_end]

        # Позиции вхождений, относящиеся к текущей строке
        line_matches = [
            (position - line_start, pattern)
            for position, pattern in all_matches
            if line_start <= position < line_end
        ]

        if line_matches:
            colored_line = ""
            cursor = 0

            for relative_position, pattern in line_matches:
                match_end = relative_position + len(pattern)

                if relative_position < cursor:
                    continue

                colored_line += line[cursor:relative_position]
                colored_line += (
                    f"{pattern_colors[pattern]}"
                    f"{line[relative_position:match_end]}"
                    f"{ANSI_RESET}"
                )
                cursor = match_end

            colored_line += line[cursor:]

            print(colored_line)
            printed_lines += 1

        line_start = line_end + 1

    if printed_lines == MAX_OUTPUT_LINES and line_start < len(string):
        print(
            f"\n[Вывод ограничен {MAX_OUTPUT_LINES} строками]",
            file=sys.stderr,
        )


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
