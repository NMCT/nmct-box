import re


class OneWire(object):  # TODO: make static? --> use metaclass to implement __getitem__ on class!
    @staticmethod
    def _w1_path(path):
        return "/sys/bus/w1/devices/w1_bus_master1/{path}".format(path=path)

    @property
    def slaves(self):
        # slaves = []
        with open(self._w1_path('w1_master_slaves'), 'r') as f:
            slaves = [s.strip('\n') for s in f.readlines()]
        return slaves

    @property
    def slave_count(self):
        res = -1
        with open(self._w1_path('w1_master_slave_count'), 'r') as f:
            res = int(f.read())
        return res

    def slave(self, slave_id):
        if slave_id not in self.slaves:
            raise ValueError("No slave found with ID {id}".format(id=slave_id), slave_id)
        else:
            return OneWire.Slave(slave_id)

    def __getitem__(self, item):
        if isinstance(item, int):
            return self.slave(self.slaves[item])
        else:
            return self.slave(item)

    class Slave(object):
        @property
        def id(self):
            return self._id

        @property
        def data(self):
            rex = re.compile(r'(?:[0-9a-fA-F]{2}\s){9}(?P<name>\w+)=(?P<value>.+)$')
            with open("/sys/bus/w1/devices/w1_bus_master1/{id}/w1_slave".format(id=self.id), 'r') as f:
                return dict([(rex.match(line).group('name'), rex.match(line).group('value'))
                             for line in f if rex.match(line)])

        def __init__(self, w1id):
            self._id = w1id

        def __getitem__(self, item):
            return self.data[item]

        def __repr__(self):
            return "OneWire slave {id}".format(id=self._id)

        def __str__(self):
            return self._id
