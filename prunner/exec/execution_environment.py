import os

from prunner.loader import (
    VariableLoader,
    FunctionLoader,
    TemplateLoader,
)
from .tasks import (
    LoadVariablesTask,
    SetVariablesTask,
    GenerateFileTask,
    FunctionTask,
)


class ExecutionEnvironment:
    def __init__(
        self,
        variables: dict,
        functions: FunctionLoader,
        templates: TemplateLoader,
        var_loader: VariableLoader,
        dryrun: bool,
        verbose: bool,
        config_dir: str,
    ):
        variables["PRUNNER_CONFIG_DIR"] = config_dir
        variables["DRYRUN"] = dryrun
        variables["VERBOSE"] = verbose
        self.variables = variables
        self.functions = functions
        self.templates = templates
        self.var_loader = var_loader
        self.config_dir = config_dir
        self.dry_run = dryrun
        self.verbose = verbose

    @staticmethod
    def from_config_dir(configuration_dir, dryrun=False, verbose=False):
        executor = ExecutionEnvironment(
            dict(os.environ),
            FunctionLoader(f"{configuration_dir}/functions.py"),
            TemplateLoader(f"{configuration_dir}/templates"),
            VariableLoader(f"{configuration_dir}/variables.yaml"),
            dryrun,
            verbose,
            configuration_dir,
        )
        return executor

    def load_variables(self, set_name):
        task = LoadVariablesTask()
        return task.execute(set_name, self.variables)

    def generate_file(self, params):
        task = GenerateFileTask()
        return task.execute(params, self.variables)

    def function(self, function_name):
        task = FunctionTask()
        return task.execute(function_name, self.variables)

    def set_variables(self, new_variables):
        task = SetVariablesTask()
        return task.execute(new_variables, self.variables)
