#!/bin/python3
import os
import yaml
import importlib.util

class FunctionNotDefined(Exception):
    def __init__(self, filename, function_name):
        super().__init__(f'The function "{function_name}" is not defined in "{filename}".')

class VariableNotSet(Exception):
    def __init__(self, variables):
        super().__init__(f'The following variable(s) have not been set: {", ".join(variables)}.')

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
        args = dict(zip(parameters[-len(defaults):], defaults))
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


def load_yaml(filename):
    if not os.path.exists(filename):
        return {}
    with open(filename) as fd:
        return yaml.load(fd, Loader=yaml.SafeLoader)


def load_pipeline(configuration_dir, pipeline_name, args):
    pass


if __name__ == '__main__':
    pass
    # load_pipeline()
