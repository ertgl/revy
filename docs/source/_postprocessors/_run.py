import glob
import os
import subprocess

from _core import DIR_PATH


def main() -> None:
    for python_file_path in glob.glob(str(DIR_PATH / '*.py'), recursive=False):
        if python_file_path.split(os.sep)[-1].startswith('_'):
            continue
        subprocess.call(['python', python_file_path])


if __name__ == '__main__':
    main()
