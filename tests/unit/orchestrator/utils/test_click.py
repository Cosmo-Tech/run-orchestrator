import pytest
from unittest.mock import MagicMock, patch

from cosmotech.orchestrator.utils.click import click


class TestClick:
    def test_rich_click_configuration(self):
        # Verify that rich_click is configured correctly
        assert click.rich_click.USE_MARKDOWN is True
        assert click.rich_click.USE_RICH_MARKUP is True
        assert click.rich_click.SHOW_ARGUMENTS is True
        assert click.rich_click.GROUP_ARGUMENTS_OPTIONS is False
        assert click.rich_click.STYLE_OPTION_ENVVAR == "yellow"
        assert click.rich_click.ENVVAR_STRING == "ENV: {}"
        assert click.rich_click.STYLE_OPTION_DEFAULT == "dim yellow"
        assert click.rich_click.DEFAULT_STRING == "DEFAULT: {}"
        assert click.rich_click.OPTIONS_PANEL_TITLE == "OPTIONS"
