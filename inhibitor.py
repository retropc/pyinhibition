class Inhibitor(object):
  def __init__(self, listener=None):
    self.listener = listener

    self._inhibitions = {}
    self._senders = {}
    self._cookie = 0

    self._was_inhibited = False
    self._update_inhibited(False)

  def _update_inhibited(self, now):
    if now == self._was_inhibited:
      return
    self._was_inhibited = now

    if self.listener:
      self.listener(now)

  @property
  def inhibited(self):
    return self._was_inhibited

  def inhibit(self, sender, path, app, reason):
    self._cookie+=1
    if self._cookie > 60000:
      self._cookie = 1
    cookie = self._cookie

    self._inhibitions[cookie] = (sender, path, app)
    self._senders.setdefault(sender, set()).add(cookie)

    self._update_inhibited(True)

    return cookie

  def uninhibit(self, sender, path, cookie):
    v = self._inhibitions.get(cookie)
    if v is None:
      return

    sender_v, path_v, _ = v
    if (sender_v, path_v) != (sender, path):
      return
    del self._inhibitions[cookie]

    sender_cookies = self._senders[sender]
    sender_cookies.remove(cookie)
    if not sender_cookies:
      del self._senders[sender]

    self._update_inhibited(bool(self._senders))

  def sender_terminated(self, sender):
    v = self._senders.get(sender)
    if v is None:
      return

    for cookie in v:
      del self._inhibitions[cookie]

    del self._senders[sender]

    if not self._senders:
      self._update_inhibited(False)
