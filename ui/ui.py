from ui.widget import CustomEditTreeWidget, CustomCheckboxDelegate, CustomTreeWidget
from core.scanner import ScanGroup, ScanInputGroup, ValueType, ScanType
from ui.dialog import EditValueDialog

from PySide2.QtWidgets import (QMainWindow, QAction, QLabel, QWidget, QVBoxLayout, QHBoxLayout, QTreeWidget, QLineEdit,
    QTreeWidgetItem, QProgressBar, QSizePolicy, QAbstractItemView, QPushButton, QSpacerItem, QRadioButton, QTabWidget,
    QGridLayout, QComboBox, QMenuBar, QMenu, QLayout, QTextEdit, QCheckBox, QGroupBox, QStackedWidget, QColorDialog,
    QMessageBox, QButtonGroup)
from PySide2.QtCore import QMetaObject, QRect, QSize, Qt
from PySide2.QtGui import QFont, QBrush, QColor, QIcon

import json


class LucidEngineUI(QMainWindow):
    def __init__(self, parent=None):
        super(LucidEngineUI, self).__init__(parent)

        self.resize(1111, 874)
        self.setWindowIcon(QIcon('resources/app-icon.ico'))

        with open('theme/default-dark/dark.qss') as file:
            self.setStyleSheet(file.read())
            file.close()

        segoe_ui_9 = QFont()
        segoe_ui_9.setFamily('Segoe UI')
        segoe_ui_9.setPointSize(9)

        self.centralwidget = QWidget(self)
        self.setCentralWidget(self.centralwidget)

        # ----- Menu Bar -----
        self.menubar = QMenuBar(self)
        self.menubar.setGeometry(QRect(0, 0, 1539, 19))
        self.menuFile = QMenu(self.menubar)
        self.menuSettings = QMenu(self.menubar)
        self.menuHelp = QMenu(self.menubar)
        self.setMenuBar(self.menubar)

        self.actionLaunch_Game = QAction(self)
        self.actionClose_Game = QAction(self)

        self.actionSave_Table = QAction(self)
        self.actionLoad_Table = QAction(self)
        self.actionSave_Logs = QAction(self)

        self.actionLucid_Engine_Tutorial = QAction(self)
        self.actionCheck_For_Updates = QAction(self)
        self.actionAbout = QAction(self)

        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuSettings.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())

        self.menuFile.addAction(self.actionLaunch_Game)
        self.menuFile.addAction(self.actionClose_Game)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionSave_Table)
        self.menuFile.addAction(self.actionLoad_Table)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionSave_Logs)

        self.menuHelp.addAction(self.actionLucid_Engine_Tutorial)
        self.menuHelp.addSeparator()
        self.menuHelp.addAction(self.actionCheck_For_Updates)
        self.menuHelp.addAction(self.actionAbout)

        # ----- Main Container -----
        self.BaseVLayoutWidget = QWidget(self.centralwidget)
        self.BaseVLayoutWidget.setGeometry(QRect(0, 10, 1111, 901))

        self.MainContainer = QVBoxLayout(self.centralwidget)
        self.MainContainer.setContentsMargins(0, 0, 0, 0)
        self.MainContainer.addWidget(self.BaseVLayoutWidget)

        self.InfoLabel = QLabel(self.BaseVLayoutWidget)
        self.InfoLabel.setAlignment(Qt.AlignCenter)
        self.MainContainer.addWidget(self.InfoLabel)


        # ----- Actions Section -----
        self.ActionsSection = QTabWidget(self.BaseVLayoutWidget)


        # ----- Tab Widget - Scan Tab -----
        self.ScanTab = QWidget()
        self.ScanTabVLayoutWidget = QWidget(self.ScanTab)
        self.ScanTabVLayoutWidget.setGeometry(QRect(0, 0, 1111, 401))
        self.ScanActionBaseContainer = QVBoxLayout(self.ScanTab)
        self.ScanActionBaseContainer.setContentsMargins(0, 0, 0, 0)

        # ----- Tab Widget - Scan Tab - Progress Bar -----
        self.ScanProgressBar = QProgressBar(self.ScanTabVLayoutWidget)
        self.ScanProgressBar.setObjectName('ScanProgressBar')
        self.ScanProgressBar.setTextVisible(False)
        self.ScanActionBaseContainer.addWidget(self.ScanProgressBar)

        # ----- Tab Widget - Scan Tab - Result Section -----
        self.ScanWidgetsContainer = QGridLayout()  # CHECK check later

        self.ResultTab = QTreeWidget(self.ScanTabVLayoutWidget)

        sizePolicy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ResultTab.sizePolicy().hasHeightForWidth())
        self.ResultTab.setSizePolicy(sizePolicy)

        self.ResultTab.setMinimumSize(QSize(700, 0))
        self.ResultTab.setEditTriggers(QAbstractItemView.DoubleClicked)
        self.ResultTab.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.ResultTab.setSortingEnabled(False)
        self.ResultTab.setIndentation(0)
        self.ResultTab.setItemsExpandable(False)
        self.ResultTab.setExpandsOnDoubleClick(False)
        self.ResultTab.setAllColumnsShowFocus(True)
        self.ResultTab.setContextMenuPolicy(Qt.CustomContextMenu)
        # self.ResultTab.doubleClicked.connect(self.rt_move_to_vl)
        # self.ResultTab.customContextMenuRequested.connect(self.rt_context_menu)
        self.ScanWidgetsContainer.addWidget(self.ResultTab, 0, 0, 1, 1)

        # ----- Tab Widget - Scan Tab - Scan Options Section -----
        self.ScanActionContainer = QVBoxLayout()
        self.ScanActionContainer.setSizeConstraint(QLayout.SetFixedSize)

        self.ScanButtonContainer = QGridLayout()
        self.ScanButtonContainer.setHorizontalSpacing(15)
        self.ScanButtonContainer.setContentsMargins(5, -1, 8, -1)

        self.ScanButton = QPushButton(self.ScanTabVLayoutWidget)
        self.ScanButtonContainer.addWidget(self.ScanButton, 0, 0, 1, 1)
        self.ScanButton.setFixedSize(QSize(80, 22))

        self.ClearButton = QPushButton(self.ScanTabVLayoutWidget)
        self.ClearButton.setFixedSize(QSize(80, 22))
        self.ClearButton.setEnabled(False)
        self.ScanButtonContainer.addWidget(self.ClearButton, 0, 1, 1, 1)

        self.ClearUndoSpacer = QSpacerItem(100, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.ScanButtonContainer.addItem(self.ClearUndoSpacer, 0, 2, 1, 1)

        self.UndoButton = QPushButton(self.ScanTabVLayoutWidget)
        self.UndoButton.setFixedSize(QSize(80, 22))
        self.UndoButton.setEnabled(False)

        self.ScanButtonContainer.addWidget(self.UndoButton, 0, 3, 1, 1)
        self.ScanActionContainer.addLayout(self.ScanButtonContainer)

        self.ScanInputContainer = QStackedWidget(self.ScanTabVLayoutWidget)

        sizePolicy1 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.ScanInputContainer.sizePolicy().hasHeightForWidth())
        self.ScanInputContainer.setSizePolicy(sizePolicy1)
        self.ScanInputContainer.setMinimumSize(QSize(0, 28))

        self.NormalScanPage = QWidget()
        self.NormalScanPageLayoutWidget = QWidget(self.NormalScanPage)
        self.NormalScanPageContainer = QVBoxLayout(self.NormalScanPage)
        self.NormalScanPageContainer.setContentsMargins(0, 0, 0, 0)

        self.ScanInput = QLineEdit(self.NormalScanPageLayoutWidget)
        self.NormalScanPageContainer.addWidget(self.ScanInput)
        self.ScanInputContainer.addWidget(self.NormalScanPage)

        self.DualInputScanPage = QWidget()
        self.DualInputScanPageContainer = QWidget(self.DualInputScanPage)
        # self.DualInputScanPageContainer.setGeometry(QRect(0, 0, 401, 26))
        self.ScanInputDualContainer = QGridLayout(self.DualInputScanPage)
        self.ScanInputDualContainer.setContentsMargins(0, 0, 0, 0)

        self.ScanInputA = QLineEdit(self.DualInputScanPageContainer)
        self.ScanInputDualContainer.addWidget(self.ScanInputA, 0, 0, 1, 1)

        self.SearchAndLabel = QLabel(self.DualInputScanPageContainer)
        self.SearchAndLabel.setAlignment(Qt.AlignCenter)

        self.ScanInputB = QLineEdit(self.DualInputScanPageContainer)
        self.ScanInputDualContainer.addWidget(self.ScanInputB, 0, 2, 1, 1)

        self.ScanInputDualContainer.addWidget(self.SearchAndLabel, 0, 1, 1, 1)
        self.ScanInputContainer.addWidget(self.DualInputScanPage)

        self.IgnoreInputScanPage = QWidget()
        self.ScanInputContainer.addWidget(self.IgnoreInputScanPage)
        self.ScanActionContainer.addWidget(self.ScanInputContainer)

        self.ScanFullOptionsContainer = QVBoxLayout()
        self.ScanByContainer = QHBoxLayout()
        self.ScanByContainer.setContentsMargins(10, -1, 5, -1)

        self.SearchByLabel = QLabel(self.ScanTabVLayoutWidget)
        self.ScanByContainer.addWidget(self.SearchByLabel)

        self.ValueRadioButton = QRadioButton(self.ScanTabVLayoutWidget)
        self.ValueRadioButton.setChecked(True)
        self.ScanByContainer.addWidget(self.ValueRadioButton)

        self.NameRadioButton = QRadioButton(self.ScanTabVLayoutWidget)
        self.ScanByContainer.addWidget(self.NameRadioButton)

        self.SearchByHSpacer = QSpacerItem(100, 20, QSizePolicy.Maximum, QSizePolicy.Minimum)
        self.ScanByContainer.addItem(self.SearchByHSpacer)

        self.ScanFullOptionsContainer.addLayout(self.ScanByContainer)

        self.ScanOptionsMainExtraContainer = QHBoxLayout()
        self.ScanMainOptionsContainer = QVBoxLayout()

        self.SearchConstraintContainer = QGridLayout()
        self.SearchConstraintContainer.setContentsMargins(6, -1, -1, -1)

        self.SearchTypeLabel = QLabel(self.ScanTabVLayoutWidget)
        self.SearchTypeLabel.setObjectName('SearchTypeLabel')
        self.SearchConstraintContainer.addWidget(self.SearchTypeLabel, 0, 2, 1, 1)

        self.SearchTypeInput = QComboBox(self.ScanTabVLayoutWidget)
        self.SearchTypeInput.setMaxVisibleItems(20)
        self.SearchConstraintContainer.addWidget(self.SearchTypeInput, 0, 3, 1, 1)

        self.ValueTypeLabel = QLabel(self.ScanTabVLayoutWidget)
        self.ValueTypeLabel.setObjectName('ValueTypeLabel')
        self.SearchConstraintContainer.addWidget(self.ValueTypeLabel, 1, 2, 1, 1)

        self.ValueTypeInput = QComboBox(self.ScanTabVLayoutWidget)
        self.SearchConstraintContainer.addWidget(self.ValueTypeInput, 1, 3, 1, 1)

        self.SearchConstraintContainer.setColumnStretch(3, 1)
        self.ScanMainOptionsContainer.addLayout(self.SearchConstraintContainer)

        self.ScanOptionsBox = QGroupBox(self.ScanTabVLayoutWidget)

        self.ScanOptionBoxMainContainer = QVBoxLayout(self.ScanOptionsBox)

        self.TimeoutContainer = QGridLayout()

        self.TimeoutLabel = QLabel(self.ScanOptionsBox)
        self.TimeoutContainer.addWidget(self.TimeoutLabel, 0, 0, 1, 1)

        self.TimeoutInput = QLineEdit(self.ScanOptionsBox)
        self.TimeoutContainer.addWidget(self.TimeoutInput, 0, 1, 1, 1)
        self.ScanOptionBoxMainContainer.addLayout(self.TimeoutContainer)

        self.SearchRootContainer = QGridLayout()

        self.SearchRootLabel = QLabel(self.ScanOptionsBox)
        self.SearchRootContainer.addWidget(self.SearchRootLabel, 1, 0, 1, 1)

        self.SearchRootF = QCheckBox(self.ScanOptionsBox)
        self.SearchRootF.setChecked(True)
        self.SearchRootContainer.addWidget(self.SearchRootF, 1, 1, 1, 1)

        self.SearchRootTF = QCheckBox(self.ScanOptionsBox)
        self.SearchRootTF.setChecked(True)
        self.SearchRootContainer.addWidget(self.SearchRootTF, 1, 2, 1, 1)


        self.SearchRootSF = QCheckBox(self.ScanOptionsBox)
        self.SearchRootContainer.addWidget(self.SearchRootSF, 1, 3, 1, 1)

        # Disabled due to lack of samples
        self.SearchRootMP = QCheckBox(self.ScanOptionsBox)
        self.SearchRootMP.setEnabled(False)
        self.SearchRootMP.setCheckable(False)
        self.SearchRootContainer.addWidget(self.SearchRootMP, 1, 4, 1, 1)

        self.ScanOptionBoxMainContainer.addLayout(self.SearchRootContainer)

        self.SearchOptionsFineTuneContainer = QGridLayout()

        self.SearchWritable = QCheckBox(self.ScanOptionsBox)
        self.SearchWritable.setChecked(True)
        self.SearchOptionsFineTuneContainer.addWidget(self.SearchWritable, 0, 0, 1, 1)

        self.SearchReadOnly = QCheckBox(self.ScanOptionsBox)
        self.SearchOptionsFineTuneContainer.addWidget(self.SearchReadOnly, 2, 0, 1, 1)

        self.SearchNullValues = QCheckBox(self.ScanOptionsBox)
        self.SearchOptionsFineTuneContainer.addWidget(self.SearchNullValues, 3, 0, 1, 1)

        self.PollingOptionGroup = QButtonGroup(self.ScanOptionsBox)
        self.PollingOptionGroup.setExclusive(True)

        self.SearchLazyPolling = QCheckBox(self.ScanOptionsBox)
        self.SearchOptionsFineTuneContainer.addWidget(self.SearchLazyPolling, 0, 1, 1, 1)
        self.PollingOptionGroup.addButton(self.SearchLazyPolling, 0)

        self.SearchNoPolling = QCheckBox(self.ScanOptionsBox)
        self.SearchOptionsFineTuneContainer.addWidget(self.SearchNoPolling, 2, 1, 1, 1)
        self.PollingOptionGroup.addButton(self.SearchNoPolling, 1)

        self.ScanOptionBoxMainContainer.addLayout(self.SearchOptionsFineTuneContainer)
        self.ScanMainOptionsContainer.addWidget(self.ScanOptionsBox)
        self.ScanOptionsMainExtraContainer.addLayout(self.ScanMainOptionsContainer)

        self.ScanExtraOptions = QStackedWidget(self.ScanTabVLayoutWidget)

        self.StringExtraOptionsContainerWidget = QWidget()
        self.StringExtraOptionsContainer = QVBoxLayout(self.StringExtraOptionsContainerWidget)

        self.SearchVTXOSTRContainer = QGridLayout()

        self.StringUTF16 = QCheckBox(self.StringExtraOptionsContainerWidget)
        self.SearchVTXOSTRContainer.addWidget(self.StringUTF16, 0, 0, 1, 1)

        self.StringCaseSensitive = QCheckBox(self.StringExtraOptionsContainerWidget)
        self.StringCaseSensitive.setChecked(True)
        self.SearchVTXOSTRContainer.addWidget(self.StringCaseSensitive, 1, 0, 1, 1)

        self.StringRegex = QCheckBox(self.StringExtraOptionsContainerWidget)
        self.SearchVTXOSTRContainer.addWidget(self.StringRegex, 2, 0, 1, 1)

        self.SearchVTX0Spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.SearchVTXOSTRContainer.addItem(self.SearchVTX0Spacer, 3, 0, 1, 1)

        self.StringExtraOptionsContainer.addLayout(self.SearchVTXOSTRContainer)
        self.ScanExtraOptions.addWidget(self.StringExtraOptionsContainerWidget)

        self.FloatExtraOptionsContainerWidget = QWidget()
        self.FloatExtraOptionsContainer = QVBoxLayout(self.FloatExtraOptionsContainerWidget)

        self.SearchVTXOFContainer = QVBoxLayout()

        self.FloatTruncated = QCheckBox(self.FloatExtraOptionsContainerWidget)
        self.SearchVTXOFContainer.addWidget(self.FloatTruncated)

        self.FloatRounded = QCheckBox(self.FloatExtraOptionsContainerWidget)
        self.FloatRounded.setChecked(True)
        self.SearchVTXOFContainer.addWidget(self.FloatRounded)

        self.SearchVTXOFSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.SearchVTXOFContainer.addItem(self.SearchVTXOFSpacer)

        self.FloatExtraOptionsContainer.addLayout(self.SearchVTXOFContainer)
        self.ScanExtraOptions.addWidget(self.FloatExtraOptionsContainerWidget)

        self.NoExtraOptionsContainerWidget = QWidget()
        self.ScanExtraOptions.addWidget(self.NoExtraOptionsContainerWidget)
        self.ScanOptionsMainExtraContainer.addWidget(self.ScanExtraOptions)

        self.ScanOptionsMainExtraContainer.setStretch(0, 1)

        self.ScanFullOptionsContainer.addLayout(self.ScanOptionsMainExtraContainer)

        self.ScanOptionsFoundSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.ScanFullOptionsContainer.addItem(self.ScanOptionsFoundSpacer)

        self.FoundLabel = QLabel(self.ScanTabVLayoutWidget)
        self.FoundLabel.setObjectName('FoundLabel')
        self.ScanFullOptionsContainer.addWidget(self.FoundLabel)

        self.ScanActionContainer.addLayout(self.ScanFullOptionsContainer)
        self.ScanWidgetsContainer.addLayout(self.ScanActionContainer, 0, 1, 1, 1)
        self.ScanWidgetsContainer.setColumnStretch(1, 0)
        self.ScanWidgetsContainer.setColumnStretch(0, 1)
        self.ScanActionBaseContainer.addLayout(self.ScanWidgetsContainer)

        self.ActionsSection.addTab(self.ScanTab, '')

        # ----- Tab Widget - Log Tab -----
        self.LogTab = QWidget()
        self.LogTabHLayoutWidget = QWidget(self.LogTab)
        self.LogTabHLayoutWidget.setGeometry(QRect(0, 0, 1111, 361))
        self.LogTabHLayoutContainer = QVBoxLayout(self.LogTab)
        self.LogTabHLayoutContainer.setContentsMargins(0, 0, 0, 0)

        self.Logs = QTextEdit(self.LogTabHLayoutWidget)
        self.Logs.setReadOnly(True)
        self.Logs.setFocusPolicy(Qt.NoFocus)
        self.LogTabHLayoutContainer.addWidget(self.Logs)

        self.ActionsSection.addTab(self.LogTab, '')

        self.MainContainer.addWidget(self.ActionsSection)

        # ----- Intermediate Widget Area ------
        self.SVSpacerMiddle = QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.MainContainer.addItem(self.SVSpacerMiddle)

        # ---- Value List Section -----
        self.ValueListsSection = QTabWidget(self.BaseVLayoutWidget)

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

        self.ScanInputContainer.setCurrentIndex(0)

        self.retranslate_ui()
        
        self.adjustStackSize()
        self.ScanExtraOptions.setCurrentIndex(2)

        self.connects()

        QMetaObject.connectSlotsByName(self)

        # ----- Main Variables -----
        self._rt_list_items = list()
        self._tree_list_items = list()
        self._pause_polling = False
        self._polling_paused = False
        self._connected = False
    
    def adjustStackSize(self):
        max_width = max_height = 0
        
        for i in range(self.ScanExtraOptions.count()):
            self.ScanExtraOptions.setCurrentIndex(i)
            self.ScanExtraOptions.updateGeometry()
            width = self.ScanExtraOptions.currentWidget().sizeHint().width()
            height = self.ScanExtraOptions.currentWidget().sizeHint().height()
            if width > max_width:
                max_width = width
            if height > max_height:
                max_height = height
        
        max_width += 20  # Account for checkbox box size
        self.ScanExtraOptions.setMinimumSize(max_width, max_height)
        
    def retranslate_ui(self):
        self.setWindowTitle('Lucid Engine')

        self.menuFile.setTitle('File')
        self.menuSettings.setTitle('Settings')
        self.menuHelp.setTitle('Help')

        self.actionLaunch_Game.setText('Launch Game..')
        self.actionClose_Game.setText('Close Game')

        self.actionSave_Table.setText('Save Table...')
        self.actionLoad_Table.setText('Load Table...')
        self.actionSave_Logs.setText('Save Logs...')
        
        self.actionLucid_Engine_Tutorial.setText('Lucid Engine Tutorial')
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
        self.SearchTypeInput.addItems(ScanGroup.FIRST_SCAN)

        self.ValueTypeLabel.setText('Value type')
        self.ValueTypeInput.addItems(ValueType.ALL)

        self.FoundLabel.setText('Found: 0')

        self.LoadButton.setText('Load')
        self.UnloadButton.setText('Unload')

        self.StringCaseSensitive.setText('Case sensitive')
        self.StringUTF16.setText('UTF-16')
        self.StringRegex.setText('Regex')
        
        self.FloatTruncated.setText('Truncated')
        self.FloatRounded.setText('Rounded')

        self.ScanOptionsBox.setTitle('Scan Options')
        self.TimeoutLabel.setText('Timeout')
        self.TimeoutInput.setText('5')

        self.SearchRootLabel.setText('Search root:     ')
        self.SearchRootF.setText('f')
        self.SearchRootTF.setText('tf')
        self.SearchRootSF.setText('sf')
        self.SearchRootMP.setText('mp')

        self.SearchWritable.setText('Writable')
        self.SearchReadOnly.setText('Read-only')
        self.SearchNullValues.setText('Null values')
        self.SearchLazyPolling.setText('Lazy polling')
        self.SearchNoPolling.setText('No polling')

        self.ResultTab.setHeaderLabels(['Variable', 'Value', 'Previous', 'First', 'Path'])
        sizes = [150, 120, 120, 120, 150]

        for s, i in zip(sizes, range(len(sizes))):
            self.ResultTab.setColumnWidth(i, s)

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

    def connects(self):
        self.ValueTypeInput.currentIndexChanged.connect(self._value_type_on_change)
        self.SearchTypeInput.currentIndexChanged.connect(self._scan_type_on_change)

        self.ResultTab.doubleClicked.connect(self.rt_move_to_vl)
        self.ResultTab.customContextMenuRequested.connect(self.rt_context_menu)

        self.ScanInput.returnPressed.connect(self.ScanButton.click)
        self.ScanInputA.returnPressed.connect(self.ScanInputB.setFocus)
        self.ScanInputB.returnPressed.connect(self.ScanButton.click)

        self.ValueRadioButton.toggled.connect(self._scan_by_on_change)

        self.ValueListWidget.customContextMenuRequested.connect(self.vl_context_menu)
        self.ValueListWidget.itemDoubleClicked.connect(self.vl_edit_item_popup)

    def _value_type_on_change(self, index):
        self.SearchTypeInput.clear()

        if index == 0:  # Integers
            self.ScanExtraOptions.setCurrentIndex(2)
            self.SearchTypeInput.addItems(ScanGroup.FIRST_SCAN)
        elif index == 1:  # Float
            self.ScanExtraOptions.setCurrentIndex(1)
            self.SearchTypeInput.addItems(ScanGroup.FIRST_SCAN)
        elif index == 2:  # String
            self.ScanExtraOptions.setCurrentIndex(0)
            self.SearchTypeInput.addItems(ScanGroup.STR_FIRST_SCAN)
        elif index == 3:  # Bool
            self.ScanExtraOptions.setCurrentIndex(2)
            self.SearchTypeInput.addItem(ScanType.EXACT_VALUE)

    def _scan_type_on_change(self):
        cur_text = self.SearchTypeInput.currentText()

        if cur_text in ScanInputGroup.DUAL_INPUT:
            self.ScanInputContainer.setCurrentIndex(1)
        elif cur_text in ScanInputGroup.NO_INPUT:
            self.ScanInputContainer.setCurrentIndex(2)
        else:
            self.ScanInputContainer.setCurrentIndex(0)

    def _scan_by_on_change(self):
        if self.ValueRadioButton.isChecked():
            self.SearchTypeInput.setEnabled(True)
            self.ValueTypeInput.setEnabled(True)
            self._scan_type_on_change()
            self._value_type_on_change(self.ValueTypeInput.currentIndex())
        else:
            self.SearchTypeInput.setEnabled(False)
            self.ValueTypeInput.setEnabled(False)
            self.ScanExtraOptions.setCurrentIndex(2)

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
        # TODO limit name length to 128 characters max
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
        change_value_to_first = menu.addAction('Change value of selected variables to first value')
        remove_selected = menu.addAction('Remove selected variables')

        action = menu.exec_(self.ResultTab.viewport().mapToGlobal(position))

        if action == add_selected:
            for item in items:
                self.add_item_to_value_list(item.text(0), item.text(4), item.text(1), self.ValueListWidget)
        elif action == change_value:
            dialog = EditValueDialog('Change Value', items[0].text(1), self)
            if dialog.exec_():
                if not dialog.new_value:
                    return
                for item in items:
                    item.setText(1, dialog.new_value)
                    self.set_value(item.text(4), dialog.new_value)
        elif action == change_value_to_previous:
            for item in items:
                item.setText(1, item.text(2))
                self.set_value(item.text(4), item.text(2))
        elif action == change_value_to_first:
            for item in items:
                item.setText(1, item.text(3))
                self.set_value(item.text(4), item.text(3))
        elif action == remove_selected:
            for item in items:
                self._rt_list_items.remove(item)
                self.ResultTab.takeTopLevelItem(self.ResultTab.indexOfTopLevelItem(item))

    def vl_context_menu(self, position):
        items = self.ValueListWidget.selectedItems()

        if not items:
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
        
