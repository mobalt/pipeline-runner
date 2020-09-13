import yaml


class VariableSetNotDefined(Exception):
    def __init__(self, filename, variable_set_name):
        super().__init__(
            f'The variable set "{variable_set_name}" is not defined in "{filename}".'
        )


class VariableLoader:
    def __init__(self, filename):
        self.filename = filename
        with open(filename) as fd:
            self.variable_sets = yaml.load(fd, Loader=yaml.SafeLoader)

    def load_set(self, variable_set_name):
        if variable_set_name not in self.variable_sets:
            raise VariableSetNotDefined(self.filename, variable_set_name)

        return self.variable_sets[variable_set_name]
