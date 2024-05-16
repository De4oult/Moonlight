class Query:
    def __call__(self):
        return { key: value for key, value in self.__dict__.items() if not key.startswith('__')}

# Standart Queries
class GetById(Query):
    def __init__(self, id: int):
        self.id = id