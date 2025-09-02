
from PyQt6 import QtCore, QtGui, QtWidgets
from typing import List, Optional

PORTS_SAMPLE = [
    "BUCK_PORB",
    "BUCK_RSTB",
    "BUCK_ASYNC_RSTB",
    "BUCK_CAL_REFBAND_H<1:0>",
    "BUCK_CAL_REFCODE_H<9:0>",
    "VREF_EN",
    "ADC_IN0",
    "ADC_IN1",
]

class AnalogTab(QtWidgets.QWidget):
    def __init__(self, title: str, ports: Optional[List[str]] = None, parent=None):
        super().__init__(parent)
        self.title = title
        self.ports = ports or PORTS_SAMPLE
        self._build_ui()

    def _build_ui(self):
        outer = QtWidgets.QVBoxLayout(self)
        outer.setContentsMargins(16, 16, 16, 16)
        outer.setSpacing(12)

        # Nice header
        header = QtWidgets.QLabel(self.title)
        header.setObjectName("sectionHeader")
        outer.addWidget(header)

        # Table for rows
        self.table = QtWidgets.QTableWidget(len(self.ports), 5, self)
        self.table.setObjectName("portsTable")
        self.table.setHorizontalHeaderLabels(["Port", "Current", "Write Value", "Default", "Desired"])
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)

        for row, port in enumerate(self.ports):
            # Port
            name_item = QtWidgets.QTableWidgetItem(port)
            name_item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignVCenter | QtCore.Qt.AlignmentFlag.AlignLeft)
            self.table.setItem(row, 0, name_item)

            # Current
            current_item = QtWidgets.QTableWidgetItem("N/A")
            current_item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 1, current_item)

            # Write Value (editable QLineEdit)
            write_editor = QtWidgets.QLineEdit()
            write_editor.setEchoMode(QtWidgets.QLineEdit.EchoMode.Normal)
            write_editor.setInputMask("")                        # <- ensure no mask
            write_editor.setInputMethodHints(QtCore.Qt.InputMethodHint.ImhNone)
            write_editor.setPlaceholderText("enter value")
            write_editor.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            
            # Assertion to catch accidental masking
            assert write_editor.echoMode() == QtWidgets.QLineEdit.EchoMode.Normal and write_editor.inputMask() == ""
            
            self.table.setCellWidget(row, 2, write_editor)

            # Default value label
            default_lbl = QtWidgets.QLabel("N/A")
            default_lbl.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            default_lbl.setObjectName("defaultBadge")
            default_lbl.setText("N/A")
            default_lbl.setTextInteractionFlags(QtCore.Qt.TextInteractionFlag.NoTextInteraction)
            default_lbl.setProperty("elideMode", QtCore.Qt.TextElideMode.ElideNone)
            self.table.setCellWidget(row, 3, default_lbl)

            # Desired
            desired_item = QtWidgets.QTableWidgetItem("N/A")
            desired_item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 4, desired_item)

        header_view = self.table.horizontalHeader()
        header_view.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeMode.Stretch)
        header_view.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
        header_view.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
        header_view.setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
        header_view.setSectionResizeMode(4, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)

        outer.addWidget(self.table, stretch=1)

        # Bottom toolbar with Read All, Write All, and Check HADC
        bottom = QtWidgets.QHBoxLayout()
        bottom.addStretch(1)

        self.read_all_btn = QtWidgets.QPushButton("Read All")
        self.read_all_btn.setProperty("kind", "secondary")
        self.read_all_btn.setToolTip("Read all ports (frontend only)")
        self.read_all_btn.clicked.connect(self.on_read_all)
        bottom.addWidget(self.read_all_btn)

        self.write_all_btn = QtWidgets.QPushButton("Write All")
        self.write_all_btn.setProperty("kind", "primary")
        self.write_all_btn.setToolTip("Write all values (frontend only)")
        self.write_all_btn.clicked.connect(self.on_write_all)
        bottom.addWidget(self.write_all_btn)

        self.check_hadc_btn = QtWidgets.QPushButton("Check HADC")
        self.check_hadc_btn.setProperty("kind", "accent")
        self.check_hadc_btn.setToolTip("Check HADC status")
        self.check_hadc_btn.clicked.connect(self.on_check_hadc_clicked)
        bottom.addWidget(self.check_hadc_btn)

        outer.addLayout(bottom)

    def on_read_all(self):
        # fill Current column with placeholder values
        for r in range(self.table.rowCount()):
            self.table.item(r, 1).setText("N/A")
        QtWidgets.QMessageBox.information(self, "Read All", f"[{self.title}] Read all (frontend only).")

    def on_write_all(self):
        # copy from Write Value -> Desired column
        for r in range(self.table.rowCount()):
            editor = self.table.cellWidget(r, 2)  # QLineEdit
            value = editor.text() if editor else ""
            self.table.item(r, 4).setText(value if value else "N/A")
        QtWidgets.QMessageBox.information(self, "Write All", f"[{self.title}] Wrote all (frontend only).")

    def on_check_hadc_clicked(self):
        QtWidgets.QMessageBox.information(self, "Check HADC", f"[{self.title}] Checking HADC... (placeholder)")


