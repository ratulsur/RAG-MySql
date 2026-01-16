from pathlib import Path
import os
import yaml

_CONFIG_CACHE = None


def _resolve_env(value):
    """
    Recursively resolve ${ENV_VAR} expressions inside YAML values.
    """
    if isinstance(value, str):
        if value.startswith("${") and value.endswith("}"):
            env_var = value[2:-1]
            return os.getenv(env_var, "")
        return value

    if isinstance(value, dict):
        return {k: _resolve_env(v) for k, v in value.items()}

    if isinstance(value, list):
        return [_resolve_env(v) for v in value]

    return value


def load_config():
    """
    Loads config from PROJECT_ROOT/config/config.yaml

    This file lives in: app/rag/utils/config_loader.py
    So we need to go up 3 levels:
        utils -> rag -> app -> PROJECT_ROOT
    """
    global _CONFIG_CACHE
    if _CONFIG_CACHE is not None:
        return _CONFIG_CACHE

    # Go up to the project root (E:\Training\RAG-MySql)
    project_root = Path(__file__).resolve().parents[3]
    config_path = project_root / "config" / "config.yaml"

    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with config_path.open("r", encoding="utf-8") as f:
        raw = yaml.safe_load(f) or {}

    resolved = _resolve_env(raw)
    _CONFIG_CACHE = resolved
    return resolved
