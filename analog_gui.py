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

# ---------- BUCK Register Definitions ----------

# Global Buck registers
# BUCK_GLOBAL_REGISTERS = [
#     ("BUCK_REFERENCE<1:0>", "0"),
#     ("BUCK_TARGET_H<7:0>", "221"),
#     ("BUCK_TARGET_L<7:0>", "144"),
#     ("BUCK_CAL_SETTLING_TIME<3:0>", "5"),
# ]

# BUCK_TOP instance registers (for both BUCK0 and BUCK1)
BUCK_TOP_REGISTERS = [
    ("BUCK_CLK_1G", "0"),
    ("BUCK_RSTB", "0"),
    ("BUCK_ASYNC_RSTB", "0"),
    ("BUCK_CLK_SEL<2:0>", "0"),
    ("BUCK_CALBUF_EN", "0"),
    ("BUCK_CAL_REFBAND_H<1:0>", "3"),
    ("BUCK_CAL_REFCODE_H<9:0>", "256"),
    ("BUCK_CAL_REFBAND_L<1:0>", "2"),
    ("BUCK_CAL_REFCODE_L<9:0>", "128"),
    ("BUCK_CONFIG_H<12:0>", "2155"),
    ("BUCK_CONFIG_L<12:0>", "2155"),
    ("BUCK_PORB", "0"),
    ("BUCK_CALEN", "0"),
    ("BUCK_REFBAND_H<1:0>", "3"),
    ("BUCK_REFCODE_H<9:0>", "256"),
    ("BUCK_REFBAND_L<1:0>", "2"),
    ("BUCK_REFCODE_L<9:0>", "128"),
    ("BUCK_ATP_EN", "0"),
    ("BUCK_TESTCODE_H<2>", "0"),
    ("BUCK_TESTCODE_H<1>", "0"),
    ("BUCK_TESTCODE_H<0>", "0"),
    ("BUCK_TESTCODE_L<2:0>", "0"),
    ("BUCK_EN_TP_TSCORE", "0"),
    ("BUCK_PDB_TSCORE", "0"),
    ("BUCK_RSTB_TSCORE", "0"),
    ("BUCK_BG_RTRIM<3:0>", "0"),
    ("BUCK_BIAS_CTRL<3:0>", "4"),
    ("BUCK_BIAS_PD", "0"),
    ("BUCK_ATP_MUX_CTRL<5:0>", "0"),
    ("BUCK_HADC_CONFIG<16:0>", "124777"),
    ("BUCK_HADC_EN", "0"),
    ("BUCK_HADC_STROBE", "0"),
    ("BUCK_HADC_VALID", "0"),
    ("BUCK_HADC_OUT<7:0>", "0"),
    ("CALCOMP_L", "0"),
    ("CALCOMP_H", "0"),
]

# Combine all BUCK registers
BUCK_ALL_REGISTERS = BUCK_TOP_REGISTERS  # BUCK_GLOBAL_REGISTERS + BUCK_TOP_REGISTERS

