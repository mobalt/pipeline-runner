import os

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
    ):
        self.variables = variables
        self.functions = functions
        self.templates = templates
        self.var_loader = var_loader
        self.config_dir = ""
        self.dry_run = False
        self.verbose = False

    @staticmethod
    def from_config_dir(configuration_dir):
        executor = ExecutionEnvironment(
            dict(os.environ),
            FunctionLoader(f"{configuration_dir}/functions.py"),
            TemplateLoader(f"{configuration_dir}/templates"),
            VariableLoader(f"{configuration_dir}/variables.yaml"),
        )
        executor.config_dir = configuration_dir
        return executor

    def load_variables(self, set_name):
        if type(set_name) != str:
            raise TypeError(
                "Expecting a string with the set of variables to load. Instead received: ",
                set_name,
            )

        raw_variables = self.var_loader.load_set(set_name)
        expanded_variables = shellexpansion_dict(raw_variables, self.variables)
        return expanded_variables

    def generate_file(self, params, dryrun=False):
        if type(params) != dict:
            raise TypeError(
                "Expecting to receive a dict as specified at https://github.com/mobalt/pipeline-runner#generate_file-dict Instead received:",
                params,
            )

        params = shellexpansion_dict(params, self.variables)

        rendered_text = self.templates.render(params["template"], self.variables)

        filepath = params["filepath"]
        filepath = os.path.abspath(filepath)

        if not dryrun:
            with open(filepath, "w") as fd:
                fd.write(rendered_text)

        varname = params.get("variable", "OUTPUT_FILE")
        return {
            varname: filepath,
        }

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
