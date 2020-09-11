#!/bin/python3
import importlib.util
import os
import re

import yaml
from jinja2 import Environment, FileSystemLoader


class VariableSetNotDefined(Exception):
    def __init__(self, filename, variable_set_name):
        super().__init__(
            f'The variable set "{variable_set_name}" is not defined in "{filename}".'
        )


class PipelineNotDefined(Exception):
    def __init__(self, filename, pipeline):
        super().__init__(f'The pipeline "{pipeline}" is not defined in "{filename}".')


class FunctionNotDefined(Exception):
    def __init__(self, filename, function_name):
        super().__init__(
            f'The function "{function_name}" is not defined in "{filename}".'
        )


class VariableNotSet(Exception):
    def __init__(self, variables):
        super().__init__(
            f'The following variable(s) have not been set: {", ".join(variables)}.'
        )


class Pipelines:
    def __init__(self, filename):
        self.filename = filename
        self.pipelines = load_yaml(filename)

    def tasks(self, pipeline):
        if pipeline not in self.pipelines:
            raise PipelineNotDefined(self.filename, self.pipelines)

        return self.pipelines[pipeline]


class VariableLoader:
    def __init__(self, filename):
        self.filename = filename
        self.variable_sets = load_yaml(filename)

    def load_set(self, variable_set_name):
        if variable_set_name not in self.variable_sets:
            raise VariableSetNotDefined(self.filename, self.variable_sets)

        return self.variable_sets[variable_set_name]


class Functions:
    def __init__(self, filename):
        spec = importlib.util.spec_from_file_location("main", filename)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        self.module = module
        self.filename = filename

    def execute(self, function_name, variables):
        if not hasattr(self.module, function_name):
            raise FunctionNotDefined(self.filename, function_name)
        fn = getattr(self.module, function_name)
        parameters = fn.__code__.co_varnames
        defaults = fn.__defaults__
        args = dict(zip(parameters[-len(defaults) :], defaults))
        args.update(variables)

        # Make sure none of the arguments are missing, else throw error
        missing = [v for v in parameters if v not in args]
        if len(missing) != 0:
            raise VariableNotSet(missing)

        # execute function
        args = [args[v] for v in parameters]
        result = fn(*args)

        # if dict returned, update variables
        if result and type(result) == dict:
            variables.update(result)

        return variables


class TemplateEnv:
    def __init__(self, templates_folder):
        self.env = Environment(
            loader=FileSystemLoader(templates_folder),
        )

    def render(self, t, variables):
        t = self.env.get_template(t)
        return t.render(**variables)


def load_yaml(filename):
    if not os.path.exists(filename):
        return {}
    with open(filename) as fd:
        return yaml.load(fd, Loader=yaml.SafeLoader)


def load_pipeline(configuration_dir, pipeline_name, args):
    variables = {}
    return


expansion_regex = re.compile(r"\$([a-zA-Z0-9_]+)|\$\{([a-zA-Z0-9_]+)(?:\:([^}]*))?\}")


def shellexpansion(string, variables):
    if string[0] == "~":
        home = os.path.expanduser("~")
        string = home + string[1:]

    def replacements(matchobj):
        variable_name = (
            matchobj.group(1) if matchobj.group(2) is None else matchobj.group(2)
        )
        default_value = matchobj.group(3)
        if variable_name in variables:
            return variables[variable_name]
        elif default_value:
            return default_value
        else:
            raise VariableNotSet((variable_name,))

    string = expansion_regex.sub(replacements, string)
    return string


def shellexpansion_dict(obj, variables):
    return {k: shellexpansion(v, variables) for k, v in obj.items()}


class Executor:
    def __init__(
        self,
        variables: dict,
        functions: Functions,
        templates: TemplateEnv,
        var_loader: VariableLoader,
    ):
        self.variables = variables
        self.functions = functions
        self.templates = templates
        self.var_loader = var_loader

    @staticmethod
    def from_config_dir(configuration_dir):
        executor = Executor(
            dict(os.environ),
            Functions(f"{configuration_dir}/functions.py"),
            TemplateEnv(f"{configuration_dir}/templates"),
            VariableLoader(f"{configuration_dir}/variables.yaml"),
        )
        return executor

    def load_variables(self, set_name):
        if type(set_name) != str:
            raise TypeError(
                "Expecting a string with the set of variables to load. Instead received: ",
                set_name,
            )

        raw_variables = self.var_loader.load_set(set_name)
        expanded_variables = shellexpansion_dict(raw_variables, self.variables)
        updated_variables = {**self.variables, **expanded_variables}
        self.variables = updated_variables


if __name__ == "__main__":
    pass
    # load_pipeline()
