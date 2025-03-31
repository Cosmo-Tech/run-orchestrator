import pytest
from unittest.mock import MagicMock, patch

from cosmotech.orchestrator.utils import strtobool, WEB_DOCUMENTATION_ROOT


def test_strtobool():
    # Test true values
    assert strtobool("y") is True
    assert strtobool("yes") is True
    assert strtobool("t") is True
    assert strtobool("true") is True
    assert strtobool("on") is True
    assert strtobool("1") is True

    # Test with uppercase
    assert strtobool("Y") is True
    assert strtobool("YES") is True
    assert strtobool("T") is True
    assert strtobool("TRUE") is True
    assert strtobool("ON") is True

    # Test with mixed case
    assert strtobool("Yes") is True
    assert strtobool("True") is True

    # Test false values
    assert strtobool("n") is False
    assert strtobool("no") is False
    assert strtobool("f") is False
    assert strtobool("false") is False
    assert strtobool("off") is False
    assert strtobool("0") is False

    # Test with uppercase
    assert strtobool("N") is False
    assert strtobool("NO") is False
    assert strtobool("F") is False
    assert strtobool("FALSE") is False
    assert strtobool("OFF") is False

    # Test with mixed case
    assert strtobool("No") is False
    assert strtobool("False") is False

    # Test invalid values
    with pytest.raises(ValueError):
        strtobool("invalid")

    with pytest.raises(ValueError):
        strtobool("")


def test_web_documentation_root():
    # Verify the constant is defined
    assert WEB_DOCUMENTATION_ROOT is not None
    assert isinstance(WEB_DOCUMENTATION_ROOT, str)
    assert WEB_DOCUMENTATION_ROOT.startswith("http")
