import os
import re


class VariableNotSet(Exception):
    def __init__(self, not_set, variables):
        super().__init__(
            f'Variable "{not_set}" has not been set.',
            f"Here is dump of the variables that exist as of this point.",
            variables,
        )


SHELL_VARIABLES_PATTERN = re.compile(
    r"\$([a-zA-Z0-9_]+)|\$\{([a-zA-Z0-9_]+)(?:\:([^}]*))?\}"
)


def shellexpansion(input_str, variables):
    if input_str[0] == "~":
        home = os.path.expanduser("~")
        input_str = home + input_str[1:]

    def replacements(matchobj):
        variable_name = matchobj.group(1) or matchobj.group(2)
        default_value = matchobj.group(3)

        if variable_name in variables:
            return variables[variable_name]
        elif default_value:
            return default_value
        else:
            raise VariableNotSet(variable_name, variables)

    return SHELL_VARIABLES_PATTERN.sub(replacements, input_str)

def shellexpansion_list(array, variables):
    return [shellexpansion_dict(v, variables) for v in array]

def shellexpansion_dict(obj, variables):
    accumulator = {}
    for k, v in obj.items():
        if type(v) == str:
            accumulator[k] = shellexpansion(v, variables)
        elif type(v) == dict:
            accumulator[k] = shellexpansion_dict(v, variables)
        elif type(v) == list:
            accumulator[k] = shellexpansion_list(v, variables)
        else:
            accumulator[k] = v

    return accumulator
