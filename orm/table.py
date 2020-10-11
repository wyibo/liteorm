from .compiler import SqlNode, SqlQueryTree, SqlNodeLegalType
from .liteorm_type import ColumnOperational, ColumnOrder


class _Dict(dict):
    def __init__(self):
        super().__init__()
        self._member_names = []

    def __setitem__(self, key, value):
        if key in self:
            raise TypeError('Attempted to reuse key: %r' % key)
        if not key.startswith("_"):
            self._member_names.append(key)
        super().__setitem__(key, value)


class LiteOrmMeta(type):
    @classmethod
    def __prepare__(metacls, name, bases):
        d = _Dict()
        return d

    def __new__(metacls, cls, bases, classdict):
        __new__ = bases[0].__new__ if bases else object.__new__
        lite_orm_class = super().__new__(metacls, cls, bases, classdict)
        for member_name in classdict._member_names:
            value = classdict[member_name]
            lite_orm_member = value
            lite_orm_member.visitor_name = "{}.{}".format(lite_orm_class.__tablename__, member_name)
            setattr(lite_orm_class, member_name, lite_orm_member)
        return lite_orm_class


class OperationOverride():
    def __eq__(self, op):
        return ColumnOperational(str(self.visitor_name), op, '=')

    def __ne__(self, op):
        return ColumnOperational(str(self.visitor_name), op, '!=')

    def __ne__(self, op):
        return ColumnOperational(str(self.visitor_name), op, '!=')

    def __gt__(self, op):
        return ColumnOperational(str(self.visitor_name), op, '>')

    def __lt__(self, op):
        return ColumnOperational(str(self.visitor_name), op, '<')

    def __ge__(self, op):
        return ColumnOperational(str(self.visitor_name), op, '>=')

    def __le__(self, op):
        return ColumnOperational(str(self.visitor_name), op, '<=')

    def in_(self, op):
        return ColumnOperational(str(self.visitor_name), op, 'IN')


class Columns(OperationOverride):
    def __init__(self,
                 col_type,
                 primary_key=False,
                 auto_increment=False,
                 nullable=False,
                 default=None):
        self.primary_key = primary_key
        self.auto_increment = auto_increment
        self.nullable = nullable
        self.default = default
        self.col_type = col_type

    def desc(self):
        return ColumnOrder(str(self.visitor_name), "DESC")

    def asc(self):
        return ColumnOrder(str(self.visitor_name), "ASC")

    def __str__(self):
        return self.visitor_name

    def __repr__(self):
        return self.visitor_name

    def __hash__(self):
        return hash(self.visitor_name)


class BaseTable(OperationOverride, metaclass=LiteOrmMeta):
    pass


