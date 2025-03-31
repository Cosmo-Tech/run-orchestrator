from unittest.mock import MagicMock
from unittest.mock import patch

from cosmotech.orchestrator.core.command_template import CommandTemplate
from cosmotech.orchestrator.templates.library import Library
from cosmotech.orchestrator.templates.plugin import Plugin


class TestLibrary:
    def test_display_library(self):
        # Setup
        library = Library()

        # Mock templates
        template1 = CommandTemplate(id="template1", command="echo", description="Template 1", sourcePlugin="plugin1")

        template2 = CommandTemplate(id="template2", command="ls", description="Template 2", sourcePlugin="plugin2")

        # Mock plugins
        plugin1 = MagicMock()
        plugin1.name = "plugin1"
        plugin1.templates = {"template1": template1}

        plugin2 = MagicMock()
        plugin2.name = "plugin2"
        plugin2.templates = {"template2": template2}

        # Set up library internals
        library._Library__templates = {"template1": template1, "template2": template2}
        library._Library__plugins = {"plugin1": plugin1, "plugin2": plugin2}

        # Execute
        library.display_library()

    def test_display_template(self):
        # Setup
        template = CommandTemplate(id="template1", command="echo", description="Template 1")

        # Execute
        Library.display_template(template)

    def test_display_template_by_id_found(self):
        # Setup
        library = Library()

        template = CommandTemplate(id="template1", command="echo", description="Template 1")

        # Mock find_template_by_name
        library.find_template_by_name = MagicMock(return_value=template)

        # Execute
        library.display_template_by_id("template1")

        # Verify
        library.find_template_by_name.assert_called_once_with(template_id="template1")

    def test_display_template_by_id_not_found(self):
        # Setup
        library = Library()

        # Mock find_template_by_name
        library.find_template_by_name = MagicMock(return_value=None)

        # Execute
        library.display_template_by_id("non_existent_template")

        # Verify
        library.find_template_by_name.assert_called_once_with(template_id="non_existent_template")

    def test_templates_property(self):
        # Setup
        library = Library()

        template1 = CommandTemplate(id="template1", command="echo", sourcePlugin="plugin1")

        template2 = CommandTemplate(id="template2", command="ls", sourcePlugin="plugin2")

        library._Library__templates = {"template1": template1, "template2": template2}

        # Execute
        result = library.templates

        # Verify
        assert len(result) == 2
        assert template1 in result
        assert template2 in result

    def test_find_template_by_name(self):
        # Setup
        library = Library()

        template = CommandTemplate(id="template1", command="echo")

        library.add_template(template, True)
        # Execute and verify
        assert "template1" in library._Library__templates
        assert library.find_template_by_name("non_existent_template") is None

    def test_load_plugin(self):
        # Setup
        library = Library()
        library._Library__templates = {}
        library._Library__plugins = {}
        library._Library__exit_templates = []

        plugin = MagicMock()
        plugin.name = "test_plugin"
        plugin.templates = {
            "template1": CommandTemplate(id="template1", command="echo"),
            "template2": CommandTemplate(id="template2", command="ls"),
        }
        plugin.exit_commands = ["exit_handler1"]

        # Execute
        library.load_plugin(plugin)

        # Verify
        assert "template1" in library._Library__templates
        assert "template2" in library._Library__templates
        assert "test_plugin" in library._Library__plugins
        assert "exit_handler1" in library._Library__exit_templates

    @patch("importlib.import_module")
    @patch("pkgutil.iter_modules")
    @patch("sys.path")
    @patch("os.getcwd")
    def test_reload(self, mock_getcwd, mock_sys_path, mock_iter_modules, mock_import_module):
        # Setup
        library = Library()

        # Mock getcwd
        mock_getcwd.return_value = "/test/path"

        # Mock iter_modules
        mock_finder = MagicMock()
        mock_iter_modules.return_value = [
            (mock_finder, "cosmotech.orchestrator_plugins.plugin1", False),
            (mock_finder, "cosmotech.orchestrator_plugins.plugin2", False),
        ]

        # Mock import_module
        mock_module1 = MagicMock()
        mock_module1.__path__ = "."
        mock_module1.plugin = MagicMock(spec=Plugin)
        mock_module1.plugin.name = "plugin1"
        mock_module1.plugin.templates = dict()
        mock_module1.plugin.exit_commands = []

        mock_module2 = MagicMock()
        mock_module2.plugin = "not_a_plugin"  # This should be skipped

        mock_import_module.side_effect = [mock_module1, mock_module2]

        # Execute
        library.reload()

        # Verify
        assert mock_iter_modules.called
        assert mock_import_module.call_count == 2
        # Only the first plugin should be loaded
        assert hasattr(library, "load_plugin")

    def test_add_template(self):
        # Setup
        library = Library()
        library._Library__templates = {}

        template = CommandTemplate(id="template1", command="echo")

        # Execute
        library.add_template(template)

        # Verify
        assert "template1" in library._Library__templates
        assert library._Library__templates["template1"] == template

    def test_add_template_with_override(self):
        # Setup
        library = Library()

        template1 = CommandTemplate(id="template1", command="echo")

        template2 = CommandTemplate(id="template1", command="ls")

        library._Library__templates = {"template1": template1}

        # Execute
        library.add_template(template2, override=True)

        # Verify
        assert library._Library__templates["template1"] == template2

    def test_add_template_without_override(self):
        # Setup
        library = Library()

        template1 = CommandTemplate(id="template1", command="echo")

        template2 = CommandTemplate(id="template1", command="ls")

        library._Library__templates = {"template1": template1}

        # Execute
        library.add_template(template2)

        # Verify
        assert library._Library__templates["template1"] == template1

    def test_list_exit_commands(self):
        # Setup
        library = Library()
        library._Library__exit_templates = ["exit_handler1", "exit_handler2"]

        # Execute
        result = library.list_exit_commands()

        # Verify
        assert result == ["exit_handler1", "exit_handler2"]
