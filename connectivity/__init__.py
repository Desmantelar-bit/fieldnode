"""Transport selection for the FieldNode edge outbox.

The package deliberately knows nothing about a physical radio.  Providers are
small adapters around transports that already exist in the repository.
"""

from .base import ConnectivityProvider
from .manager import ConnectivityManager

__all__ = ["ConnectivityManager", "ConnectivityProvider"]
