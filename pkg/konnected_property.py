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
    def __init__(self, device, ki, zone, title):
        KonnectedProperty.__init__(self, device,
                                   'temp_'+str(zone), {
                                       'title': title,
                                       'label': title,
                                       '@type': 'LevelProperty',
                                       'type': 'number',
                                       'unit': 'degree celsius',
                                       'readOnly': True,
                                       'minimum': -40, 'maximum': 80
                                   })
        self.ki = ki
        self.zone = zone

    def get_new_value(self):
        return self.ki.get_zone_status(self.zone)


class KIHumidProperty(KonnectedProperty):
    """Hour integer property type."""
    def __init__(self, device, ki, zone, title):
        KonnectedProperty.__init__(self, device,
                                   'humidity_'+str(zone), {
                                       'title': title,
                                       'label': title,
                                       '@type': 'LevelProperty',
                                       'type': 'number',
                                       'unit': 'percent',
                                       'readOnly': True,
                                       'minimum': 0,
                                       'maximum': 100
                                   })
        self.ki = ki
        self.zone = zone

    def get_new_value(self):
        return self.ki.get_zone_humi(self.zone)


class KIArmedProperty(KonnectedProperty):
    """Armed boolean property type."""
    def __init__(self, device, ki):
        KonnectedProperty.__init__(self, device,
                                   'armed', {
                                       'title': 'Armed',
                                       'label': 'Armed',
                                       'type': 'string',
                                       '@type': 'LockedProperty',
                                       'readOnly': True,
                                       'enum': [
                                           'locked',
                                           'unlocked',
                                           'unknown'
                                       ]
                                   })
        self.ki = ki

    def get_new_value(self):
        return self.ki.get_armed()

    def set_value(self, value):
        self.ki.set_armed(value)


class KIAlarmProperty(KonnectedProperty):
    """Alarm integer property type."""
    def __init__(self, device, ki):
        KonnectedProperty.__init__(self, device,
                                   'alarm', {
                                       'title': 'Siren',
                                       'label': 'Siren',
                                       'type': 'boolean',
                                       '@type': 'AlarmProperty',
                                       'readOnly': True
                                   })
        self.ki = ki

    def get_new_value(self):
        return self.ki.get_alarm()


class KIDoorProperty(KonnectedProperty):
    """Door binary property type."""
    def __init__(self, device, ki, zone, title):
        KonnectedProperty.__init__(self, device,
                                   'zone_'+str(zone), {
                                       'title': title,
                                       'label': title,
                                       'type': 'boolean',
                                       '@type': 'OpenProperty',
                                       'readOnly': True
                                   })
        self.ki = ki
        self.zone = zone

    def get_new_value(self):
        return self.ki.get_zone_status(self.zone)


class KIMotionProperty(KonnectedProperty):
    """Motion integer property type."""
    def __init__(self, device, ki, zone, title):
        KonnectedProperty.__init__(self, device,
                                   'zone_'+str(zone), {
                                       'title': title,
                                       'label': title,
                                       'type': 'boolean',
                                       '@type': 'MotionProperty',
                                       'readOnly': True
                                   })
        self.ki = ki
        self.zone = zone

    def get_new_value(self):
        return self.ki.get_zone_status(self.zone)
