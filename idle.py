import ctypes
import threading
import select
import os
import struct
import select

class Display(ctypes.Structure):
  _fields_ = []

class Screen(ctypes.Structure):
  _fields_ = []

class XScreenSaverInfo(ctypes.Structure):
  _fields_ = [("window",      ctypes.c_ulong),
              ("state",       ctypes.c_int),
              ("kind",        ctypes.c_int),
              ("since",       ctypes.c_ulong),
              ("idle",        ctypes.c_ulong),
              ("event_mask",  ctypes.c_ulong)]

class XEvent(ctypes.Structure):
  _fields_ =[("type",  ctypes.c_int),
             ("other", ctypes.c_byte * 500)]

x11 = ctypes.cdll.LoadLibrary("libX11.so")
x11.XOpenDisplay.argtypes = [ctypes.c_char_p]
x11.XOpenDisplay.restype = ctypes.POINTER(Display)
x11.XCloseDisplay.argtypes = [ctypes.POINTER(Display)]

x11.XDefaultScreen.argtypes = [ctypes.POINTER(Display)]
x11.XDefaultScreen.restype = ctypes.c_int
x11.XDefaultRootWindow.argtypes = [ctypes.POINTER(Display), ctypes.c_int]
x11.XConnectionNumber.argtypes = [ctypes.POINTER(Display)]
x11.XConnectionNumber.restype = ctypes.c_int

x11.XNextEvent.argtypes = [ctypes.POINTER(Display), ctypes.POINTER(XEvent)]
x11.XNextEvent.restype = ctypes.c_int

xss = ctypes.cdll.LoadLibrary("libXss.so.1")
xss.XScreenSaverAllocInfo.restype = ctypes.POINTER(XScreenSaverInfo)
xss.XScreenSaverQueryInfo.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p]
xss.XFree.argtypes = [ctypes.c_void_p]

class X(object):
  INT_SIZE = struct.calcsize("i")
  def __init__(self):
    self.__display = x11.XOpenDisplay(None)
    if not self.__display:
      raise Exception("can't connect to display")

    self.__root = x11.XDefaultRootWindow(self.__display, x11.XDefaultScreen(self.__display))
    self.__xssinfo = xss.XScreenSaverAllocInfo()
    self.__x_fd = x11.XConnectionNumber(self.__display)

#    x11.XCreateSimpleWindow.argtypes = [ctypes.POINTER(Display), ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_void_p, ctypes.c_long, ctypes.c_void_p]
#    x11.XSelectInput.argtypes = [ctypes.POINTER(Display), ctypes.c_void_p, ctypes.c_int]
#    x11.XMapWindow.argtypes = [ctypes.POINTER(Display), ctypes.c_void_p]
#    w = x11.XCreateSimpleWindow(self.__display, self.__root, 1, 1, 256, 256, 0, 0, None, 0, None)
#    x11.XSelectInput(self.__display, w, int("1000000000000001", 2))
#    x11.XMapWindow(self.__display, w)

    self.__in_pipe = os.pipe()
    self.__out_pipe = os.pipe()

    self.__thread = threading.Thread(target=self.__run)
    self.__thread.name = "X watchdog"
    self.__thread.daemon = True
    self.__thread.start()

  def __run(self):
    e = XEvent()
    x_fd, in_fd, out_fd, display = self.__x_fd, self.__in_pipe[0], self.__out_pipe[1], self.__display
    while True:
      r, _, _ = select.select([x_fd, in_fd], [], [])
      if x_fd in r:
        x11.XNextEvent(display, e)

      if in_fd in r:
        cmd = os.read(in_fd, 1)

        if not cmd:
          break
        elif cmd == b"i":
          os.write(out_fd, struct.pack("i", self.__idle()))

  def __idle(self):
    display, xssinfo = self.__display, self.__xssinfo
    if xssinfo is None or display is None:
      return -1
    xss.XScreenSaverQueryInfo(display, self.__root, xssinfo)
    return xssinfo.contents.idle

  def idle(self):
    os.write(self.__in_pipe[1], b"i")
    v = os.read(self.__out_pipe[0], self.INT_SIZE)
    return struct.unpack("i", v)[0]

  def close(self):
    if self.__in_pipe is not None:
      in_pipe, out_pipe, self.__in_pipe, self.__out_pipe = self.__in_pipe, self.__out_pipe, None, None
      os.close(in_pipe[1])
      self.__thread.join()
      os.close(in_pipe[0])
      os.close(out_pipe[0])
      os.close(out_pipe[1])

    if self.__xssinfo is not None:
      xssinfo, self.__xssinfo = self.__xssinfo, None
      xss.XFree(xssinfo)
    if self.__display is not None:
      display, self.__display = self.__display, None
      x11.XCloseDisplay(display)

CONN = X()
def idle_time():
  return CONN.idle()

if __name__ == "__main__":
  print(idle_time())
  while True:
    pass
  CONN.close()
