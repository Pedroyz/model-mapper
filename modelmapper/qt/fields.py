from __future__ import unicode_literals

import numbers
from datetime import datetime

from modelmapper import compat
from modelmapper.accessors import FieldAccessor
from modelmapper import pubsub


class QWidgetAccessor(FieldAccessor):

    @property
    def widget(self):
        return self.field

    def get_value(self):
        return self.widget.metaObject().userProperty().read(self.widget)

    def set_value(self, value):
        self.widget.metaObject().userProperty().write(self.widget, value)

    def connect_signals(self):
        if self.value_changed:
            self.value_changed.connect(self.publish_changes)

    @property
    def value_changed(self):
        pass

    def publish_changes(self, value):
        pubsub.publish('widget_value_changed', self)

    def clear_error(self):
        pass

    def show_error(self, error):
        pass


class QLineEditAccessor(QWidgetAccessor):

    def get_value(self):
        return self.widget.text()

    def set_value(self, value):
        val = compat.unicode(value) if value else ''
        self.widget.setText(val)

    @property
    def value_changed(self):
        return self.widget.textEdited

    def clear_error(self):
        self.widget.setStyleSheet('border: 1px solid lightgray;'
                                  'border-radius: 5px;')
        self.widget.setToolTip('')
        self.widget.setStatusTip('')

    def show_error(self, error):
        self.widget.setStyleSheet('border: 1px solid red;'
                                  'border-radius: 5px')
        self.widget.setStatusTip(error)
        self.widget.setToolTip(error)


class MemoryListAccessor(QWidgetAccessor):

    def get_value(self):
        return [row[1] for row in self.widget.model().get_objects()]

    def set_value(self, value):
        self.widget.model().set_source(value)


class String(QLineEditAccessor):

    def get_value(self):
        value = super(String, self).get_value()
        return compat.unicode(value) if value else None


class Autocomplete(QLineEditAccessor):

    def get_value(self):
        value = self.widget.value
        return value or None

    def set_value(self, value):
        self.widget.value = value if value is not None else ''

    def reset(self):
        self.widget.clear()

    @property
    def value_changed(self):
        return self.widget.selected

    def clear_error(self):
        self.widget.setStyleSheet('border: 1px solid lightgray;'
                                  'border-radius: 5px;')
        self.widget.setToolTip('')
        self.widget.setStatusTip('')

    def show_error(self, error):
        error = "ERROOOR" if isinstance(error, dict) else error
        self.widget.setStyleSheet('border: 1px solid red;'
                                  'border-radius: 5px')
        self.widget.setStatusTip(error)
        self.widget.setToolTip(error)



class LineDate(QLineEditAccessor):

    def __init__(self, access, parent_accessor=None, from_format='%Y-%m-%dT%H:%M:%S'):
        self.from_format = from_format
        super(LineDate, self).__init__(access, parent_accessor=parent_accessor)

    def set_value(self, value):
        if value and isinstance(value, compat.basestring):
            super(LineDate, self).set_value(datetime.strptime(value, self.from_format))

    def get_value(self):
        value = super(LineDate, self).get_value()
        return datetime.strptime(value, '%d-%m-%Y') if value and value != 'dd-mm-aaaa' else None


class CheckBoxList(QWidgetAccessor):

    def get_value(self):
        return [item.text() for _, item in self.widget.checkedItems()]

    def set_value(self, value):
        pass


class SpinBox(QWidgetAccessor):

    def get_value(self):
        return self.widget.value() if self.widget.text() else None

    def set_value(self, value):
        widget = self.widget
        if value is None:
            widget.setValue(widget.minimum())
            widget.clear()
        elif isinstance(value, numbers.Number):
            widget.setValue(value)
        else:
            widget.setValue(float(value) if '.' in value else int(value))


class Integer(QLineEditAccessor):

    def get_value(self):
        value = super(Integer, self).get_value()
        return int(value) if value else None


class ReadOnlyAccessor(FieldAccessor):

    def set_value(self, value):
        pass

    def get_value(self):
        return self._parent_accessor[self.access]


class PlainTextEdit(QWidgetAccessor):

    def set_value(self, value):
        val = value if value is not None else ''
        self.widget.setPlainText(val)

    def get_value(self):
        return self.widget.toPlainText() or None
