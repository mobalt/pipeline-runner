import importlib.util


class FunctionNotDefined(Exception):
    def __init__(self, filename, function_name):
        super().__init__(
            f'The function "{function_name}" is not defined in "{filename}".'
        )


class ParamsNotDefined(Exception):
    def __init__(self, not_set, variables):
        super().__init__(
            f'These params have not been set: {", ".join(not_set)}',
            "If this is okay, give the params a default value."
            f"Here is dump of the variables that exist as of this point.",
            variables,
        )


class FunctionLoader:
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
            raise ParamsNotDefined(missing, variables)

        # execute function
        args = [args[v] for v in parameters]
        result = fn(*args)

        if not result or type(result) != dict:
            return {}
        else:
            return result
