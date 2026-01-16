# RAG_Sql/utils/config_loader.py

from pathlib import Path
import os
import yaml

_CONFIG_CACHE = None


def _resolve_env(value):
    """
    Recursively resolve ${ENV_VAR} expressions inside YAML values.
    """
    if isinstance(value, str):
        # simple ${VAR} pattern
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
    Loads YAML config from project_root/config/config.yaml
    and resolves environment variables like ${VAR_NAME}.
    """
    global _CONFIG_CACHE
    if _CONFIG_CACHE is not None:
        return _CONFIG_CACHE

    # Calculate project root relative to this file
    project_root = Path(__file__).resolve().parents[2]
    config_path = project_root / "config" / "config.yaml"

    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with config_path.open("r", encoding="utf-8") as f:
        raw = yaml.safe_load(f) or {}

    # resolve ${VAR_NAME}
    resolved = _resolve_env(raw)

    _CONFIG_CACHE = resolved
    return resolved
