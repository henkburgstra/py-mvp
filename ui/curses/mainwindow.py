#
#  -*- coding: iso8859-1 -*-
#  /ui/curses/__init__.py
#
import curses
from ui.curses.curses_view import Window, CursesView, VBoxLayout
from kern.test.view import TestPresenter, TestModel, TestView


class MainWindow(CursesView):
    def __init__(self, window, parent=None, title=""):
        super(MainWindow, self).__init__(window, parent=parent, title=title)
        layout = VBoxLayout()
        self.layout = layout
        self.set_title("TestView")


class CursesApp(Window):
    def __init__(self, window, parent=None, title=""):
        super(CursesApp, self).__init__(window, parent=parent, title=title)

        self.mainwindow = MainWindow(window, parent=self, title="Main Window")
        presenter = TestPresenter(TestModel)
        TestView(self.mainwindow, presenter)
        self.mainwindow.update_view()

        layout = VBoxLayout()
        self.layout = layout
        layout.add(self.mainwindow)

    def show(self):
        self.layout.show(0, 0)
        super(CursesApp, self).show()

    def main_loop(self):
        self.mainwindow.focus()


def curses_init(mainwindow):
    curses.curs_set(0)  # cursor uit
    app = CursesApp(mainwindow)
    app.show()
    app.main_loop()


curses.wrapper(curses_init)