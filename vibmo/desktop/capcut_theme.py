"""
CapCut / DaVinci Resolve Style Desktop Pro Dark Theme for Vibmo.
Production-grade stylesheet with deep studio blacks, clean borders, and sleek accents.
"""

CAPCUT_STYLESHEET = """
QMainWindow, QDialog, QWidget {
    background-color: #0E0E10;
    color: #E2E2E5;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    font-size: 13px;
}

/* Top Navigation Bar */
#TopBar {
    background-color: #141417;
    border-bottom: 1px solid #1E1E22;
}

#BrandLogo {
    font-weight: 800;
    font-size: 14px;
    color: #F5F5F7;
    letter-spacing: 0.5px;
}

#ProjectTitle {
    font-weight: 500;
    font-size: 12px;
    color: #8F8F94;
}

/* Status Badges */
#AgentBadge {
    background-color: rgba(10, 132, 255, 0.1);
    color: #0A84FF;
    border: 1px solid rgba(10, 132, 255, 0.3);
    border-radius: 4px;
    padding: 3px 8px;
    font-size: 10px;
    font-weight: 700;
}

/* Primary Export Button */
#ExportBtn {
    background-color: #0A84FF;
    color: #FFFFFF;
    font-weight: 600;
    font-size: 12px;
    border-radius: 4px;
    padding: 6px 16px;
    border: none;
}
#ExportBtn:hover {
    background-color: #0070E0;
}
#ExportBtn:pressed {
    background-color: #005BB5;
}

/* Category Segmented Navigation Tabs */
#NavTabBtn {
    background: transparent;
    color: #8F8F94;
    border: none;
    border-radius: 4px;
    padding: 6px 14px;
    font-weight: 500;
    font-size: 13px;
    margin: 0px 2px;
}
#NavTabBtn:hover {
    color: #E2E2E5;
    background-color: rgba(255, 255, 255, 0.05);
}
#NavTabBtn:checked {
    background-color: #1E1E22;
    color: #FFFFFF;
    font-weight: 600;
}

/* Panels, Media Cards & Bins */
QTreeWidget, QListWidget, QTableWidget {
    background-color: #141417;
    border: 1px solid #1E1E22;
    border-radius: 6px;
    color: #E2E2E5;
    outline: none;
    padding: 4px;
}

QTreeWidget::item, QListWidget::item {
    border-radius: 4px;
    padding: 4px;
}

QTreeWidget::item:selected, QListWidget::item:selected {
    background-color: #1E1E22;
    color: #FFFFFF;
}

QTreeWidget::item:hover, QListWidget::item:hover {
    background-color: rgba(255, 255, 255, 0.03);
}

/* Standard Buttons */
QPushButton {
    background-color: #1E1E22;
    color: #E2E2E5;
    border: 1px solid #2C2C30;
    border-radius: 4px;
    padding: 5px 12px;
    font-weight: 500;
}
QPushButton:hover {
    background-color: #262629;
    border-color: #38383C;
}
QPushButton:pressed {
    background-color: #141417;
}

/* Inputs */
QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
    background-color: #141417;
    border: 1px solid #2C2C30;
    border-radius: 4px;
    padding: 5px 8px;
    color: #E2E2E5;
    selection-background-color: #0A84FF;
}
QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {
    border: 1px solid #0A84FF;
}

/* Subdued Scrollbars */
QScrollBar:vertical {
    border: none;
    background: transparent;
    width: 10px;
    margin: 2px;
}
QScrollBar::handle:vertical {
    background: #2C2C30;
    min-height: 24px;
    border-radius: 4px;
}
QScrollBar::handle:vertical:hover {
    background: #38383C;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    border: none;
    background: transparent;
    height: 10px;
    margin: 2px;
}
QScrollBar::handle:horizontal {
    background: #2C2C30;
    min-width: 24px;
    border-radius: 4px;
}
QScrollBar::handle:horizontal:hover {
    background: #38383C;
}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}

/* Modern Splitter (Invisible but draggable) */
QSplitter::handle {
    background-color: transparent;
}
QSplitter::handle:horizontal {
    width: 6px;
}
QSplitter::handle:vertical {
    height: 6px;
}
QSplitter::handle:hover {
    background-color: rgba(255, 255, 255, 0.05);
}

/* Group Boxes (Inspector Panels) */
QGroupBox {
    border: none;
    border-top: 1px solid #1E1E22;
    margin-top: 16px;
    padding-top: 12px;
    font-weight: 600;
    color: #F5F5F7;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0;
    color: #F5F5F7;
}

/* Workspace Tabs */
QTabWidget::pane {
    border: 1px solid #1E1E22;
    background-color: #141417;
    border-radius: 6px;
}
QTabBar::tab {
    background: transparent;
    color: #8F8F94;
    padding: 8px 16px;
    border-bottom: 2px solid transparent;
    font-weight: 500;
}
QTabBar::tab:selected {
    color: #FFFFFF;
    font-weight: 600;
    border-bottom: 2px solid #0A84FF;
}
QTabBar::tab:hover:!selected {
    color: #E2E2E5;
}
"""
