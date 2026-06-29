import re
from pathlib import Path

from ..core.constants import KNOWLEDGE_CHARS_PER_FILE, KNOWLEDGE_FILE_LIMIT
from ..core.types import ProjectUnderstanding, SystemConcept
from .system_translator import detect_system_concepts, format_system_summary


EXCLUDED_DIRS = {".git", ".next", "dist", "node_modules", "target"}
SOURCE_PATTERNS = ("*.rs", "*.ts", "*.tsx", "*.js", "*.jsx", "*.py", "*.md", "*.txt")

# File patterns that likely contain purpose/reasoning
WHY_PATTERNS = (
    "README*",
    "*.md",
    "*.txt",
    "CHANGELOG*",
    "ARCHITECTURE*",
    "DESIGN*",
    "DOC*",
    "*.rst",
)


def load_project_knowledge(paths: tuple[Path, ...]) -> str:
    """Load raw project knowledge from source files."""
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


def load_project_understanding(paths: tuple[Path, ...]) -> ProjectUnderstanding:
    """Load and process project knowledge into a structured understanding.

    This combines raw knowledge with system-level translations and purpose extractions.
    """
    raw_knowledge = load_project_knowledge(paths)

    # Detect system concepts from implementation
    system_results = detect_system_concepts(raw_knowledge)
    system_concepts = [result.concept for result in system_results]

    # Extract "why" statements from documentation
    purpose_extractions = extract_purpose_from_docs(paths)

    # Generate system summary for context
    system_summary = format_system_summary(system_results)

    # Combine raw knowledge with system summary
    enhanced_knowledge = f"{raw_knowledge}\n\n## System-Level Understanding\n\n{system_summary}"

    return ProjectUnderstanding(
        system_concepts=system_concepts,
        purpose_extractions=purpose_extractions,
        analogies=[],  # Analogies are selected based on audience during generation
        raw_knowledge=enhanced_knowledge,
    )


def extract_purpose_from_docs(paths: tuple[Path, ...]) -> list[str]:
    """Extract purpose statements from documentation files.

    Looks for:
    - README files
    - Design documents
    - Architecture notes
    - Docstrings
    - Comments explaining WHY
    """
    purposes: list[str] = []

    for file_path in _iter_doc_files(paths):
        try:
            content = file_path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue

        # Extract purpose from file name if it's a doc file
        file_purposes = _extract_from_content(content, file_path.name)
        purposes.extend(file_purposes)

    return purposes[:20]  # Limit to most relevant


def _extract_from_content(content: str, source_name: str) -> list[str]:
    """Extract purpose/reasoning statements from content.
    
    Extracts categorized statements for:
    - purpose: why something exists
    - protection: what it protects against
    - tradeoff: design compromises made
    - risk: potential failure scenarios
    """
    purposes: list[str] = []

    # Patterns for PURPOSE (why something exists)
    purpose_patterns = [
        r"(?i)(?:purpose|goal|objective)\s*[:\-]\s*([^\n.]{15,200})",
        r"(?i)(?:designed to|built to|meant to|intended to|created to)\s+([^\n.]{20,200})",
        r"(?i)(?:why|because|reason)\s*[:\-]\s*([^\n.]{15,200})",
        r"(?i)the\s+(?:goal|point|idea|reason)\s+is\s+([^\n.]{20,200})",
    ]

    # Patterns for PROTECTION (what it protects)
    protection_patterns = [
        r"(?i)(?:protects?|safeguards?|secures?)\s+([^\n.]{20,200})",
        r"(?i)(?:prevents?|stops?|blocks?|blocks?)\s+([^\n.]{20,200})",
        r"(?i)(?:ensures?|guarantees?|makes sure)\s+([^\n.]{20,200})",
        r"(?i)(?:defends?|shields?|guards?)\s+([^\n.]{20,200})",
    ]

    # Patterns for TRADEOFF (design compromises)
    tradeoff_patterns = [
        r"(?i)(?:trade-?off|compromise|balance|tradeoff)\s*[:\-]\s*([^\n.]{15,200})",
        r"(?i)(?:instead of|rather than|over)\s+([^\n.]{20,200})",
        r"(?i)we\s+(?:chose|selected|prefer|opted)\s+([^\n.]{20,200})",
        r"(?i)(?:sacrificed?|exchanged?|traded?)\s+([^\n.]{20,200})",
    ]

    # Patterns for RISK/FAILURE (what could go wrong)
    risk_patterns = [
        r"(?i)(?:risk|hazard|danger|threat|vulnerability)\s*[:\-]\s*([^\n.]{15,200})",
        r"(?i)(?:without|if|when)\s+([^\n.]{20,200})\s+(?:would|could|may|might)\s+([^\n.]{10,100})",
        r"(?i)(?:attack|exploit|breach|failure)\s+([^\n.]{20,200})",
        r"(?i)if\s+this\s+(?:check|validation|verification)\s+(?:fails?|breaks?)([^\n.]{10,100})",
    ]

    # Combine all patterns with categories
    all_patterns = [
        ("purpose", purpose_patterns),
        ("protection", protection_patterns),
        ("tradeoff", tradeoff_patterns),
        ("risk", risk_patterns),
    ]

    for category, patterns in all_patterns:
        for pattern in patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                # Handle multiple capture groups
                if isinstance(match, tuple):
                    match = " ".join(m for m in match if m)
                cleaned = str(match).strip()
                if len(cleaned) > 15 and len(cleaned) < 300:
                    purposes.append(f"[{category}] {cleaned}")

    # Look for TODO/FIXME with reasoning
    todo_pattern = r"(?:TODO|FIXME|HACK|NOTE)[:\s]+([^\n]{20,200})"
    todos = re.findall(todo_pattern, content)
    for todo in todos:
        if any(reason_word in todo.lower() for reason_word in ["why", "because", "reason", "security", "protect", "risk", "fail"]):
            purposes.append(f"[todo] {todo.strip()}")

    return purposes


def _iter_source_files(paths: tuple[Path, ...]):
    """Iterate over source code files."""
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


def _iter_doc_files(paths: tuple[Path, ...]):
    """Iterate over documentation files that may contain purpose/reasoning."""
    files: list[Path] = []

    for source_path in paths:
        if source_path.is_file() and _is_doc_file(source_path.name):
            files.append(source_path)
            continue

        if not source_path.exists() or not source_path.is_dir():
            continue

        for pattern in WHY_PATTERNS:
            files.extend(source_path.rglob(pattern))

    for file_path in sorted(files):
        if any(part in EXCLUDED_DIRS for part in file_path.parts):
            continue
        yield file_path


def _is_doc_file(filename: str) -> bool:
    """Check if a filename indicates a documentation file."""
    doc_extensions = {".md", ".txt", ".rst", ".adoc"}
    doc_names = {"readme", "changelog", "architecture", "design", "docs", "doc"}

    name_lower = filename.lower()
    if any(name_lower.startswith(doc) for doc in doc_names):
        return True
    if any(name_lower.endswith(ext) for ext in doc_extensions):
        return True
    return False
