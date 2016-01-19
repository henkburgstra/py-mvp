#
#  -*- coding: iso8859-1 -*-
#  /ui/wx/__init__.py
#
import wx
from ui.wx.wx_view import WxView
from kern.test.view import TestPresenter, TestModel, TestView

class TestPanel(WxView):
    def __init__(self, parent):
        WxView.__init__(self, parent)
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(sizer)
        self.set_title("TestView")

class TestFrame(wx.Frame):
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title)

        self.testwidget = TestPanel(self)
        presenter = TestPresenter(TestModel)
        TestView(self.testwidget, presenter)
        self.testwidget.update_view()

        sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(sizer)
        sizer.Add(self.testwidget, 0, wx.ALL, 5)
        sizer.Fit(self)
        
    

app = wx.App()

frame = TestFrame(None, -1, 'Test py-mvp')
frame.Show()

app.MainLoop()