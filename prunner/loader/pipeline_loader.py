import yaml


class PipelineNotDefined(Exception):
    def __init__(self, filename, pipeline):
        super().__init__(f'The pipeline "{pipeline}" is not defined in "{filename}".')


class PipelineLoader:
    def __init__(self, filename):
        self.filename = filename
        with open(filename) as fd:
            self.pipelines = yaml.load(fd, Loader=yaml.SafeLoader)

    def tasks(self, pipeline):
        if pipeline not in self.pipelines:
            raise PipelineNotDefined(self.filename, pipeline)

        return self.pipelines[pipeline]
