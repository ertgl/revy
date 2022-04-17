from typing import List

from _core import DOCS_SOURCE_DIR_PATH


FILE_PATH = DOCS_SOURCE_DIR_PATH / 'api' / 'modules.rst'


def main() -> None:
    lines: List[str]
    with open(FILE_PATH, 'r') as f:
        lines = f.readlines()
    lines[0] = 'API Reference\n'
    lines[1] = f'{"=" * (len(lines[0]) - 1)}\n'
    with open(FILE_PATH, 'w') as f:
        f.writelines(lines)


if __name__ == '__main__':
    main()
