import os
import re


def shellexpand(item, variables):
    item_type = type(item)
    if item_type == str:
        return expand_string(item, variables)
    elif item_type == dict:
        return expand_dict(item, variables)
    elif item_type == list:
        return expand_list(item, variables)
    else:
        return item


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


def expand_string(input_str, variables):
    # short-circuit if is a single variable
    result = SHELL_VARIABLES_PATTERN.match(input_str)
    if result and result.end() == len(input_str):
        variable_name = result[1] or result[2]
        if variable_name in variables:
            # notice lack of string-cohercion
            # this allows non-str variables with their native type
            return variables[variable_name]

    if input_str[0] == "~":
        home = os.path.expanduser("~")
        input_str = home + input_str[1:]

    def replacements(matchobj):
        variable_name = matchobj.group(1) or matchobj.group(2)
        default_value = matchobj.group(3)

        if variable_name in variables:
            # string cohercion of value, otherwise
            # re.sub throws error
            return str(variables[variable_name])
        elif default_value:
            return default_value
        else:
            raise VariableNotSet(variable_name, variables)

    return SHELL_VARIABLES_PATTERN.sub(replacements, input_str)


def expand_dict(obj, variables):
    return {k: shellexpand(v, variables) for k, v in obj.items()}


def expand_list(array, variables):
    return [shellexpand(v, variables) for v in array]
