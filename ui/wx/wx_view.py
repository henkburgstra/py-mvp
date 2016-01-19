#
#  -*- coding: iso8859-1 -*-
#  openac/desktop/wx_view.py
#
import wx
from logica.views import (View, ViewField, ViewEvent, ViewContainer, ViewLayout)


class FakeTransparentBackground(object):
    """
    Met deze mixin klasse emuleren we transparantie door de achtergrondbitmap
    van de "desktop" te kopiëren.
    """
    def get_desktop_bitmap(self):
        parent = self.GetParent()
        while parent:
            if hasattr(parent, "_desktop_bitmap"):
                return parent._desktop_bitmap
            parent = parent.GetParent()
        
    def on_background(self, event):
        dc = event.GetDC()
  
        if not dc:
            dc = wx.ClientDC(self)
            rect = self.GetUpdateRegion().GetBox()
            dc.SetClippingRect(rect)

        dc.SetBrush(wx.TRANSPARENT_BRUSH)
        dc.Clear()
        desktop_bitmap = self.get_desktop_bitmap()
        if desktop_bitmap is None:
            return
        
        x, y = self.GetPositionTuple()
        width, height = self.GetSizeTuple()
        bitmap_width = desktop_bitmap.GetWidth()
        bitmap_height = desktop_bitmap.GetHeight()
         
        x_offset = -(x % bitmap_width)
        y_offset = -(y % bitmap_height)
         
        for x in range(x_offset, width, bitmap_width):
            for y in range(y_offset, height, bitmap_height): 
                dc.DrawBitmap(desktop_bitmap, x, y)
    


class TransparentText(wx.StaticText):
    def __init__(self, parent, id=wx.ID_ANY, label='', pos=wx.DefaultPosition, size=wx.DefaultSize, 
        style=wx.TRANSPARENT_WINDOW, name='transparenttext'):
        wx.StaticText.__init__(self, parent, id, label, pos, size, style, name)
        
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_ERASE_BACKGROUND, lambda event: None)
        self.Bind(wx.EVT_SIZE, self.on_size)
    
    def on_paint(self, event):
        bdc = wx.PaintDC(self)
        dc = wx.GCDC(bdc)
    
        font_face = self.GetFont()
        font_color = self.GetForegroundColour()
        
        dc.SetFont(font_face)
        dc.SetTextForeground(font_color)
        if not wx.Platform == "__WXMAC__":
            dc.DrawText(self.GetLabel(), 0, 0)
        event.Skip()
    
    def on_size(self, event):
        self.Refresh()
        event.Skip()
        
        
class Hyperlink(wx.HyperlinkCtrl, FakeTransparentBackground):
    def __init__(self, parent, id=wx.ID_ANY, label="", pos=wx.DefaultPosition, size=wx.DefaultSize):
        url = ""
        FakeTransparentBackground.__init__(self)
        wx.HyperlinkCtrl.__init__(self, parent, id, label, url, pos, size)
        self.SetBackgroundColour((35, 142, 35, 128))
        self.SetHoverColour((255, 255, 255))
        self.SetNormalColour((255, 255, 255))
        self.SetVisitedColour((255, 255, 255))
        self.background = None
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.on_background)
        self.Bind(wx.EVT_SIZE, self.on_size)
        

    def on_paint(self, event):
        pdc = wx.PaintDC(self)
        try:
            dc = wx.GCDC(pdc)
        except:
            dc = pdc

        size = self.GetSize()
        r, g, b = (35, 142, 35)
        rect = wx.Rect(0, 0, size.GetWidth(), size.GetHeight())
        penclr   = wx.Colour(r, g, b, wx.ALPHA_OPAQUE)
        brushclr = wx.Colour(r, g, b, 128)   # half transparent
        dc.SetPen(wx.Pen(penclr))
        dc.SetBrush(wx.Brush(brushclr))
        dc.Clear()
        dc.DrawRectangleRect(rect)
     
        font_face = self.GetFont()
        font_color = self.GetForegroundColour()
         
        dc.SetFont(font_face)
        dc.SetTextForeground(font_color)
        dc.DrawText(self.GetLabel(), 0, 0)
        
        
    def on_size(self, event):
        self.Refresh()
        event.Skip()


