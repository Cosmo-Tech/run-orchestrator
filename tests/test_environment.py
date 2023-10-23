from cosmotech.orchestrator.core.environment import EnvironmentVariable


class TestEnvironment:

    def test_load_command(self):
        name = "ENVVAR"
        _e_content = {
            "defaultValue": "DEFAULT",
            "value": "SET_VALUE",
            "description": "An environment variable with a default value",
            "optional": False
        }
        e = EnvironmentVariable(name, **_e_content)
        assert e.name == name
        assert e.defaultValue == _e_content.get('defaultValue')
        assert e.value == _e_content.get('value')
        assert e.description == _e_content.get('description')

    def test_serialize(self):
        name = "ENVVAR"
        _e_content = {
            "defaultValue": "DEFAULT",
            "value": "SET_VALUE",
            "description": "An environment variable with a default value",
            "optional": False
        }
        e = EnvironmentVariable(name, **_e_content)
        assert _e_content == e.serialize()

    def test_non_optional(self):
        name = "ENVVAR"
        _e_content = {
            "description": "A non optional environment variable",
            "optional": False
        }
        e = EnvironmentVariable(name, **_e_content)
        assert e.is_required()

    def test_optional(self):
        name = "ENVVAR"
        _e_content = {
            "description": "An optional environment variable",
            "optional": True
        }
        e = EnvironmentVariable(name, **_e_content)
        assert not e.is_required()
