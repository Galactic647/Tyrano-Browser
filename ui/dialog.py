from PySide2.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QSpacerItem, QSizePolicy, QPushButton, QLineEdit
from PySide2.QtCore import Qt


class EditValueDialog(QDialog):
    def __init__(self, header, value, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle(f'Change {header}')
        self.setWindowFlags(self.windowFlags() | Qt.Drawer)

        self.setModal(True)
        self.setFixedSize(600, 80)

        layout = QVBoxLayout()

        self.line_edit = QLineEdit(value)
        layout.addWidget(self.line_edit)

        button_layout = QHBoxLayout()

        button_layout.addItem(QSpacerItem(400, 1, QSizePolicy.Fixed, QSizePolicy.Fixed))
        ok_button = QPushButton("OK")
        cancel_button = QPushButton("Cancel")
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        button_layout.addItem(QSpacerItem(8, 1, QSizePolicy.Fixed, QSizePolicy.Fixed))

        layout.addLayout(button_layout)

        self.setLayout(layout)

        ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        self.line_edit.returnPressed.connect(self.accept)

        self.new_value = None
        
    def accept(self):
        self.new_value = self.line_edit.text()
        super().accept()

