#
#  -*- coding: iso8859-1 -*-
#  openac/logica/view/presenter.py
#
# Domeinmodel moet wijzigingen doorgeven aan de View
# View moet wijzigingen doorgeven aan DomeinModel
# 
from viewmodel import ViewModel

class Presenter(object):
    ON_SAVE = "ON_SAVE"
    ACTION_SAVE = "ACTION_SAVE"
    ACTION_UPDATE = "ACTION_UPDATE"
    
    def __init__(self, *args, **kwargs):
        self._view = None
        self._viewmodel = None
        self._datamodel = None
        self._selection = None
        self._connections = {}
        for arg in args:
            if issubclass(arg, ViewModel):
                self._viewmodel = arg()
        
    def set_viewmodel(self, viewmodel):
        self._viewmodel = viewmodel
        
    def get_viewmodel(self):
        return self._viewmodel
    
    def initialize_viewmodel(self):
        """
        
        """
    
    def set_view(self, view):
        self._view = view
        
    def get_view(self):
        return self._view

    viewmodel = property(get_viewmodel, set_viewmodel)
    view = property(get_view, set_view)
        
    def on(self, event):
        """
        Event handlers, aangeroepen door de view
        """
        event_type = event.get_event_type()
        control_id = event.get_control_id()
        field = self.get_viewmodel().get_field(control_id)
        event_handler = getattr(self, "on_%s_%s" % (field.get_name(), event_type), None)
        if field is None:
            return
        if event_type == "change":
            self._viewmodel.set_value_by_id(control_id, event.get_value())
        elif event_type == "check":
            self._viewmodel.set_value_by_id(control_id, event.get_value())
        elif event_type == "click":
            value = self._viewmodel.get_value_by_id(control_id)
            if value == Presenter.ACTION_SAVE:
                self.save()
            elif value == Presenter.ACTION_UPDATE:
                self.update_view()
        elif event_type == "select":
            field.items.set_value(event.get_value())

        if event_handler:
            event_handler(field)

    
    def select(self, selection=None):
        self._selection = selection
        
    def update_view(self):
        view = self.get_view()
        if view and view._impl:
            view._impl.update_view()
        
    def load_data(self):
        """
        Laad gegevens in het viewmodel
        """
        self._connections = {}
        self.do_load_data()
        self._view.clear_fields()
        self._view.clear_groups()
        self._view.add_to_group(self._viewmodel)
    
    def do_load_data(self):
        """
        De eigenlijke laadactie, aangeroepen door load_data().
        Te implementeren in afgeleide klassen.
        """
        
    def connect(self, connection_type, func):
        connections = self._connections.get(connection_type, [])
        connections += [func]
        self._connections[connection_type] = connections
        
    def save(self):
        connections = self._connections.get(Presenter.ON_SAVE, [])
        for func in connections:
            func()
