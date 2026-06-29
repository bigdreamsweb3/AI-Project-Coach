import os
from pathlib import Path

from .constants import (
    ANTHROPIC_MODEL_ENV,
    ANSWER_MAX_TOKENS,
    ANSWER_MAX_TOKENS_ENV,
    DEFAULT_ANTHROPIC_MODEL,
    DEFAULT_GEMINI_MODEL,
    GEMINI_MODEL_ENV,
    LIVE_CONTEXT_CHARS,
    LIVE_CONTEXT_CHARS_ENV,
    LIVE_DRAFT_MAX_TOKENS,
    LIVE_DRAFT_MAX_TOKENS_ENV,
    LIVE_REGENERATE_AFTER_CHARS,
    LIVE_REGENERATE_AFTER_CHARS_ENV,
    LIVE_WINDOW_ALPHA,
    LIVE_WINDOW_ALPHA_ENV,
    MIN_ANSWER_KEY_TERMS,
    MIN_ANSWER_KEY_TERMS_ENV,
    MIN_ANSWER_WORDS,
    MIN_ANSWER_WORDS_ENV,
    OBSERVATION_LOG_PATH,
    OBSERVATION_LOG_PATH_ENV,
    PRACTICE_CONTEXT_CHARS,
    PRACTICE_CONTEXT_CHARS_ENV,
    PRACTICE_MODEL_ANSWER_ENV,
    PROJECT_NAME_ENV,
    PROVIDER_ORDER_ENV,
    QUESTION_MAX_TOKENS,
    QUESTION_MAX_TOKENS_ENV,
    RULES_PATH,
    RULES_PATH_ENV,
    RULE_PROPOSALS_PATH,
    RULE_PROPOSALS_PATH_ENV,
    SPEAKER_NAME_ENV,
    SOURCE_PATHS_ENV,
)
from .types import CoachConfig


APP_DIR = Path(__file__).resolve().parents[1]
APP_ENV_PATH = APP_DIR / ".env"


def load_env_file(env_path: Path = APP_ENV_PATH) -> None:
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def build_config() -> CoachConfig:
    load_env_file()
    source_paths = parse_source_paths(os.getenv(SOURCE_PATHS_ENV))
    rules_path = parse_path(os.getenv(RULES_PATH_ENV), RULES_PATH)
    project_name = os.getenv(PROJECT_NAME_ENV, source_paths[0].stem if source_paths else Path.cwd().name)

    return CoachConfig(
        anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
        gemini_api_key=os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"),
        anthropic_model=os.getenv(ANTHROPIC_MODEL_ENV, DEFAULT_ANTHROPIC_MODEL),
        gemini_model=os.getenv(GEMINI_MODEL_ENV, DEFAULT_GEMINI_MODEL),
        project_name=project_name,
        speaker_name=os.getenv(SPEAKER_NAME_ENV, "the project builder"),
        source_paths=source_paths,
        rules_path=rules_path,
        project_rules=load_project_rules(rules_path),
        provider_order=parse_provider_order(os.getenv(PROVIDER_ORDER_ENV)),
        practice_model_answer_enabled=parse_bool(os.getenv(PRACTICE_MODEL_ANSWER_ENV), default=False),
        question_max_tokens=parse_int(os.getenv(QUESTION_MAX_TOKENS_ENV), QUESTION_MAX_TOKENS, minimum=40, maximum=300),
        answer_max_tokens=parse_int(os.getenv(ANSWER_MAX_TOKENS_ENV), ANSWER_MAX_TOKENS, minimum=80, maximum=700),
        live_draft_max_tokens=parse_int(os.getenv(LIVE_DRAFT_MAX_TOKENS_ENV), LIVE_DRAFT_MAX_TOKENS, minimum=80, maximum=500),
        practice_context_chars=parse_int(os.getenv(PRACTICE_CONTEXT_CHARS_ENV), PRACTICE_CONTEXT_CHARS, minimum=1000, maximum=12000),
        live_context_chars=parse_int(os.getenv(LIVE_CONTEXT_CHARS_ENV), LIVE_CONTEXT_CHARS, minimum=1000, maximum=12000),
        live_regenerate_after_chars=parse_int(
            os.getenv(LIVE_REGENERATE_AFTER_CHARS_ENV),
            LIVE_REGENERATE_AFTER_CHARS,
            minimum=40,
            maximum=1000,
        ),
        live_window_alpha=parse_float(
            os.getenv(LIVE_WINDOW_ALPHA_ENV),
            LIVE_WINDOW_ALPHA,
            minimum=0.25,
            maximum=1.0,
        ),
        min_answer_words=parse_int(os.getenv(MIN_ANSWER_WORDS_ENV), MIN_ANSWER_WORDS, minimum=4, maximum=80),
        min_answer_key_terms=parse_int(
            os.getenv(MIN_ANSWER_KEY_TERMS_ENV),
            MIN_ANSWER_KEY_TERMS,
            minimum=2,
            maximum=30,
        ),
        observation_log_path=parse_path(os.getenv(OBSERVATION_LOG_PATH_ENV), OBSERVATION_LOG_PATH),
        rule_proposals_path=parse_path(os.getenv(RULE_PROPOSALS_PATH_ENV), RULE_PROPOSALS_PATH),
    )


