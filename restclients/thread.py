"""
This is a wrapper around threading.Thread, but it will only actually thread
if django configuration is enabled.  Otherwise, it will be an object with the
same api where start just calls run and.
"""

import threading
from django.conf import settings

class Thread(threading.Thread):
    _use_thread = False

    def __init__(self, *args, **kwargs):
        if hasattr(settings, "RESTCLIENTS_USE_THREADING"):
            if settings.RESTCLIENTS_USE_THREADING:
                self._use_thread = True

        super(Thread, self).__init__(*args, **kwargs)

    def start(self):
        if self._use_thread:
            super(Thread, self).start()

        else:
            self.run()


    def join(self):
        if self._use_thread:
            return super(Thread, self).join()

        return True
