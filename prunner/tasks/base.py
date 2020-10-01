from abc import ABC, abstractmethod


class TaskStrategy(ABC):
    @abstractmethod
    def execute(self, params, variables=None):
        pass

    @classmethod
    def from_settings(cls, settings):
        return cls()

    @classmethod
    def task_name(cls):
        return ""
