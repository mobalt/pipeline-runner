#!/usr/bin/env python3
import argparse
import logging
import os
import shutil
from datetime import datetime
from pprint import pformat

import pkg_resources

from prunner.ImmutableDict import ImmutableDict
from prunner.executioner import Executioner
from prunner.util import convert_args_to_dict

version = pkg_resources.require("prunner")[0].version

def parse_arguments(args=None):
    description = "The Pipeline runner creates a series of scripts from templates using variables stored in a YAML " \
                  "file and executes them in a pipeline. "
    parser = argparse.ArgumentParser(prog="prunner", description=description)
    parser.add_argument('--version', action='version', version=f'%(prog)s {version}')
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
    args = parse_arguments()

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # create logs directory
    log_dir = os.path.join(os.getcwd(), "logs")
    if not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)

    # create file handler which logs even debug messages
    log_file = os.path.join(log_dir, datetime.now().strftime('%y-%m-%d %H:%M:%S') + f".{os.getpid()}.log")
    fh = logging.FileHandler(log_file, mode='w')
    fh.setLevel(logging.DEBUG)

    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)

    # just output the message to the console, but log the relative time to the log file
    ch.setFormatter(logging.Formatter("%(message)s"))
    fh.setFormatter(logging.Formatter("%(levelname)s:%(relativeCreated)d: %(message)s"))

    # add the handlers to the logger
    logger.addHandler(fh)
    logger.addHandler(ch)


    if args['VERBOSE']:
        ch.setLevel(logging.DEBUG)

    logger.info(f"prunner version: {version}")
    logging.info(f"CWD: {args['PRUNNER_CONFIG_DIR']}")
    logging.info("System call: %s", " ".join(os.sys.argv))
    logging.debug("Parsed args:\n%s", pformat(args))

    # Import all the environment variables and prefix with `ENV_`
    variables = ImmutableDict({f"ENV_{k}": v for k, v in os.environ.items()})

    # Add the CLI args to variables
    variables.update(args)

    r = Executioner(variables)
    r.execute_pipeline(variables["DEFAULT_PIPELINE"])
    if 'PRUNNER_LOG_PATH' in variables:
        if args['DRYRUN']:
            logging.warning("Dry-run is on. Otherwise, this would copy log to: %s", variables['PRUNNER_LOG_PATH'])
        else:
            logging.info("Copying log to: %s", variables['PRUNNER_LOG_PATH'])
            shutil.copyfile(log_file, variables['PRUNNER_LOG_PATH'])
    return r

def wrapper():
    # This wrapper function consumes the return value of main() to prevent non-zero exit code
    main()

if __name__ == "__main__":
    m = main()
