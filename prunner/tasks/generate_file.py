import os

from prunner.loaders import TemplateLoader
from .base import TaskStrategy


class GenerateFileTask(TaskStrategy):
    def __init__(self, templates_folder):
        self.loader = TemplateLoader(templates_folder)

    @classmethod
    def from_settings(cls, settings):
        return GenerateFileTask(f"{settings['PRUNNER_CONFIG_DIR']}/templates")

    @classmethod
    def task_name(cls):
        return "generate_file"

    def execute(self, params, variables=None):
        if type(params) != dict:
            raise TypeError(
                "Expecting to receive a dict as specified at https://github.com/mobalt/pipeline-runner#generate_file-dict Instead received:",
                params,
            )

        template = self.loader.get_template(params["template"])
        rendered_text = template.render(**variables)

        filepath = params["filepath"]
        filepath = os.path.abspath(filepath)

        dryrun = variables["DRYRUN"]
        if dryrun:
            os.makedirs("generated/", exist_ok=True)
            filepath = filepath.replace("/", "\\")
            filepath = os.path.abspath("generated/" + filepath)

        with open(filepath, "w") as fd:
            fd.write(rendered_text)

        varname = params.get("variable", "OUTPUT_FILE")
        return {
            varname: filepath,
        }
