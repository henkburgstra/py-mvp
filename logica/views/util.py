#
#  -*- coding: iso8859-1 -*-
#  openac/logica/view/util.py
#
import threading

class FieldRef(object):
    def __init__(self, inst, fieldname):
        self._inst = inst
        self._fieldname = fieldname

    def get_value(self):
        if self._inst:
            return getattr(self._inst, self._fieldname, None)
        
    def set_value(self, value):
        if self._inst:
            setattr(self._inst, self._fieldname, value)
            
    value = property(get_value, set_value)

    @property
    def inst(self):
        return self._inst
    
    @property
    def fieldname(self):
        return self._fieldname
    
    
class Counter(object):
    
    def __init__(self):
        self._lock = threading.RLock()
        self._count = 0
    
    def reset(self, ident):
        self._lock.acquire()
        try:
            self._count = 0
        finally:
            self._lock.release()
    
    def inc(self, n=1):
        self._lock.acquire()
        try:
            self._count += n
            if self._count > 1000000000000:
                self._count = 1
        finally:
            self._lock.release()
        return self._count
        
    def dec(self, n=1):
        self._lock.acquire()
        try:
            self._count -= n
        finally:
            self._lock.release()
        return self._count
    
    @property
    def value(self):
        return self._count
 
counter = Counter()

def signal(signaltype=None):

    class Signal(object):
        def __init__(self, func):
            self.func = func
            self._slots = []

        def __call__(self, signal_obj, value=None):
            assert type(value) is signaltype, "Signal argument '%r' %r heeft niet het correcte type %r" % (value, type(value), signaltype)
            dead_slots = []
            for slot_obj, slot_name in self._slots:
                try:
                    slot = getattr(slot_obj, slot_name, None)
                    if slot:
                        assert signaltype is slot.signaltype, \
                            "Slot %r.%s heeft type %r, het signaal van %r schrijft type %r voor" % (
                                slot_obj, slot_name, slot.signaltype, signal_obj, signaltype
                            )
                        slot(slot_obj, signal_obj, value)
                    else:
                        dead_slots += [(slot_obj, slot_name)]
                except:
                    dead_slots += [(slot_obj, slot_name)]

            for slot in dead_slots:
                self._slots.remove(slot)

            result = self.func(signal_obj, value)

            return result

        @property
        def signaltype(self):
            return signaltype

        @property
        def slots(self):
            return self._slots

        def connect(self, obj, name):
            if not (obj, name) in self._slots:
                self._slots += [(obj, name)]

    return Signal


def slot(signaltype=None):

    class Slot(object):
        def __init__(self, func):
            self.func = func

        def __call__(self, slot_obj, sender, value):
            assert type(value) is signaltype, "Signal argument '%r' %r heeft niet het correcte type %r" % (value, type(value), signaltype)
            return self.func(slot_obj, sender, value)

        @property
        def signaltype(self):
            return signaltype

    return Slot
