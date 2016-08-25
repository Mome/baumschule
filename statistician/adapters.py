from statistician import get_config
from datasets import DatabaseAdapter
import openml

c = get_config()

if 'openml_apikey' in c:
    openml.apikey = c.openml_apikey

class OpenMLDatabaseAdapter(DatabaseAdapter):

    @property
    def name(self):
        return 'openml'
    
    def list_datasets(self):
        return openml.datasets.list_datasets()

    def download(self, id_):
        oml_ds = openml.datasets.get_dataset(id_)
        return oml_ds


database_adapters = [
    OpenMLDatabaseAdapter()
]