def parse_source_paths(raw_value: str | None) -> tuple[Path, ...]:
    if not raw_value:
        return (Path.cwd(),)

    paths: list[Path] = []
    for raw_path in raw_value.split(";"):
        cleaned = raw_path.strip().strip('"').strip("'")
        if not cleaned:
            continue

        path = Path(cleaned).expanduser()
        if not path.is_absolute():
            path = (Path.cwd() / path).resolve()
        paths.append(path)

    return tuple(paths) if paths else (Path.cwd(),)


def parse_provider_order(raw_value: str | None) -> tuple[str, ...]:
    if not raw_value:
        return ("gemini", "claude")

    providers: list[str] = []
    for raw_provider in raw_value.split(","):
        provider = raw_provider.strip().lower()
        if provider in {"gemini", "claude"} and provider not in providers:
            providers.append(provider)

    return tuple(providers) if providers else ("gemini", "claude")


def parse_bool(raw_value: str | None, default: bool) -> bool:
    if raw_value is None:
        return default
    return raw_value.strip().lower() in {"1", "true", "yes", "on"}


def parse_int(raw_value: str | None, default: int, minimum: int, maximum: int) -> int:
    if raw_value is None:
        return default

    try:
        value = int(raw_value.strip())
    except ValueError:
        return default

    return max(minimum, min(value, maximum))


def parse_float(raw_value: str | None, default: float, minimum: float, maximum: float) -> float:
    if raw_value is None:
        return default

    try:
        value = float(raw_value.strip())
    except ValueError:
        return default

    return max(minimum, min(value, maximum))


def parse_path(raw_value: str | None, default: str) -> Path:
    cleaned = (raw_value or default).strip().strip('"').strip("'")
    path = Path(cleaned).expanduser()
    if not path.is_absolute():
        path = (Path.cwd() / path).resolve()
    return path


def load_project_rules(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8").strip()
    except OSError:
        return ""


def configuration_help() -> str:
    return (
        "Configure at least one real AI provider before running the coach.\n"
        f"Add the values to {APP_ENV_PATH}.\n"
        f'  $env:{ANTHROPIC_MODEL_ENV}="{DEFAULT_ANTHROPIC_MODEL}"\n'
        f'  $env:{GEMINI_MODEL_ENV}="{DEFAULT_GEMINI_MODEL}"\n'
        f'  $env:{PROJECT_NAME_ENV}="My Project"\n'
        f'  $env:{SPEAKER_NAME_ENV}="my name"\n'
        f'  $env:{SOURCE_PATHS_ENV}="C:\\path\\to\\project;C:\\path\\to\\project-brief.md"'
    )
