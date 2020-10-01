import copy

from prunner.loader import PipelineLoader

from .tasks import (
    TaskStrategy,
    LoadVariablesTask,
    SetVariablesTask,
    GenerateFileTask,
    FunctionTask,
)


class Executor:
    def __init__(self, config_dir, variables, dryrun=False, verbose=False):
        self.variables = {
            "PRUNNER_CONFIG_DIR": config_dir,
            "DRYRUN": dryrun,
            "VERBOSE": verbose,
            **variables,
        }
        self.tasks = {}
        self.add_standard_tasks()

    def add_task(self, task: TaskStrategy):
        self.tasks[task.task_name] = task

    def add_standard_tasks(self):
        self.add_task(LoadVariablesTask())
        self.add_task(SetVariablesTask())
        self.add_task(FunctionTask.from_settings(self.variables))
        self.add_task(GenerateFileTask())

    def execute_pipeline(self, pipeline_name):
        self.variables["PIPELINE_NAME"] = pipeline_name

        config_dir = self.variables["PRUNNER_CONFIG_DIR"]
        yaml_file = f"{config_dir}/pipelines.yaml"
        pipelines = PipelineLoader(yaml_file)
        pipeline = pipelines.tasks(pipeline_name)

        for i, task in enumerate(pipeline):
            task: dict = copy.deepcopy(task)
            task_name, task_value = task.popitem()

            if task_name not in self.tasks:
                raise Exception("That task is not available: ", task_name)

            print("-" * 80)
            if type(task_value) == str:
                print(f"Task {i}: {task_name} = {task_value}")
            else:
                print(f"Task {i}: {task_name}\n{task_value}")

            updates = self.tasks[task_name].execute(task_value, self.variables)
            if updates is None or type(updates) != dict:
                updates = {}
            if self.variables["VERBOSE"]:
                new_variables = {
                    k: v for k, v in updates.items() if k not in self.variables
                }
                mutations = {k: v for k, v in updates.items() if k in self.variables}
                print("Mutations = ", mutations)
                print("New Values = ", new_variables)
            self.variables = {
                **self.variables,
                **updates,
            }
