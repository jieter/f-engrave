class Header(object):
    def __init__(self):
        self.variables = dict()
        self.last_var = None

    def new_var(self, kw):
        self.variables.update({kw: dict()})
        self.last_var = self.variables[kw]

    def new_val(self, val):
        self.last_var.update({
            str(val[0]): val[1]
        })


class Entity(object):
    def __init__(self, _type):
        self.type = _type
        self.data = dict()

    def update(self, value):
        key = str(value[0])
        val = value[1]
        if key in self.data:
            if type(self.data[key]) != list:
                self.data[key] = [self.data[key]]
            self.data[key].append(val)
        else:
            self.data.update({key: val})


class Entities(object):
    def __init__(self):
        self.entities = []
        self.last = None

    def new_entity(self, _type):
        e = Entity(_type)
        self.entities.append(e)
        self.last = e

    def update(self, value):
        self.last.update(value)


class Block(object):
    def __init__(self, master):
        self.master = master
        self.data = dict()
        self.entities = []
        self.le = None

    def new_entity(self, value):
        self.le = Entity(value)
        self.entities.append(self.le)

    def update(self, value):
        if self.le is None:
            val = str(value[0])
            self.data.update({val: value[1]})
            if val == "2":
                self.master.blocks[value[1]] = self
        else:
            self.le.update(value)


class Blocks(object):
    def __init__(self):
        self.blocks = dict()
        self.last_var = None

    def new_block(self):
        b = Block(self)
        self.last_block = b
        self.last_var = b

    def new_entity(self, value):
        self.last_block.new_entity(value)

    def update(self, value):
        self.last_block.update(value)


class PointClass(object):
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def __str__(self):
        return ('X ->%6.3f  Y ->%6.3f' % (self.x, self.y))
