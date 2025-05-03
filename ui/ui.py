from ui.widget import CustomEditTreeWidget, CustomCheckboxDelegate, CustomTreeWidget
from ui.dialog import EditValueDialog

from PySide2.QtWidgets import (QMainWindow, QAction, QLabel, QWidget, QVBoxLayout, QHBoxLayout, QTreeWidget, QLineEdit,
    QTreeWidgetItem, QProgressBar, QSizePolicy, QAbstractItemView, QPushButton, QSpacerItem, QRadioButton, QTabWidget,
    QGridLayout, QComboBox, QMenuBar, QMenu, QLayout, QTextEdit, QStackedWidget, QColorDialog, QMessageBox)
from PySide2.QtCore import QMetaObject, QRect, QSize, Qt
from PySide2.QtGui import QFont, QBrush, QColor, QIcon

import json

class TyranoBrowserUI(QMainWindow):
    def __init__(self, parent=None):
        super(TyranoBrowserUI, self).__init__(parent)

        self.resize(1111, 874)
        font = QFont()
        font.setPointSize(9)
        self.setFont(font)
        self.setWindowIcon(QIcon('resources/app-icon.ico'))

        with open('theme/default-dark/dark.qss') as file:
            self.setStyleSheet(file.read())
            file.close()

        self.centralwidget = QWidget(self)
        self.setCentralWidget(self.centralwidget)

        # ----- Menu Bar -----
        self.menubar = QMenuBar(self)
        self.menubar.setGeometry(QRect(0, 0, 1693, 21))
        self.menuFile = QMenu(self.menubar)
        self.menuSettings = QMenu(self.menubar)
        self.menuHelp = QMenu(self.menubar)
        self.setMenuBar(self.menubar)

        self.actionLaunch_Game = QAction(self)
        self.actionStop_Game = QAction(self)
        self.actionSave_Table = QAction(self)
        self.actionLoad_Table = QAction(self)
        self.actionSave_Logs = QAction(self)

        self.actionTyrano_Browser_Tutorial = QAction(self)
        self.actionCheck_For_Updates = QAction(self)
        self.actionAbout = QAction(self)

        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuSettings.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())

        self.menuFile.addAction(self.actionLaunch_Game)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionSave_Table)
        self.menuFile.addAction(self.actionLoad_Table)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionSave_Logs)

        self.menuHelp.addAction(self.actionTyrano_Browser_Tutorial)
        self.menuHelp.addSeparator()
        self.menuHelp.addAction(self.actionCheck_For_Updates)
        self.menuHelp.addAction(self.actionAbout)

        # ----- Main Container -----
        self.BaseVLayoutWidget = QWidget(self.centralwidget)
        self.BaseVLayoutWidget.setGeometry(QRect(0, 10, 1111, 831))

        self.MainContainer = QVBoxLayout(self.centralwidget)
        self.MainContainer.setContentsMargins(0, 0, 0, 0)
        self.MainContainer.addWidget(self.BaseVLayoutWidget)

        self.InfoLabel = QLabel(self.BaseVLayoutWidget)
        self.InfoLabel.setFont(font)
        self.InfoLabel.setAlignment(Qt.AlignCenter)
        self.MainContainer.addWidget(self.InfoLabel)

        # ----- Actions Section -----
        self.ActionsSection = QTabWidget(self.BaseVLayoutWidget)
        self.ActionsSection.setFont(font)

        # ----- Tab Widget - Scan Tab -----
        self.ScanTab = QWidget()
        self.ScanTabVLayoutWidget = QWidget(self.ScanTab)
        self.ScanTabVLayoutWidget.setGeometry(QRect(0, 0, 1101, 361))
        self.ScanActionBaseContainer = QVBoxLayout(self.ScanTab)
        self.ScanActionBaseContainer.setContentsMargins(0, 0, 0, 0)

        # ----- Tab Widget - Scan Tab - Scan Progress Bar -----
        self.ScanProgressBar = QProgressBar(self.ScanTabVLayoutWidget)
        self.ScanProgressBar.setObjectName('ScanProgressBar')
        self.ScanProgressBar.setTextVisible(False)
        self.ScanActionBaseContainer.addWidget(self.ScanProgressBar)

        # ----- Tab Widget - Scan Tab - Result Section -----
        self.ResultTab = QTreeWidget(self.ScanTabVLayoutWidget)

        sizePolicy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ResultTab.sizePolicy().hasHeightForWidth())
        self.ResultTab.setSizePolicy(sizePolicy)

        self.ResultTab.setMinimumSize(QSize(700, 0))
        self.ResultTab.setFont(font)
        self.ResultTab.setEditTriggers(QAbstractItemView.DoubleClicked)
        self.ResultTab.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.ResultTab.setSortingEnabled(False)
        self.ResultTab.setIndentation(0)
        self.ResultTab.setItemsExpandable(False)
        self.ResultTab.setExpandsOnDoubleClick(False)
        self.ResultTab.setAllColumnsShowFocus(True)
        self.ResultTab.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ResultTab.doubleClicked.connect(self.rt_move_to_vl)
        self.ResultTab.customContextMenuRequested.connect(self.rt_context_menu)

        # ----- Tab Widget - Scan Tab - Scan Option Section -----
        self.ScanActionContainer = QVBoxLayout()
        self.ScanActionContainer.setSizeConstraint(QLayout.SetFixedSize)

        self.ScanButtonContainer = QGridLayout()
        self.ScanButtonContainer.setHorizontalSpacing(15)
        self.ScanButtonContainer.setContentsMargins(5, -1, 8, -1)

        self.ScanButton = QPushButton(self.ScanTabVLayoutWidget)
        self.ScanButton.setFont(font)
        self.ScanButtonContainer.addWidget(self.ScanButton, 0, 0, 1, 1)

        self.ClearButton = QPushButton(self.ScanTabVLayoutWidget)
        self.ClearButton.setEnabled(False)
        self.ClearButton.setFont(font)
        self.ScanButtonContainer.addWidget(self.ClearButton, 0, 1, 1, 1)

        self.UndoButton = QPushButton(self.ScanTabVLayoutWidget)
        self.UndoButton.setEnabled(False)
        self.UndoButton.setFont(font)
        self.ScanButtonContainer.addWidget(self.UndoButton, 0, 2, 1, 1)
        self.ScanActionContainer.addLayout(self.ScanButtonContainer)

        self.ScanInputContainer = QStackedWidget(self.ScanTabVLayoutWidget)
        self.ScanInputContainer.resize(301, 31)

        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ScanInputContainer.sizePolicy().hasHeightForWidth())
        self.ScanInputContainer.setSizePolicy(sizePolicy)
        self.ScanInputContainer.setMinimumSize(QSize(0, 28))

        self.NormalScanPage = QWidget()
        self.NormalScanPageLayoutWidget = QWidget(self.NormalScanPage)
        self.NormalScanPageContainer = QVBoxLayout(self.NormalScanPage)
        self.NormalScanPageContainer.setContentsMargins(0, 0, 0, 0)

        self.ScanInput = QLineEdit(self.NormalScanPageLayoutWidget)
        self.ScanInput.setFont(font)
        self.ScanInput.returnPressed.connect(self.ScanButton.click)
        self.NormalScanPageContainer.addWidget(self.ScanInput)
        self.ScanInputContainer.addWidget(self.NormalScanPage)

        self.DoubleInputScanPage = QWidget()
        self.DoubleInputScanPageLayoutWidget = QWidget(self.DoubleInputScanPage)
        self.DoubleInputScanPageLayoutWidget.setGeometry(QRect(0, 0, 365, 31))
        self.DoubleInputScanPageContainer = QGridLayout(self.DoubleInputScanPage)
        self.DoubleInputScanPageContainer.setContentsMargins(0, 0, 0, 0)

        self.ScanInputA = QLineEdit(self.DoubleInputScanPageLayoutWidget)
        self.ScanInputA.setFont(font)
        self.DoubleInputScanPageContainer.addWidget(self.ScanInputA, 0, 0, 1, 1)

        self.SearchAndLabel = QLabel(self.DoubleInputScanPageLayoutWidget)
        self.SearchAndLabel.setFont(font)
        self.SearchAndLabel.setAlignment(Qt.AlignCenter)
        self.DoubleInputScanPageContainer.addWidget(self.SearchAndLabel, 0, 1, 1, 1)

        self.ScanInputB = QLineEdit(self.DoubleInputScanPageLayoutWidget)
        self.ScanInputB.setFont(font)
        self.ScanInputA.returnPressed.connect(self.ScanInputB.setFocus)
        self.ScanInputB.returnPressed.connect(self.ScanButton.click)
        self.DoubleInputScanPageContainer.addWidget(self.ScanInputB, 0, 2, 1, 1)
        self.ScanInputContainer.addWidget(self.DoubleInputScanPage)

        self.IgnoreInputScanPage = QWidget()
        self.ScanInputContainer.addWidget(self.IgnoreInputScanPage)
        self.ScanActionContainer.addWidget(self.ScanInputContainer)

        self.ScanActionVSpacerScan2SB = QSpacerItem(20, 5, QSizePolicy.Minimum, QSizePolicy.Maximum)
        self.ScanActionContainer.addItem(self.ScanActionVSpacerScan2SB)

        self.SearchByContainer = QHBoxLayout()
        self.SearchByContainer.setContentsMargins(10, -1, 5, -1)

        self.SearchByLabel = QLabel(self.ScanTabVLayoutWidget)
        self.SearchByLabel.setFont(font)
        self.SearchByContainer.addWidget(self.SearchByLabel)

        self.ValueRadioButton = QRadioButton(self.ScanTabVLayoutWidget)
        self.ValueRadioButton.setFont(font)
        self.ValueRadioButton.setChecked(True)
        self.SearchByContainer.addWidget(self.ValueRadioButton)
        self.ValueRadioButton.toggled.connect(self._update_scan_by)

        self.NameRadioButton = QRadioButton(self.ScanTabVLayoutWidget)
        self.NameRadioButton.setFont(font)
        self.SearchByContainer.addWidget(self.NameRadioButton)

        self.SearchByHSpacerRight = QSpacerItem(50, 20, QSizePolicy.Maximum, QSizePolicy.Minimum)
        self.SearchByContainer.addItem(self.SearchByHSpacerRight)

        self.ScanActionContainer.addLayout(self.SearchByContainer)

        self.ScanActionVSpacerSearchBy2SI = QSpacerItem(20, 5, QSizePolicy.Minimum, QSizePolicy.Maximum)
        self.ScanActionContainer.addItem(self.ScanActionVSpacerSearchBy2SI)

        self.SearchConstraintContainer = QGridLayout()
        self.SearchConstraintContainer.setContentsMargins(6, -1, -1, -1)

        self.SearchTypeInput = QComboBox(self.ScanTabVLayoutWidget)
        self.SearchTypeInput.setFont(font)
        self.SearchConstraintContainer.addWidget(self.SearchTypeInput, 0, 1, 1, 1)
        self.SearchTypeInput.currentIndexChanged.connect(self._update_scan_type)

        self.SearchTypeLabel = QLabel(self.ScanTabVLayoutWidget)
        self.SearchTypeLabel.setFont(font)
        self.SearchTypeLabel.setObjectName('SearchTypeLabel')
        self.SearchConstraintContainer.addWidget(self.SearchTypeLabel, 0, 0, 1, 1)

        self.SearchInHSpacer = QSpacerItem(150, 20, QSizePolicy.Maximum, QSizePolicy.Minimum)
        self.SearchConstraintContainer.addItem(self.SearchInHSpacer, 0, 2, 1, 1)
        self.ScanActionContainer.addLayout(self.SearchConstraintContainer)

        self.ScanActionVSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.ScanActionContainer.addItem(self.ScanActionVSpacer)

        self.FoundLabel = QLabel(self.ScanTabVLayoutWidget)
        self.FoundLabel.setFont(font)
        self.FoundLabel.setObjectName('FoundLabel')
        self.ScanActionContainer.addWidget(self.FoundLabel)

        self.ScanWidgetsContainer = QGridLayout()
        self.ScanWidgetsContainer.addWidget(self.ResultTab, 0, 0, 1, 1)
        self.ScanWidgetsContainer.addLayout(self.ScanActionContainer, 0, 1, 1, 1)
        self.ScanWidgetsContainer.setColumnStretch(0, 1)
        self.ScanActionBaseContainer.addLayout(self.ScanWidgetsContainer)

        self.ActionsSection.addTab(self.ScanTab, '')

        # ----- Tab Widget - Log Tab -----
        self.LogTab = QWidget()
        self.LogTabHLayoutWidget = QWidget(self.LogTab)
        self.LogTabHLayoutWidget.setGeometry(QRect(0, 0, 1111, 361))
        self.LogTabHLayoutContainer = QVBoxLayout(self.LogTab)
        self.LogTabHLayoutContainer.setContentsMargins(0, 0, 0, 0)

        self.LogLineEdit = QTextEdit(self.LogTabHLayoutWidget)
        self.LogLineEdit.setReadOnly(True)
        self.LogLineEdit.setFocusPolicy(Qt.NoFocus)
        self.LogTabHLayoutContainer.addWidget(self.LogLineEdit)

        self.ActionsSection.addTab(self.LogTab, '')

        self.MainContainer.addWidget(self.ActionsSection)

        # ----- Intermediate Widget Area -----
        self.IntermediateSpacer = QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.MainContainer.addItem(self.IntermediateSpacer)

        # ---- Value List Section -----
        self.ValueListsSection = QTabWidget(self.BaseVLayoutWidget)
        self.ValueListsSection.setFont(font)

        # ----- Tab Widget - Value List Tab -----
        self.ValueListTab = QWidget()
        self.ValueListTabVLayoutWidget = QWidget(self.ValueListTab)
        self.ValueListTabVLayoutWidget.setGeometry(QRect(0, 0, 1111, 411))
        self.ValueListContainer = QVBoxLayout(self.ValueListTab)
        self.ValueListContainer.setContentsMargins(0, 0, 0, 0)

        self.ValueListWidget = CustomTreeWidget(self.ValueListTabVLayoutWidget)
        self.ValueListWidget.setSortingEnabled(False)
        self.ValueListWidget.setDragEnabled(True)
        self.ValueListWidget.setAcceptDrops(True)
        self.ValueListWidget.setDropIndicatorShown(True)
        self.ValueListWidget.setAllColumnsShowFocus(True)
        self.ValueListWidget.setDragDropMode(QAbstractItemView.InternalMove)
        self.ValueListWidget.setDefaultDropAction(Qt.MoveAction)
        self.ValueListWidget.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.ValueListWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ValueListWidget.setItemDelegateForColumn(0, CustomCheckboxDelegate(parent=self.ValueListWidget))
        self.ValueListWidget.customContextMenuRequested.connect(self.vl_context_menu)
        self.ValueListWidget.itemDoubleClicked.connect(self.vl_edit_item_popup)
        self.ValueListContainer.addWidget(self.ValueListWidget)

        self.ValueListsSection.addTab(self.ValueListTab, '')

        # ----- Tab Widget - Raw List Tab -----
        self.RawListTab = QWidget()
        self.RawListActionContainerVLayoutWidget = QWidget(self.RawListTab)
        self.RawListActionContainerVLayoutWidget.setGeometry(QRect(0, 0, 1111, 351))
        self.RawListActionContainer = QVBoxLayout(self.RawListTab)
        self.RawListActionContainer.setContentsMargins(0, 0, 0, 0)
        
        self.RawListActionContainerWidget = QStackedWidget(self.RawListActionContainerVLayoutWidget)
        
        # ----- Manual Load Page -----
        self.ManualLoadPage = QWidget()
        self.ManualLoadPageLayoutWidget = QWidget(self.ManualLoadPage)
        self.ManualLoadPageLayoutWidget.setGeometry(QRect(0, 0, 1101, 351))
        self.ManualLoadContainer = QVBoxLayout(self.ManualLoadPage)
        self.ManualLoadContainer.setContentsMargins(0, 0, 0, 0)

        self.LoadProgressBar = QProgressBar(self.ManualLoadPageLayoutWidget)
        self.LoadProgressBar.setObjectName('LoadProgressBar')
        self.LoadProgressBar.setTextVisible(False)
        self.ManualLoadContainer.addWidget(self.LoadProgressBar)

        self.LoadButtonContainer = QGridLayout()

        self.LoadButtonSpacerLeft = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.LoadButtonContainer.addItem(self.LoadButtonSpacerLeft, 1, 0, 1, 1)

        self.LoadButtonSpacerRight = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.LoadButtonContainer.addItem(self.LoadButtonSpacerRight, 1, 3, 1, 1)

        self.LoadButton = QPushButton(self.ManualLoadPageLayoutWidget)
        self.LoadButton.setObjectName('LoadButton')
        self.LoadButton.setFont(font)
        self.LoadButtonContainer.addWidget(self.LoadButton, 1, 1, 1, 1)

        self.LoadButtonSpacerBottom = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.LoadButtonContainer.addItem(self.LoadButtonSpacerBottom, 2, 1, 1, 1)

        self.LoadButtonSpacerTop = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.LoadButtonContainer.addItem(self.LoadButtonSpacerTop, 0, 1, 1, 1)

        self.ManualLoadContainer.addLayout(self.LoadButtonContainer)

        self.RawListActionContainerWidget.addWidget(self.ManualLoadPage)

        # ----- Raw List Page -----
        self.RawListPage = QWidget()
        self.RawListPageVLayoutWidget = QWidget(self.RawListPage)
        self.RawListPageVLayoutWidget.setGeometry(QRect(0, 0, 1111, 411))
        self.RawListContainer = QVBoxLayout(self.RawListPage)
        self.RawListContainer.setContentsMargins(0, 0, 0, 0)

        self.UnloadButton = QPushButton(self.RawListPageVLayoutWidget)
        self.UnloadButton.setObjectName('UnloadButton')
        self.UnloadButton.setFont(font)
        self.RawListContainer.addWidget(self.UnloadButton)

        self.RawListWidget = CustomEditTreeWidget([0], self.RawListPageVLayoutWidget)
        self.RawListWidget.setExpandsOnDoubleClick(False)
        self.RawListWidget.setAllColumnsShowFocus(True)
        self.RawListWidget.setItemDelegateForColumn(0, CustomCheckboxDelegate(self.RawListPageVLayoutWidget))
        self.RawListContainer.addWidget(self.RawListWidget)

        self.RawListActionContainerWidget.addWidget(self.RawListPage)

        self.RawListActionContainer.addWidget(self.RawListActionContainerWidget)

        self.ValueListsSection.addTab(self.RawListTab, '')

        self.MainContainer.addWidget(self.ValueListsSection)

        self.ScanInputContainer.setCurrentIndex(1)

        QMetaObject.connectSlotsByName(self)

        # ----- Main Variables -----
        self._rt_list_items = list()
        self._tree_list_items = list()
        self._pause_polling = False
        self._polling_paused = False
        self._connected = False

        self.retranslate_ui()

    def retranslate_ui(self):
        self.setWindowTitle('Tyrano Browser')

        self.menuFile.setTitle('File')
        self.menuSettings.setTitle('Settings')
        self.menuHelp.setTitle('Help')

        self.actionLaunch_Game.setText('Launch Game..')
        self.actionStop_Game.setText('Stop Game')
        self.actionSave_Table.setText('Save Table...')
        self.actionLoad_Table.setText('Load Table...')
        self.actionSave_Logs.setText('Save Logs...')

        self.actionTyrano_Browser_Tutorial.setText('Tyrano Browser Tutorial')
        self.actionCheck_For_Updates.setText('Check For Updates')
        self.actionAbout.setText('About')

        self.InfoLabel.setText('No game loaded')
        self.ScanButton.setText('Scan')
        self.ClearButton.setText('Clear')
        self.UndoButton.setText('Undo')
        self.SearchAndLabel.setText('and ')
        self.SearchByLabel.setText('Scan by')
        self.ValueRadioButton.setText('Value')
        self.NameRadioButton.setText('Name')

        self.SearchTypeLabel.setText('Scan type')

        self.SearchTypeInput.addItem('Exact value')
        self.SearchTypeInput.addItem('Bigger than...')
        self.SearchTypeInput.addItem('Smaller than...')
        self.SearchTypeInput.addItem('Between...')
        self.SearchTypeInput.addItem('Unknown')
        self.SearchTypeInput.addItem('Increased value')
        self.SearchTypeInput.addItem('Increased by...')
        self.SearchTypeInput.addItem('Decreased value')
        self.SearchTypeInput.addItem('Decreased by...')
        self.SearchTypeInput.addItem('Changed value')
        self.SearchTypeInput.addItem('Unchanged value')
        self.SearchTypeInput.addItem('Ignore')
        self.SearchTypeInput.addItem('Contains ...')
        self.SearchTypeInput.addItem('Starts with...')
        self.SearchTypeInput.addItem('Ends with...')
        self.SearchTypeInput.addItem('Regex')

        self.FoundLabel.setText('Found: 0')

        self.LoadButton.setText('Load')
        self.UnloadButton.setText('Unload')

        self.ResultTab.setHeaderLabels(['Variable', 'Value', 'Previous', 'Path'])

        for i in range(self.ResultTab.columnCount()):
            self.ResultTab.header().resizeSection(i, 180)

        self.ValueListWidget.setHeaderLabels(['Description', 'Path', 'Value'])

        for i in range(self.ValueListWidget.columnCount()):
            self.ValueListWidget.header().resizeSection(i, 200)

        self.RawListWidget.setHeaderLabels(['Description', 'Path', 'Value'])

        for i in range(self.RawListWidget.columnCount()):
            self.RawListWidget.header().resizeSection(i, 300)

        self.ActionsSection.setTabText(self.ActionsSection.indexOf(self.ScanTab), 'Scan')
        self.ActionsSection.setTabText(self.ActionsSection.indexOf(self.LogTab), 'Logs')

        self.ValueListsSection.setTabText(self.ValueListsSection.indexOf(self.ValueListTab), 'Value List')
        self.ValueListsSection.setTabText(self.ValueListsSection.indexOf(self.RawListTab), 'Raw List')

    def _update_scan_by(self):
        if self.ValueRadioButton.isChecked():
            self.SearchTypeInput.setEnabled(True)
            self._update_scan_type()
        else:
            self.SearchTypeInput.setEnabled(False)
            self.ScanInputContainer.setCurrentIndex(0)

    def _update_scan_type(self):
        no_input = ['Unknown', 'Ignore', 'Increased value', 'Decreased value', 'Changed value', 'Unchanged value']
        if self.SearchTypeInput.currentText() in no_input:
            self.ScanInputContainer.setCurrentIndex(2)
        elif self.SearchTypeInput.currentText() == 'Between...':
            self.ScanInputContainer.setCurrentIndex(1)
        else:
            self.ScanInputContainer.setCurrentIndex(0)

    def add_item_to_value_list(self, name, path, value, parent):
        if not isinstance(value, str):
            value = json.dumps(value)
        item = QTreeWidgetItem(parent, [name, path, value])
        item.setFlags(item.flags() & ~Qt.ItemIsDropEnabled | Qt.ItemIsUserCheckable)
        item.setCheckState(0, Qt.Unchecked)
        item.setForeground(0, QBrush(QColor(255, 255, 255)))
        self._tree_list_items.append(item)

    def rt_move_to_vl(self, index):
        item = self.ResultTab.itemFromIndex(index)
        if item is None:
            return

        self.add_item_to_value_list(item.text(0), item.text(3), item.text(1), self.ValueListWidget)

    def vl_edit_item_popup(self, item, column):
        header = self.ValueListWidget.headerItem().text(column)
        value = item.text(column)

        if not item.text(1) and column:
            # We only allow changing the name, but not anything else for groups
            return
        
        dialog = EditValueDialog(f'Change {header}', value, self)
        if dialog.exec_():
            if not dialog.new_value:
                return
            item.setText(column, dialog.new_value)

            if column == 2:
                self.set_value(item.text(1), item.text(2))

    def rt_context_menu(self, position):
        items = self.ResultTab.selectedItems()
        if not items:
            return
        
        menu = QMenu(self)
        add_selected = menu.addAction('Add selected variables to value list')
        change_value = menu.addAction('Change value of selected variables')
        change_value_to_previous = menu.addAction('Change value of selected variables to previous value')
        remove_selected = menu.addAction('Remove selected variables')

        action = menu.exec_(self.ResultTab.viewport().mapToGlobal(position))

        if action == add_selected:
            for item in items:
                self.add_item_to_value_list(item.text(0), item.text(3), item.text(1), self.ValueListWidget)
        elif action == change_value:
            dialog = EditValueDialog('Change Value', items[0].text(1), self)
            if dialog.exec_():
                if not dialog.new_value:
                    return
                for item in items:
                    item.setText(1, dialog.new_value)
                    self.set_value(item.text(3), dialog.new_value)
        elif action == change_value_to_previous:
            for item in items:
                item.setText(1, item.text(2))
                self.set_value(item.text(3), item.text(2))
        elif action == remove_selected:
            for item in items:
                self._rt_list_items.remove(item)
                self.ResultTab.takeTopLevelItem(self.ResultTab.indexOfTopLevelItem(item))

    def vl_context_menu(self, position):
        items = self.ValueListWidget.selectedItems()

        if items is None:
            self._vl_context_menu_empty(position)
        else:
            self._vl_context_menu_item(items, position)

    def _vl_context_menu_empty(self, position):
        menu = QMenu(self)

        create_item = menu.addAction('Create Item')
        menu.addSeparator()
        create_header = menu.addAction('Create Header')

        action = menu.exec_(self.ValueListWidget.viewport().mapToGlobal(position))

        if action == create_item:
            name = EditValueDialog('Create Item', '', self)
            if name.exec_():
                if not name.new_value:
                    return
                self.add_item_to_value_list(name.new_value, 'path', '??', self.ValueListWidget)
        elif action == create_header:
            name = EditValueDialog('Create Header', '', self)
            if name.exec_():
                if not name.new_value:
                    return
                item = QTreeWidgetItem(self.ValueListWidget, [name.new_value, '', ''])
                item.setForeground(0, QBrush(QColor(255, 255, 255)))

    def _remove_vl_items(self, items):
        for item in items:
            parent = item.parent()
            children = item.takeChildren()
            is_group = True if not item.text(1) and not item.text(2) else False

            if children:
                self._remove_vl_items(children)

            if parent is None:
                self.ValueListWidget.takeTopLevelItem(self.ValueListWidget.indexOfTopLevelItem(item))
            else:
                self.ValueListWidget.removeChildItem(parent, item)

            if not is_group:
                self._tree_list_items.remove(item)

    def _vl_context_menu_item(self, items, position):
        menu = QMenu(self)

        _item_text = 'Item'
        if len(items) > 1:
            _item_text = 'Items'
        delete_item = menu.addAction(f'Delete {_item_text}')

        edit_sub_menu = menu.addMenu('Change')
        edit_sub_menu.addAction('Name')
        edit_sub_menu.addAction('Path')
        edit_sub_menu.addAction('Value')

        change_color = menu.addAction('Change Color')
        create_item = menu.addAction('Create Item')

        menu.addSeparator()

        create_header = menu.addAction('Create Header')

        action = menu.exec_(self.ValueListWidget.viewport().mapToGlobal(position))

        if action == delete_item:
            confirmation = QMessageBox.question(
                self,
                'Confirm', f'Are you sure you want to delete {len(items)} {_item_text}?'
            )
            if confirmation == QMessageBox.No:
                return
            self._remove_vl_items(items)
        elif action == edit_sub_menu.actions()[0]:
            dialog = EditValueDialog('Change Name', items[0].text(0), self)
            if dialog.exec_():
                if not dialog.new_value:
                    return
                for item in items:
                    item.setText(0, dialog.new_value)
        elif action == edit_sub_menu.actions()[1]:
            dialog = EditValueDialog('Change Path', items[0].text(1), self)
            if dialog.exec_():
                if not dialog.new_value:
                    return
                for item in items:
                    if not item.text(1) and not item.text(2):
                        continue
                    item.setText(1, dialog.new_value)
        elif action == edit_sub_menu.actions()[2]:
            dialog = EditValueDialog('Change Value', items[0].text(2), self)
            if dialog.exec_():
                if not dialog.new_value:
                    return
                for item in items:
                    if not item.text(1) and not item.text(2):
                        continue
                    item.setText(2, dialog.new_value)
        elif action == change_color:
            color = QColorDialog.getColor()

            if color.isValid():
                for item in items:
                    item.setForeground(0, QBrush(color))
                    item.setForeground(1, QBrush(color))
                    item.setForeground(2, QBrush(color))
        elif action == create_item:
            name = EditValueDialog('Create Item', '', self)
            if name.exec_():
                if not name.new_value:
                    return
                self.add_item_to_value_list(name.new_value, 'path', '??', self.ValueListWidget)
        elif action == create_header:
            name = EditValueDialog('Create Header', '', self)
            if name.exec_():
                if not name.new_value:
                    return
                item = QTreeWidgetItem(self.ValueListWidget, [name.new_value, '', ''])
                item.setForeground(0, QBrush(QColor(255, 255, 255)))
        
