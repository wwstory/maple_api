class StorageAdapter:
    def get_client(self):
        ...

    def upload_object(self, file):
        ...

    def get_object(self, object_name):
        ...

    def get_object_content(self, object_name):
        ...

    def get_object_url(self, object_name):
        ...
