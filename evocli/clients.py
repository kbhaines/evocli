from evohomeclient2 import EvohomeClient

class HeatingControlClient(object):
    def set_zone_temperature(self, zone_id, temperature, until=None):
        print 'set {} to {} until {}'.format(zone_id, temperature, until)

    def set_hotwater_on(self, until=None):
        print 'set hotwater on until {}'.format(until)

    def set_hotwater_off(self, until=None):
        print 'set hotwater off until {}'.format(until)

    def set_hotwater_auto(self):
        print 'set hotwater auto'

    def get_temperatures(self):
        return {}


class EvohomeControlClient(HeatingControlClient):

    def __init__(self, username, password):
        self._username = username
        self._password = password
        self._evohome = EvohomeClient(username, password)._get_single_heating_system()

    def set_zone_temperature(self, zone_id, temperature, until=None):
        self._evohome.zones[zone_id].set_temperature(temperature, until)

    def set_hotwater_on(self, until=None):
        self._evohome.hotwater.set_dhw_on(until)

    def set_hotwater_off(self, until=None):
        self._evohome.hotwater.set_dhw_off(until)

    def set_hotwater_auto(self):
        self._evohome.hotwater.set_dhw_auto()

    def get_temperatures(self):
        temps = self._evohome.temperatures()
        results = { }
        for device in temps:
            (name,setpoint) = ('WATER', '-') \
                    if device['thermostat'] == 'DOMESTIC_HOT_WATER' \
                    else (device['name'],device['setpoint'])
            results[name] = (device['temp'], setpoint)
