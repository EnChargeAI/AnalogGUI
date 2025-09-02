from PyQt6 import QtCore, QtGui, QtWidgets
from typing import List, Optional

# ---------- Custom widgets that force visible text ----------

class ClearLineEdit(QtWidgets.QLineEdit):
    """QLineEdit that always renders a readable placeholder on dark UIs."""
    def __init__(self, *args, placeholder: str = "", align_center: bool = True, **kwargs):
        super().__init__(*args, **kwargs)
        self._ph = placeholder
        if placeholder:
            # Keep Qt's placeholder empty so we fully control paint
            super().setPlaceholderText("")
        if align_center:
            self.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.setEchoMode(QtWidgets.QLineEdit.EchoMode.Normal)
        self.setInputMask("")
        self.setInputMethodHints(QtCore.Qt.InputMethodHint.ImhNone)

    def setPlaceholderText(self, text: str) -> None:  # type: ignore[override]
        self._ph = text
        super().setPlaceholderText("")  # ensure Qt does not paint its own dots
        self.update()

    def paintEvent(self, e: QtGui.QPaintEvent) -> None:
        # Let the normal line edit paint first
        super().paintEvent(e)

        # If empty, draw our placeholder centered with a clear color
        if not self.text() and self._ph:
            p = QtGui.QPainter(self)
            p.setRenderHint(QtGui.QPainter.RenderHint.TextAntialiasing, True)
            p.setPen(QtGui.QColor("#b9c0cc"))  # readable light gray
            rect = self.rect().adjusted(10, 0, -10, 0)
            flags = QtCore.Qt.AlignmentFlag.AlignVCenter | QtCore.Qt.AlignmentFlag.AlignHCenter
            p.drawText(rect, int(flags), self._ph)
            p.end()


class BadgeLabel(QtWidgets.QLabel):
    """Capsule label that always shows bright text, never dotted/ellipsized."""
    def __init__(self, text="N/A", parent=None):
        super().__init__(text, parent)
        self.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.setMinimumWidth(64)
        self.setObjectName("defaultBadge")

    def paintEvent(self, e: QtGui.QPaintEvent) -> None:
        # Custom paint to guarantee contrast & no elide
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing, True)
        bg = QtGui.QColor("#2c3342")
        fg = QtGui.QColor("#e7ecf2")
        # rounded background
        r = self.rect()
        path = QtGui.QPainterPath()
        path.addRoundedRect(QtCore.QRectF(r.adjusted(0, 0, -1, -1)), 10, 10)
        painter.fillPath(path, bg)
        # text
        painter.setPen(fg)
        flags = QtCore.Qt.AlignmentFlag.AlignCenter
        painter.drawText(r, int(flags), self.text())
        painter.end()

# ---------- Demo data ----------

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

# ---------- Tabs ----------

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

        header = QtWidgets.QLabel(self.title)
        header.setObjectName("sectionHeader")
        outer.addWidget(header)

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

            # Write Value (editable)
            write_editor = ClearLineEdit(placeholder="enter value")
            self.table.setCellWidget(row, 2, write_editor)

            # Default value label
            default_lbl = BadgeLabel("N/A")
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

        # Bottom toolbar
        bottom = QtWidgets.QHBoxLayout()
        bottom.addStretch(1)

        self.read_all_btn = QtWidgets.QPushButton("Read All")
        self.read_all_btn.setProperty("kind", "secondary")
        self.read_all_btn.clicked.connect(self.on_read_all)
        bottom.addWidget(self.read_all_btn)

        self.write_all_btn = QtWidgets.QPushButton("Write All")
        self.write_all_btn.setProperty("kind", "primary")
        self.write_all_btn.clicked.connect(self.on_write_all)
        bottom.addWidget(self.write_all_btn)

        self.check_hadc_btn = QtWidgets.QPushButton("Check HADC")
        self.check_hadc_btn.setProperty("kind", "accent")
        self.check_hadc_btn.clicked.connect(self.on_check_hadc_clicked)
        bottom.addWidget(self.check_hadc_btn)

        outer.addLayout(bottom)

    def on_read_all(self):
        for r in range(self.table.rowCount()):
            self.table.item(r, 1).setText("N/A")
        QtWidgets.QMessageBox.information(self, "Read All", f"[{self.title}] Read all (frontend only).")

    def on_write_all(self):
        for r in range(self.table.rowCount()):
            editor = self.table.cellWidget(r, 2)  # ClearLineEdit
            value = editor.text() if isinstance(editor, QtWidgets.QLineEdit) else ""
            self.table.item(r, 4).setText(value if value else "N/A")
        QtWidgets.QMessageBox.information(self, "Write All", f"[{self.title}] Wrote all (frontend only).")

    def on_check_hadc_clicked(self):
        QtWidgets.QMessageBox.information(self, "Check HADC", f"[{self.title}] Checking HADC... (placeholder)")


