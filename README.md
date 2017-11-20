pyinhibitor
===========

inhibits screensaver while videos are playing by providing dbus interface

supports
========

- chrome
- vlc
- xscreensaver
- any supported xdg-screensaver screensaver

requirements
============

- python 3.5
- python3-dbus
- python3-gi

usage
=====

place in your .xinitrc:

- default (use "/usr/bin/xdg-screensaver reset"): ./pyinhibitor
- custom: ./pyinhibitor [program to run to inhibit screensaver] [arg 1] ...

check status
============

```
dbus-send --print-reply --reply-timeout=2000 --session --dest=org.freedesktop.ScreenSaver --type=method_call /ScreenSaver org.freedesktop.ScreenSaver.GetActive
```

returns true if inhibiting, false otherwise

notes
=====

- chrome will only send supported inhibition events if it detects dpms is on and that either DESKTOP_SESSION=xfce or it detects KDE, see: https://cs.chromium.org/chromium/src/services/device/wake_lock/power_save_blocker/power_save_blocker_x11.cc?q=screensaver&sq=package:chromium&dr=C&l=461
- chrome only sends inhibition events if video is playing in a visible tab

TODO
====

- support vlc pause (trap seeking/pause events) -- currently if paused inhibition continues
- support other chrome dbus APIs for inhibition

WONTFIX
=======

- xdg-screensaver suspend/resume is not supported as it doesn't hold the dbus session open (but forks off another copy... horrible)