class CimaTab(AnalogTab):
    def __init__(self, title: str, ports: Optional[List[str]] = None, parent=None):
        super().__init__(title, ports, parent)
        self._add_cima_controls()

    def _add_cima_controls(self):
        # Add CIMA controls under the header
        cima_bar = QtWidgets.QHBoxLayout()
        
        # CIMA index spinbox
        self.cima_index = QtWidgets.QSpinBox()
        self.cima_index.setRange(0, 63)
        self.cima_index.setPrefix("CIMA idx: ")
        self.cima_index.setToolTip("Single CIMA index (0–63).")
        cima_bar.addWidget(self.cima_index)
        
        # CIMA mask input
        self.cima_mask = QtWidgets.QLineEdit()
        self.cima_mask.setPlaceholderText("64'h0000_0000_0000_0001")
        self.cima_mask.setToolTip("Optional 64'h… bitmask; if provided, overrides index on writes (frontend only).")
        cima_bar.addWidget(self.cima_mask)
        
        # Mask error label (hidden by default)
        self.mask_error = QtWidgets.QLabel("Invalid mask")
        self.mask_error.setStyleSheet("color: #ff6b6b; font-weight: 600;")
        self.mask_error.hide()
        cima_bar.addWidget(self.mask_error)
        
        cima_bar.addStretch(1)
        
        # Insert the CIMA controls after the header
        layout = self.layout()
        layout.insertLayout(1, cima_bar)
        
        # Connect mask validation
        self.cima_mask.textChanged.connect(self._validate_mask)
        self.cima_index.valueChanged.connect(self._validate_mask)

    def _validate_mask(self):
        import re
        mask_text = self.cima_mask.text()
        
        if not mask_text:
            # Empty mask is valid
            self.mask_error.hide()
            self.write_all_btn.setEnabled(True)
            return
        
        # Validate mask format: 64'h[0-9A-Fa-f_]{1,19}
        if re.match(r'^64\'h[0-9A-Fa-f_]{1,19}$', mask_text):
            self.mask_error.hide()
            self.write_all_btn.setEnabled(True)
        else:
            self.mask_error.show()
            self.write_all_btn.setEnabled(False)


