# Copyright (C) - 2023 - 2025 - Cosmo Tech
# This document and all information contained herein is the exclusive property -
# including all intellectual property rights pertaining thereto - of Cosmo Tech.
# Any use, reproduction, translation, broadcasting, transmission, distribution,
# etc., to any person is prohibited unless it has been previously and
# specifically authorized by written means by Cosmo Tech.

import flowpipe

from cosmotech.orchestrator.core.step import Step


class Runner(flowpipe.INode):
    def __init__(self, step: Step, dry_run: bool, **kwargs):
        super(Runner, self).__init__(**kwargs)
        flowpipe.InputPlug("step", self, step)
        flowpipe.InputPlug("previous", self)
        flowpipe.InputPlug("dry_run", self, dry_run)
        flowpipe.InputPlug("input_data", self, {})
        flowpipe.OutputPlug("status", self)
        flowpipe.OutputPlug("output_data", self)

    def compute(self, step: Step, dry_run: bool, previous: dict, input_data: dict):
        # Transform input data to match step's input configuration
        transformed_inputs = {}
        for input_name, input_config in step.inputs.items():
            if input_config["stepId"] in previous:
                # Get the output value from the input_data
                output_name = input_config["output"]
                if output_name in input_data:
                    transformed_inputs[input_name] = input_data[output_name]

        status = step.run(dry=dry_run, previous=previous, input_data=transformed_inputs)
        return {"status": status, "output_data": step.captured_output}
