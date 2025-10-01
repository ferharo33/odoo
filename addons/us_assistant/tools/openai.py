# -*- coding: utf-8 -*-
from importlib import import_module
from importlib.util import find_spec

from odoo.exceptions import UserError
from odoo.tools.translate import _


_OPENAI_MODULE = None


def _load_openai_module():
    """Return the imported ``openai`` module or raise a user friendly error."""
    global _OPENAI_MODULE
    if _OPENAI_MODULE is None:
        if find_spec("openai") is None:
            raise UserError(
                _(
                    "The python package 'openai' is required to use the assistant integration. "
                    "Please install it with: pip install openai"
                )
            )
        _OPENAI_MODULE = import_module("openai")
    return _OPENAI_MODULE


def get_openai_module():
    """Expose the cached ``openai`` module."""
    return _load_openai_module()


def get_openai_client(api_key):
    """Return an OpenAI client for the provided API key."""
    if not api_key:
        raise UserError(_("The API key is missing for the assistant configuration."))
    openai_module = _load_openai_module()
    return openai_module.OpenAI(api_key=api_key)
