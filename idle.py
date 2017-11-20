import ctypes

class XScreenSaverInfo(ctypes.Structure):
  _fields_ = [("window",      ctypes.c_ulong),
              ("state",       ctypes.c_int),
              ("kind",        ctypes.c_int),
              ("since",       ctypes.c_ulong),
              ("idle",        ctypes.c_ulong),
              ("event_mask",  ctypes.c_ulong)]

class Display(ctypes.Structure):
 pass

class XWindowAttributes(ctypes.Structure):
  pass

"""
  _fields_ = [("x", ctypes.c_int32),
              ("y", ctypes.c_int32),
              ("width", ctypes.c_int32),
              ("height", ctypes.c_int32),
              ("border_width", ctypes.c_int32),
              ("depth", ctypes.c_int32),
              ("visual", ctypes.c_ulong),
              ("root", ctypes.c_ulong),
              ("class", ctypes.c_int32),
              ("bit_gravity", ctypes.c_int32),
              ("win_gravity", ctypes.c_int32),
              ("backing_store", ctypes.c_int32),
              ("backing_planes", ctypes.c_ulong),
              ("backing_pixel", ctypes.c_ulong),
              ("save_under", ctypes.c_int32),
              ("colourmap", ctypes.c_ulong),
              ("mapinstalled", ctypes.c_uint32),
              ("map_state", ctypes.c_uint32),
              ("all_event_masks", ctypes.c_ulong),
              ("your_event_mask", ctypes.c_ulong),
              ("do_not_propagate_mask", ctypes.c_ulong),
              ("override_redirect", ctypes.c_int32),
              ("screen", ctypes.c_ulong)]
"""

XLIB = ctypes.cdll.LoadLibrary("libX11.so")
XLIB.XOpenDisplay.argtypes = [ctypes.c_char_p]
XLIB.XOpenDisplay.restype = ctypes.POINTER(Display)
XLIB.XDefaultScreen.argtypes = [ctypes.POINTER(Display)]
XLIB.XDefaultScreen.restype = ctypes.c_int
XLIB.XDefaultRootWindow.restype = ctypes.POINTER(XWindowAttributes)
XLIB.XDefaultRootWindow.argtypes = [ctypes.POINTER(Display), ctypes.c_int]

XSS = ctypes.cdll.LoadLibrary("libXss.so.1")
XSS.XScreenSaverAllocInfo.restype = ctypes.POINTER(XScreenSaverInfo)

class IdleQuery(object):
  def __init__(self):
    self.display = XLIB.XOpenDisplay(None)
    self.root = XLIB.XDefaultRootWindow(self.display, XLIB.XDefaultScreen(self.display))
    self.xssinfo = XSS.XScreenSaverAllocInfo()

  def get(self, since=False):
    if self.xssinfo is None or self.display is None:
      return
    XSS.XScreenSaverQueryInfo(self.display, self.root, self.xssinfo)
    return self.xssinfo.contents.idle

  def close(self):
    if self.xssinfo is not None:
      xssinfo, self.xssinfo = self.xssinfo, None
      XSS.XFree(xssinfo)

    if self.display is not None:
      display, self.display = self.display, None
      XLIB.XCloseDisplay(display)

IDLE_QUERY = IdleQuery()
def idle_time():
  return IDLE_QUERY.get()

if __name__ == "__main__":
  i = IdleQuery()
  print(i.get())
  i.close()