class SqlQuery(object):
    def __init__(self, table):
        self.table = table
        self.query_tree = SqlQueryTree(table)
        self.condition_node_joiner = SqlNode(SqlNodeLegalType.JOINER, None)
        self.end_condition_node = None
        self.order_node_joiner = SqlNode(SqlNodeLegalType.JOINER, None)
        self.end_order_node = None
        self.limit_node = SqlNode(SqlNodeLegalType.JOINER, None)
        self.end_limit_node = None

        self.query_tree.head_node.r_children = self.condition_node_joiner
        self.condition_node_joiner.r_children = self.order_node_joiner
        self.order_node_joiner.r_children = self.limit_node

        self.where_node = SqlNode(SqlNodeLegalType.RESERVED_WORD, value="WHERE")

    def add_and_condition(self, *args):
        if self.end_condition_node is None:
            self.condition_node_joiner.l_children = self.where_node
            self.end_condition_node = self.where_node

        for col_operation in args:
            k = col_operation.l_o
            v = col_operation.r_o
            operator = col_operation.op
            judgement_node = SqlNode(SqlNodeLegalType.OPERATION, value=operator)
            judgement_node.l_children = SqlNode(SqlNodeLegalType.FIELD, value=k)
            judgement_node.r_children = SqlNode(SqlNodeLegalType.FIELD, value=v)
            if self.end_condition_node != self.where_node:
                and_joiner_node = SqlNode(SqlNodeLegalType.CONDITION, value="AND")
                self.end_condition_node.r_children = and_joiner_node
                self.end_condition_node = and_joiner_node

            condition_node_joiner = SqlNode(SqlNodeLegalType.JOINER, value=None)

            judgement_node = SqlNode(SqlNodeLegalType.OPERATION, value=operator)
            judgement_node.l_children = SqlNode(SqlNodeLegalType.FIELD, value=k)
            judgement_node.r_children = SqlNode(SqlNodeLegalType.FIELD, value=v)
            condition_node_joiner.l_children = judgement_node
            self.end_condition_node.r_children = condition_node_joiner
            self.end_condition_node = condition_node_joiner

    def order_op(self, order_op):
        if self.end_order_node is None:
            tmp_order_joiner = SqlNode(SqlNodeLegalType.RESERVED_WORD, value="ORDER BY")
            self.order_node_joiner.l_children = tmp_order_joiner
            none_joiner = SqlNode(SqlNodeLegalType.JOINER, value=None)
            tmp_order_joiner.r_children = none_joiner
            self.end_order_node = none_joiner
        else:
            comma_joiner = SqlNode(SqlNodeLegalType.COMMA, value=',')
            none_joiner = SqlNode(SqlNodeLegalType.JOINER, value=None)
            comma_joiner.r_children = none_joiner
            self.end_order_node.r_children = comma_joiner
            self.end_order_node = none_joiner

        order_col = SqlNode(SqlNodeLegalType.FIELD, value=order_op.l_o)
        sort = SqlNode(SqlNodeLegalType.RESERVED_WORD, value=order_op.order)
        order_col.r_children = sort
        self.end_order_node.l_children = order_col

    def limit_record(self, num):
        limit_node = SqlNode(SqlNodeLegalType.RESERVED_WORD, "LIMIT")
        num_node = SqlNode(SqlNodeLegalType.NUM, num)
        limit_node.r_children = num_node
        self.limit_node.l_children = limit_node

    def init_select(self):
        select_node = SqlNode(SqlNodeLegalType.RESERVED_WORD, value="SELECT")
        end_field = select_node
        for field, _inst in self.table.__dict__.items():
            if not isinstance(_inst, Columns):
                continue

            field_key_node = SqlNode(SqlNodeLegalType.FIELD, value=None)

            filed_name_node = SqlNode(SqlNodeLegalType.FIELD, value=field)
            if end_field != select_node:
                comma_node = SqlNode(SqlNodeLegalType.COMMA, value=',')
                end_field.l_children.r_children = comma_node

            field_key_node.l_children = filed_name_node
            end_field.r_children = field_key_node
            end_field = field_key_node

        from_node = SqlNode(SqlNodeLegalType.RESERVED_WORD, value="FROM")
        self.query_tree.head_node.l_children = from_node
        from_node.l_children = select_node

    def init_delete(self):
        delete_node = SqlNode(SqlNodeLegalType.RESERVED_WORD, value="DELETE")
        from_node = SqlNode(SqlNodeLegalType.RESERVED_WORD, value="FROM")
        self.query_tree.head_node.l_children = from_node
        from_node.l_children = delete_node

    def init_update(self, **kwargs):
        update_node = SqlNode(SqlNodeLegalType.RESERVED_WORD, value="UPDATE")
        self.query_tree.head_node.l_children = update_node
        set_node = SqlNode(SqlNodeLegalType.RESERVED_WORD, value="SET")
        joiner_node = SqlNode(SqlNodeLegalType.JOINER, value=None)
        if self.query_tree.head_node.r_children is not None:
            joiner_node.r_children = self.query_tree.head_node.r_children
        self.query_tree.head_node.r_children = joiner_node
        joiner_node.l_children = set_node
        end_value_node = set_node
        for k, v in kwargs.items():
            value_joiner = SqlNode(SqlNodeLegalType.JOINER, value=None)
            if end_value_node == set_node:
                end_value_node.r_children = value_joiner
                end_value_node = value_joiner
            else:
                comma_joiner = SqlNode(SqlNodeLegalType.COMMA, value=",")
                _value_joiner = SqlNode(SqlNodeLegalType.JOINER, value=None)
                comma_joiner.r_children = _value_joiner
                value_joiner.r_children = comma_joiner
                end_value_node.r_children = value_joiner
                end_value_node = _value_joiner

            value_node = SqlNode(SqlNodeLegalType.OPERATION, value="=")
            value_node.l_children = SqlNode(SqlNodeLegalType.FIELD, value=k)
            value_node.r_children = SqlNode(SqlNodeLegalType.FIELD, value=v)

            end_value_node.l_children = value_node
            end_value_node = value_joiner


class Query(SqlQuery):
    def filter_by(self, **kwargs):
        condition_list = []
        for k, v in kwargs.items():
            condition_list.append(ColumnOperational(k, v, '='))
        self.add_and_condition(*condition_list)
        return self

    def filter(self, col_operational):
        self.add_and_condition(*[col_operational])
        return self

    def update(self, _dict):
        for k, v in _dict.items():
            if isinstance(k, Columns):
                del _dict[k]
                _dict[str(k)] = v
        self.init_update(**_dict)
        print("-" * 20)
        sql = self.query_tree.dump_sql()
        print(sql)
        return self

    def delete(self):
        self.init_delete()
        print("-" * 20)
        sql = self.query_tree.dump_sql()
        print(sql)
        return self

    def all(self):
        self.init_select()
        print("-" * 20)
        sql = self.query_tree.dump_sql()
        print(sql)

    def one(self):
        self.init_select()

    def add(self):
        pass

    def order_by(self, col_order):
        self.order_op(col_order)
        return self

    def limit(self, num):
        self.limit_record(num)
        return self

    def offset(self, num):
        pass