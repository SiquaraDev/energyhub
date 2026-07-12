"""Pacote de configuração da aplicação.

Reexporta a API estável de configuração para manter `from energyhub.config import settings`.
"""

from energyhub.config.settings import Settings, get_settings, settings

__all__ = ["Settings", "get_settings", "settings"]
