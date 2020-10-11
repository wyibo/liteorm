from enum import Enum, auto


class Node(object):
    def __init__(self, value=None, l_children=None, r_children=None):
        self.value = value
        self.l_children = l_children
        self.r_children = r_children


class SqlNodeLegalType(Enum):
    TABLE_NAME = auto()
    RESERVED_WORD = auto()
    COMMA = auto()
    BRACKETS = auto()
    FIELD = auto()
    CONDITION = auto()
    OPERATION = auto()
    JUDGEMENT = auto()
    JOINER = auto()
    NUM = auto()


class SqlNode(Node):
    def __init__(self, node_type=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.node_type = node_type


class BinTree(object):
    def __init__(self):
        pass

    def preorder_traversal(self):
        pass

    def inorder_traversal(self, node):
        if not node:
            return None
        self.inorder_traversal(node.l_children)
        self.value_list.append(node.value)
        self.inorder_traversal(node.r_children)

    def postorder_traversal(self):
        pass


class SqlQueryTree(BinTree):
    def __init__(self, table):
        self.value_list = []
        self.head_node = SqlNode(SqlNodeLegalType.TABLE_NAME,
                                 value=table.__tablename__)
        super().__init__()

    def dump_sql(self):
        self.inorder_traversal(self.head_node)
        value_list = [str(v) for v in self.value_list if v is not None]
        sql = " ".join(value_list)
        return sql
