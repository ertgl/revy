import sys
from typing import (
    Optional,
    Sequence,
)

from revy._argparse import ArgumentParser


def main(
    argv: Optional[Sequence[str]] = None,
) -> int:
    argv = argv or sys.argv
    arg_parser = ArgumentParser()
    arg_parser.parse_known_args(argv)
    return 0


if __name__ == '__main__':
    status_code = main(argv=sys.argv)
    sys.exit(status_code)
