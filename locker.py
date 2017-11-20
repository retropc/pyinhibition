import logging
from gi.repository import GLib

logger = logging.getLogger(__name__)

class Locker(object):
  def __init__(self, locker):
    self.locker = locker

  def reset(self):
    logger.info("triggering reset")
    GLib.spawn_async(self.locker, flags=GLib.SPAWN_STDERR_TO_DEV_NULL|GLib.SPAWN_STDOUT_TO_DEV_NULL)
