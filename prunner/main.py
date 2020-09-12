#!/bin/python3
import argparse
import copy
import importlib.util
import os
import re

import yaml
from jinja2 import Environment, FileSystemLoader, StrictUndefined


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
    def __init__(self, not_set, variables):
        super().__init__(
            f'The following variable(s) have not been set: {", ".join(not_set)}',
            f"Here is dump of the variables that exist as of this point.",
            variables,
        )


class Pipelines:
    def __init__(self, filename):
        self.filename = filename
        self.pipelines = load_yaml(filename)

    def tasks(self, pipeline):
        if pipeline not in self.pipelines:
            raise PipelineNotDefined(self.filename, pipeline)

        return self.pipelines[pipeline]


class VariableLoader:
    def __init__(self, filename):
        self.filename = filename
        self.variable_sets = load_yaml(filename)

    def load_set(self, variable_set_name):
        if variable_set_name not in self.variable_sets:
            raise VariableSetNotDefined(self.filename, variable_set_name)

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
        parameters = fn.__code__.co_varnames[: fn.__code__.co_argcount]
        defaults = fn.__defaults__ if fn.__defaults__ is not None else []
        args = dict(zip(parameters[-len(defaults) :], defaults))
        args.update(variables)

        # Make sure none of the arguments are missing, else throw error
        missing = [v for v in parameters if v not in args]
        if len(missing) != 0:
            raise VariableNotSet(missing, variables)

        # execute function
        args = [args[v] for v in parameters]
        result = fn(*args)

        if not result or type(result) != dict:
            return {}
        else:
            return result


class TemplateEnv:
    def __init__(self, templates_folder):
        self.env = Environment(
            loader=FileSystemLoader(templates_folder), undefined=StrictUndefined
        )

    def render(self, template_name, variables):
        t = self.env.get_template(template_name)
        return t.render(**variables)


def load_yaml(filename):
    if not os.path.exists(filename):
        return {}
    with open(filename) as fd:
        return yaml.load(fd, Loader=yaml.SafeLoader)


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
            raise VariableNotSet((variable_name,), variables)

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
        self.config_dir = ""
        self.dry_run = False
        self.verbose = False

    @staticmethod
    def from_config_dir(configuration_dir):
        executor = Executor(
            dict(os.environ),
            Functions(f"{configuration_dir}/functions.py"),
            TemplateEnv(f"{configuration_dir}/templates"),
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
        updated_variables = {**self.variables, **expanded_variables}
        self.variables = updated_variables

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

        updated_variables = {
            **self.variables,
            params.get("variable", "OUTPUT_FILE"): filepath,
        }
        self.variables = updated_variables

        return rendered_text

    def function(self, function_name):
        if type(function_name) != str:
            raise TypeError(
                "Expecting a string with the set of variables to load. Instead received: ",
                function_name,
            )
        result = self.functions.execute(function_name, self.variables)
        self.variables.update(result)

        return result

    def set_variables(self, new_variables):
        if type(new_variables) != dict:
            raise TypeError(
                "Expecting to receive a flat dict of new variables. Instead received:",
                new_variables,
            )
        expanded = shellexpansion_dict(new_variables, self.variables)
        self.variables.update(expanded)
        return expanded


def list_of_methods(class_):
    method_list = [
        func
        for func in dir(class_)
        if callable(getattr(class_, func)) and not func.startswith("__")
    ]
    return method_list


def execute_pipeline(exec: Executor):
    yaml_file = f"{exec.config_dir}/pipelines.yaml"
    pipelines = Pipelines(yaml_file)
    pipeline_to_execute = exec.variables["PIPELINE_NAME"]

    methods_available = list_of_methods(Executor)

    pipeline = pipelines.tasks(pipeline_to_execute)
    for i, task in enumerate(pipeline):
        task: dict = copy.deepcopy(task)
        task_name, task_value = task.popitem()

        if task_name not in methods_available:
            raise Exception("That task is not available: ", task_name)

        if type(task_value) == str:
            print(f"Task {i}: {task_name} = {task_value}")
        else:
            print(f"Task {i}: {task_name}\n{task_value}")

        func = getattr(exec, task_name)
        func(task_value)


arg_pattern = re.compile("--([a-zA-Z0-9_]+)(?:=(.+))?")


def parse_rest_of_args(args):
    positional = []
    named = {}
    for x in args:
        match = arg_pattern.match(x)
        if match:
            named[match.group(1)] = match.group(2) or ""
        else:
            positional.append(x)
    escape_spaces = [x if " " not in x else f'"{x}"' for x in positional]
    arg_zero = " ".join(escape_spaces)
    positional = [arg_zero] + positional
    positional_dict = {f"_{i}": value for i, value in enumerate(positional)}
    return {**positional_dict, **named}


def parse_arguments(args=None):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        "-c",
        type=str,
        help="The configuration directory to use. Default is $PWD.",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Verbose (for debugging pipeline)."
    )
    parser.add_argument(
        "--dryrun",
        "-n",
        action="store_true",
        help="Dry-run. Don't execute local scripts.",
    )
    parser.add_argument(
        "PIPELINE", help="The name of the pipeline to run", default="DEFAULT"
    )
    parser.add_argument(
        "ARGS",
        help="The rest of the args get passed to the pipeline.",
        nargs=argparse.REMAINDER,
    )
    parsed_args = parser.parse_args(args)
    config_dir = (
        os.path.abspath(parsed_args.config) if parsed_args.config else os.getcwd()
    )
    print(config_dir, parsed_args)
    executor = Executor.from_config_dir(config_dir)
    executor.verbose = parsed_args.verbose
    executor.dry_run = parsed_args.dryrun
    executor.variables["PIPELINE_NAME"] = parsed_args.PIPELINE
    executor.variables.update(parse_rest_of_args(parsed_args.ARGS))

    return executor


def main():
    exec = parse_arguments()
    execute_pipeline(exec)


if __name__ == "__main__":
    main()
