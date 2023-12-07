import importlib
import os
import pathlib
import pkgutil
import sys
from typing import Optional
import pprint

import cosmotech.orchestrator_templates
from cosmotech.orchestrator.core.command_template import CommandTemplate
from cosmotech.orchestrator.templates.plugin import Plugin
from cosmotech.orchestrator.utils.logger import LOGGER


class Library:
    __instance = None
    __templates = None
    __plugins = None

    def display_library(self, log_function=LOGGER.info, verbose=False):
        current_plugin = None
        for _template in self.templates:
            if _template.sourcePlugin != current_plugin:
                current_plugin = _template.sourcePlugin
                log_function(f"Templates from '{current_plugin}':")
            self.display_template(_template.id, log_function=log_function, verbose=verbose)

    def display_template(self, template_id, log_function=LOGGER.info, verbose=False):
        tpl = self.find_template_by_name(template_id=template_id)
        if tpl is None:
            log_function(f"{template_id} is not a valid template id")
            return
        if verbose:
            log_function(pprint.pformat(tpl, width=os.get_terminal_size().columns))
        else:
            _desc = f": '{tpl.description}'" if tpl.description else ""
            log_function(f"- '{tpl.id}'{_desc}")

    @property
    def templates(self) -> list[CommandTemplate]:
        return list(sorted(self.__templates.values(), key=lambda t: t.sourcePlugin))

    def find_template_by_name(self, template_id) -> Optional[CommandTemplate]:
        return self.__templates.get(template_id)

    def load_plugin(self, plugin: Plugin, plugin_module: Optional = None):
        LOGGER.debug(f"Loading plugin {plugin.name}")
        if plugin_module is not None:
            loaded_templates_from_file = plugin.load_folder(pathlib.Path(plugin_module.__path__[0]))
            if loaded_templates_from_file:
                LOGGER.debug(f" - Loaded {loaded_templates_from_file} templates from plugin files")
        LOGGER.debug(f" - Plugin contains {len(plugin.templates.values())} templates")
        self.__templates.update(plugin.templates)
        self.__plugins[plugin.name] = plugin

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
        self.__plugins = dict()

        for finder, name, _ in pkgutil.iter_modules(cosmotech.orchestrator_templates.__path__,
                                                    cosmotech.orchestrator_templates.__name__ + "."):
            _mod = importlib.import_module(name)
            if "plugin" in _mod.__dict__:
                _plug: Plugin = _mod.plugin
                if isinstance(_plug, Plugin):
                    self.load_plugin(_plug, plugin_module=_mod)

    def add_template(self, template: CommandTemplate, override: bool = False):
        if override or template.id not in self.__templates:
            self.__templates[template.id] = template

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            if os.getcwd() not in sys.path:
                sys.path.append(os.getcwd())
            cls.__instance = object.__new__(cls)
            cls.__instance.reload()
        return cls.__instance
