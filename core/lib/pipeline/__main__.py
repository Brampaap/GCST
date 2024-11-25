from core.lib.pipeline.context import Context


class Pipeline:
    def __init__(self):
        self.steps = []

    def run(self, context: Context):
        results = [step.run(context) for step in self.steps]

        step_scores, step_responses, step_success = (
            zip(*results) if results else ([], [], [])
        )
        return step_scores, step_responses, step_success
