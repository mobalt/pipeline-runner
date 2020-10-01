from prunner.util import shellexpansion_dict
from .base import TaskStrategy


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
