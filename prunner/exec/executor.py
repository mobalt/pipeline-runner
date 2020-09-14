import copy

from prunner.loader import PipelineLoader
from .execution_environment import ExecutionEnvironment


def list_of_methods(class_):
    method_list = [
        func
        for func in dir(class_)
        if callable(getattr(class_, func)) and not func.startswith("__")
    ]
    return method_list


class Executor:
    def __init__(self, config_dir, variables, dryrun=False, verbose=False):
        env = ExecutionEnvironment.from_config_dir(config_dir)
        env.verbose = verbose
        env.dry_run = dryrun
        env.variables.update(variables)
        self.env = env
        self.config_dir = config_dir

    def execute_pipeline(self, pipeline_name):
        self.env.variables["PIPELINE_NAME"] = pipeline_name
        yaml_file = f"{self.config_dir}/pipelines.yaml"
        pipelines = PipelineLoader(yaml_file)
        methods_available = list_of_methods(ExecutionEnvironment)

        pipeline = pipelines.tasks(pipeline_name)
        for i, task in enumerate(pipeline):
            task: dict = copy.deepcopy(task)
            task_name, task_value = task.popitem()

            if task_name not in methods_available:
                raise Exception("That task is not available: ", task_name)

            print("-" * 80)
            if type(task_value) == str:
                print(f"Task {i}: {task_name} = {task_value}")
            else:
                print(f"Task {i}: {task_name}\n{task_value}")

            func = getattr(self.env, task_name)
            updates = func(task_value)
            if updates is None or type(updates) != dict:
                updates = {}
            self.env.variables = {
                **self.env.variables,
                **updates,
            }
