#
#  -*- coding: iso8859-1 -*-
#  openac/desktop/html_view.py
#
import curses
from curses import panel
from itertools import dropwhile
from logica.views import (View, ViewField, ViewEvent, ViewContainer, ViewLayout)
from logica.views.util import signal, slot
import math

#==============================================================================
#  LAYOUTS
#==============================================================================
#  Layout
#------------------------------------------------------------------------------
class Layout(object):
    def __init__(self):
        self._items = []
        self._x = 0
        self._y = 0
        self._gridmargin = 1

    def get_x(self):
        return self._x

    def set_x(self, x):
        self._x = x

    def get_y(self):
        return self._y

    def set_y(self, y):
        self._y = y

    def get_gridmargin(self):
        return self._gridmargin

    def set_gridmargin(self, margin):
        self._gridmargin = margin

    @property
    def items(self):
        return self._items

    x = property(get_x, set_x)
    y = property(get_y, set_y)
    gridmargin = property(get_gridmargin, set_gridmargin)

    def add(self, item):
        self._items += [item]

    def show(self, x, y):
        self.x = x
        self.y = y
#------------------------------------------------------------------------------
#  VBoxLayout
#------------------------------------------------------------------------------
class VBoxLayout(Layout):
    def __init__(self):
        super(VBoxLayout, self).__init__()

    @property
    def height(self):
        return sum([item.height for item in self._items])

    @property
    def width(self):
        self._items and max([item.width for item in self._items]) or 0

    def show(self, x, y):
        super(VBoxLayout, self).show(x, y)
        for item in self._items:
            if isinstance(item, Window):
                item.layout.show(x, y)
            else:
                item.show(x, y)
            y += item.height

#------------------------------------------------------------------------------
#  HBoxLayout
#------------------------------------------------------------------------------
class HBoxLayout(Layout):
    def __init__(self):
        super(HBoxLayout, self).__init__()
        self._gridmargin = 2

    @property
    def height(self):
        return self._items and max([item.height for item in self._items]) or 0

    @property
    def width(self):
        margin = 1
        return sum([item.width for item in self._items] + [margin] * (len(self._items) - 1))

    def show(self, x, y):
        super(HBoxLayout, self).show(x, y)
        for item in self._items:
            if isinstance(item, Window):
                item.layout.show(x, y)
            else:
                item.show(x, y)
            x += item.width + self.gridmargin

#------------------------------------------------------------------------------
#  GridLayout
#------------------------------------------------------------------------------
class GridLayout(Layout):
    def __init__(self, colcount):
        super(GridLayout, self).__init__()
        self._colcount = colcount
        self._colwidths = []
        self._gridmargin = 2

    def get_colcount(self):
        return self._colcount

    def set_colcount(self, colcount):
        self._colcount = colcount

    @property
    def height(self):
        return self.rowcount

    @property
    def width(self):
        self.calc_colwidths()
        #  som van de breedte van alle kolommen gescheiden door 1 karakter
        return sum(self._colwidths + [self.gridmargin] * (self.colcount - 1))

    @property
    def rowcount(self):
        return int(math.ceil(len(self._items) / float(self.colcount)))

    colcount = property(get_colcount, set_colcount)

    def calc_colwidths(self):
        self._colwidths = [0] * self.colcount
        col = 0
        for item in self._items:
            if item.width > self._colwidths[col]:
                self._colwidths[col] = item.width
                col += 1
                if col == self.colcount:
                    col = 0

    def show(self, x, y):
        super(GridLayout, self).show(x, y)
        if not self._colwidths:
            self.calc_colwidths()
        itemx = x
        itemy = y
        col = 0
        for item in self._items:
            item.show(itemx, itemy)
            itemx += self._colwidths[col] + self.gridmargin
            col += 1
            if col == self.colcount:
                col = 0
                itemx = x
                itemy += 1

