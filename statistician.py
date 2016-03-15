import os
import pandas
import collections


class Statistician:
    def __init__(self):
        self.tasks = []
        self.statistics = []
        self.prediction_algorithms = []


class Task:
    def __init__(self, dataset_path, validation_function):
        self.statistic_dict = {}
        self.dataset = DataSet(dataset_path)
        self.target_function = None
        self.task_description = None


class Statistic(collections.abc.Callable):
    def __init__(self, name, func):
        self.name = name
        self.func = func

    def __call__(self, *args, **keyargs):
        return self.func(*args, **keyargs)


class PredictionAlgorithm(Statistic):
    def __init__(self, name, func):
        super(PredictionAlgorithm, self).__init__(name, func)


class DataSet(dict):
    """Represents multiple Datatables in a Dataset."""

    def __init__(self, path):
        self.name = os.path.basename(path)
        self.path = path

        # load meta file
        meta_path = os.path.join(path, name)
        if os.path.exists(meta_path):
            with open(os.path.join(path, name)) as f:
                self.meta = f.read()
        else:
            self.meta = None

        # load datafiles
        for filename in os.path.listdir(path):
            if filename.startswith('.'):
                continue
            if not filnename.endswith('.csv'):
                continue
            
            filepath = os.join(path, filename)
            data = pandas.read_csv(filepath)
            self[filename] = data
