"""CLI для поиска подстрок в строке или файле."""

import argparse
import sys
from search import search

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
        help="Количество выведенных результатов (по умолчанию 10)",
        default=10,
        type=int,
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
    else:
        print("Не найдено вхождений")
    return 0

if __name__ == "__main__":
    sys.exit(main())
