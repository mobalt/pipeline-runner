#!/bin/python3
import argparse
import copy
import os
import re
from prunner.exec import ExecutionEnvironment
from prunner.loader import PipelineLoader


def list_of_methods(class_):
    method_list = [
        func
        for func in dir(class_)
        if callable(getattr(class_, func)) and not func.startswith("__")
    ]
    return method_list


def execute_pipeline(exec: ExecutionEnvironment):
    yaml_file = f"{exec.config_dir}/pipelines.yaml"
    pipelines = PipelineLoader(yaml_file)
    pipeline_to_execute = exec.variables["PIPELINE_NAME"]

    methods_available = list_of_methods(ExecutionEnvironment)

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
    executor = ExecutionEnvironment.from_config_dir(config_dir)
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
