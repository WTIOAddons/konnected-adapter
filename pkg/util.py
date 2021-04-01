"""Utility functions."""

import datetime
import ephem
import logging
import pytz
import math


class DT():
    def __init__(self, timezone, lat, lng, horizon):
        self.timezone = timezone
        self.lat = lat
        self.lng = lng
        self.horizon = horizon
        self.iix = 1200
        self.azimuth = 0  # will compute in calc_sunrise
        self.elevation = 0  # will compute in calc_sunrise
        self.computetoggle = 0
        self.last_sunrise = None
        self.last_sunset = None
        self.next_sunrise = self.calc_sunrise()
        self.next_sunset = self.calc_sunset()
        self.minute = self.now()-datetime.timedelta(minutes=2)
        self.next_time = 0
        self.last_time = 0
        logging.info('DTS lat: %s lng: %s', self.lat, self.lng)

    def now(self):
        return datetime.datetime.now(tz=pytz.timezone(self.timezone))

    def timestamp(self):
        """
        Get the current time.
        Returns the current time in the form YYYY-mm-ddTHH:MM:SS+00:00
        """
        return self.now().strftime('%Y-%m-%dT%H:%M:%S+00:00')

    def get_year(self):
        return self.now().year

    def get_month(self):
        return self.now().month

    def get_day(self):
        return self.now().day

    def get_weekday(self):
        return self.now().weekday()

    def is_sat_sun(self):
        isoweekday = self.now().isoweekday()
        return isoweekday > 5

    def is_even_minute(self):
        minute = self.now().minute
        even = minute % 2
        return even == 0

    def is_even_hour(self):
        hour = self.now().hour
        even = hour % 2
        return even == 0

    def get_minute(self):
        return self.now().minute

    def compute_azel(self):
        if (self.is_even_minute() and
            self.computetoggle == 0) or (self.is_even_minute() is False and
                                         self.computetoggle == 1):
            self.computetoggle = 1 - self.computetoggle
            observer_today = self.get_observer()
            s = ephem.Sun(observer_today)
            self.azimuth = s.az.znorm * 180 / math.pi
            self.elevation = s.alt.znorm * 180 / math.pi

    def get_azimuth(self):
        self.compute_azel()
        return self.azimuth

    def get_elevation(self):
        self.compute_azel()
        return self.elevation

    def get_hour(self):
        return self.now().hour

    def get_observer(self):
        # Make an observer
        observer_today = ephem.Observer()
        # observer_today.date = self.now()
        observer_today.date = datetime.datetime.now(tz=pytz.timezone('UTC'))

        # Location of Göteborg, Sweden long 11.89 lat 57.67
        observer_today.lon = self.lng
        observer_today.lat = self.lat

        # Elevation, in metres
        observer_today.elev = 25
        observer_today.pressure = 0
        # To get U.S. Naval Astronomical Almanac values, use these settings
        # observer_today.horizon = '-0:34'
        # observer_today.horizon = '-6' #-6=civil twilight, -12=nautical,
        # -18=astronomical
        observer_today.horizon = self.horizon
        return observer_today

    def check_time_now(self, time_to_check, log_txt):
        nu = self.now()
        diff = abs(nu - time_to_check)
        # delta = datetime.timedelta(minutes=1)
        self.iix += 1
        if self.iix > 240:
            logging.debug('%s will happen in %s at %s', log_txt, diff,
                          time_to_check)
        if self.iix > 241:
            self.iix = 0
        if diff < datetime.timedelta(minutes=1):
            logging.debug('SUNRISE/SUNSET=%s %s', log_txt, time_to_check)
            return True
        return False

    def calc_sunrise(self):
        observer_today = self.get_observer()
        sunrise = observer_today.next_rising(ephem.Sun())
        sunrise_local = self.to_localtime(sunrise.datetime())
        logging.info('CALC_SUNRISE tdy.utc: %s sunrise: %s sunrise_local: %s',
                     observer_today.date, sunrise, sunrise_local)
        logging.debug('DTSRISE lat: %s lng: %s observer_today: %s',
                      self.lat, self.lng, observer_today)
        observer_today.date = ephem.Date(observer_today.date - 24*ephem.hour)
        sunrise = observer_today.next_rising(ephem.Sun())
        self.last_sunrise = self.to_localtime(sunrise.datetime())
        logging.debug('LAST_SUNRISE old.utc: %s sunrise: %s last_sunrise: %s',
                      observer_today.date, sunrise, self.last_sunrise)
        return sunrise_local

    def sunrise(self):
        if self.next_sunrise + datetime.timedelta(minutes=1) < self.now():
            self.next_sunrise = self.calc_sunrise()
            # force recompute of next/last
            self.minute = self.now()-datetime.timedelta(minutes=2)
            self.compute_nextlast()
            logging.debug('New sunrise %s', self.next_sunrise)
        return self.next_sunrise

    def calc_sunset(self):
        observer_today = self.get_observer()
        sunset = observer_today.next_setting(ephem.Sun())
        sunset_local = self.to_localtime(sunset.datetime())
        logging.info('CALC_SUNSET today.utc: %s sunset: %s sunset_local: %s',
                     observer_today.date, sunset, sunset_local)
        logging.debug('DTSET lat: %s lng: %s observer_today: %s',
                      self.lat, self.lng, observer_today)
        observer_today.date = ephem.Date(observer_today.date - 24*ephem.hour)
        sunset = observer_today.next_setting(ephem.Sun())
        self.last_sunset = self.to_localtime(sunset.datetime())
        logging.debug('LAST_SUNSET old.utc: %s sunset: %s last_sunset: %s',
                      observer_today.date, sunset, self.last_sunset)
        return sunset_local

    def sunset(self):
        if self.next_sunset + datetime.timedelta(minutes=1) < self.now():
            self.next_sunset = self.calc_sunset()
            # force recompute of next/last
            self.minute = self.now()-datetime.timedelta(minutes=2)
            self.compute_nextlast()
            logging.debug('New sunset %s', self.next_sunset)
        return self.next_sunset

    def to_localtime(self, dt):
        utc = pytz.timezone('UTC')
        local_timezone = pytz.timezone(self.timezone)
        # convert from naive to timezone UTC
        dt_utc = dt.replace(tzinfo=utc)
        # convert to localtimezone
        dt_local = dt_utc.astimezone(local_timezone)
        return dt_local

    def get_nexttime(self):
        self.compute_nextlast()
        return self.next_time

    def get_lasttime(self):
        self.compute_nextlast()
        return self.last_time

    def compute_nextlast(self):
        td = self.now() - self.minute
        if td.seconds < 60:
            return None
        self.minute = self.now()
        rise = self.sunrise()
        sset = self.sunset()
        lastrise = self.last_sunrise
        lastset = self.last_sunset
        self.next_time = 0
        self.last_time = 0
        if sset > rise:  # it's dark, sunrise is next, sunset was last
            td = rise - self.now()
            self.next_time = td.seconds/60  # time in minutes to next event
            td = self.now() - lastset
            self.last_time = td.seconds/60
        if rise > sset:  # it's light, sunset is next
            td = sset - self.now()
            self.next_time = td.seconds/60
            td = self.now() - lastrise
            self.last_time = td.seconds/60
        return None
