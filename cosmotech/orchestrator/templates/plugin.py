import json
import pathlib

from cosmotech.orchestrator.core.command_template import CommandTemplate


class Plugin:

    def __init__(self, __file: str):
        self.name: str = pathlib.Path(__file).parent.name

        self.templates: dict[str, CommandTemplate] = dict()

    def __register_template(self, template_name: str, template: CommandTemplate):
        template.sourcePlugin = self.name
        self.templates[template_name] = template

    def register_template(self, template_as_dict: dict):
        try:
            _template = CommandTemplate(**template_as_dict)
            _template_name = _template.id
            self.__register_template(_template_name, _template)
        except ValueError:
            return False
        return _template

    def load_folder(self, plugin_folder: pathlib.Path):
        count = 0
        for _path in plugin_folder.glob("templates/*.json"):
            if _path.is_file():
                with _path.open("r") as _file:
                    try:
                        _file_content = json.load(_file)
                    except json.JSONDecodeError:
                        pass
                    finally:
                        if not isinstance(_file_content, dict):
                            continue

                        def _read(_template_as_dict):
                            try:
                                _template = CommandTemplate(**_template_as_dict)
                            except ValueError:
                                return 0
                            _template_name = _template.id
                            self.__register_template(_template_name, _template)
                            return 1

                        if _templates := _file_content.get("commandTemplates", []):
                            for _template_dict in _templates:
                                count += _read(_template_dict)
                        else:
                            count += _read(_file_content)
        return count
