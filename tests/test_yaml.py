import main

CONFIG_DIR = "example/"

def test_load_existing_yaml():
    pipelines = main.load_yaml(f"{CONFIG_DIR}/pipelines.yaml")
    assert type(pipelines) == dict
    assert len(pipelines) == 5

def test_load_nonexisting_yaml():
    pipelines = main.load_yaml(f"{CONFIG_DIR}/nonexistent.yaml")
    assert type(pipelines) == dict
    assert len(pipelines) == 0