#==============================================================================
#  CONTROLS
#==============================================================================
#  Control
#------------------------------------------------------------------------------
class Control(object):
    def __init__(self, parent=None):
        self._parent = parent
        self._id = 0
        self._x = 0
        self._y = 0
        self._width = None
        self._height = 1
        self._window = None
        self._color = curses.color_pair(0)
        self._text = ""
        self._bold = False
        self._can_focus = False
        self._has_focus = False

    def get_parent(self):
        return self._parent

    def set_parent(self, parent):
        self._parent = parent

    def get_id(self):
        return self._id

    def set_id(self, id):
        self._id = id

    def get_x(self):
        return self._x

    def set_x(self, x):
        self._x = x

    def get_y(self):
        return self._y

    def set_y(self, y):
        self._y = y

    def get_width(self):
        return self._width is None and 0 or self._width

    def set_width(self, width):
        self._width = width

    def get_height(self):
        return self._height

    def set_height(self, height):
        self._height = height

    def get_window(self):
        return self._window

    def set_window(self, window):
        self._window = window

    def get_color(self):
        return self._color

    def set_color(self, color):
        self._color = color

    def get_text(self):
        return self._text

    def set_text(self, text):
        self._text = text

    def get_bold(self):
        return self._bold

    def set_bold(self, bold):
        self._bold = bold

    def get_can_focus(self):
        return self._can_focus

    def set_can_focus(self, can_focus):
        self._can_focus = can_focus

    def get_has_focus(self):
        return self._has_focus

    def set_has_focus(self, has_focus):
        self._has_focus = has_focus

    parent = property(get_parent, set_parent)
    id = property(get_id, set_id)
    x = property(get_x, set_x)
    y = property(get_y, set_y)
    width = property(get_width, set_width)
    height = property(get_height, set_height)
    window = property(get_window, set_window)
    color = property(get_color, set_color)
    text = property(get_text, set_text)
    bold = property(get_bold, set_bold)
    can_focus = property(get_can_focus, set_can_focus)
    has_focus = property(get_has_focus, set_has_focus)

    def show(self, x, y):
        self.x = x
        self.y = y
        if self._window is None:
            self._window = self.parent.window.subwin(self.height, self.width, y, x)

    def focus(self):
        self._has_focus = True

    def blur(self):
        self._has_focus = False
#------------------------------------------------------------------------------
#  Label
#------------------------------------------------------------------------------
class Label(Control):
    def __init__(self, parent=None, label=""):
        super(Label, self).__init__(parent=parent)
        self._label = label

    def get_label(self):
        return self._label

    def set_label(self, label):
        self._label = label

    def get_height(self):
        return 1

    def set_height(self, height):
        super(Label, self).set_height(height)

    def get_width(self):
        if self._width is None:
            self._width = len(self.label)
        return self._width

    def set_width(self, width):
        super(Label, self).set_width(width)

    def get_color(self):
        if self.bold:
            self._color |= curses.A_BOLD
        return self._color

    def set_color(self, color):
        super(Label, self).set_color(color)

    def get_text(self):
        return self.label

    def set_text(self):
        super(Label, self).set_text(self)

    height = property(get_height, set_height)
    width = property(get_width, set_width)
    label = property(get_label, set_label)
    color = property(get_color, set_color)
    text = property(get_text, set_text)

    @signal(signaltype=str)
    def on_click(self, value):
        pass

    def show(self, x, y):
        super(Label, self).show(x, y)
        try:
            self.window.addstr(self.height / 2, (self.width - len(self.text)) / 2, self.text, self.color)
        except:
            pass

#------------------------------------------------------------------------------
#  Hyperlink
#------------------------------------------------------------------------------
class Hyperlink(Label):
    def __init__(self, parent=None, label=""):
        super(Hyperlink, self).__init__(parent=parent, label=label)
        self._can_focus = True

    def get_width(self):
        return super(Hyperlink, self).get_width() + 4

    def set_width(self, width):
        super(Hyperlink, self).set_width(width)

    def get_height(self):
        self._height = super(Hyperlink, self).get_height() + 2
        return self._height

    def set_height(self, height):
        super(Hyperlink, self).set_height(height)

    def get_color(self):
        self._color |= curses.A_BOLD
        self._color |= curses.A_UNDERLINE
        return self._color

    def set_color(self, color):
        super(Hyperlink, self).set_color(color)

    color = property(get_color, set_color)
    width = property(get_width, set_width)
    height = property(get_height, set_height)

    def focus(self):
        super(Hyperlink, self).focus()
        curses.curs_set(0)  # cursor uit

        while True:
            key = self.window.getch()
            if key in (9, 27, curses.KEY_UP, curses.KEY_DOWN):
                return key

#------------------------------------------------------------------------------
#  Button
#------------------------------------------------------------------------------
class Button(Label):
    def __init__(self, parent=None, label=""):
        super(Button, self).__init__(parent=parent, label=label)
        self._can_focus = True

    def get_width(self):
        return super(Button, self).get_width() + 4

    def set_width(self, width):
        super(Button, self).set_width(width)

    def get_height(self):
        self._height = super(Button, self).get_height() + 2
        return self._height

    def set_height(self, height):
        super(Button, self).set_height(height)

    def get_text(self):
        return " %s " % super(Button, self).get_text()

    def set_text(self, text):
        super(Button, self).set_text(text)

    text = property(get_text, set_text)
    width = property(get_width, set_width)
    height = property(get_height, set_height)

    def show(self, x, y):
        super(Button, self).show(x, y)
        self.window.box()

    def focus(self):
        super(Button, self).focus()
        curses.curs_set(0)  # cursor uit
        self.window.addstr(1, 1, self.text, self.color | curses.A_REVERSE)

        while True:
            key = self.window.getch()
            if key == 10:
                self.on_click(self, self.text)
            elif key in (9, 27, curses.KEY_UP, curses.KEY_DOWN):
                return key

    def blur(self):
        super(Button, self).blur()
        self.window.addstr(1, 1, self.text, self.color)
        self.window.refresh()
