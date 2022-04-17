import ast
from pathlib import Path
from typing import (
    Optional,
    cast,
)


BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

SWAPPABLE_SAMPLE_DIR = BASE_DIR / 'samples' / 'django' / 'swappable'

INITIAL_MIGRATION_FILE_PATH = SWAPPABLE_SAMPLE_DIR / 'revisions' / 'migrations' / '0001_initial.py'


def main():
    migration_file_content = INITIAL_MIGRATION_FILE_PATH.read_text()
    migration_module = ast.parse(migration_file_content)
    migration_class_def: Optional[ast.ClassDef] = None
    for node in migration_module.body:
        if isinstance(node, ast.ClassDef) and node.name == 'Migration':
            migration_class_def = node
            break
    if migration_class_def is None:
        return
    for node in migration_class_def.body:
        if isinstance(node, ast.Assign):
            name = cast(ast.Name, node.targets[0])
            if name.id == 'replaces':
                return
    replaces_node = ast.Assign(
        lineno=-1,
        targets=[
            ast.Name(
                id='replaces',
                ctx=ast.Store(),
            ),
        ],
        value=ast.List(
            elts=[
                ast.Tuple(
                    elts=[
                        ast.Constant(value='revy'),
                        ast.Constant(value='0001_initial'),
                    ],
                ),
            ],
        ),
    )
    migration_class_def.body.insert(0, replaces_node)
    INITIAL_MIGRATION_FILE_PATH.write_text(
        ast.unparse(migration_module),
    )


if __name__ == '__main__':
    main()
