from utils.dz_script import run


class Project:
    def __init__(self, samples, script="load all \n bandwidth:10 \n plot -kde -cdf"):
        self.samples = samples
        self.script = script

    def execute_project(self):
        html_out = run(self.script, self.samples)
        return html_out