class CimaTab(AnalogTab):
    def __init__(self, title: str, ports: Optional[List[str]] = None, parent=None):
        super().__init__(title, ports, parent)
        self._add_cima_controls()

    def _add_cima_controls(self):
        cima_bar = QtWidgets.QHBoxLayout()

        self.cima_index = QtWidgets.QSpinBox()
        self.cima_index.setRange(0, 63)
        self.cima_index.setPrefix("CIMA idx: ")
        self.cima_index.setToolTip("Single CIMA index (0–63).")
        cima_bar.addWidget(self.cima_index)

        self.cima_mask = ClearLineEdit(placeholder="64'h0000_0000_0000_0001", align_center=False)
        self.cima_mask.setToolTip("Optional 64'h… bitmask; if provided, overrides index on writes (frontend only).")
        cima_bar.addWidget(self.cima_mask)

        self.mask_error = QtWidgets.QLabel("Invalid mask")
        self.mask_error.setStyleSheet("color: #ff6b6b; font-weight: 600;")
        self.mask_error.hide()
        cima_bar.addWidget(self.mask_error)

        cima_bar.addStretch(1)

        layout = self.layout()
        layout.insertLayout(1, cima_bar)

        self.cima_mask.textChanged.connect(self._validate_mask)
        self.cima_index.valueChanged.connect(self._validate_mask)

    def _validate_mask(self):
        import re
        mask_text = self.cima_mask.text().strip()
        if not mask_text:
            self.mask_error.hide()
            self.write_all_btn.setEnabled(True)
            return

        if re.match(r"^64'h[0-9A-Fa-f_]{1,19}$", mask_text):
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

        header = QtWidgets.QLabel("CIMA_MVM")
        header.setObjectName("sectionHeader")
        outer.addWidget(header)

        top_bar = QtWidgets.QHBoxLayout()
        target_label = QtWidgets.QLabel("Target CIMA: ")
        self.target_cima = QtWidgets.QSpinBox()
        self.target_cima.setRange(0, 63)
        top_bar.addWidget(target_label)
        top_bar.addWidget(self.target_cima)
        top_bar.addStretch(1)
        outer.addLayout(top_bar)

        self.table = QtWidgets.QTableWidget(16, 5, self)
        self.table.setObjectName("portsTable")
        self.table.setHorizontalHeaderLabels(["ACT VAL", "No rows (ACT)", "WT VAL (WT0)", "No rows (WT0)", "WT1 (ADC weights)"])
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.DoubleClicked)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)

        for row in range(16):
            for col in range(5):
                it = QtWidgets.QTableWidgetItem("")
                if col == 1:  # Column B (No rows ACT)
                    it.setData(QtCore.Qt.ItemDataRole.UserRole, "input")
                    it.setBackground(QtGui.QColor("#2a1f1f"))
                elif col == 3:  # Column D (No rows WT0)
                    it.setData(QtCore.Qt.ItemDataRole.UserRole, "input")
                    it.setBackground(QtGui.QColor("#2a1f1f"))
                self.table.setItem(row, col, it)

        header_view = self.table.horizontalHeader()
        header_view.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeMode.Stretch)
        header_view.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
        header_view.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
        header_view.setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
        header_view.setSectionResizeMode(4, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)

        outer.addWidget(self.table, stretch=1)

        footer = QtWidgets.QHBoxLayout()
        self.sum_b_label = QtWidgets.QLabel("Sum B = 0")
        self.sum_d_label = QtWidgets.QLabel("Sum D = 0")
        footer.addWidget(self.sum_b_label)
        footer.addWidget(self.sum_d_label)
        footer.addStretch(1)
        self.status_label = QtWidgets.QLabel("Needs one dimension distributed to 576 and the other a single 576 row.")
        self.status_label.setStyleSheet("color: #ff6b6b; font-weight: 600;")
        self.status_label.setToolTip("Exactly one of B or D must be a single 576 in one row (others 0). The other column must distribute to 576 across rows. If D[r] > 0, enter WT1[r].")
        footer.addWidget(self.status_label)
        outer.addLayout(footer)

        bottom = QtWidgets.QHBoxLayout()
        bottom.addStretch(1)
        self.do_mvm_btn = QtWidgets.QPushButton("DO_MVM")
        self.do_mvm_btn.setProperty("kind", "accent")
        self.do_mvm_btn.setEnabled(False)
        self.do_mvm_btn.clicked.connect(self.on_do_mvm_clicked)
        bottom.addWidget(self.do_mvm_btn)
        outer.addLayout(bottom)

    def _wire(self):
        self.table.itemChanged.connect(self._recompute_validation)

    def _recompute_validation(self):
        # Parse integer columns safely
        def col_int(r, c):
            try:
                return int(self.table.item(r, c).text() or "0")
            except Exception:
                return 0

        rows = self.table.rowCount()
        colB = [col_int(r, 1) for r in range(rows)]  # No rows (ACT)
        colD = [col_int(r, 3) for r in range(rows)]  # No rows (WT0)

        sum_b = sum(colB)
        sum_d = sum(colD)
        self.sum_b_label.setText(f"Sum B = {sum_b}")
        self.sum_d_label.setText(f"Sum D = {sum_d}")

        # Helper: exactly one entry equals 576 and all others are 0
        def is_single_576(vec):
            return vec.count(576) == 1 and all((v in (0, 576)) for v in vec)

        # WT1 requirement: if D[r] > 0 then WT1[r] must be non-empty
        wt1_ok = True
        for r in range(rows):
            if colD[r] > 0:
                txt = (self.table.item(r, 4).text() or "").strip()
                if not txt:
                    wt1_ok = False
                    break

        # Two legal modes per spec:
        #  - Differing weights:  D distributes to 576, B is a single 576 row
        #  - Differing activation: B distributes to 576, D is a single 576 row
        differing_weights_ok   = (sum_d == self.TOTAL) and is_single_576(colB)
        differing_activation_ok = (sum_b == self.TOTAL) and is_single_576(colD)

        valid = wt1_ok and (differing_weights_ok or differing_activation_ok)

        if valid:
            self.status_label.setText("OK")
            self.status_label.setStyleSheet("color: #4ade80; font-weight: 600;")
        else:
            self.status_label.setText("Needs one dimension distributed to 576 and the other a single 576 row.")
            self.status_label.setStyleSheet("color: #ff6b6b; font-weight: 600;")

        self.do_mvm_btn.setEnabled(valid)

    def on_do_mvm_clicked(self):
        sum_b = 0
        sum_d = 0
        non_zero_b_count = 0
        non_zero_d_count = 0

        for row in range(16):
            try:
                val_b = int(self.table.item(row, 1).text() or "0")
                if val_b > 0: non_zero_b_count += 1
                sum_b += val_b
            except ValueError:
                pass
            try:
                val_d = int(self.table.item(row, 3).text() or "0")
                if val_d > 0: non_zero_d_count += 1
                sum_d += val_d
            except ValueError:
                pass

        # Determine active mode under the corrected rules
        def is_single_576(vec):
            return vec.count(576) == 1 and all((v in (0, 576)) for v in vec)

        if (sum_d == self.TOTAL) and is_single_576([int(self.table.item(r, 1).text() or "0") for r in range(16)]):
            active_mode = "Differing weights (WT0 distributed, ACT fixed @ single 576 row)"
        elif (sum_b == self.TOTAL) and is_single_576([int(self.table.item(r, 3).text() or "0") for r in range(16)]):
            active_mode = "Differing activation (ACT distributed, WT0 fixed @ single 576 row)"
        else:
            active_mode = "Invalid/ambiguous"
        summary = f"""CIMA MVM Summary:

Selected CIMA index: {self.target_cima.value()}
Active mode: {active_mode}
Sum B: {sum_b}
Sum D: {sum_d}
Rows with non-zero B entries: {non_zero_b_count}
Rows with non-zero D entries: {non_zero_d_count}"""
        QtWidgets.QMessageBox.information(self, "DO_MVM Summary", summary)

# ---------- Main Window ----------

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

        self.tabs = QtWidgets.QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.setTabPosition(QtWidgets.QTabWidget.TabPosition.North)

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

        status = QtWidgets.QStatusBar()
        status.showMessage("Ready")
        self.setStatusBar(status)

    def _apply_style(self):
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
            QTableWidget::item { padding: 8px; }
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
            /* Line edit chrome */
            QLineEdit {
                color: #ffffff;
                background: #1a1e26;
                border: 1px solid #3a3f4b;
                border-radius: 8px;
                padding: 6px 10px;
            }
            QLineEdit:focus { border-color: #63b3ed; }
            /* Input cell styling */
            QTableWidget::item.inputCell { background: #2a1f1f; }
            /* BadgeLabel uses custom paint; no extra CSS needed */
        ''')

# ---------- App ----------

def main():
    import sys
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
