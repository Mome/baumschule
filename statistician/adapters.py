from datasets import DatabaseAdapter
import openml

if 'openml_apikey' in c:
    openml.apikey = c.openml_apikey

database_adapters = [
	OpenMLDatabaseAdapter()
]

class OpenMLDatabaseAdapter(DatabaseAdapter):

	@property
	def name(self):
	    return 'openml'
	
    def list_datasets(self):
        return openml.datasets.list_datasets()

    def download(self, id_):
        oml_ds = openml.datasets.get_dataset(id_)
        return oml_ds