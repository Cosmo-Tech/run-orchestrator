import importlib
import os
import pathlib
import pkgutil
import sys
from typing import Optional

import cosmotech.orchestrator_templates
from cosmotech.orchestrator.core.command_template import CommandTemplate
from cosmotech.orchestrator.templates.plugin import Plugin
from cosmotech.orchestrator.utils.logger import LOGGER


class Library:
    __instance = None
    __templates = None

    @property
    def templates(self) -> list[CommandTemplate]:
        return list(sorted(self.__templates.values(), key=lambda t: t.sourcePlugin))

    def find_template_by_name(self, template_id) -> Optional[CommandTemplate]:
        return self.__templates.get(template_id)

    def reload(self):
        """
        Allow a reload of the template library,
        should only be used after the content of `sys.path` got changed to check for any new template
        """
        if self.__templates:
            LOGGER.debug("Reloading template library")
        else:
            LOGGER.debug("Loading template library")
        self.__templates = dict()

        for finder, name, _ in pkgutil.iter_modules(cosmotech.orchestrator_templates.__path__,
                                                    cosmotech.orchestrator_templates.__name__ + "."):
            _mod = importlib.import_module(name)
            if "plugin" in _mod.__dict__:
                _plug: Plugin = _mod.plugin
                if isinstance(_plug, Plugin):
                    LOGGER.debug(f"Found plugin {_plug.name}")
                    loaded_templates_from_file = _plug.load_folder(pathlib.Path(_mod.__path__[0]))
                    if loaded_templates_from_file:
                        LOGGER.debug(f" - Loaded {loaded_templates_from_file} templates from plugin files")
                    LOGGER.debug(f" - Plugin contains {len(_plug.templates.values())} templates")
                    self.__templates.update(_plug.templates)

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            if os.getcwd() not in sys.path:
                sys.path.append(os.getcwd())
            cls.__instance = object.__new__(cls)
            cls.__instance.reload()
        return cls.__instance
