from cosmotech.orchestrator.core.command_template import CommandTemplate
import json
import pathlib
import typing


class Plugin:

    def __init__(self, __file: str):
        self.name: str = pathlib.Path(__file).parent.name

        self.templates: dict[str, CommandTemplate] = dict()

    def __register_template(self, template_name: str, template: CommandTemplate):
        template.sourcePlugin = self.name
        self.templates[template_name] = template

    def register_template(self, json_template: str):
        try:
            _template = CommandTemplate(**(json.loads(json_template)))
            _template_name = _template.id
            self.__register_template(_template_name, _template)
        except ValueError:
            return False
        return True

    def load_folder(self, plugin_folder: pathlib.Path):
        count = 0
        for _path in plugin_folder.glob("Templates/*.json"):
            if _path.is_file():
                with _path.open("r") as _file:
                    try:
                        _file_content = json.load(_file)
                    except json.JSONDecodeError:
                        pass
                    finally:
                        if not isinstance(_file_content, dict):
                            continue
                        _templates = _file_content.get("commandTemplates", [])
                        for _template_dict in _templates:
                            try:
                                _template = CommandTemplate(**_template_dict)
                            except ValueError:
                                pass
                            finally:
                                _template_name = _template.id
                                self.__register_template(_template_name, _template)
                                count += 1

        return count
