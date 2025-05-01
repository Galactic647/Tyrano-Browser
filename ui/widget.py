from PySide2.QtWidgets import QTreeWidget, QStyledItemDelegate, QStyleOptionViewItem, QStyle, QStyleOptionButton
from PySide2.QtGui import QBrush, QColor, QPen
from PySide2.QtWidgets import QApplication
from PySide2.QtCore import Qt, QRect

from typing import Union


class CustomCheckboxDelegate(QStyledItemDelegate):
    def __init__(self, parent=None) -> None:
        super(CustomCheckboxDelegate, self).__init__(parent)

    def paint(self, painter, option, index):
        if not index.column() and index.data(Qt.CheckStateRole) is not None:
            opt = QStyleOptionViewItem(option)
            self.initStyleOption(opt, index)
            style = opt.widget.style() if opt.widget else QApplication.style()

            style.drawControl(QStyle.CE_ItemViewItem, opt, painter, opt.widget)
            check_rect = style.subElementRect(QStyle.SE_ItemViewItemCheckIndicator, opt, opt.widget)

            scale = 1.5
            w = check_rect.width()
            h = check_rect.height()
            center = check_rect.center()

            larger_rect = QRect(
                center.x() - int(w * scale / 2),
                center.y() - int(h * scale / 2),
                int(w * scale),
                int(h * scale)
            )

            check_state = index.data(Qt.CheckStateRole)
            cb_opt = QStyleOptionButton()
            cb_opt.state = QStyle.State_Enabled | QStyle.State_Active
            if check_state == Qt.Checked:
                cb_opt.state |= QStyle.State_On
            else:
                cb_opt.state |= QStyle.State_Off

            cb_opt.rect = larger_rect
            style.drawPrimitive(QStyle.PE_IndicatorViewItemCheck, cb_opt, painter, opt.widget)
        else:
            super().paint(painter, option, index)

    def createEditor(self, parent, option, index):
        return None

class NoEditDelegate(QStyledItemDelegate):
    def __init__(self, parent) -> None:
        super(NoEditDelegate, self).__init__(parent=parent)

    def createEditor(self, parent, option, index):
        return None

class CustomEditTreeWidget(QTreeWidget):
    def __init__(self, non_editable_columns: Union[list, tuple], parent=None) -> None:
        super(CustomEditTreeWidget, self).__init__(parent=parent)

        for i in non_editable_columns:
            self.setItemDelegateForColumn(i, NoEditDelegate(self))

class CustomTreeWidget(QTreeWidget):
    def __init__(self, parent=None) -> None:
        super(CustomTreeWidget, self).__init__(parent=parent)

    def dropEvent(self, event):
        super().dropEvent(event)
        self.itemChanged.emit(self.currentItem(), 1)

    def takeTopLevelItem(self, index):
        item = super().takeTopLevelItem(index)
        self.itemChanged.emit(item, 1)
        return item
    
    def removeChildItem(self, parent, item):
        parent.removeChild(item)
        self.itemChanged.emit(item, 1)
    