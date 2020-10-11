class ColumnOperational(object):
    def __init__(self, l_o, r_o, op):
        self.l_o = l_o
        self.r_o = r_o
        self.op = op

class ColumnOrder():
    def __init__(self, l_o, order):
        self.l_o = l_o
        self.order = order

class BaseType(object):
    def or_op(self, o):
        pass


class Integer(BaseType):
    def __init__(self, *args, **kwargs):
        self.__visit__ = 'Integer'
        super().__init__(args, kwargs)


class String(BaseType):
    def __init__(self, length, *args, **kwargs):
        self.__visit__ = 'String'
        self.length = length
        super().__init__(args, kwargs)


class Text(String):
    def __init__(self, *args, **kwargs):
        self.__visit__ = 'Text'
        super().__init__(args, kwargs)


class Boolean(BaseType):
    def __init__(self, *args, **kwargs):
        self.__visit__ = 'Boolean'
        super().__init__(args, **kwargs)