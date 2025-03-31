import pytest
from unittest.mock import MagicMock, patch
import flowpipe

from cosmotech.orchestrator.core.runner import Runner
from cosmotech.orchestrator.core.step import Step


class TestRunner:
    def test_init_creates_input_and_output_plugs(self):
        # Setup
        mock_step = MagicMock()
        mock_graph = MagicMock()

        # Execute
        runner = Runner(graph=mock_graph, name="test_runner", step=mock_step, dry_run=False)

        # Verify
        assert hasattr(runner, "inputs")
        assert hasattr(runner, "outputs")
        assert "step" in runner.inputs
        assert "previous" in runner.inputs
        assert "dry_run" in runner.inputs
        assert "input_data" in runner.inputs
        assert "status" in runner.outputs
        assert "output_data" in runner.outputs

    def test_compute_runs_step_and_returns_status_and_output(self):
        # Setup
        mock_step = MagicMock()
        mock_step.run.return_value = "Done"
        mock_step.captured_output = {"output1": "value1", "output2": "value2"}

        # Execute
        runner = Runner(step=mock_step, dry_run=False, name="test_runner")
        result = runner.compute(step=mock_step, dry_run=False, previous={}, input_data={})

        # Verify
        mock_step.run.assert_called_once_with(dry=False, previous={}, input_data={})
        assert result["status"] == "Done"
        assert result["output_data"] == {"output1": "value1", "output2": "value2"}

    def test_compute_with_dry_run(self):
        # Setup
        mock_step = MagicMock()
        mock_step.run.return_value = "DryRun"
        mock_step.captured_output = {}

        # Execute
        runner = Runner(step=mock_step, dry_run=True, name="test_runner2")
        result = runner.compute(step=mock_step, dry_run=True, previous={}, input_data={})

        # Verify
        mock_step.run.assert_called_once_with(dry=True, previous={}, input_data={})
        assert result["status"] == "DryRun"
        assert result["output_data"] == {}

    def test_compute_with_previous_steps(self):
        # Setup
        mock_step = MagicMock()
        mock_step.run.return_value = "Done"
        mock_step.captured_output = {"output1": "value1"}

        previous = {"step1": "Done", "step2": "Done"}

        # Execute
        runner = Runner(step=mock_step, dry_run=False, name="test_runner3")
        result = runner.compute(step=mock_step, dry_run=False, previous=previous, input_data={})

        # Verify
        mock_step.run.assert_called_once_with(dry=False, previous=previous, input_data={})
        assert result["status"] == "Done"
        assert result["output_data"] == {"output1": "value1"}

    def test_compute_with_input_data(self):
        # Setup
        mock_step = MagicMock()
        mock_step.run.return_value = "Done"
        mock_step.captured_output = {"output1": "value1"}
        mock_step.inputs = {"input1": {"stepId": "step1", "output": "output1"}}

        input_data = {"output1": "input_value1"}

        # Execute
        runner = Runner(step=mock_step, dry_run=False, name="test_runner4")
        result = runner.compute(step=mock_step, dry_run=False, previous={"step1": "Done"}, input_data=input_data)

        # Verify
        mock_step.run.assert_called_once_with(
            dry=False, previous={"step1": "Done"}, input_data={"input1": "input_value1"}
        )
        assert result["status"] == "Done"
        assert result["output_data"] == {"output1": "value1"}

    def test_compute_with_multiple_inputs(self):
        # Setup
        mock_step = MagicMock()
        mock_step.run.return_value = "Done"
        mock_step.captured_output = {"output1": "value1"}
        mock_step.inputs = {
            "input1": {"stepId": "step1", "output": "output1"},
            "input2": {"stepId": "step2", "output": "output2"},
        }

        input_data = {"output1": "input_value1", "output2": "input_value2"}

        # Execute
        runner = Runner(step=mock_step, dry_run=False, name="test_runner5")
        result = runner.compute(
            step=mock_step, dry_run=False, previous={"step1": "Done", "step2": "Done"}, input_data=input_data
        )

        # Verify
        mock_step.run.assert_called_once_with(
            dry=False,
            previous={"step1": "Done", "step2": "Done"},
            input_data={"input1": "input_value1", "input2": "input_value2"},
        )
        assert result["status"] == "Done"
        assert result["output_data"] == {"output1": "value1"}
