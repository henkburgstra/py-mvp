#
#  -*- coding: iso8859-1 -*-
#  openac/logica/view/__init__.py
#
from include.ordereddict import OrderedDict
from viewmodel import ViewField, ViewModel

class ViewLayout(object):
    """
    Opsomming van layout typen voor ViewGroup
    """
    VERTICAL = "VERTICAL"
    HORIZONTAL = "HORIZONTAL"
    FLEXGRID = "FLEXGRID"

class ViewGroup(object):
    """
    Layout en andere opmaak voor een verzameling van velden
    """
    def __init__(self, name, layout, fieldcount=0):
        self._name = name
        self._layout = layout
        self._fieldcount = fieldcount
        self._header = None
        
    def get_name(self):
        return self._name
    
    def set_name(self, name):
        self._name = name
        
    def get_layout(self):
        return self._layout
    
    def set_layout(self, layout):
        self._layout = layout
        
    def get_fieldcount(self):
        return self._fieldcount
        
    def set_fieldcount(self, fieldcount):
        self._fieldcount = fieldcount

    def get_header(self):
        return self._header

    def set_header(self, header):
        self._header = header
        
    name = property(get_name, set_name)
    layout = property(get_layout, set_layout)
    fieldcount = property(get_fieldcount, set_fieldcount)
    header = property(get_header, set_header)
    
    def inc_fieldcount(self):
        self._fieldcount += 1

        
class ViewContainer(object):
    """
    Koppeling tussen de 'abstracte' ViewGroup en
    de concrete implementatie van een containertype
    """
    def __init__(self, viewgroup, impl):
        self._group = viewgroup
        self._impl = impl
        
    def get_impl(self):
        return self._impl
    
    def set_impl(self, impl):
        self._impl = impl
        
    impl = property(get_impl, set_impl)
        
    @property
    def name(self):
        return self._group.name
    
    @property
    def layout(self):
        return self._group.layout
    
    @property
    def fieldcount(self):
        return self._group.fieldcount

    @property
    def header(self):
        return self._group.header

    
class ViewEvent(object):
    def __init__(self, event_type, control_id, value=None):
        self._event_type = event_type
        self._control_id = control_id
        self._value = value
        
    def get_event_type(self):
        return self._event_type
    
    def get_control_id(self):
        return self._control_id
    
    def get_value(self):
        return self._value


class View(object):
    DLG_OK = "DLG_OK"
    DLG_OK_CANCEL = "DLG_OK_CANCEL"
    DLG_YES_NO = "DLG_YES_NO"

    CMD_OK = "CMD_OK"
    CMD_CANCEL = "CMD_CANCEL"
    CMD_YES = "CMD_YES"
    CMD_NO = "CMD_NO"

    def __init__(self, impl, presenter):
        self._impl = impl
        self._title = ""
        self._presenter = presenter
        self._model = self._presenter.get_viewmodel()
        self._fields = OrderedDict()
        self._groups = OrderedDict()
        self._presenter.set_view(self)
        self._groupcounter = {}  # veldnaam => counter, t.b.v. geneste groepen met herhalende records 
        self._receiving = False  #  voorkom deadlocks; geef geen events door aan presenter als _receiving True is.
        self._main_group = ViewGroup("main", ViewLayout.VERTICAL)
        if impl:
            impl.set_base(self)


    def get_impl(self):
        return self._impl
    
    def set_impl(self, impl):
        self._impl = impl
        if impl:
            impl.set_base(self)
            
    def get_title(self):
        return self._title
            
    def set_title(self, title):
        self._title = title
        if self._impl:
            self._impl.set_title(title)
    
    def clear_fields(self):
        if self._impl:
            self._impl.clear_fields()
        self._fields = OrderedDict()
            
    
    def clear_groups(self):
        self._groups = OrderedDict()
        

    def add_to_group(self, *args):
        """
        Maak veldgroepen aan. De volgende methods zijn toolkit-afhankelijk
        en zitten daarom in een toolkit-specifieke implementatie (bijv. desktop/wx_view):
        - create_container()
        - add_to_container()
        - create_field
        
        add_to_group() wordt aangeroepen vanuit Presenter.load_data().
        """
        if not self._impl:
            return
        container = None
        thing = None

        if len(args) == 1:
            thing = args[0]
        elif len(args) > 1:
            container = args[0]
            thing = args[1]
            
        containers = {}

        if container is None:
            assert isinstance(thing, ViewModel), "%r is not an instance of ViewModel" % thing
            main_container = self._groups.get("main")
        
            if not main_container:
                self._groups["main"] = self._impl.create_container(self._main_group)
                
            containers["main"] = self._groups["main"]
            viewgroup = getattr(thing, "__group__", None)

            if viewgroup is None:
                container = containers["main"]
            else:
                container = self._impl.create_container(viewgroup)
                containers[viewgroup.name] = container
                self._impl.add_to_container(containers["main"], container)
            
        if isinstance(thing, ViewModel):
            model = thing  #  voor de leesbaarheid

            for fieldname in model.get_field_attributes().keys():
                modelfield = model.get_field(fieldname)
                
                if modelfield.__fieldtype__ == "title":
                    self.set_title(modelfield.get_value())
                    continue
                
                if modelfield.group is None:
                    if modelfield.__fieldtype__ in ("one_to_one", "one_to_many"):
                        fieldcontainer = self._impl.create_container(self._main_group)
                        self._impl.add_to_container(container, fieldcontainer)
                    else:
                        fieldcontainer = container
                else:
                    fieldcontainer = containers.get(modelfield.group.name)
                    if fieldcontainer is None:
                        containers[modelfield.group.name] = fieldcontainer = self._impl.create_container(modelfield.group)
                        self._impl.add_to_container(container, fieldcontainer)
                
                self.add_to_group(fieldcontainer, modelfield)
                
        elif isinstance(thing, ViewField):
            viewfield = thing  #  voor de leesbaarheid
            if viewfield.__fieldtype__ in ("one_to_one", "one_to_many"):
                collectiongroup = viewfield.group or self._main_group
                if collectiongroup.layout in [ViewLayout.FLEXGRID]:
                    if collectiongroup.header:
                        self.add_to_group(container, collectiongroup.header)
                    rows = viewfield.get_value()
                    for row in rows:
                        self.add_to_group(container, row)
                else:
                    item_count = len(viewfield.get_value())
                    for model in viewfield.get_value():
                        modelcontainer = self._impl.create_container(getattr(model, "__group__", None) or self._main_group)
                        self._impl.add_to_container(container, modelcontainer)
                        self.add_to_group(modelcontainer, model)
                        
                    if item_count == 0:
                        self._impl.add_to_container(container, None)
            
            else:
                self._impl.add_to_container(container, self._impl.create_field(viewfield, viewfield.get_value()))
                
        
    def update_view(self):
        if not self._impl:
            return
        self._impl.update_view()
        
    def on(self, event):
        if not self._impl:
            return
        self._impl.on(event)

    def set_field_attr(self, field, attr, value):
        if type(field) in (str, unicode, int):
            field = self._model.get_field(field)
        if not field:
            return
        field.set(attr, value)
        self.on(ViewEvent(attr, field.get_id(), value=value))
    
    def open_dossier(self, patient_key):
        if not self._impl:
            return
        self._impl.open_dossier(patient_key)
        
    def messagebox(self, title, message, dialog_type=None):
        if not self._impl:
            return
        if dialog_type is None:
            dialog_type = self.DLG_OK
        return self._impl.messagebox(title, message, dialog_type)
