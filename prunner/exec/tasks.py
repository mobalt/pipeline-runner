import os
from abc import ABC, abstractmethod

from prunner.util import shellexpansion_dict
from prunner import loaders
from prunner.util.convert import split_file_component


class TaskStrategy(ABC):
    @property
    def task_name(self):
        return ""

    @abstractmethod
    def execute(self, params, variables=None):
        pass


class LoadVariablesTask(TaskStrategy):
    def __init__(self, default_filename):
        self.loader = loaders.YamlLoader(default_filename)

    @classmethod
    def from_settings(cls, settings):
        return LoadVariablesTask(f"{settings['PRUNNER_CONFIG_DIR']}/variables.yaml")

    @property
    def task_name(self):
        return "load_variables"

    def execute(self, params, variables=None):
        if type(params) != str:
            raise TypeError(
                "Expecting a string with the set of variables to load. Instead received: ",
                params,
            )

        section_name, filename = split_file_component(params)
        raw_variables = self.loader.get_section(section_name, filename)
        expanded_variables = shellexpansion_dict(raw_variables, variables)
        return expanded_variables


class GenerateFileTask(TaskStrategy):
    def __init__(self, templates_folder):
        self.loader = loaders.TemplateLoader(templates_folder)

    @classmethod
    def from_settings(cls, settings):
        return GenerateFileTask(f"{settings['PRUNNER_CONFIG_DIR']}/templates")

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


class ParamsNotDefined(Exception):
    def __init__(self, not_set, variables):
        super().__init__(
            f'These params have not been set: {", ".join(not_set)}',
            "If this is okay, give the params a default value."
            f"Here is dump of the variables that exist as of this point.",
            variables,
        )


def generate_args_from_function_signature(fn, variables):
    param_names = fn.__code__.co_varnames[: fn.__code__.co_argcount]
    param_default_values = fn.__defaults__ if fn.__defaults__ is not None else []
    param_defaults = dict(
        zip(param_names[-len(param_default_values) :], param_default_values)
    )
    overall_vars = {**variables, **param_defaults}

    # Make sure none of the arguments are missing, else throw error
    missing = [param for param in param_names if param not in overall_vars]
    if len(missing) != 0:
        raise ParamsNotDefined(missing, variables)

    args = [overall_vars[v] for v in param_names]
    return args


class FunctionTask(TaskStrategy):
    def __init__(self, default_filename):
        self.loader = loaders.FunctionLoader(default_filename)

    @classmethod
    def from_settings(cls, settings):
        return FunctionTask(f"{settings['PRUNNER_CONFIG_DIR']}/functions.py")

    @property
    def task_name(self):
        return "function"

    def execute(self, params, variables=None):
        if type(params) != str:
            raise TypeError(
                "Expecting a string with the set of variables to load. Instead received: ",
                params,
            )
        function_name, filename = split_file_component(params)
        fn = self.loader.get_function(function_name, filename)
        args = generate_args_from_function_signature(fn, variables)
        return fn(*args)


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
