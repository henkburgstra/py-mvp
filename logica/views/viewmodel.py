#
#  -*- coding: iso8859-1 -*-
#  openac/kern/s010_dashboard/viewmodel.py
#
# ModelBase klassen moeten wijzigingen doorgeven aan ViewModel
# m.b.v. SQLAlchemy event.listen()
# Wijzigingen van DomainModel naar ModelBase gebeuren alleen met save
#
import inspect
from include.ordereddict import OrderedDict
from util import counter

#==============================================================================
#  FIELDS
#==============================================================================
#  ViewList
#------------------------------------------------------------------------------
class ViewList(OrderedDict):
    def __init__(self, *args, **kwargs):
        super(ViewList, self).__init__(self, *args, **kwargs)
        self._selected = None
        self._value = None

    def get_selected(self):
        return self._selected

    def set_selected(self, selected):
        self._selected = selected

    def get_value(self):
        return self._value

    def set_value(self, value):
        for key, _value in self.items():
            if value == _value:
                self._selected = key
                break

        self._value = value

    selected = property(get_selected, set_selected)
    value = property(get_value, set_value)

    def append(self, item):
        self[item] = item

    # def clear(self):
    #     self[:] = []

#------------------------------------------------------------------------------
#  ViewField
#------------------------------------------------------------------------------
class ViewField(object):
    __fieldtype__ = "base"
    _class_sequence = 0
    ENABLED = "enabled"
    VISIBLE = "visible"

    def __init__(self, *args, **kwargs):
        self._idx = 0
        self._model = None
        self._name = kwargs.get("name", "")
        self._value = kwargs.get("value")
        self._group = kwargs.get("group")
        self._label = kwargs.get("label", "")
        self._visible = kwargs.get("visible", True)
        self._enabled = kwargs.get("enabled", True)
        self._width = kwargs.get("width")
        if not self._label:
            self._label = self._name
        config = kwargs.get("config")
        if config:
            self.copy_config(config)
            return
        ViewField._class_sequence += 1
        self._sequence = ViewField._class_sequence

    def copy_config(self, config):
        self._group = config._group
        self._label = config._label
        if not self._label:
            self._label = self._name
        self._value = config._value
        self._visible = config._visible
        self._enabled = config._enabled
        self._width = config._width

    #--------------------------------------------------------------------------
    #  ViewField getters, setters
    #--------------------------------------------------------------------------
    def get_id(self):
        return self._idx

    def set_id(self, idx):
        self._idx = idx

    def get_model(self):
        return self._model

    def set_model(self, model):
        self._model = model

    def get_name(self):
        return self._name

    def get_label(self):
        return self._label

    def set_label(self, label):
        self._label = label

    def get_value(self):
        return self._value

    def set_value(self, value):
        self._value = value

    def get_group(self):
        return self._group

    def set_group(self, group):
        self._group = group

    def get_visible(self):
        return self._visible

    def set_visible(self, visible):
        self._visible = visible

    def get_enabled(self):
        return self._enabled

    def set_enabled(self, enabled):
        self._enabled = enabled

    def get_width(self):
        return self._width

    def set_width(self, width):
        self._width = width

    def set(self, attr, value):
        setattr(self, attr, value)

    #--------------------------------------------------------------------------
    #  ViewField properties
    #--------------------------------------------------------------------------
    group = property(get_group, set_group)
    model = property(get_model, set_model)
    label = property(get_label, set_label)
    value = property(get_value, set_value)
    visible = property(get_visible, set_visible)
    enabled = property(get_enabled, set_enabled)
    width = property(get_width, set_width)


#------------------------------------------------------------------------------
#  HiddenField
#------------------------------------------------------------------------------
class HiddenField(ViewField):
    __fieldtype__ = "hidden"
    def __init__(self, *args, **kwargs):
        kwargs["visible"] = False
        super(HiddenField, self).__init__(*args, **kwargs)

#------------------------------------------------------------------------------
#  LineField
#------------------------------------------------------------------------------
class LineField(ViewField):
    __fieldtype__ = "line"

