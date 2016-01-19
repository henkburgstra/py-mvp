from util import signal, slot

class SignalTest(object):
    def __init__(self):
        self._name = ""

    def get_name(self):
        return self._name

    def set_name(self, name):
        self._name = name
        self.after_name_changed(self, name)

    name = property(get_name, set_name)

    @signal(signaltype=str)
    def after_name_changed(self, name):
        print "after name changed: %s" % name


class SlotTest(object):
    @slot(signaltype=str)
    def name_slot(self, sender, value):
        print "Slot name: %s, sender: %r" % (value, sender)

signal_test = SignalTest()
print signal_test.after_name_changed.signaltype
slot_test = SlotTest()
signal_test.after_name_changed.connect(slot_test, "name_slot")
signal_test.name = "henk"

