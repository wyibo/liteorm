from orm.table import BaseTable, Columns, Query
from orm.liteorm_type import Integer, String, Text, Boolean

class TestTable(BaseTable):
    __tablename__ = "test_table"

    test_int = Columns(Integer)
    name = Columns(Text)


if __name__ == "__main__":
    Query(TestTable).all()
    Query(TestTable).filter_by(test_int=1, name='a').all()
    # Query(TestTable).filter_by(test_int=1, name='a').delete()
    # Query(TestTable).filter_by(test_int=1).filter_by(name='a').all()

    Query(TestTable).filter(TestTable.test_int==1).filter(TestTable.name >= 'a').all()
    # Query(TestTable).filter(TestTable.test_int==1).update({"test_int": 2})
    # Query(TestTable).filter(TestTable.test_int==1).update({TestTable.test_int: 2, TestTable.name: 3})

    # Query(TestTable).filter(TestTable.test_int==1).order_by(TestTable.name.desc()).all()
    # Query(TestTable).filter(TestTable.test_int==1).order_by(TestTable.name.desc()).order_by(TestTable.test_int.asc()).all()
    # Query(TestTable).filter(TestTable.test_int==1).filter(TestTable.name=='a').limit(1).all()
    #in operation 
    #test = Query(TestTable).filter_in(in_(name=['a','b']))