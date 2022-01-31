#!/bin/python3
import argparse
import logging
import os
import shutil
from datetime import datetime

from prunner.ImmutableDict import ImmutableDict
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
    logging.info("System call: %s", " ".join(os.sys.argv))
    logging.info(f"Using config directory: {config_dir}")
    logging.info("Parsed args: %s", parsed_args)

    rest_of_args = convert_args_to_dict(parsed_args.ARGS)

    variables = {
        "PRUNNER_CONFIG_DIR": config_dir,
        "DRYRUN": parsed_args.dryrun,
        "VERBOSE": parsed_args.verbose,
        "DEFAULT_PIPELINE": parsed_args.PIPELINE.split(':')[0],
        "PIPELINE_ARGS": parsed_args.PIPELINE.split(':')[1] if ":" in parsed_args.PIPELINE else "",
        **rest_of_args,
    }
    return variables


def main():
    logging.basicConfig(level=logging.DEBUG)
    log_dir = os.path.join(os.getcwd(), "logs")
    if not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, datetime.now().strftime('%y-%m-%d %H:%M:%S') + f".{os.getpid()}.log")
    logging.getLogger().addHandler(logging.FileHandler(log_file))

    args = parse_arguments()

    # Import all the environment variables and prefix with `ENV_`
    variables = ImmutableDict({f"ENV_{k}": v for k, v in os.environ.items()})

    # Add the CLI args to variables
    variables.update(args)

    r = Executioner(variables)
    r.execute_pipeline(variables["DEFAULT_PIPELINE"])
    if 'PRUNNER_LOG_PATH' in variables:
        logging.info("Copying log to: %s", variables['PRUNNER_LOG_PATH'])
        shutil.copyfile(log_file, variables['PRUNNER_LOG_PATH'])
    return r


if __name__ == "__main__":
    main()
