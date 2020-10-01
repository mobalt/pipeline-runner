import importlib
import os


class FunctionLoader:
    def __init__(self, default_filename=None):
        self.data = {}
        self.default_filename = default_filename if default_filename else None

    def load(self, filename=None):
        if not filename:
            filename = self.default_filename

        fullpath = os.path.abspath(filename)

        # Short-circuit if already loaded
        if fullpath in self.data:
            return self.data[fullpath]

        # if file doesn't exist
        if not os.path.exists(fullpath):
            raise FileNotFoundError(fullpath)

        base = os.path.splitext(os.path.basename(fullpath))[0]
        spec = importlib.util.spec_from_file_location(base, fullpath)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        self.data[fullpath] = module
        return module

    def has_function(self, function_name, filename=None):
        module = self.load(filename)
        return hasattr(module, function_name)

    def get_function(self, function_name, filename=None):
        if self.has_function(function_name, filename):
            module = self.load(filename)
            return getattr(module, function_name)
        else:
            raise FunctionNotDefined(filename, function_name)


class FunctionNotDefined(Exception):
    def __init__(self, filename, function_name):
        super().__init__(
            f'The function "{function_name}" is not defined in "{filename}".'
        )
