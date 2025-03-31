import importlib
import os
import pkgutil
from typing import Callable

import i18n


def get_translate_function(
    locale: str = os.environ.get("CSM_LOCALE", "en-US"),
    fallback: str = "en-US",
    use_rich: bool = os.environ.get("CSM_USE_RICH", "False").lower() in ("true", "1", "yes", "t", "y"),
) -> Callable:
    import cosmotech.translation

    for finder, name, _ in pkgutil.iter_modules(cosmotech.translation.__path__, cosmotech.translation.__name__ + "."):
        _mod = importlib.import_module(name)
        i18n.load_path.extend(_mod.__path__)
    i18n.set("file_format", "yml")
    i18n.set("skip_locale_root_data", True)
    i18n.set("use_locale_dirs", True)
    i18n.set("filename_format", "{namespace}.{format}")

    i18n.set("locale", locale)
    i18n.set("fallback", fallback)
    if use_rich:

        def translate(key, **kwargs) -> str:
            rich_key = f"rich.{key}"
            result = i18n.t(rich_key, **kwargs)
            if result == rich_key:
                return i18n.t(key, **kwargs)
            return result

        return translate
    return i18n.t


DEFAULT_TRANSLATOR = get_translate_function()
T = DEFAULT_TRANSLATOR
