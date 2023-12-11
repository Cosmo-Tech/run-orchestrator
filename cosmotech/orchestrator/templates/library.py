import importlib
import os
import pathlib
import pkgutil
import pprint
import sys
from typing import Optional

import cosmotech.orchestrator_plugins
from cosmotech.orchestrator.core.command_template import CommandTemplate
from cosmotech.orchestrator.templates.plugin import Plugin
from cosmotech.orchestrator.utils.logger import LOGGER


class Library:
    __instance = None
    __templates = None
    __plugins = None

    def display_library(self, log_function=LOGGER.info, verbose=False):
        log_function("Library content:")
        for _plugin_name, _plugin in self.__plugins.items():
            log_function(f"Templates from '{_plugin_name}':")
            for _template in _plugin.templates.values():
                if _template in self.__templates.values():
                    self.display_template(_template, log_function=log_function, verbose=verbose)
                else:
                    log_function(f"- '{_template.id}': [red]OVERRIDEN[/]")

    @staticmethod
    def display_template(template, log_function=LOGGER.info, verbose=False):
        if verbose:
            log_function(pprint.pformat(template, width=os.get_terminal_size().columns))
        else:
            _desc = f": '{template.description}'" if template.description else ""
            log_function(f"- '{template.id}'{_desc}")

    def display_template_by_id(self, template_id, log_function=LOGGER.info, verbose=False):
        tpl = self.find_template_by_name(template_id=template_id)
        if tpl is None:
            log_function(f"{template_id} is not a valid template id")
            return
        self.display_template(tpl, log_function=LOGGER.info, verbose=verbose)

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

        for finder, name, _ in pkgutil.iter_modules(cosmotech.orchestrator_plugins.__path__,
                                                    cosmotech.orchestrator_plugins.__name__ + "."):
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
