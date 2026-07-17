"""Expose the bundled LuckMail SDK when running from the repository root.

The dependency directory and the SDK's import package are both named
``luckmail``. Without this file, Python treats the outer directory as a
namespace package and shadows the editable installation.
"""

from .luckmail import LuckMailClient

__all__ = ["LuckMailClient"]
