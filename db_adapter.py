class DataBaseAdapter:
    def get_db(self):
        ...

    def get_data(self, table_name, query):
        ...

    def get_datas(self, table_name, query):
        ...

    def create_data(self, table_name, data):
        ...

    def update_data(self, table_name, old_data, new_data):
        ...

    def delete_data(self, table_name, query):
        ...
