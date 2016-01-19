#
#  -*- coding: iso8859-1 -*-
#  openac/desktop/wx_view.py
#
from PySide import QtCore, QtGui
from logica.views import (View, ViewField, ViewEvent, ViewContainer, ViewLayout)


class QtView(QtGui.QWidget):
    """
    View mixin voor wxPython
    """
    def __init__(self, parent):
        super(QtView, self).__init__(parent)
        self._base = None

    def get_base(self):
        return self._base
    
    def set_base(self, base):
        self._base = base
        
    def create_container(self, group):
        if group.layout == ViewLayout.HORIZONTAL:
            return ViewContainer(group, QtGui.QHBoxLayout())
        elif group.layout == ViewLayout.VERTICAL:
            return ViewContainer(group, QtGui.QVBoxLayout())
        elif group.layout == ViewLayout.FLEXGRID:
            container = ViewContainer(group, QtGui.QGridLayout())
            container.col = 0
            container.row = 0
            return container
        return ViewContainer(group, QtGui.QVBoxLayout())
    
    def add_to_container(self, container, item):
        #  Als item None is, voeg dan een placeholder toe aan de layout.
        if container.impl is None:
            return
        add = container.impl.addWidget
        if item is None:
            item = QtGui.QLabel(" ", parent=self)
        elif isinstance(item, ViewContainer):
            item = item.impl
            add = container.impl.addLayout

        if isinstance(container.impl, QtGui.QGridLayout):
            add(item, container.row, container.col)
            container.col += 1
            if container.col == container._group.fieldcount:
                container.col = 0
                container.row += 1
        else:
            add(item)


    def get_control_id(self, field_id):
        return field_id

    def get_field_id(self, control_id):
        return control_id
    
    def create_field(self, modelfield, value):
        control_id = self.get_control_id(modelfield._idx)
        width = modelfield.width or -1
        field = None

        if modelfield.__fieldtype__ == "checkbox":
            field = QtGui.QCheckBox(modelfield._label, parent=self)
            field.setChecked(bool(value))
            field.stateChanged.connect(self.on_check)
        elif modelfield.__fieldtype__ == "list":
            field = QtGui.QVBoxLayout()
            for item in value:
                label = QtGui.QLabel(item, parent=self)
                if modelfield.width:
                    label.resize(modelfield.width, label.height())
                field.addWidget(label)  # TODO: padding, marges, 0, wx.BOTTOM, 3)
        elif modelfield.__fieldtype__ == "hyperlink":
            field = QtGui.QLabel('<a href="hyperlink">%s</a>' % str(value), parent=self)
            field.linkActivated.connect(self.on_click)
        elif modelfield.__fieldtype__ == "label":
            field = QtGui.QLabel(str(value), parent=self)
        elif modelfield.__fieldtype__ == "header":
            field = QtGui.QLabel("<b>%s</b>" % str(value), parent=self)
        elif modelfield.__fieldtype__ == "text":
            field = QtGui.QLineEdit(str(value), parent=self)
        elif modelfield.__fieldtype__ == "button":
            field = QtGui.QPushButton(modelfield._label, parent=self)
            field.clicked.connect(self.on_click)
        elif modelfield.__fieldtype__ == "select":
            field = QtGui.QComboBox(self)
            field.addItems(modelfield.items.values())
            field.activated[str].connect(self.on_select)
        else:
            field = QtGui.QLabel(str(value), parent=self)

        if field is not None:
            field._py_mvp_id = control_id

        if modelfield.width and modelfield.__fieldtype__ not in ["list"]:
            field.resize(modelfield.width, field.height())
        
        if not modelfield.visible:
            field.setVisible(False)
        if not modelfield.enabled:
            field.setEnabled(False)
        return field
        
    def clear_fields(self):
        if self._base is None:
            return
        container = self._base._groups.get("main")
        if container:
            container.impl.Clear(deleteWindows=True)

    def update_view(self):
        if not self._base:
            return

        layout = self.layout()
        container = self._base._groups.get("main")
        if container:
            main_layout = container.impl
        else:
            main_layout = None
        if main_layout:
            main_layout.ShowItems(False)

        try:
            #QtGui.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
            #self.Freeze()
            self._base._presenter.load_data()
        finally:
            pass
            #QtGui.QApplication.restoreOverrideCursor()
            #self.Thaw()

        container = self._base._groups.get("main")
        if container:
            main_layout = container.impl
        else:
            main_layout = QtGui.QVBoxLayout()
        layout.addLayout(main_layout)

    
    def on_check(self):
        if self._base is None:
            return
        checkbox = self.sender()
        self._base._presenter.on(ViewEvent("check", checkbox._py_mvp_id, value=checkbox.isChecked()))
        

    def on_click(self):
        if self._base is None:
            return
        try:
            QtGui.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
            widget = self.sender()
            self._base._presenter.on(ViewEvent("click", widget._py_mvp_id))
        finally:
            QtGui.QApplication.restoreOverrideCursor()

    def on_select(self, selected):
        widget = self.sender()
        self._base._presenter.on(ViewEvent("select", widget._py_mvp_id, value=selected))


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
            control.setVisible(value)
        elif event_type == ViewField.ENABLED:
            control.setEnabled(value)

    def messagebox(self, title, message, dialog_type=View.DLG_OK):
        dlg = QtGui.QMessageBox(self, title, message)
        dlg.setText(message)

        if dialog_type == View.DLG_YES_NO:
            dlg.setStandardButtons(QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
            dlg.setDefaultButton(QtGui.QMessageBox.Yes)
        else:
            dlg.setStandardButtons(QtGui.QMessageBox.Ok)
            dlg.setDefaultButton(QtGui.QMessageBox.Ok)

        resp = dlg.exec_()
        if resp == QtGui.QMessageBox.Yes:
            return View.CMD_YES
        elif resp == QtGui.QMessageBox.No:
            return View.CMD_NO
        elif resp == QtGui.QMessageBox.Ok:
            return View.CMD_OK
        elif resp == QtGui.QMessageBox.Cancel:
            return View.CMD_CANCEL

        return View.CMD_OK
