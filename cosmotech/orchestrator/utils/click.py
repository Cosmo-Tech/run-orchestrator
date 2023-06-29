import rich_click as click

click.rich_click.USE_MARKDOWN = True
click.rich_click.USE_RICH_MARKUP = True
click.rich_click.SHOW_ARGUMENTS = True
click.rich_click.GROUP_ARGUMENTS_OPTIONS = False
click.rich_click.STYLE_OPTION_ENVVAR = "yellow"
click.rich_click.ENVVAR_STRING = "ENV: {}"
click.rich_click.STYLE_OPTION_DEFAULT = "dim yellow"
click.rich_click.DEFAULT_STRING = "DEFAULT: {}"
click.rich_click.OPTIONS_PANEL_TITLE = "OPTIONS"
