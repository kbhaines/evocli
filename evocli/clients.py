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

    def _find_real_zone_id(self, user_given_id):
        zone_keys = { id.lower(): id for id in self._evohome.zones.keys() if id.lower().startswith(user_given_id) }
        if len(zone_keys) == 0:
            raise ZoneNotFoundException(user_given_id)
        if len(zone_keys) > 1:
            raise AmbiguousZoneId(user_given_id, zone_keys)
        key, value = zone_keys.popitem()
        return self._evohome.zones[value]

    def set_zone_temperature(self, zone_id, temperature, until=None):
        zone = self._find_real_zone_id(zone_id)
        if temperature:
            zone.set_temperature(temperature, until)
        else:
            zone.cancel_temp_override(zone_id)

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
        return results


class ZoneNotFoundException(Exception):
    pass


class AmbiguousZoneId(Exception):
    pass

