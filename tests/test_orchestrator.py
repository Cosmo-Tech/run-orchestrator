import copy
import os

from cosmotech.orchestrator.core.orchestrator import FileLoader
from cosmotech.orchestrator.core.orchestrator import Orchestrator


class TestOrchestrator:
    def test_load_command(self):
        o = Orchestrator()
        # Copy of examples/simple.json
        # Setting env var to ensure file is valid to run
        old_env = copy.deepcopy(os.environ)
        os.environ.setdefault("NO_EXIST", "SET")
        steps = FileLoader("examples/simple.json")()
        assert len(steps) == 3
        s, g = o._load_from_json_content("examples/simple.json", steps, False, False)
        os.environ = old_env
        assert len(s) == 3

    def test_load_command_missing_env(self):
        o = Orchestrator()
        # Copy of examples/simple.json
        # Setting env var to ensure file is valid to run
        try:
            steps = FileLoader("examples/simple.json")()
            assert len(steps) == 3
            o._load_from_json_content("examples/simple.json", steps, False, False)
        except ValueError:
            assert True
        else:
            assert False
