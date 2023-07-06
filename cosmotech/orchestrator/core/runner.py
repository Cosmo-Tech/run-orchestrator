import flowpipe

from cosmotech.orchestrator.core.step import Step


class Runner(flowpipe.INode):

    def __init__(self, step: Step, dry_run: bool, **kwargs):
        super(Runner, self).__init__(**kwargs)
        flowpipe.InputPlug("step", self, step)
        flowpipe.InputPlug("previous", self)
        flowpipe.InputPlug("dry_run", self, dry_run)
        flowpipe.OutputPlug("status", self)

    def compute(self, step: Step, dry_run: bool, previous: dict):
        return {
            'status': step.run(dry=dry_run, previous=previous)
        }
