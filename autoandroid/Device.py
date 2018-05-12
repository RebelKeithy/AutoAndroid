import time
from com.dtmilano.android.viewclient import ViewClient


class Device:
    """
    Handle automation of android devices. Handle finding and pressing buttons, switches, etc. Keep track of when the
    view updates.
    """
    def __init__(self):
        d, s = ViewClient.connectToDeviceOrExit()
        self.viewclient = ViewClient(d, s)
        self.dirty = True
        self.time_set_dirty = time.time()
        self.min_update_wait = 0
        self.max_update_wait = 0

    @property
    def dirty(self):
        return self.dirty

    @dirty.setter
    def dirty(self, value):
        self.dirty = value
        if value is True:
            self.time_set_dirty = time.time()

    def refresh(self):
        """
        If the data has been marked dirty, wait until min_update_wait seconds has passed before getting the data dump
        from the device. If nothing has changed, continue updating the data dump until max_update_wait seconds has
        passed.

        :return:
        """
        if self.dirty:
            wait_time = self.time_set_dirty + self.min_update_wait - time.time()
            if wait_time < 0:
                wait_time = 0
            old_data = self.viewclient.views
            self.viewclient.dump(sleep=wait_time)
            while time.time() < self.time_set_dirty + self.max_update_wait:
                if self.has_data_changed(old_data, self.viewclient.views):
                    break

                old_data = self.viewclient.views
                self.viewclient.dump()

            self.dirty = False

    def has_data_changed(self, old_data, new_data):
        """Compare old_data with the current data, if view's data has changed, return true"""