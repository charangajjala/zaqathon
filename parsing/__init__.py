"""Parsing module for email processing."""

from .email_data import EmailData
from .email_parser import LangChainEmailParser

__all__ = ["LangChainEmailParser", "EmailData"]
