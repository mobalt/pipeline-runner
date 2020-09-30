import os
from abc import ABC, abstractmethod

from prunner.loader import VariableLoader, TemplateLoader, FunctionLoader
from prunner.util import shellexpansion_dict


class TaskStrategy(ABC):
    @property
    def task_name(self):
        return ""

    @abstractmethod
    def execute(self, params, variables=None):
        pass


class LoadVariablesTask(TaskStrategy):
    @property
    def task_name(self):
        return "load_variables"

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
    @property
    def task_name(self):
        return "generate_file"

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


class FunctionTask(TaskStrategy):
    @property
    def task_name(self):
        return "function"

    def execute(self, function_name, variables=None):
        if type(function_name) != str:
            raise TypeError(
                "Expecting a string with the set of variables to load. Instead received: ",
                function_name,
            )
        configuration_dir = variables["PRUNNER_CONFIG_DIR"]
        functions = FunctionLoader(f"{configuration_dir}/functions.py")
        update_variables = functions.execute(function_name, variables)
        return update_variables


class SetVariablesTask(TaskStrategy):
    @property
    def task_name(self):
        return "set_variables"

    def execute(self, new_variables, variables=None):
        if type(new_variables) != dict:
            raise TypeError(
                "Expecting to receive a flat dict of new variables. Instead received:",
                new_variables,
            )
        expanded = shellexpansion_dict(new_variables, variables)
        return expanded
