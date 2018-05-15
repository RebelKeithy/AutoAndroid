import time
from com.dtmilano.android.viewclient import ViewClient, View
import logging


class ViewTemplate(object):
    """
    Used to represent a android View object. When you want to find a view, you need to specify which parameters
    to match. It will compare all non None attributes to see if it matches a View.
    """
    def __init__(self):
        self.index = None
        self.text = None
        self.resource_id = None
        self.clazz = None
        self.package = None
        self.content_desc = None
        self.checkable = None
        self.checked = None
        self.clickable = None
        self.enabled = None
        self.focusable = None
        self.focused = None
        self.scrollable = None
        self.long_clickable = None
        self.password = None
        self.selected = None
        self.bounds = None

    @staticmethod
    def from_view(view):
        """Create a ViewTemplate from a ViewClient View"""
        template = ViewTemplate()
        template.index = int(view.map['index'])
        template.text = view.map['text']
        template.resource_id = view.map['resource-id']
        template.clazz = view.map['class']
        template.package = view.map['package']
        template.content_desc = view.map['content-desc']
        template.checkable = view.map['checkable'] == 'true'
        template.checked = view.map['checked'] == 'true'
        template.clickable = view.map['clickable'] == 'true'
        template.enabled = view.map['enabled'] == 'true'
        template.focusable = view.map['focusable'] == 'true'
        template.focused = view.map['focused'] == 'true'
        template.scrollable = view.map['scrollable'] == 'true'
        template.long_clickable = view.map['long-clickable'] == 'true'
        template.password = view.map['password'] == 'true'
        template.selected = view.map['selected'] == 'true'
        template.bounds = view.map['bounds']
        return template

    def __eq__(self, other):
        """Compare each filled out attribute for equality."""
        if type(other) == ViewTemplate:
            print('test')
            for key in self.__dict__:
                print(key + ': (' + repr(self.__dict__[key]) + ', ' + repr(other.__dict__[key]))
                if self.__dict__[key] is not None and other.__dict__[key] is not None:
                    if self.__dict__[key] != other.__dict__[key]:
                        return False
            return True
        elif type(other) == View or issubclass(other.__class__, View):
            other = ViewTemplate.from_view(other)
            return self.__eq__(other)
        else:
            return False


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
        """Return true or false, depending of if data needs to be refreshed"""

        return self.dirty

    @dirty.setter
    def dirty(self, value):
        """Mark the data as needing to be refreshed"""
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
            else:
                logging.debug('update timed out')

            self.dirty = False

    @staticmethod
    def has_data_changed(old_data, new_data):
        """Compare old_data with the current data, if view's data has changed, return true"""
        if len(old_data) != len(new_data):
            return False

        for view1, view2 in zip(old_data, new_data):
            if view1.map != view2.map:
                return False

        return True

    def find_view(self, template):
        """Searches the views on the device and returns a list of views that match the template"""
        self.refresh()
        views = []
        for view in self.viewclient.views:
            if template == view:
                views.append(ViewTemplate.from_view(view))
        return views
