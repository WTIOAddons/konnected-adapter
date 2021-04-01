"""Properties for Konnected addon for WebThings Gateway."""

import logging

from gateway_addon import Property


class KonnectedProperty(Property):
    """Konnected property type."""

    def __init__(self, device, name, description):
        """
        Initialize the object.

        device -- the Device this property belongs to
        name -- name of the property
        description -- description of the property, as a dictionary

        description e.g. {'type': 'boolean'} or more
        'visible'
        'title', before 'label'
        'type'
        '@type'
        'unit'
        'description'
        'minimum'
        'maximum'
        'enum'
        'readOnly'
        """
        Property.__init__(self, device, name, description)

# Abstract
    def get_new_value(self):
        logging.error('Missing function property: %s', self)
        return

    """Will be called when a value is changed for a property. Normally
       the property do not need to know if it has been hanged but if it
       want to take som actions this can be overridden
    """
    def new_value(self, old_value, new_value):
        return

    def update(self):
        """
        Update the current value, if necessary.
        """
        try:
            new_value = self.get_new_value()

            if new_value != self.get_value():
                self.new_value(self.get_value(), new_value)
                self.set_cached_value(new_value)
                self.device.notify_property_changed(self)
        except Exception as ex:
            logging.exception('Update Exception %s', ex)


# name is shown in rules
# label is shown in thing
class KITempProperty(KonnectedProperty):
    """Minutes integer property"""
    def __init__(self, device, ki):
        KonnectedProperty.__init__(self, device,
                                  'Temp', {'title': 'Temperature',
                                             'label': 'Temperature',
                                             '@type': 'LevelProperty',
                                             'type': 'number',
                                             'unit': 'degree celcius',
                                             'readOnly': True,
                                             'minimum': -80, 'maximum': 80})
        self.ki = ki

    def get_new_value(self):
        return self.ki.get_temperature()


class KIHumidProperty(KonnectedProperty):
    """Hour integer property type."""
    def __init__(self, device, ki):
        KonnectedProperty.__init__(self, device,
                                  'humidity', {'title': 'Humidity',
                                               'label': 'Humidity',
                                               '@type': 'LevelProperty',
                                               'type': 'number',
                                               'unit': 'percent',
                                               'readOnly': True,
                                               'minimum': 0,
                                               'maximum': 100})
        self.ki = ki

    def get_new_value(self):
        return self.ki.get_humidity()

class KIAlarmProperty(KonnectedProperty):
    """Alarm integer property type."""
    def __init__(self, device, ki):
        KonnectedProperty.__init__(self, device,
                                  'alarm', {'title': 'Siren',
                                               'label': 'Siren',
                                               'type': 'boolean',
                                               '@type': 'AlarmProperty'
                                               'readOnly': True})
        self.ki = ki

    def get_new_value(self):
        return self.ki.get_alarm()

class KIDoorProperty(KonnectedProperty):
    """Alarm integer property type."""
    def __init__(self, device, ki, zone):
        KonnectedProperty.__init__(self, device,
                                  'zone_'+zone, {'title': 'Zone'+zone,
                                               'label': 'Zone'+zone,
                                               'type': 'boolean',
                                               '@type': 'OpenProperty',
                                               'readOnly': True})
        self.ki = ki
        self.zone = zone

    def get_new_value(self):
        return self.ki.get_zone_status(self.zone)
