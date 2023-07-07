import os

from cosmotech.orchestrator.core.step import Step


class TestStep:

    def test_load_command(self):
        _step_content = {
            "id": "STEP",
            "command": "echo",
            "arguments": ["Test"]
        }
        s = Step(**_step_content)
        assert s.id == _step_content.get('id')
        assert s.command == _step_content.get('command')
        assert s.arguments == _step_content.get('arguments')
        assert s.status == "Init"

    def test_serialize(self):
        _step_content = {
            "id": "STEP",
            "command": "echo",
            "arguments": ["Test"]
        }
        s = Step(**_step_content)
        assert _step_content == s.serialize()

    def test__effective_env(self):
        _step_content = {
            "id": "STEP",
            "command": "echo",
            "arguments": ["Test"],
            "environment": {
                "ENV": {
                    "value": "VALUE"
                }
            }
        }
        s = Step(**_step_content)
        assert s._effective_env() == {"ENV": "VALUE"}

    def test_check_env(self):
        unset_env_key = "UNSET_ENV"
        while unset_env_key in os.environ:
            unset_env_key = unset_env_key + "_1"
        _step_content = {
            "id": "STEP",
            "command": "echo",
            "arguments": ["Test"],
            "environment": {
                unset_env_key: {
                    "description": "UNSET"
                },
                "DEFAULT_ENV": {
                    "defaultValue": "DEFAULT"
                },
                "SET_ENV": {
                    "value": "SET"
                }
            }
        }
        s = Step(**_step_content)
        assert s.check_env() == {unset_env_key: "UNSET"}

    def test_dry_run(self):
        _step_content = {
            "id": "STEP",
            "command": "echo",
            "arguments": ["Test"]
        }
        s = Step(**_step_content)
        assert s.run(dry=True) == "DryRun"

    def test_run(self):
        _step_content = {
            "id": "STEP",
            "command": "echo",
            "arguments": ["Test"]
        }
        s = Step(**_step_content)
        assert s.run(dry=False) == "Done"