# Legacy sample ports for other tabs
PORTS_SAMPLE = [
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

        # Handle both old string format and new tuple format
        if self.ports and isinstance(self.ports[0], tuple):
            # New format: list of (port_name, default_value) tuples
            ports_data = self.ports
            port_names = [port[0] for port in ports_data]
            default_values = [port[1] for port in ports_data]
        else:
            # Old format: list of port names
            ports_data = [(port, "N/A") for port in self.ports]
            port_names = self.ports
            default_values = ["N/A"] * len(self.ports)

        self.table = QtWidgets.QTableWidget(len(ports_data), 7, self)
        self.table.setObjectName("portsTable")
        self.table.setHorizontalHeaderLabels(["Port", "Current", "Write Value", "Default", "Desired", "Read", "Write"])
        self.table.verticalHeader().setVisible(False)
        vh = self.table.verticalHeader()
        vh.setDefaultSectionSize(42)          # taller rows to enlarge surrounding boxes
        vh.setMinimumSectionSize(38)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)

        # subtle drop shadow to give table depth
        shadow = QtWidgets.QGraphicsDropShadowEffect(self.table)
        shadow.setBlurRadius(18)
        shadow.setOffset(0, 2)
        shadow.setColor(QtGui.QColor(0, 0, 0, 180))
        self.table.setGraphicsEffect(shadow)

        for row, (port_name, default_value) in enumerate(ports_data):
            # Port
            name_item = QtWidgets.QTableWidgetItem(port_name)
            name_item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignVCenter | QtCore.Qt.AlignmentFlag.AlignLeft)
            self.table.setItem(row, 0, name_item)

            # Current
            current_item = QtWidgets.QTableWidgetItem("N/A")
            current_item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 1, current_item)

            # Write Value (editable)
            write_editor = ClearLineEdit(placeholder="enter value", align_center=True)
            write_editor.setMinimumHeight(26)               # <-- add height
            write_editor.setTextMargins(6, 0, 6, 0)         # <-- inner padding
            self.table.setCellWidget(row, 2, write_editor)

            # Default value label (centered with inner padding)
            default_lbl = BadgeLabel(default_value)
            default_lbl.setFixedHeight(24)
            default_container = QtWidgets.QWidget()
            default_layout = QtWidgets.QHBoxLayout(default_container)
            default_layout.setContentsMargins(0, 0, 0, 0)
            default_layout.setSpacing(0)
            default_layout.addStretch(1)
            default_layout.addWidget(default_lbl)
            default_layout.addStretch(1)
            default_container.setObjectName("cellBox")
            self.table.setCellWidget(row, 3, default_container)

            # Desired
            desired_item = QtWidgets.QTableWidgetItem("N/A")
            desired_item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 4, desired_item)

            # Individual Read button
            read_btn = QtWidgets.QPushButton("Read")
            read_btn.setProperty("kind", "secondary")
            read_btn.setProperty("size", "small")
            read_btn.setFixedWidth(75)
            read_btn.setFixedHeight(26)
            # keep elevation so text renders crisply inside cell
            read_btn.setFlat(False)
            read_btn.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
            read_btn.clicked.connect(lambda checked, r=row: self.on_read_single(r))
            container_read = QtWidgets.QWidget()
            layout_read = QtWidgets.QHBoxLayout(container_read)
            layout_read.setContentsMargins(6, 0, 6, 0)
            layout_read.setSpacing(0)
            layout_read.addStretch(1)
            layout_read.addWidget(read_btn)
            layout_read.addStretch(1)
            # Keep read cell plain to avoid halo around button
            # container_read.setObjectName("cellBox")
            self.table.setCellWidget(row, 5, container_read)

            # Individual Write button
            write_btn = QtWidgets.QPushButton("Write")
            write_btn.setProperty("kind", "primary")
            write_btn.setProperty("size", "small")
            write_btn.setFixedWidth(75)
            write_btn.setFixedHeight(26)
            write_btn.setFlat(False)
            write_btn.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
            write_btn.clicked.connect(lambda checked, r=row: self.on_write_single(r))
            container_write = QtWidgets.QWidget()
            layout_write = QtWidgets.QHBoxLayout(container_write)
            layout_write.setContentsMargins(6, 0, 6, 0)
            layout_write.setSpacing(0)
            layout_write.addStretch(1)
            layout_write.addWidget(write_btn)
            layout_write.addStretch(1)
            # Keep write cell plain to avoid halo around button
            # container_write.setObjectName("cellBox")
            self.table.setCellWidget(row, 6, container_write)

        header_view = self.table.horizontalHeader()
        header_view.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeMode.Stretch)
        header_view.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
        header_view.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
        header_view.setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeMode.Fixed)
        header_view.setSectionResizeMode(4, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
        header_view.setSectionResizeMode(5, QtWidgets.QHeaderView.ResizeMode.Fixed)
        header_view.setSectionResizeMode(6, QtWidgets.QHeaderView.ResizeMode.Fixed)
        header_view.resizeSection(3, 79)  # Default column box wider
        header_view.resizeSection(5, 124)  # Read column box wider
        header_view.resizeSection(6, 124)  # Write column box wider

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

    def on_read_single(self, row: int):
        """Handle individual read button click for a specific row."""
        port_name = self.table.item(row, 0).text()
        self.table.item(row, 1).setText("N/A")  # Update current value
        QtWidgets.QMessageBox.information(self, "Read Single", f"[{self.title}] Read {port_name} (frontend only).")

    def on_write_single(self, row: int):
        """Handle individual write button click for a specific row."""
        port_name = self.table.item(row, 0).text()
        editor = self.table.cellWidget(row, 2)  # ClearLineEdit
        value = editor.text() if isinstance(editor, QtWidgets.QLineEdit) else ""
        self.table.item(row, 4).setText(value if value else "N/A")  # Update desired value
        QtWidgets.QMessageBox.information(self, "Write Single", f"[{self.title}] Wrote {port_name} = {value} (frontend only).")


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
        vh = self.table.verticalHeader()
        vh.setDefaultSectionSize(30)          # <-- taller rows while editing
        vh.setMinimumSectionSize(28)
        
        # Custom delegate for comfortable editor sizing
        class _ComfyDelegate(QtWidgets.QStyledItemDelegate):
            def createEditor(self, parent, option, index):
                ed = QtWidgets.QLineEdit(parent)
                ed.setMinimumHeight(26)                  # <-- height so text isn't cramped
                ed.setTextMargins(6, 0, 6, 0)            # <-- inner padding
                # keep your dark look consistent
                ed.setStyleSheet("""
                    QLineEdit {
                        color: #ffffff;
                        background: #1a1e26;
                        border: 1px solid #3a3f4b;
                        border-radius: 8px;
                        padding: 4px 8px;
                    }
                    QLineEdit:focus { border-color: #63b3ed; }
                """)
                return ed

        # install for all columns
        self.table.setItemDelegate(_ComfyDelegate(self.table))
        
        # Make vertical headers visible to emphasize row index
        self.table.verticalHeader().setVisible(True)
        self.table.verticalHeader().setDefaultAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.table.setVerticalHeaderLabels([str(i) for i in range(self.table.rowCount())])
        
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.AllEditTriggers)
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
        rows = self.table.rowCount()
        sum_b = sum(int(self.table.item(r, 1).text() or "0") for r in range(rows))
        sum_d = sum(int(self.table.item(r, 3).text() or "0") for r in range(rows))

        def is_single_576(vec):
            return vec.count(576) == 1 and all((v == 0 or v == 576) for v in vec)

        colB = [int(self.table.item(r, 1).text() or "0") for r in range(rows)]
        colD = [int(self.table.item(r, 3).text() or "0") for r in range(rows)]

        if (sum_d == self.TOTAL) and is_single_576(colB):
            active_mode = "Differing weights (WT0 distributed, ACT fixed @ single 576 row)"
        elif (sum_b == self.TOTAL) and is_single_576(colD):
            active_mode = "Differing activation (ACT distributed, WT0 fixed @ single 576 row)"
        else:
            active_mode = "Invalid/ambiguous"

        non_zero_b_count = sum(1 for v in colB if v > 0)
        non_zero_d_count = sum(1 for v in colD if v > 0)
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

        self.tab_buck0 = AnalogTab("BUCK0", BUCK_ALL_REGISTERS)
        self.tab_buck1 = AnalogTab("BUCK1", BUCK_ALL_REGISTERS)
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
                gridline-color: transparent; /* hide grid lines for cleaner look */
                background: #181b21;
                font-size: 13px;              /* <-- add this */
            }
            QTableWidget::item:selected {
                background: #2b3445;
                color: #ffffff;
            }
            QHeaderView::section {
                background: #222734; color: #e6e8eb; padding: 10px 8px;
                border: none; border-right: 1px solid #2b3040;
                font-weight: 600;
                text-align: center; /* center header labels */
            }
            QTableWidget::item { padding: 8px; }
            /* Cell box background to visually enlarge the surrounding boxes */
            QWidget#cellBox {
                background: #202632;
                border: 1px solid #2b3040;
                border-radius: 12px;
            }
            QPushButton {
                padding: 8px 14px; border-radius: 10px; border: 1px solid #3a3f4b;
                font-weight: 600;
            }
            QPushButton:hover { border-color: #63b3ed; }
            QPushButton[kind="primary"] { background: #2a3342; }
            QPushButton[kind="secondary"] { background: #242b37; }
            QPushButton[kind="accent"] { background: #63b3ed; color: #0e1116; border-color: #63b3ed; }
            /* Small buttons for individual row actions */
            QPushButton[size="small"] {
                padding: 4px 12px; border-radius: 8px; font-size: 12px;
                font-weight: 600; min-height: 26px; max-height: 32px; color: #ffffff;
            }
            QPushButton[size="small"]:hover {
                transform: translateY(-1px);
                box-shadow: 0 2px 4px rgba(99, 179, 237, 0.3);
            }
            QPushButton[size="small"][kind="primary"] {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #4a90e2, stop:1 #357abd);
                border: 1px solid #357abd; color: #ffffff;
            }
            QPushButton[size="small"][kind="primary"]:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #5ba0f2, stop:1 #4a90e2);
                color: #ffffff;
            }
            QPushButton[size="small"][kind="secondary"] {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #3a3f4b, stop:1 #2a2f3a);
                border: 1px solid #4a5568; color: #e6e8eb;
            }
            QPushButton[size="small"][kind="secondary"]:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #4a5568, stop:1 #3a3f4b);
                color: #ffffff;
            }
            /* Sleek scrollbars */
            QScrollBar:vertical {
                background: #1b1f27; width: 12px; margin: 4px 2px 4px 0;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: #3a3f4b; min-height: 24px; border-radius: 6px;
            }
            QScrollBar::handle:vertical:hover { background: #4a5568; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
            QScrollBar:horizontal { height: 10px; background: #1b1f27; margin: 0 4px; }
            QScrollBar::handle:horizontal { background: #3a3f4b; border-radius: 6px; }
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
