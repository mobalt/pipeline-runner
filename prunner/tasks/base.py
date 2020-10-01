from abc import ABC, abstractmethod


class TaskStrategy(ABC):
    @property
    def task_name(self):
        return ""

    @abstractmethod
    def execute(self, params, variables=None):
        pass
