from cosmotech.orchestrator.core.command_template import CommandTemplate


class TestTemplate:

    def test_load_command(self):
        _ct_content = {
            "id": "STEP",
            "command": "echo",
            "arguments": ["Test"]
        }
        ct = CommandTemplate(**_ct_content)
        assert ct.id == _ct_content.get('id')
        assert ct.command == _ct_content.get('command')
        assert ct.arguments == _ct_content.get('arguments')

    def test_serialize(self):
        _ct_content = {
            "id": "STEP",
            "command": "echo",
            "arguments": ["Test"]
        }
        ct = CommandTemplate(**_ct_content)
        assert _ct_content == ct.serialize()
