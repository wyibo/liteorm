from table import Query
class DBSession
    def __init__(self):
        """init db session"""
        self.umcommit_list = []


    def query(self,table):
        table_query = Query(table)
        return table_query

    def commit(self):
        pass

    def add(self):
        pass

    def close(self):
        pass