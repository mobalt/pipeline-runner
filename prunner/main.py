#!/bin/python3
import argparse
import os
import re
from prunner.exec import Executor


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
    rest_of_args = parse_rest_of_args(parsed_args.ARGS)
    return (
        config_dir,
        parsed_args.PIPELINE,
        rest_of_args,
        parsed_args.dryrun,
        parsed_args.verbose,
    )


def main():
    config_dir, pipeline, rest_of_args, dryrun, verbose = parse_arguments()
    r = Executor(config_dir, rest_of_args, dryrun, verbose)
    r.execute_pipeline(pipeline)
    return r


if __name__ == "__main__":
    main()
