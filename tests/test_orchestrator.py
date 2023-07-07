import copy
import os

from cosmotech.orchestrator.core.orchestrator import Orchestrator


class TestOrchestrator:
    file_content = {
        "commandTemplates": [
            {
                "id": "TEMPLATE_ID",
                "command": "echo",
                "arguments": [
                    "list",
                    "of",
                    "arguments",
                    "$ENV_VALUE"
                ],
                "environment": {
                    "ENV_VALUE": {
                        "defaultValue": "DEFAULT",
                        "description": "An environment variable with a default value"
                    }
                }
            }
        ],
        "steps": [
            {
                "id": "UseTemplate",
                "commandId": "TEMPLATE_ID"
            },
            {
                "id": "OverrideTemplate",
                "commandId": "TEMPLATE_ID",
                "arguments": [
                    "Added",
                    "arguments"
                ],
                "environment": {
                    "ENV_VALUE": {
                        "value": "OVERRIDE",
                        "description": "An environment variable with a forced value"
                    }
                },
                "precedents": [
                    "UseTemplate"
                ]
            },
            {
                "id": "NewCommand",
                "command": "echo",
                "arguments": [
                    "$NO_EXIST"
                ],
                "environment": {
                    "NO_EXIST": {
                        "description": "An environment variable with no value"
                    }
                },
                "precedents": [
                    "OverrideTemplate"
                ]
            }
        ]
    }

    def test_load_command(self):
        o = Orchestrator()
        # Copy of examples/simple.json
        # Setting env var to ensure file is valid to run
        old_env = copy.deepcopy(os.environ)
        os.environ.setdefault("NO_EXIST", "SET")
        c, s, g = o._load_from_json_content("example/simple.json", self.file_content, False, False, [])
        os.environ = old_env
        assert len(c) == 1
        assert len(s) == 3

    def test_load_command_missing_env(self):
        o = Orchestrator()
        # Copy of examples/simple.json
        # Setting env var to ensure file is valid to run
        try:
            o._load_from_json_content("example/simple.json", self.file_content, False, False, [])
        except ValueError:
            assert True
        else:
            assert False
