import argparse
from typing import Any

from revy.__version__ import __version__


__all__ = (
    'ArgumentParser',
)


class ArgumentParser(argparse.ArgumentParser):

    def __init__(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        kwargs.setdefault('prog', 'revy')
        kwargs.setdefault('description', 'A toolkit for building version control systems.')
        super(ArgumentParser, self).__init__(*args, **kwargs)
        self.add_argument(
            '-v',
            '--version',
            action='version',
            version=f'%(prog)s {__version__}',
        )
