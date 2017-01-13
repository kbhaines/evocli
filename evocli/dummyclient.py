
class DummyClient(object):
    def __init__(self):
        self.hotwater = self
        self.zones = {
                'lounge': DummyZone('lounge'),
                'kitchen': DummyZone('kitchen')
                }

    def _get_single_heating_system(self):
        return self

    def set_dhw_on(self, until):
        print 'Hotwater on until {}'.format(until)

    def set_dhw_off(self, until):
        print 'Hotwater off until {}'.format(until)

    def set_dhw_auto(self):
        print 'Hotwater to auto'


class DummyZone(object):

    def __init__(self, zone_id):
        self._zone_id = zone_id

    def set_temperature(self, temp, until=None):
        if until:
            print '{} set to {} until {}'.format(self._zone_id, temp, until)
        else:
            print '{} set to {}'.format(self._zone_id, temp)

