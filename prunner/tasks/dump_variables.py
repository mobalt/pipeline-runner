import os

from prunner.tasks import TaskStrategy


class DumpVarsTask(TaskStrategy):
    @classmethod
    def task_name(cls):
        return "dump_variables"

    def execute(self, params, variables=None):
        filepath, varname = standardize_param(params, variables.get("DRYRUN", False))
        rendered_text = generate_sh(variables)
        with open(filepath, "w") as fd:
            fd.write(rendered_text)

        return {} if varname is None else {varname: filepath}


def generate_sh(variables):
    result = ""
    for k, v in variables.items():
        if type(v) is str:
            v = v.replace("'", "\\'")
            result += f"\nexport {k}='{v}'"
    return result


def standardize_param(params, dryrun=False):
    if type(params) == str:
        filename, variable = params, None
    elif type(params) == dict:
        if "filename" not in params:
            raise ValueError(
                "The key `filename` is required for task `dump_variables`."
            )
        filename = params["filename"]
        variable = params.get("variable")  # optional, don't raise errors if missing
    else:
        raise TypeError(
            "Expecting either a string or dict. Instead received: ",
            params,
        )

    if not filename.endswith(".sh"):
        raise ValueError("Only generation of bash files is available.")

    filename = os.path.abspath(filename)

    if dryrun:
        os.makedirs("generated/", exist_ok=True)
        filename = filename.replace("/", "\\")
        filename = os.path.abspath("generated/" + filename)

    return filename, variable