class WxView(wx.Panel):
    """
    View mixin voor wxPython
    """
    def __init__(self, parent, style=None):
        wx.Panel.__init__(self, parent) #, style=style)
        self._base = None
        self._base_id = None
        
    def get_base(self):
        return self._base
    
    def set_base(self, base):
        self._base = base
        
    def create_container(self, group):
        if group.layout == ViewLayout.HORIZONTAL:
            return ViewContainer(group, wx.BoxSizer(wx.HORIZONTAL))
        elif group.layout == ViewLayout.VERTICAL:
            return ViewContainer(group, wx.BoxSizer(wx.VERTICAL))
        elif group.layout == ViewLayout.FLEXGRID:
            return ViewContainer(group, wx.FlexGridSizer(rows=0, cols=group.fieldcount, vgap=0, hgap=0))
        return ViewContainer(group, wx.BoxSizer(wx.VERTICAL))
    
    def add_to_container(self, container, item):
        #  Als item None is, voeg dan een placeholder toe aan de sizer.
        if item == None:
            item = TransparentText(self, -1, label=" ")
        elif isinstance(item, ViewContainer):
            item = item.impl
        container.impl.Add(item, 0, wx.ALL, 5)

    def get_control_id(self, field_id):
        if self._base_id is None:
            self._base_id = wx.NewId()
        return self._base_id + field_id
    
    def get_field_id(self, control_id):
        return control_id - self._base_id
    
    def create_field(self, modelfield, value):
        control_id = self.get_control_id(modelfield._idx)
        width = modelfield.width or -1
        field = None
        if modelfield.__fieldtype__ == "checkbox":
            field = wx.CheckBox(self, control_id, label=modelfield._label)
            field.SetValue(bool(value))
            field.Bind(wx.EVT_CHECKBOX, self.on_check)
        elif modelfield.__fieldtype__ == "line":
            field = wx.StaticLine(self, control_id) # TODO: style=LI_HORIZONTAL, LI_VERTICAL
        elif modelfield.__fieldtype__ == "list":
            field = wx.BoxSizer(wx.VERTICAL)
            for item in value:
                field.Add(TransparentText(self, control_id, label=item), 0, wx.BOTTOM, 3)
        elif modelfield.__fieldtype__ == "hyperlink":
            field = Hyperlink(self, control_id, label=str(value), size=(width, -1))
            field.Bind(wx.EVT_HYPERLINK, self.on_click)
        elif modelfield.__fieldtype__ == "label":
            field = TransparentText(self, control_id, label=str(value), size=(width, -1))
        elif modelfield.__fieldtype__ == "header":
            field = TransparentText(self, control_id, label=str(value), size=(width, -1))
            font = field.GetFont()
            font.SetWeight(wx.FONTWEIGHT_BOLD)
            field.SetFont(font)
        elif modelfield.__fieldtype__ == "text":
            field = wx.TextCtrl(self, control_id, str(value), size=(width, -1))
        elif modelfield.__fieldtype__ == "button":
            field = wx.Button(self, control_id, label=modelfield._label)
            field.Bind(wx.EVT_BUTTON, self.on_click)
        elif modelfield.__fieldtype__ == "select":
            field = wx.ComboBox(self, control_id, choices=modelfield.items.values())
            field.Bind(wx.EVT_COMBOBOX, self.on_select)
        else:
            field = TransparentText(self, control_id, label=str(value), size=(width, -1))
        
        if not modelfield.visible:
            field.Show(False)
        if not modelfield.enabled:
            field.Enable(False)
        return field
        
    def clear_fields(self, sizer=None):
        if self._base is None:
            return
        if sizer is not None:
            children = sizer.GetChildren()
            for child in children:
                if child.IsSizer():
                    child_sizer = child.GetSizer()
                    self.clear_fields(sizer=child_sizer)
                    sizer.Remove(child_sizer)
                elif child.IsSpacer():
                    child_spacer = child.GetSpacer()
                    sizer.Remove(child_spacer)
                elif child.IsWindow():
                    child_window = child.GetWindow()
                    sizer.Remove(child_window)
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
        sizer = self.GetSizer()
        container = self._base._groups.get("main")
        if container:
            main_sizer = container.impl
        else:
            main_sizer = None
        if main_sizer:
            main_sizer.ShowItems(False)

        try:
            self.SetCursor(wx.StockCursor(wx.CURSOR_WAIT))
            self.Freeze()
            self._base._presenter.load_data()
        finally:
            self.SetCursor(wx.StockCursor(wx.CURSOR_DEFAULT))
            self.Thaw()

        container = self._base._groups.get("main")
        if container:
            main_sizer = container.impl
        else:
            main_sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(main_sizer)
        sizer.Fit(self)
        
    
    def on_check(self, event):
        if self._base is None:
            return
        checkbox = event.GetEventObject()
        self._base._presenter.on(ViewEvent("check", self.get_field_id(checkbox.GetId()), value=checkbox.GetValue()))
        
    def on_click(self, event):
        if self._base is None:
            return
        try:
            self.SetCursor(wx.StockCursor(wx.CURSOR_WAIT))
            widget = event.GetEventObject()
            self._base._presenter.on(ViewEvent("click", self.get_field_id(widget.GetId())))
        finally:
            self.SetCursor(wx.StockCursor(wx.CURSOR_DEFAULT))

    def on_select(self, event):
        widget = event.GetEventObject()
        selected = widget.GetValue()
        self._base._presenter.on(ViewEvent("select", self.get_field_id(widget.GetId()), value=widget.GetValue()))


        
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

    def messagebox(self, title, message, dialog_type=View.DLG_OK):
        if dialog_type == View.DLG_YES_NO:
            style = wx.ICON_QUESTION | wx.YES_NO
        else:
            style = wx.ICON_INFORMATION | wx.OK
        dlg = wx.MessageDialog(self, message, title, style=style)
        resp = dlg.ShowModal()
        dlg.Destroy()
        if resp == wx.ID_YES:
            return View.CMD_YES
        elif resp == wx.ID_NO:
            return View.CMD_NO
        elif resp == wx.ID_OK:
            return View.CMD_OK
        elif resp == wx.ID_CANCEL:
            return View.CMD_CANCEL

        return View.CMD_OK
