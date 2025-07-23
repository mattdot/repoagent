import os
import sys


def get_env_var(
    name: str,
    required: bool = True,
    cast_func: callable = None,
    default=None,
    error_message: str = None,
) -> any:
    """
    Retrieve and validate an environment variable, with optional type casting and default value.

    Args:
        name (str): Environment variable name.
        required (bool): Whether the variable is required. Defaults to True.
        cast_func (callable, optional): Function to cast the value. Defaults to None.
        default: Default value if variable is not set. Defaults to None.
        error_message (str, optional): Custom error message if variable is missing. Defaults to None.

    Returns:
        any: The environment variable value, possibly casted.

    Raises:
        SystemExit: If required variable is missing or casting fails.
    """
    value = os.getenv(name, default)
    if required and (value is None or value == ""):
        msg = error_message or f"Error: Missing required environment variable: {name}"
        print(msg, file=sys.stderr)
        sys.exit(1)
    if cast_func and value is not None:
        try:
            value = cast_func(value)
        except Exception as e:
            print(
                f"Error: Could not cast {name} to required type: {e}", file=sys.stderr
            )
            sys.exit(1)
    return value
