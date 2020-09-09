#!/bin/python3
import os
import yaml


def load_yaml(filename):
    if not os.path.exists(filename):
        return {}
    with open(filename) as fd:
        return yaml.load(fd, Loader=yaml.SafeLoader)

def load_pipeline(configuration_dir, pipeline_name, args):
    pass

if __name__ == '__main__':
    pass
    # load_pipeline()
