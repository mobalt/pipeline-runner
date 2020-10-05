#!/bin/python3
import argparse
import os
from prunner.executioner import Executioner
from prunner.util import convert_args_to_dict


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
    rest_of_args = convert_args_to_dict(parsed_args.ARGS)
    return (
        config_dir,
        parsed_args.PIPELINE,
        rest_of_args,
        parsed_args.dryrun,
        parsed_args.verbose,
    )


def main():
    config_dir, pipeline, rest_of_args, dryrun, verbose = parse_arguments()
    vars = {
        **os.environ,
        **rest_of_args,
    }
    r = Executioner(config_dir, vars, dryrun, verbose)
    r.execute_pipeline(pipeline)
    return r


if __name__ == "__main__":
    main()
