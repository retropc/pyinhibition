import dbus
import dbus.service
import dbus.mainloop.glib
import inhibitor
import logging

logger = logging.getLogger(__name__)

class FakeScreenSaver(dbus.service.Object):
  def __init__(self, session_bus, path, inhibitor, on_lock):
    self.inhibitor = inhibitor
    self.on_lock = on_lock
    self.path = path
    name = dbus.service.BusName("org.freedesktop.ScreenSaver", bus=session_bus)
    dbus.service.Object.__init__(self, name, path)

  @dbus.service.method("org.freedesktop.ScreenSaver", in_signature="ss", out_signature="u", sender_keyword="sender")
  def Inhibit(self, application_name, reason_for_inhibit, sender=None):
    logger.debug("FakeScreenSaver Inhibit %r %r %r" % (application_name, reason_for_inhibit, sender))
    return self.inhibitor.inhibit(sender, self.path, application_name, reason_for_inhibit)

  @dbus.service.method("org.freedesktop.ScreenSaver", in_signature="u", out_signature="", sender_keyword="sender")
  def UnInhibit(self, cookie, sender=None):
    logger.debug("FakeScreenSaver Uninhibit %r %r" % (cookie, sender))
    self.inhibitor.uninhibit(sender, self.path, cookie)

  @dbus.service.method("org.freedesktop.ScreenSaver", in_signature="", out_signature="")
  def Lock(self):
    logger.debug("FakeScreenSaver Lock")
    self.on_lock()

  @dbus.service.method("org.freedesktop.ScreenSaver", in_signature="", out_signature="b")
  def GetActive(self):
    logger.debug("FakeScreenSaver GetActive")
    return self.inhibitor.inhibited

  @dbus.service.method("org.freedesktop.ScreenSaver", in_signature="", out_signature="b", sender_keyword="sender")
  def Reset(self, sender=None):
    logger.debug("FakeScreenSaver Reset")
    cookie = self.inhibitor.inhibit(sender, self.path, "pyautolock", "resetting inhibitor")
    self.inhibitor.uninhibit(cookie, sender)

class ScreensaverFacade(object):
  def __init__(self, on_lock, inhibition_changed):
    self.inhibitor = inhibitor.Inhibitor(inhibition_changed)

    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    session_bus = dbus.SessionBus()

    fake = FakeScreenSaver(session_bus, "/org/freedesktop/ScreenSaver", self.inhibitor, on_lock)
    fake2 = FakeScreenSaver(session_bus, "/ScreenSaver", self.inhibitor, on_lock)

    dbus_obj = session_bus.get_object("org.freedesktop.DBus", "/org/freedesktop/DBus")
    dbus_obj.connect_to_signal("NameOwnerChanged", self.__name_owner_changed)

  @property
  def active(self):
    return self.inhibitor.inhibited

  def __name_owner_changed(self, name, old_name, new_name):
    logger.debug("FakeScreenSaver NameOwnerChanged name=%r old=%r new=%r" % (name, old_name, new_name))
    if new_name == "":
      self.inhibitor.sender_terminated(name)
