#
#  -*- coding: iso8859-1 -*-
#  /ui/wx/__init__.py
#
import sys
from PySide import QtGui
from ui.qt.qt_view import QtView
from kern.test.view import TestPresenter, TestModel, TestView


class TestPanel(QtView):
    def __init__(self, parent):
        super(TestPanel, self).__init__(parent)
        layout = QtGui.QVBoxLayout()
        self.setLayout(layout)
        self.set_title("TestView")


class TestWindow(QtGui.QMainWindow):
    def __init__(self, title):
        super(TestWindow, self).__init__()
        self.testwidget = TestPanel(self)
        self.setCentralWidget(self.testwidget)
        presenter = TestPresenter(TestModel)
        TestView(self.testwidget, presenter)
        self.testwidget.update_view()
        self.show()


app = QtGui.QApplication(sys.argv)
_ = TestWindow('Test py-mvp')
sys.exit(app.exec_())