#------------------------------------------------------------------------------
#  Text
#------------------------------------------------------------------------------
class Text(Control):
    def __init__(self, parent=None, text="", label=""):
        super(Text, self).__init__(parent=parent)
        self._can_focus = True
#------------------------------------------------------------------------------
#  CheckBox
#------------------------------------------------------------------------------
class CheckBox(Label):
    def __init__(self, parent=None, label=""):
        super(CheckBox, self).__init__(parent=parent, label=label)
        self._checked = False
        self._can_focus = True

    def get_checked(self):
        return self._checked

    def set_checked(self, checked):
        self._checked = checked
        self.on_check(self, checked)
        if self.window:
            self.window.addstr(0, 1, self._checked and "X" or " ")
            self.window.move(0, 1)

    def get_width(self):
        width = super(CheckBox, self).get_width()
        return width + 4

    def set_width(self, width):
        super(CheckBox, self).set_width(width)

    def get_text(self):
        return "[%s] %s" % (self.checked and "X" or " ", super(CheckBox, self).get_text())

    def set_text(self, text):
        super(CheckBox, self).set_text(text)

    checked = property(get_checked, set_checked)
    width = property(get_width, set_width)
    text = property(get_text, set_text)

    @signal(signaltype=bool)
    def on_check(self, checked):
        pass

    def focus(self):
        super(CheckBox, self).focus()
        curses.curs_set(1)
        self.window.move(0, 1)

        while True:
            key = self.window.getch()
            if key == 32:
                self.checked = not self.checked
            elif key in (9, 27, curses.KEY_UP, curses.KEY_DOWN):
                return key
#------------------------------------------------------------------------------
#  Line
#------------------------------------------------------------------------------
class Line(Control):
    pass

#==============================================================================
#  WINDOWS
#==============================================================================
#  Window
#------------------------------------------------------------------------------
class Window(object):
    def __init__(self, window=None, parent=None, title=""):
        """
        @p window: curses window object
        @p parent: Window instance or None
        @p title: window title
        """
        self.window = window
        self.parent = parent
        self.title = title
        self._fields = []
        self._layout = None

    def get_layout(self):
        return self._layout

    def set_layout(self, layout):
        self._layout = layout

    @property
    def width(self):
        return self.layout and self.layout.width or 0

    @property
    def height(self):
        return self.layout and self.layout.height or 0

    @property
    def fields(self):
        if self._fields:
            return self._fields
        self.get_fields(self.layout)
        return self._fields

    layout = property(get_layout, set_layout)

    def get_fields(self, layout):
        for item in layout.items:
            if isinstance(item, Window):
                self.get_fields(item.layout)
            elif isinstance(item, Layout):
                self.get_fields(item)
            else:
                self._fields += [item]

    def show(self):
        self.window.refresh()