#------------------------------------------------------------------------------
#  TextField
#------------------------------------------------------------------------------
class TextField(ViewField):
    __fieldtype__ = "text"
    def __init__(self, *args, **kwargs):
        super(TextField, self).__init__(*args, **kwargs)

#------------------------------------------------------------------------------
#  DateField
#------------------------------------------------------------------------------
class DateField(TextField):
    __fieldtype__ = "date"

#------------------------------------------------------------------------------
#  LabelField
#------------------------------------------------------------------------------
class LabelField(TextField):
    __fieldtype__ = "label"

#------------------------------------------------------------------------------
#  HeaderField
#------------------------------------------------------------------------------
class HeaderField(LabelField):
    __fieldtype__ = "header"

#------------------------------------------------------------------------------
#  HyperlinkField
#------------------------------------------------------------------------------
class HyperlinkField(LabelField):
    __fieldtype__ = "hyperlink"
    def __init__(self, *args, **kwargs):
        super(HyperlinkField, self).__init__(*args, **kwargs)
        self._link = ""

    def get_link(self):
        return self._link

    def set_link(self, link):
        self._link = link

    link = property(get_link, set_link)

#------------------------------------------------------------------------------
#  TitleField
#------------------------------------------------------------------------------
class TitleField(TextField):
    __fieldtype__ = "title"

#------------------------------------------------------------------------------
#  CheckboxField
#------------------------------------------------------------------------------
class CheckboxField(ViewField):
    __fieldtype__ = "checkbox"

#------------------------------------------------------------------------------
#  ButtonField
#------------------------------------------------------------------------------
class ButtonField(ViewField):
    __fieldtype__ = "button"

#------------------------------------------------------------------------------
#  ItemsField
#------------------------------------------------------------------------------
class ItemsField(ViewField):
    __fieldtype__ = "items"
    def __init__(self, *args, **kwargs):
        super(ItemsField, self).__init__(*args, **kwargs)
        self._value = ViewList()

#------------------------------------------------------------------------------
#  SelectField
#------------------------------------------------------------------------------
class SelectField(ItemsField):
    __fieldtype__ = "select"

    def get_items(self):
        """
        alias voor get_value()
        """
        return super(SelectField, self).get_value()

    def set_items(self, items):
        """
        alias voor set_value()
        """
        self._value = items

    #  alias voor property value
    items = property(get_items, set_items)

#------------------------------------------------------------------------------
#  ListField
#------------------------------------------------------------------------------
class ListField(ItemsField):
    __fieldtype__ = "list"

#------------------------------------------------------------------------------
#  RelationField
#------------------------------------------------------------------------------
class RelationField(ItemsField):
    __fieldtype__ = "relation"
    def __init__(self, *args, **kwargs):
        super(RelationField, self).__init__(*args[1:], **kwargs)
        if kwargs.get("config"):
            return
        assert args, "Geen relatie opgegeven"
        assert issubclass(args[0], ViewModel), "Argument is geen subklasse van ViewModel: %r" % args[0]
        self._relation = args[0]
        if self._group:
            self._group.fieldcount = self.fieldcount
            headers = OrderedDict()
            for fieldname, field in self._relation._fieldattrs.items():
                headers[fieldname] = HeaderField(name=fieldname, value=fieldname.capitalize())
            HeaderCls = type(
                "%sHeader" % self._relation.__name__, (ViewModel,), headers)
            self._group.header = HeaderCls()

    def copy_config(self, config):
        super(RelationField, self).copy_config(config)
        self._relation = config._relation

    def get_relation(self):
        return self._relation

    def set_relation(self, relation):
        self._relation = relation

    relation = property(get_relation, set_relation)

    @property
    def fieldcount(self):
        return len(self._relation._fieldattrs)

#------------------------------------------------------------------------------
#  OneToOne
#------------------------------------------------------------------------------
class OneToOne(RelationField):
    __fieldtype__ = "one_to_one"

#------------------------------------------------------------------------------
#  OneToMany
#------------------------------------------------------------------------------
class OneToMany(RelationField):
    __fieldtype__ = "one_to_many"

