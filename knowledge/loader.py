from pathlib import Path

from ..core.constants import KNOWLEDGE_CHARS_PER_FILE, KNOWLEDGE_FILE_LIMIT


EXCLUDED_DIRS = {".git", ".next", "dist", "node_modules", "target"}
SOURCE_PATTERNS = ("*.rs", "*.ts", "*.tsx", "*.js", "*.jsx", "*.py", "*.md", "*.txt")


def load_project_knowledge(paths: tuple[Path, ...]) -> str:
    snippets: list[str] = []

    for file_path in _iter_source_files(paths):
        try:
            content = file_path.read_text(encoding="utf-8")[:KNOWLEDGE_CHARS_PER_FILE]
        except UnicodeDecodeError:
            continue
        except OSError:
            continue

        snippets.append(f"\n--- {file_path.as_posix()} ---\n{content}\n")
        if len(snippets) >= KNOWLEDGE_FILE_LIMIT:
            break

    return "".join(snippets)


def _iter_source_files(paths: tuple[Path, ...]):
    files: list[Path] = []

    for source_path in paths:
        if source_path.is_file():
            files.append(source_path)
            continue

        if not source_path.exists() or not source_path.is_dir():
            continue

        for pattern in SOURCE_PATTERNS:
            files.extend(source_path.rglob(pattern))

    for file_path in sorted(files):
        if any(part in EXCLUDED_DIRS for part in file_path.parts):
            continue
        yield file_path
