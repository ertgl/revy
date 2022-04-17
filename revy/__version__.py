from typing import Tuple


__all__ = (
    'VersionTuple',
    'Version',
    'version',
    'VERSION',
    '__version__',
)


VersionTuple = Tuple[int, int, int, str, int]


class Version:

    major: int

    minor: int

    micro: int

    segment: str

    build: int

    def __init__(
        self,
        major: int,
        minor: int,
        micro: int,
        segment: str = 'final',
        build: int = 0,
    ) -> None:
        assert segment in ('alpha', 'beta', 'rc', 'final')  # noqa
        assert build >= 0  # noqa
        self.major = major
        self.minor = minor
        self.micro = micro
        self.segment = segment
        self.build = build

    def to_tuple(self) -> VersionTuple:
        return self.major, self.minor, self.micro, self.segment, self.build

    def __str__(self) -> str:
        segment = self.segment if self.segment != 'final' else ''
        build = str(self.build) if self.build > 0 else ''
        return f'{self.major}.{self.minor}.{self.micro}{segment}{build}'


version = Version(1, 0, 0, 'alpha', 12)

VERSION = version.to_tuple()

__version__ = str(version)