#==============================================================================
#  MODELS
#==============================================================================
#  ViewModelMeta
#------------------------------------------------------------------------------
class ViewModelMeta(type):
    """
    Metaclass for ViewModel.
    The purpose of this metaclass is to keep the attributes in the same order
    as in the declaration of a ViewModel, which is not possible with the
    default __dict__ implementatation.
    """
    def __new__(cls, clsname, bases, dct):
        new_cls = type.__new__(cls, clsname, bases, dct)
        # Veldattributen moeten worden afgebeeld in volgorde van declaratie.
        new_cls._fieldattrs = OrderedDict()
        for fieldname, field in sorted(
            inspect.getmembers(
                new_cls,
                lambda member:isinstance(member, ViewField)
            ),
            key=lambda name_and_field:name_and_field[1]._sequence
        ):
            new_cls._fieldattrs[fieldname] = field

        return new_cls

#------------------------------------------------------------------------------
#  ViewModel
#------------------------------------------------------------------------------
class ViewModel(object):
    __metaclass__ = ViewModelMeta

    def __init__(self, **kwargs):
        self._fieldindex = OrderedDict()  #  mapping tussen ids en veldnamen
        self._fltr = None

        #  voor elke instantie van ViewModel krijgen de
        #  veldnamen een uniek id
        for fieldname, classfield in self._fieldattrs.items():
            idx = counter.inc()
            field = classfield.__class__(name=fieldname, config=classfield)
            field._idx = idx
            field.set_model(self)
            object.__setattr__(self, fieldname, field)
            self._fieldindex[idx] = fieldname

    def __getattribute__(self, name):
        if name.startswith("__"):
            return object.__getattribute__(self, name)
        attr = object.__getattribute__(self, name)
        if attr:
            if isinstance(attr, ViewField):
                return attr.get_value()
            else:
                return attr

        return object.__getattribute__(self, name)

    def __setattr__(self, name, value):
        attr = self.__dict__.get(name)
        if attr and isinstance(attr, ViewField):
            attr.set_value(value)
        else:
            object.__setattr__(self, name, value)

    def get_field(self, id_or_name):
        if str(id_or_name).isdigit():
            field_id = int(id_or_name)

            if field_id in self._fieldindex.keys():
                return object.__getattribute__(self, self._fieldindex[field_id])

            for fieldname, fieldtype in self.get_field_attributes().items():
                item = getattr(self, fieldname, None)
                if item:
                    if isinstance(fieldtype, OneToOne):
                        field = item.get_field(id_or_name)
                        if field:
                            return field
                    elif isinstance(fieldtype, OneToMany):
                        for subitem in item:
                            field = subitem.get_field(id_or_name)
                            if field:
                                return field

        else:
            field = self.__dict__.get(id_or_name)
            if field:
                return field


    def __del__(self):
        pass

    def save(self):
        """
        Wijzigingen doorvoeren in de database
        """

    def get_value_by_id(self, field_id):
        if field_id in self._fieldindex.keys():
            return getattr(self, self._fieldindex[field_id], None)

        for fieldname, fieldtype in self.get_field_attributes().items():
            item = getattr(self, fieldname, None)
            if item:
                if isinstance(fieldtype, OneToOne):
                    value = item.get_value_by_id(field_id)
                    if value:
                        return value
                elif isinstance(fieldtype, OneToMany):
                    for subitem in item:
                        value = subitem.get_value_by_id(field_id)
                        if value:
                            return value


    def set_value_by_id(self, field_id, value):
        if field_id in self._fieldindex.keys():
            setattr(self, self._fieldindex[field_id], value)
            return True

        for fieldname, fieldtype in self.get_field_attributes().items():
            item = getattr(self, fieldname, None)
            if item:
                if isinstance(fieldtype, OneToOne):
                    result = item.set_value_by_id(field_id, value)
                    if result:
                        return result
                elif isinstance(fieldtype, OneToMany):
                    for subitem in item:
                        result = subitem.set_value_by_id(field_id, value)
                        if result:
                            return result
        return False

    def get_field_attributes(self):
        """
        Geeft veldattributen terug in de juiste volgorde: de volgorde
        waarin ze zijn gedeclareerd.
        """
        return self._fieldattrs


    def undo(self):
        self.select(fltr=self._fltr)