class CimaMvmTab(QtWidgets.QWidget):
    TOTAL = 576
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
        self._wire()

    def _build_ui(self):
        outer = QtWidgets.QVBoxLayout(self)
        outer.setContentsMargins(16, 16, 16, 16)
        outer.setSpacing(12)

        # Header
        header = QtWidgets.QLabel("CIMA_MVM")
        header.setObjectName("sectionHeader")
        outer.addWidget(header)

        # Top bar with target CIMA
        top_bar = QtWidgets.QHBoxLayout()
        target_label = QtWidgets.QLabel("Target CIMA: ")
        self.target_cima = QtWidgets.QSpinBox()
        self.target_cima.setRange(0, 63)
        top_bar.addWidget(target_label)
        top_bar.addWidget(self.target_cima)
        top_bar.addStretch(1)
        outer.addLayout(top_bar)

        # Table: 16 rows, 5 columns
        self.table = QtWidgets.QTableWidget(16, 5, self)
        self.table.setObjectName("portsTable")
        self.table.setHorizontalHeaderLabels(["ACT VAL", "No rows (ACT)", "WT VAL (WT0)", "No rows (WT0)", "WT1 (ADC weights)"])
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.DoubleClicked)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)

        # Make all cells editable
        for row in range(16):
            for col in range(5):
                item = QtWidgets.QTableWidgetItem("")
                self.table.setItem(row, col, item)

        # Set column stretch and resize modes
        header_view = self.table.horizontalHeader()
        header_view.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeMode.Stretch)
        header_view.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
        header_view.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
        header_view.setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
        header_view.setSectionResizeMode(4, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)

        outer.addWidget(self.table, stretch=1)

        # Footer with sums and status
        footer = QtWidgets.QHBoxLayout()
        
        self.sum_b_label = QtWidgets.QLabel("Sum B = 0")
        self.sum_d_label = QtWidgets.QLabel("Sum D = 0")
        footer.addWidget(self.sum_b_label)
        footer.addWidget(self.sum_d_label)
        
        footer.addStretch(1)
        
        self.status_label = QtWidgets.QLabel("Needs total 576 in exactly one of B or D (the other must be 0).")
        self.status_label.setStyleSheet("color: #ff6b6b; font-weight: 600;")
        footer.addWidget(self.status_label)
        
        outer.addLayout(footer)

        # Bottom button
        bottom = QtWidgets.QHBoxLayout()
        bottom.addStretch(1)
        
        self.do_mvm_btn = QtWidgets.QPushButton("DO_MVM")
        self.do_mvm_btn.setProperty("kind", "accent")
        self.do_mvm_btn.setEnabled(False)
        self.do_mvm_btn.clicked.connect(self.on_do_mvm_clicked)
        bottom.addWidget(self.do_mvm_btn)
        
        outer.addLayout(bottom)

    def _wire(self):
        # Connect itemChanged to recompute sums/valid, and DO_MVM clicked to summary dialog
        self.table.itemChanged.connect(self._recompute_validation)

    def _recompute_validation(self):
        # Helper: recompute sums, validate rules
        sum_b = 0
        sum_d = 0
        
        # Calculate sums
        for row in range(16):
            # Sum B: column 1 (blank/non-int → 0)
            try:
                val_b = int(self.table.item(row, 1).text() or "0")
                sum_b += val_b
            except ValueError:
                pass
            
            # Sum D: column 3
            try:
                val_d = int(self.table.item(row, 3).text() or "0")
                sum_d += val_d
            except ValueError:
                pass
        
        # Update sum labels
        self.sum_b_label.setText(f"Sum B = {sum_b}")
        self.sum_d_label.setText(f"Sum D = {sum_d}")
        
        # Validate rules
        valid = False
        status_text = ""
        status_color = ""
        
        # Rule: exactly one of sumB or sumD == 576 and the other == 0
        if (sum_b == self.TOTAL and sum_d == 0) or (sum_d == self.TOTAL and sum_b == 0):
            # Check additional rule: if any row has D>0, require nonempty WT1 in same row
            wt1_rule_valid = True
            for row in range(16):
                try:
                    val_d = int(self.table.item(row, 3).text() or "0")
                    if val_d > 0:
                        wt1_value = self.table.item(row, 4).text().strip()
                        if not wt1_value:
                            wt1_rule_valid = False
                            break
                except ValueError:
                    pass
            
            if wt1_rule_valid:
                valid = True
                status_text = "OK"
                status_color = "#4ade80"  # green
            else:
                status_text = "Invalid: WT1 required when D > 0"
                status_color = "#ff6b6b"  # red
        else:
            status_text = "Needs total 576 in exactly one of B or D (the other must be 0)."
            status_color = "#ff6b6b"  # red
        
        # Update status label
        self.status_label.setText(status_text)
        self.status_label.setStyleSheet(f"color: {status_color}; font-weight: 600;")
        
        # Enable DO_MVM only when valid
        self.do_mvm_btn.setEnabled(valid)

    def on_do_mvm_clicked(self):
        # Calculate summary
        sum_b = 0
        sum_d = 0
        non_zero_b_count = 0
        non_zero_d_count = 0
        
        for row in range(16):
            try:
                val_b = int(self.table.item(row, 1).text() or "0")
                if val_b > 0:
                    non_zero_b_count += 1
                sum_b += val_b
            except ValueError:
                pass
            
            try:
                val_d = int(self.table.item(row, 3).text() or "0")
                if val_d > 0:
                    non_zero_d_count += 1
                sum_d += val_d
            except ValueError:
                pass
        
        # Determine active mode
        if sum_b == self.TOTAL:
            active_mode = "B (ACT)"
        else:
            active_mode = "D (WT0)"
        
        # Show summary dialog
        summary = f"""CIMA MVM Summary:
        
Selected CIMA index: {self.target_cima.value()}
Active mode: {active_mode}
Sum B: {sum_b}
Sum D: {sum_d}
Rows with non-zero B entries: {non_zero_b_count}
Rows with non-zero D entries: {non_zero_d_count}"""
        
        QtWidgets.QMessageBox.information(self, "DO_MVM Summary", summary)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AnalogTeam Control Panel")
        self.resize(1000, 600)
        self._apply_style()
        self._build_ui()

    def _build_ui(self):
        central = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(central)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        # Tabs
        self.tabs = QtWidgets.QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.setTabPosition(QtWidgets.QTabWidget.TabPosition.North)
        self.tabs.setMovable(False)

        # Create tabs
        self.tab_buck0 = AnalogTab("BUCK0")
        self.tab_buck1 = AnalogTab("BUCK1")
        self.tab_cima = CimaTab("CIMA")
        self.tab_cima_mvm = CimaMvmTab()
        self.tab_board = AnalogTab("Board")
        self.tab_functions = AnalogTab("Functions")

        self.tabs.addTab(self.tab_buck0, "BUCK0")
        self.tabs.addTab(self.tab_buck1, "BUCK1")
        self.tabs.addTab(self.tab_cima, "CIMA")
        self.tabs.addTab(self.tab_cima_mvm, "CIMA_MVM")
        self.tabs.addTab(self.tab_board, "Board")
        self.tabs.addTab(self.tab_functions, "Functions")

        layout.addWidget(self.tabs)
        self.setCentralWidget(central)

        # Status bar
        status = QtWidgets.QStatusBar()
        status.showMessage("Ready")
        self.setStatusBar(status)

    def _apply_style(self):
        # Fusion + subtle dark palette
        QtWidgets.QApplication.setStyle("Fusion")
        palette = QtGui.QPalette()
        base = QtGui.QColor(30, 34, 42)
        alt = QtGui.QColor(38, 43, 52)
        text = QtGui.QColor(230, 232, 235)
        accent = QtGui.QColor(99, 179, 237)

        palette.setColor(QtGui.QPalette.ColorRole.Window, base)
        palette.setColor(QtGui.QPalette.ColorRole.WindowText, text)
        palette.setColor(QtGui.QPalette.ColorRole.Base, QtGui.QColor(24, 27, 33))
        palette.setColor(QtGui.QPalette.ColorRole.AlternateBase, alt)
        palette.setColor(QtGui.QPalette.ColorRole.ToolTipBase, text)
        palette.setColor(QtGui.QPalette.ColorRole.ToolTipText, text)
        palette.setColor(QtGui.QPalette.ColorRole.Text, text)
        palette.setColor(QtGui.QPalette.ColorRole.Button, alt)
        palette.setColor(QtGui.QPalette.ColorRole.ButtonText, text)
        palette.setColor(QtGui.QPalette.ColorRole.Highlight, accent)
        palette.setColor(QtGui.QPalette.ColorRole.HighlightedText, QtGui.QColor(0, 0, 0))
        palette.setColor(QtGui.QPalette.ColorRole.PlaceholderText, QtGui.QColor("#b9c0cc"))
        QtWidgets.QApplication.setPalette(palette)

        # Stylesheet for modern look
        self.setStyleSheet('''
            QMainWindow { background: #1e222a; }
            QLabel#sectionHeader {
                font-size: 18px; font-weight: 700; letter-spacing: 0.5px;
                padding: 2px 0 6px 2px; color: #e6e8eb;
            }
            QTableWidget {
                border: 1px solid #3a3f4b;
                border-radius: 12px;
                gridline-color: #2b3040;
                background: #181b21;
            }
            QHeaderView::section {
                background: #222734; color: #e6e8eb; padding: 8px;
                border: none; border-right: 1px solid #2b3040;
                font-weight: 600;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QLabel#defaultBadge {
                color: #e7ecf2;                        /* bright text, not dots */
                background: #2c3342;
                padding: 6px 10px;
                border-radius: 10px;
                font-weight: 600;
            }
            QPushButton {
                padding: 8px 14px; border-radius: 10px; border: 1px solid #3a3f4b;
                font-weight: 600;
            }
            QPushButton:hover { border-color: #63b3ed; }
            QPushButton[kind="primary"] { background: #2a3342; }
            QPushButton[kind="secondary"] { background: #242b37; }
            QPushButton[kind="accent"] { background: #63b3ed; color: #0e1116; border-color: #63b3ed; }
            QTabBar::tab {
                background: #242a36; padding: 10px 16px; border-top-left-radius: 10px; border-top-right-radius: 10px;
                margin-right: 4px; color: #cfd5de; font-weight: 600;
            }
            QTabBar::tab:selected { background: #2c3342; color: #ffffff; }
            QStatusBar { background: #202532; color: #cfd5de; }
            QLineEdit {
                color: #ffffff;                       /* typed text */
                background: #1a1e26;
                border: 1px solid #3a3f4b;
                border-radius: 8px;
                padding: 6px 10px;
            }
            QLineEdit::placeholder {
                color: #b9c0cc;                       /* light gray placeholder */
            }
            QLineEdit:focus {
                border-color: #63b3ed;
            }
            QLineEdit[echoMode="0"] {                  /* Normal echo only */
                /* macOS bullet rendering disabled via echo mode */
            }
        ''')

def main():
    import sys
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
