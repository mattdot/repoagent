import os

from typing import Callable, Any, Optional


def get_env_var(
    key: str,
    default: Any = None,
    cast_func: Optional[Callable[[str], Any]] = None,
    required: bool = True,
) -> Any:
    """
    Retrieve an environment variable with optional casting and default value management.

    Args:
        key (str): The environment variable name.
        default (Any, optional): Default value if variable is not set. Defaults to None.
        cast_func (Callable[[str], Any], optional): Function to cast the value. Defaults to None.
        required (bool, optional): Whether the variable is required. Defaults to True.

    Returns:
        Any: The value of the environment variable, cast if specified.

    Raises:
        ValueError: If required variable is missing or casting fails.
    """
    val = os.getenv(key)
    if val is None or val == "":
        if required:
            raise ValueError(f"Missing required environment variable: {key}")
        return default
    if cast_func:
        try:
            return cast_func(val)
        except Exception:
            raise ValueError(
                f"Invalid value for environment variable '{key}': could not cast '{val}'"
            )
    return val
