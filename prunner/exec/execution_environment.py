import os
from abc import abstractmethod, ABC

from prunner.loader import (
    VariableLoader,
    FunctionLoader,
    TemplateLoader,
)
from prunner.util.expand import shellexpansion_dict


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
        if type(function_name) != str:
            raise TypeError(
                "Expecting a string with the set of variables to load. Instead received: ",
                function_name,
            )
        update_variables = self.functions.execute(function_name, self.variables)
        return update_variables

    def set_variables(self, new_variables):
        if type(new_variables) != dict:
            raise TypeError(
                "Expecting to receive a flat dict of new variables. Instead received:",
                new_variables,
            )
        expanded = shellexpansion_dict(new_variables, self.variables)
        return expanded


class TaskStrategy(ABC):
    @abstractmethod
    def execute(self, params, variables=None):
        pass


class LoadVariablesTask(TaskStrategy):
    def execute(self, set_name, variables=None):
        if type(set_name) != str:
            raise TypeError(
                "Expecting a string with the set of variables to load. Instead received: ",
                set_name,
            )
        configuration_dir = variables["PRUNNER_CONFIG_DIR"]
        var_loader = VariableLoader(f"{configuration_dir}/variables.yaml")

        raw_variables = var_loader.load_set(set_name)
        expanded_variables = shellexpansion_dict(raw_variables, variables)
        return expanded_variables


class GenerateFileTask(TaskStrategy):
    def execute(self, params, variables=None):
        if type(params) != dict:
            raise TypeError(
                "Expecting to receive a dict as specified at https://github.com/mobalt/pipeline-runner#generate_file-dict Instead received:",
                params,
            )

        params = shellexpansion_dict(params, variables)

        configuration_dir = variables["PRUNNER_CONFIG_DIR"]
        templates = TemplateLoader(f"{configuration_dir}/templates")
        rendered_text = templates.render(params["template"], variables)

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