#------------------------------------------------------------------------------
#  CursesView
#------------------------------------------------------------------------------
class CursesView(Window):
    """
    View mixin voor Curses
    """
    def __init__(self, window=None, parent=None, title=""):
        super(CursesView, self).__init__(window=window, parent=parent, title=title)
        self._base = None

    def get_base(self):
        return self._base
    
    def set_base(self, base):
        self._base = base
        
    def create_container(self, group):
        if group.layout == ViewLayout.HORIZONTAL:
            return ViewContainer(group, HBoxLayout())
        elif group.layout == ViewLayout.VERTICAL:
            return ViewContainer(group, VBoxLayout())
        elif group.layout == ViewLayout.FLEXGRID:
            return ViewContainer(group, GridLayout(colcount=group.fieldcount))
        return ViewContainer(group, VBoxLayout())
    
    def add_to_container(self, container, item):
        #  Als item None is, voeg dan een placeholder toe aan de sizer.
        if item == None:
            item = Label(parent=self, label=" ")
        elif isinstance(item, ViewContainer):
            item = item.impl
        container.impl.add(item)

    def get_control_id(self, field_id):
        return field_id

    def get_field_id(self, control_id):
        return control_id
    
    def create_field(self, modelfield, value):
        control_id = self.get_control_id(modelfield._idx)
        width = modelfield.width or -1
        field = None
        if modelfield.__fieldtype__ == "checkbox":
            field = CheckBox(parent=self, label=modelfield._label)
            field.checked = bool(value)
            field.on_check.connect(self, "on_check")
        elif modelfield.__fieldtype__ == "line":
            field = Line(parent=self) # TODO: style=LI_HORIZONTAL, LI_VERTICAL
        elif modelfield.__fieldtype__ == "list":
            field = VBoxLayout()
            for item in value:
                field.add(Label(parent=self, label=item))
        elif modelfield.__fieldtype__ == "hyperlink":
            field = Hyperlink(parent=self, label=str(value))
            field.on_click.connect(self, "on_click")
        elif modelfield.__fieldtype__ == "label":
            field = Label(parent=self, label=str(value))
        elif modelfield.__fieldtype__ == "header":
            field = Label(parent=self, label=str(value))
            field.bold = True
        elif modelfield.__fieldtype__ == "text":
            field = Text(parent=self, text=str(value))
        elif modelfield.__fieldtype__ == "button":
            field = Button(parent=self, label=modelfield._label)
            field.on_click.connect(self, "on_click")
        else:
            field = Label(parent=self, label=str(value))

        if field is not None:
            field.id = control_id

        if not modelfield.visible:
            field.Show(False)
        if not modelfield.enabled:
            field.Enable(False)
        return field
        
    def clear_fields(self, sizer=None):
        if self._base is None:
            return
        if sizer is not None:
            children = sizer.items
            for child in children:
                if isinstance(child, Layout):
                    self.clear_fields(sizer=child)
                elif isinstance(child, Window):
                    pass
                sizer.remove(child)
            return
        container = self._base._groups.get("main")
        if container and container.impl:
            sizer = container.impl
            window = sizer.GetContainingWindow()
            self.clear_fields(sizer)
            del self._base._groups["main"]

    def update_view(self):
        if not self._base:
            return
        layout = self.layout
        container = self._base._groups.get("main")
        if container:
            main_layout = container.impl
        else:
            main_layout = None
        if main_layout:
            pass
            #main_layout.ShowItems(False)

        try:
            #self.SetCursor(wx.StockCursor(wx.CURSOR_WAIT))
            #self.Freeze()
            self._base._presenter.load_data()
        finally:
            pass
            #self.SetCursor(wx.StockCursor(wx.CURSOR_DEFAULT))
            #self.Thaw()

        container = self._base._groups.get("main")
        if container:
            main_layout = container.impl
        else:
            main_layout = VBoxLayout()
        layout.add(main_layout)


    def get_field_by_id(self, id):
        for field in self.fields:
            if field.id == id:
                return field

    def focus_fields(self):
        return [field.id for field in self.fields if field.can_focus]

    def focus(self):
        focus_fields = self.focus_fields()
        if focus_fields:
            self.focus_field = self.get_field_by_id(focus_fields[0])
            if self.focus_field:
                while True:
                    key = self.focus_field.focus()
                    if key in (9, curses.KEY_DOWN):
                        next_fields = [id for id in dropwhile(lambda x: x != self.focus_field.id, focus_fields)]
                        if len(next_fields) > 1:
                            field_id = next_fields[1]
                        else:
                            field_id = focus_fields[0]
                        focus_field = self.get_field_by_id(field_id)
                        if focus_field != self.focus_field:
                            self.focus_field.blur()
                            self.focus_field = focus_field

    @slot(signaltype=bool)
    def on_check(self, sender, checked):
        if self._base is None:
            return
        self._base._presenter.on(ViewEvent("check", sender.id, value=checked))
        
    @slot(signaltype=str)
    def on_click(self, sender, _):
        if self._base is None:
            return
        self._base._presenter.on(ViewEvent("click", sender.id))


    def set_title(self, title):
        pass  # implementatie in afgeleide klasse
    
    def on(self, event):
        if self._base is None:
            return
        event_type = event.get_event_type()
        control_id = event.get_control_id()
        value = event.get_value()
        control = self._base._fields.get(control_id)
        if not control:
            return
        
        if event_type == ViewField.VISIBLE:
            control.Show(value)
        elif event_type == ViewField.ENABLED:
            control.Enable(value)

    def messagebox(self, title, message, dialog_type):
        dialog = Dialog(parent=self, title=title, message=message, dialog_type=dialog_type)
        resp = dialog.show()
        dialog.hide()
        return resp

#------------------------------------------------------------------------------
#  Dialog
#------------------------------------------------------------------------------
class Dialog(Window):
    def __init__(self, window=None, parent=None, title="", message="", dialog_type=View.DLG_OK):
        super(Dialog, self).__init__(window=window, parent=parent, title=title)
        #  TODO: window aanmaken en grootte berekenen
        self.window = curses.newwin(10, 60, )
        self.panel = panel.new_panel(self.window)

    def show(self):
        self.panel.show()
        return View.CMD_OK

    def hide(self):
        self.panel.hide()

