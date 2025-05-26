# Copyright (C) - 2023 - 2025 - Cosmo Tech
# This document and all information contained herein is the exclusive property -
# including all intellectual property rights pertaining thereto - of Cosmo Tech.
# Any use, reproduction, translation, broadcasting, transmission, distribution,
# etc., to any person is prohibited unless it has been previously and
# specifically authorized by written means by Cosmo Tech.

import importlib
import os
import pathlib
import pkgutil
import pprint
from typing import Optional

import sys

import cosmotech.orchestrator_plugins
from cosmotech.orchestrator.core.command_template import CommandTemplate
from cosmotech.orchestrator.templates.plugin import Plugin
from cosmotech.orchestrator.utils.logger import LOGGER
from cosmotech.orchestrator.utils.translate import T


class Library:
    __instance = None
    __templates = None
    __plugins = None
    __exit_templates = None

    def display_library(self, log_function=LOGGER.info, verbose=False):
        log_function(T("csm-orc.orchestrator.library.content"))
        for _plugin_name, _plugin in self.__plugins.items():
            log_function(T("csm-orc.orchestrator.library.templates_from").format(plugin_name=_plugin_name))
            for _template in _plugin.templates.values():
                if _template in self.__templates.values():
                    self.display_template(_template, log_function=log_function, verbose=verbose)
                else:
                    log_function(T("csm-orc.orchestrator.library.template_overriden").format(template_id=_template.id))

    @staticmethod
    def display_template(template, log_function=LOGGER.info, verbose=False):
        if verbose:
            log_function(
                T("csm-orc.orchestrator.library.template_info").format(
                    template=pprint.pformat(template, width=os.get_terminal_size().columns)
                )
            )
        else:
            _desc = f": '{template.description}'" if template.description else ""
            log_function(T("csm-orc.orchestrator.library.template_desc").format(id=template.id, description=_desc))

    def display_template_by_id(self, template_id, log_function=LOGGER.info, verbose=False):
        tpl = self.find_template_by_name(template_id=template_id)
        if tpl is None:
            log_function(T("csm-orc.orchestrator.library.template_invalid").format(template_id=template_id))
            return
        self.display_template(tpl, log_function=LOGGER.info, verbose=verbose)

    @property
    def templates(self) -> list[CommandTemplate]:
        return list(sorted(self.__templates.values(), key=lambda t: t.sourcePlugin))

    def find_template_by_name(self, template_id) -> Optional[CommandTemplate]:
        return self.__templates.get(template_id)

    def load_plugin(self, plugin: Plugin, plugin_module: Optional = None):
        LOGGER.debug(T("csm-orc.orchestrator.library.plugin.loading").format(name=plugin.name))
        if plugin_module is not None:
            loaded_templates_from_file = plugin.load_folder(pathlib.Path(plugin_module.__path__[0]))
            if loaded_templates_from_file:
                LOGGER.debug(
                    T("csm-orc.orchestrator.library.plugin.loaded_templates").format(count=loaded_templates_from_file)
                )
        LOGGER.debug(
            T("csm-orc.orchestrator.library.plugin.template_count").format(count=len(plugin.templates.values()))
        )
        self.__templates.update(plugin.templates)
        for command in plugin.exit_commands:
            if command not in self.__exit_templates:
                self.__exit_templates.append(command)
        self.__plugins[plugin.name] = plugin

    def reload(self):
        """
        Allow a reload of the template library,
        should only be used after the content of `sys.path` got changed to check for any new template
        """
        if self.__templates:
            LOGGER.debug(T("csm-orc.orchestrator.library.reloading"))
        else:
            LOGGER.debug(T("csm-orc.orchestrator.library.loading"))
        self.__templates = dict()
        self.__plugins = dict()
        self.__exit_templates = list()

        for finder, name, _ in pkgutil.iter_modules(
            cosmotech.orchestrator_plugins.__path__, cosmotech.orchestrator_plugins.__name__ + "."
        ):
            _mod = importlib.import_module(name)
            if "plugin" in _mod.__dict__:
                _plug: Plugin = _mod.plugin
                if isinstance(_plug, Plugin):
                    self.load_plugin(_plug, plugin_module=_mod)

    def add_template(self, template: CommandTemplate, override: bool = False):
        if override or template.id not in self.__templates:
            self.__templates[template.id] = template

    def list_exit_commands(self) -> list[str]:
        return self.__exit_templates

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            if os.getcwd() not in sys.path:
                sys.path.append(os.getcwd())
            cls.__instance = object.__new__(cls)
            cls.__instance.reload()
        return cls.__instance
