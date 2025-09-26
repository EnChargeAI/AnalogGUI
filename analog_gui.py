from PyQt6 import QtCore, QtGui, QtWidgets
from typing import List, Optional, Callable

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

# ---------- CIMA IO Register List (filtered) ----------
# Kept only Data/Config/Control; skipped SCAN_*, supplies (DVDD/AVDD*/DVSS/AGND), signals, and CLKs
CIMA_REGISTERS = [
    # Data banks (read-only placeholders retained where applicable)
    ("DATA_RD_BANK0<127:0>", "0"),
    ("DATA_RD_BANK1<127:0>", "0"),
    ("DATA_RD_BANK2<127:0>", "0"),
    ("DATA_RD_BANK3<127:0>", "0"),
    ("MEM_CH_FAULT<67:0>", "0"),

    # Wordline controls
    ("WL_WID_CTRL<3:0>", "8"),
    ("WL_DLY_CTRL<3:0>", "8"),

    # (ADDR_BANK* and CIMA_BANK*_EN removed: not controlled by register)

    # ACT calibration controls
    ("ACT_CAL_CTRL1<11:0>", "1536"),
    ("ACT_CAL_CTRL2<11:0>", "1877"),
    ("ACT_CAL_CTRL3<11:0>", "2347"),
    ("ACT_CAL_CTRL4<11:0>", "2688"),
    ("ACT_CAL_CTRL_RST1<11:0>", "1280"),
    ("ACT_CAL_CTRL_RST2<11:0>", "1451"),
    ("ACT_CAL_CTRL_FLT_RST<11:0>", "2389"),

    # ACT programming controls
    ("ACT_PROG_CTRL1<7:0>", "93"),
    ("ACT_PROG_CTRL2<7:0>", "108"),
    ("ACT_PROG_CTRL3<7:0>", "115"),
    ("ACT_PROG_CTRL4<7:0>", "122"),
    ("ACT_PROG_CTRL_RST1<7:0>", "85"),
    ("ACT_PROG_CTRL_RST2<7:0>", "84"),
    ("ACT_PROG_CTRL_FLT_RST<7:0>", "115"),
    ("ACT_PROG_CTRL_SPARE<19>", "0"),
    ("ACT_PROG_CTRL_SPARE<18:16>", "0"),
    ("ACT_PROG_CTRL_SPARE<15>", "0"),
    ("ACT_PROG_CTRL_SPARE<14>", "0"),
    ("ACT_PROG_CTRL_SPARE<13>", "0"),
    ("ACT_PROG_CTRL_SPARE<12>", "0"),
    ("ACT_PROG_CTRL_SPARE<11>", "0"),
    ("ACT_PROG_CTRL_SPARE<10>", "0"),
    ("ACT_PROG_CTRL_SPARE<9>", "0"),
    ("ACT_PROG_CTRL_SPARE<8:6>", "4"),
    ("ACT_PROG_CTRL_SPARE<5>", "0"),
    ("ACT_PROG_CTRL_SPARE<4>", "1"),
    ("ACT_PROG_CTRL_SPARE<3>", "1"),
    ("ACT_PROG_CTRL_SPARE<2:0>", "3"),

    # COM
    ("ACT_PROG_COM<9>", "0"),
    ("ACT_PROG_COM<8:5>", "15"),
    ("ACT_PROG_COM<4>", "0"),
    ("ACT_PROG_COM<3>", "0"),
    ("ACT_PROG_COM<2:0>", "3"),

    # Misc config
    ("DMUX_CTRL<4:0>", "0"),
    ("D_FLT_RST_RISE<2:0>", "1"),
    ("D_FLT_RST_FALL<2:0>", "5"),
    ("D_FLT_RST_GAP<1:0>", "1"),
    ("D_RST_EVAL_GAP<1:0>", "2"),
    ("D_EVAL_PW<1:0>", "1"),
    ("D_ADC_SMPL_PW<2:0>", "2"),
    ("D_AZ_RISE<2:0>", "0"),
    ("D_AZ_PW<2:0>", "0"),

    # (IA_BIT*, MASK_B removed: not controlled by CWRAP register)

    # ADC and CIMA resets/enables (ADC_CH_EN removed: not controlled by CWRAP)
    ("ADC_PWR_MODE<1:0>", "0"),
    ("ADC_TMSB_CTRL<2:0>", "3"),
    ("ADC_TDAC_CTRL<2:0>", "3"),
    ("ADC_INTR_RSTB", "0"),
    ("ADC_INTR_ASYNC_RSTB", "0"),
    ("CIMA_RSTB", "0"),
    ("CIMA_ASYNC_RSTB", "0"),
    ("CIMA_BLWL_RSTB", "0"),
    ("CIMA_BLWL_ASYNC_RSTB", "0"),

    # Starts and DCDL
    ("STARTCAL", "0"),
    ("CAL_DONE", "0"),
    # (START removed: not controlled by CWRAP)
    ("DCDL_CTRL_EXT<9:0>", "512"),
    # (DCDL_OVERRIDE_EN removed: deprecated)

    # References and bias
    ("CLK_SEL<2:0>", "0"),
    ("VREF_CAL_CTRL<7:0>", "128"),
    ("VREF_SCALE_CTRL<1:0>", "0"),
    ("BG_TRIM<3:0>", "8"),
    ("CIMA_BIAS_CTRL<3:0>", "0"),
    ("CIMA_BIAS_PD", "0"),

    # TScore
    ("EN_TP_TSCORE", "0"),
    ("PDB_VBG_TSCORE", "0"),
    ("RSTB_VBG_TSCORE", "0"),

    # ATP and HADC controls
    ("EN_TP_ATP", "0"),
    ("ATP_MUX_CTRL<5:0>", "0"),
    ("ACT_TSTMUX_CTRL<6:0>", "0"),
    ("HADC_CTRL_CPRE<1:0>", "2"),
    ("HADC_CURR_CPRE<1:0>", "1"),
    ("HADC_TDLY_CPRE<2:0>", "4"),
    ("HADC_TDAC_CPRE<2:0>", "7"),
    ("HADC_TMSB_CPRE<2:0>", "7"),
    ("HADC_CTRL_GAIN<1:0>", "1"),
    ("HADC_CTRL_VCM2<1:0>", "2"),
    ("HADC_EN", "0"),
    ("HADC_STROBE", "0"),
    ("HADC_VALID", "0"),
    ("HADC<7:0>", "0"),

    # ANA_GEN_SPAREs
    ("ANA_GEN_SPARE<31>", "0"),
    ("ANA_GEN_SPARE<30>", "0"),
    ("ANA_GEN_SPARE<29>", "0"),
    ("ANA_GEN_SPARE<28>", "0"),
    ("ANA_GEN_SPARE<27:22>", "0"),
    ("ANA_GEN_SPARE<21>", "0"),
    ("ANA_GEN_SPARE<20:10>", "0"),
    ("ANA_GEN_SPARE<9>", "0"),
    ("ANA_GEN_SPARE<8>", "0"),
    ("ANA_GEN_SPARE<7>", "0"),
    ("ANA_GEN_SPARE<6:1>", "0"),
    ("ANA_GEN_SPARE<0>", "0"),

    # ADC outputs
    ("ADCX_OUT<8:0>", "0"),
    ("ADC_VALID", "0"),
]

# ---------- Tabs ----------

class AnalogTab(QtWidgets.QWidget):
    def __init__(self, title: str, ports: Optional[List[str]] = None, parent=None):
        super().__init__(parent)
        self.title = title
        self.ports = ports or PORTS_SAMPLE
        self._build_ui()

    def _on_filter_all_toggled(self, checked: bool):
        # When All is toggled, set all individual types to the same state
        if not hasattr(self, "_function_filter_checkboxes"):
            return
        
        # Get current state of individual checkboxes
        states = [cb.isChecked() for cb in self._function_filter_checkboxes.values()]
        any_on = any(states)
        all_on = all(states)
        
        # Determine the target state based on current state
        # If currently all on or partially on, turn all off
        # If currently all off, turn all on
        target_state = not any_on
        
        # Block signals on all checkboxes to prevent recursive calls
        for cb in self._function_filter_checkboxes.values():
            cb.blockSignals(True)
        
        # Set all individual checkboxes to the target state
        for cb in self._function_filter_checkboxes.values():
            cb.setChecked(target_state)
        
        # Re-enable signals on all checkboxes
        for cb in self._function_filter_checkboxes.values():
            cb.blockSignals(False)
        
        # Update the All checkbox state to reflect the new state
        self._filter_all_checkbox.blockSignals(True)
        if target_state:
            self._filter_all_checkbox.setCheckState(QtCore.Qt.CheckState.Checked)
        else:
            self._filter_all_checkbox.setCheckState(QtCore.Qt.CheckState.Unchecked)
        self._filter_all_checkbox.blockSignals(False)
        
        self._apply_function_filter()

    def _on_filter_type_toggled(self, _checked: bool):
        # Update All checkbox tristate behavior and apply filter
        if not hasattr(self, "_function_filter_checkboxes"):
            return
        
        # Small delay to ensure all state changes are processed
        QtCore.QTimer.singleShot(0, self._update_all_checkbox_state)
        self._apply_function_filter()
    
    def _update_all_checkbox_state(self):
        """Update the All checkbox state based on individual checkbox states"""
        if not hasattr(self, "_function_filter_checkboxes") or not hasattr(self, "_filter_all_checkbox"):
            return
        
        states = [cb.isChecked() for cb in self._function_filter_checkboxes.values()]
        any_on = any(states)
        all_on = all(states)
        
        # Block signals to prevent recursive calls
        self._filter_all_checkbox.blockSignals(True)
        
        # Set the appropriate check state
        if all_on:
            self._filter_all_checkbox.setCheckState(QtCore.Qt.CheckState.Checked)
        elif any_on:
            self._filter_all_checkbox.setCheckState(QtCore.Qt.CheckState.PartiallyChecked)
        else:
            self._filter_all_checkbox.setCheckState(QtCore.Qt.CheckState.Unchecked)
        
        # Re-enable signals
        self._filter_all_checkbox.blockSignals(False)

    def _apply_function_filter(self):
        # Hide/show rows based on selected function kinds
        if not hasattr(self, "_row_function_kind"):
            return
        # Build allowed kinds
        allowed = set()
        if hasattr(self, "_function_filter_checkboxes"):
            for kind, cb in self._function_filter_checkboxes.items():
                if cb.isChecked():
                    allowed.add(kind)
        # Also apply text search filter if present
        search_text = ""
        if hasattr(self, "_filter_search_edit"):
            search_text = self._filter_search_edit.text().strip().lower()
        # If none selected, show nothing
        for row, kind in self._row_function_kind.items():
            show_kind = (kind in allowed) if allowed else False
            if show_kind and search_text:
                # match on port name or function text
                try:
                    port_name = self.table.item(row, self._columns["port"]).text()
                except Exception:
                    port_name = ""
                func_text = kind
                match = (search_text in port_name.lower()) or (search_text in func_text.lower())
                show_kind = show_kind and match
            self.table.setRowHidden(row, not show_kind)

    def _on_search_changed(self, _text: str):
        self._apply_function_filter()

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

        # Add a Function column for CIMA and BUCK tabs
        is_cima_tab = str(self.title).upper() == "CIMA"
        is_buck_tab = str(self.title).upper().startswith("BUCK")
        headers = ["Port", "Current", "Write Value", "Default", "Read", "Write"]
        if is_cima_tab or is_buck_tab:
            headers = ["Port", "Function", "Current", "Write Value", "Default", "Read", "Write"]
        self.table = QtWidgets.QTableWidget(len(ports_data), len(headers), self)
        self.table.setObjectName("portsTable")
        self.table.setHorizontalHeaderLabels(headers)
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

        # Function filter bar (only for CIMA and BUCK tabs)
        if is_cima_tab or is_buck_tab:
            self._function_filter_checkboxes = {}
            self._filter_all_checkbox = QtWidgets.QCheckBox("All")
            self._filter_all_checkbox.setTristate(True)
            self._filter_all_checkbox.setCheckState(QtCore.Qt.CheckState.Checked)
            self._filter_all_checkbox.toggled.connect(self._on_filter_all_toggled)

            filter_layout = QtWidgets.QHBoxLayout()
            filter_layout.addWidget(QtWidgets.QLabel("Filter:"))
            filter_layout.addSpacing(6)
            filter_layout.addWidget(self._filter_all_checkbox)
            for kind in ["Control", "Config", "Data"]:
                cb = QtWidgets.QCheckBox(kind)
                cb.setChecked(True)
                cb.toggled.connect(self._on_filter_type_toggled)
                self._function_filter_checkboxes[kind] = cb
                filter_layout.addWidget(cb)
            filter_layout.addStretch(1)

            # Search field (live filter by port/function)
            self._filter_search_edit = ClearLineEdit(placeholder="Search registers…", align_center=False)
            try:
                self._filter_search_edit.setClearButtonEnabled(True)
            except Exception:
                pass
            self._filter_search_edit.setFixedWidth(240)
            self._filter_search_edit.textChanged.connect(self._on_search_changed)
            filter_layout.addWidget(self._filter_search_edit)

            # Place just under the section header (index 1)
            outer.insertLayout(1, filter_layout)

        # Determine tab-specific output-only fields to disable writes per-row
        # Column indices mapping (differs when Function column is present)
        has_function_col = is_cima_tab or is_buck_tab
        if has_function_col:
            self._columns = {
                "port": 0,
                "function": 1,
                "current": 2,
                "write_val": 3,
                "default": 4,
                "read": 5,
                "write": 6,
            }
        else:
            self._columns = {
                "port": 0,
                "function": None,
                "current": 1,
                "write_val": 2,
                "default": 3,
                "read": 4,
                "write": 5,
            }

        # Simple function classifier for CIMA entries
        def _classify_function(name: str) -> str:
            mapping = {
                # -------- BUCK mapping --------
                # Global Buck registers
                "BUCK_REFERENCE<1:0>": "Control",
                "BUCK_TARGET_H<7:0>": "Config",
                "BUCK_TARGET_L<7:0>": "Config",
                "BUCK_CAL_SETTLING_TIME<3:0>": "Config",
                # BUCK_TOP instance registers
                "BUCK_CLK_1G": "Clock",
                "BUCK_RSTB": "Control",
                "BUCK_ASYNC_RSTB": "Control",
                "BUCK_CLK_SEL<2:0>": "Config",
                "BUCK_CALBUF_EN": "Control",
                "BUCK_CAL_REFBAND_H<1:0>": "Config",
                "BUCK_CAL_REFCODE_H<9:0>": "Config",
                "BUCK_CAL_REFBAND_L<1:0>": "Config",
                "BUCK_CAL_REFCODE_L<9:0>": "Config",
                "BUCK_CONFIG_H<12:0>": "Config",
                "BUCK_CONFIG_L<12:0>": "Config",
                "BUCK_PORB": "Control",
                "BUCK_CALEN": "Control",
                "BUCK_REFBAND_H<1:0>": "Config",
                "BUCK_REFCODE_H<9:0>": "Config",
                "BUCK_REFBAND_L<1:0>": "Config",
                "BUCK_REFCODE_L<9:0>": "Config",
                "BUCK_ATP_EN": "Config",
                "BUCK_TESTCODE_H<2>": "Config",
                "BUCK_TESTCODE_H<1>": "Config",
                "BUCK_TESTCODE_H<0>": "Config",
                "BUCK_TESTCODE_L<2:0>": "Config",
                "BUCK_EN_TP_TSCORE": "Config",
                "BUCK_PDB_TSCORE": "Control",
                "BUCK_RSTB_TSCORE": "Control",
                "BUCK_BG_RTRIM<3:0>": "Config",
                "BUCK_BIAS_CTRL<3:0>": "Config",
                "BUCK_BIAS_PD": "Config",
                "BUCK_ATP_MUX_CTRL<5:0>": "Control",
                "BUCK_HADC_CONFIG<16:0>": "Config",
                "BUCK_HADC_EN": "Control",
                "BUCK_HADC_STROBE": "Control",
                "BUCK_HADC_VALID": "Data",
                "BUCK_HADC_OUT<7:0>": "Data",
                "CALCOMP_L": "Data",
                "CALCOMP_H": "Data",
                # Signals / supplies for completeness
                "BUCK_ATP": "Signal",
                "BUCK_VOUTFB_H": "Signal",
                "BUCK_VOUTFB_L": "Signal",
                "BUCK_VSW_H": "Signal",
                "BUCK_VSW_L": "Signal",
                "BUCK_LSHRT_H": "Signal",
                "BUCK_LSHRT_L": "Signal",
                "PVDD": "Supply",
                "PVSS": "Supply",
                "DVDD": "Supply",
                "DVSS": "Supply",
                "AVDD": "Supply",
                "AVDD18": "Supply",
                "AVSS": "Supply",
                # Scan
                "SCAN_MODE": "Control",
                "SCAN_EN": "Control",
                "SCAN_IN": "Data",
                "SCAN_OUT": "Data",
                # Clocks
                "CLK_ADC_1G": "Clock",
                "CLK_MVM_1G": "Clock",
                "CLK_BLRDWR_1G": "Clock",
                # Config
                "CLK_SEL<2:0>": "Config",
                "WL_WID_CTRL<3:0>": "Config",
                "WL_DLY_CTRL<3:0>": "Config",
                "ACT_CAL_CTRL1<11:0>": "Config",
                "ACT_CAL_CTRL2<11:0>": "Config",
                "ACT_CAL_CTRL3<11:0>": "Config",
                "ACT_CAL_CTRL4<11:0>": "Config",
                "ACT_CAL_CTRL_RST1<11:0>": "Config",
                "ACT_CAL_CTRL_RST2<11:0>": "Config",
                "ACT_CAL_CTRL_FLT_RST<11:0>": "Config",
                "ACT_PROG_CTRL1<7:0>": "Config",
                "ACT_PROG_CTRL2<7:0>": "Config",
                "ACT_PROG_CTRL3<7:0>": "Config",
                "ACT_PROG_CTRL4<7:0>": "Config",
                "ACT_PROG_CTRL_RST1<7:0>": "Config",
                "ACT_PROG_CTRL_RST2<7:0>": "Config",
                "ACT_PROG_CTRL_FLT_RST<7:0>": "Config",
                "ACT_PROG_CTRL_SPARE<19>": "Config",
                "ACT_PROG_CTRL_SPARE<18:16>": "Config",
                "ACT_PROG_CTRL_SPARE<15>": "Config",
                "ACT_PROG_CTRL_SPARE<14>": "Config",
                "ACT_PROG_CTRL_SPARE<12>": "Config",
                "ACT_PROG_CTRL_SPARE<11>": "Config",
                "ACT_PROG_CTRL_SPARE<10>": "Config",
                "ACT_PROG_CTRL_SPARE<9>": "Config",
                "ACT_PROG_CTRL_SPARE<8:6>": "Config",
                "ACT_PROG_CTRL_SPARE<5>": "Config",
                "ACT_PROG_CTRL_SPARE<4>": "Config",
                "ACT_PROG_CTRL_SPARE<3>": "Config",
                "ACT_PROG_CTRL_SPARE<2:0>": "Config",
                "ACT_PROG_COM<9>": "Config",
                "ACT_PROG_COM<8:5>": "Config",
                "ACT_PROG_COM<4>": "Config",
                "ACT_PROG_COM<3>": "Config",
                "ACT_PROG_COM<2:0>": "Config",
                "DMUX_CTRL<4:0>": "Config",
                "D_FLT_RST_RISE<2:0>": "Config",
                "D_FLT_RST_FALL<2:0>": "Config",
                "D_FLT_RST_GAP<1:0>": "Config",
                "D_RST_EVAL_GAP<1:0>": "Config",
                "D_EVAL_PW<1:0>": "Config",
                "D_ADC_SMPL_PW<2:0>": "Config",
                "D_AZ_RISE<2:0>": "Config",
                "D_AZ_PW<2:0>": "Config",
                "ADC_PWR_MODE<1:0>": "Config",
                "ADC_TMSB_CTRL<2:0>": "Config",
                "ADC_TDAC_CTRL<2:0>": "Config",
                "DCDL_CTRL_EXT<9:0>": "Config",
                "VREF_CAL_CTRL<7:0>": "Config",
                "VREF_SCALE_CTRL<1:0>": "Config",
                "BG_TRIM<3:0>": "Config",
                "CIMA_BIAS_CTRL<3:0>": "Config",
                "CIMA_BIAS_PD": "Config",
                "EN_TP_TSCORE": "Config",
                "PDB_VBG_TSCORE": "Config",
                "RSTB_VBG_TSCORE": "Config",
                "HADC_CTRL_CPRE<1:0>": "Config",
                "HADC_CURR_CPRE<1:0>": "Config",
                "HADC_TDLY_CPRE<2:0>": "Config",
                "HADC_TDAC_CPRE<2:0>": "Config",
                "HADC_TMSB_CPRE<2:0>": "Config",
                "HADC_CTRL_GAIN<1:0>": "Config",
                "HADC_CTRL_VCM2<1:0>": "Config",
                "CAL_DONE": "Config",
                "ANA_GEN_SPARE<31>": "Config",
                "ANA_GEN_SPARE<30>": "Config",
                "ANA_GEN_SPARE<29>": "Config",
                "ANA_GEN_SPARE<28>": "Config",
                "ANA_GEN_SPARE<27:22>": "Config",
                "ANA_GEN_SPARE<21>": "Config",
                "ANA_GEN_SPARE<20:10>": "Config",
                "ANA_GEN_SPARE<9>": "Config",
                "ANA_GEN_SPARE<8>": "Config",
                "ANA_GEN_SPARE<7>": "Config",
                "ANA_GEN_SPARE<6:1>": "Config",
                "ANA_GEN_SPARE<0>": "Config",
                # Data
                "DATA_WR_BANK0<127:0>": "Data",
                "DATA_WR_BANK1<127:0>": "Data",
                "DATA_WR_BANK2<127:0>": "Data",
                "DATA_WR_BANK3<127:0>": "Data",
                "DATA_RD_BANK0<127:0>": "Data",
                "DATA_RD_BANK1<127:0>": "Data",
                "DATA_RD_BANK2<127:0>": "Data",
                "DATA_RD_BANK3<127:0>": "Data",
                "ADDR_BANK0<8:0>": "Data",
                "ADDR_BANK1<8:0>": "Data",
                "ADDR_BANK2<8:0>": "Data",
                "ADDR_BANK3<8:0>": "Data",
                "IA_BIT0<575:0>": "Data",
                "IA_BIT1<575:0>": "Data",
                "IA_BIT2<575:0>": "Data",
                "IA_BIT3<575:0>": "Data",
                "HADC_VALID": "Data",
                "HADC<7:0>": "Data",
                "ADCX_OUT<8:0>": "Data",
                "ADC_VALID": "Data",
                "SCAN_IN_A<5:0>": "Data",
                "SCAN_OUT_A<5:0>": "Data",
                "SCAN_IN_B<2:0>": "Data",
                "SCAN_OUT_B<2:0>": "Data",
                "SCAN_IN_C": "Data",
                "SCAN_OUT_C": "Data",
                # Control
                "CIMA_WR_RDB": "Control",
                "MEM_CH_FAULT<67:0>": "Control",
                "CIMA_BANK0_EN": "Control",
                "CIMA_BANK1_EN": "Control",
                "CIMA_BANK2_EN": "Control",
                "CIMA_BANK3_EN": "Control",
                "ACT_PROG_CTRL_SPARE<13>": "Control",
                "ADC_CH_EN<63:0>": "Control",
                "ADC_INTR_RSTB": "Control",
                "ADC_INTR_ASYNC_RSTB": "Control",
                "CIMA_RSTB": "Control",
                "CIMA_ASYNC_RSTB": "Control",
                "CIMA_BLWL_RSTB": "Control",
                "CIMA_BLWL_ASYNC_RSTB": "Control",
                "STARTCAL": "Control",
                "START": "Control",
                "EN_TP_ATP": "Control",
                "ATP_MUX_CTRL<5:0>": "Control",
                "ACT_TSTMUX_CTRL<6:0>": "Control",
                "HADC_EN": "Control",
                "HADC_STROBE": "Control",
                "SCAN_MODE_A": "Control",
                "SCAN_EN_A": "Control",
                "SCAN_MODE_B": "Control",
                "SCAN_EN_B": "Control",
                "SCAN_MODE_C": "Control",
                "SCAN_EN_C": "Control",
                # Signal/Supply (not shown in current list but kept for completeness)
                "CIMA_ATP": "Signal",
                "DVDD": "Supply",
                "AVDD_BUCKH": "Signal",
                "AVDD_BUCKL": "Signal",
                "AVDD": "Supply",
                "AVDD_ADC": "Supply",
                "AVDD_MEM": "Supply",
                "AVDD18": "Supply",
                "DVSS": "Supply",
                "AGND": "Supply",
                "DCDL_OVERIDE_EN": "Config",
            }
            return mapping.get(name, "Config")

        # For CIMA and BUCK tabs, group rows by Function and sort within groups by Port name
        if has_function_col:
            function_order = {
                "Control": 0,
                "Config": 1,
                "Data": 2,
                "Clock": 3,
                "Signal": 4,
                "Supply": 5,
            }

            def _sort_key(entry: tuple) -> tuple:
                port_name, _default_val = entry
                func = _classify_function(port_name)
                return (function_order.get(func, 999), port_name)

            ports_data = sorted(ports_data, key=_sort_key)

        # Recompute flags (already computed above)
        buck_output_only_ports = {"BUCK_HADC_VALID", "BUCK_HADC_OUT<7:0>"} if is_buck_tab else set()
        cima_output_only_ports = {"CAL_DONE", "HADC_VALID", "HADC<7:0>", "ADCX_OUT<8:0>", "ADC_VALID"} if is_cima_tab else set()
        # Note: ADCX_OUT requires special read behavior (reads 64 pairs of CWRAP_TF_REGs)
        cima_note_ports = {"ADCX_OUT<8:0>"} if is_cima_tab else set()
        self._output_only_rows = set()

        for row, (port_name, default_value) in enumerate(ports_data):
            is_output_only = (port_name in buck_output_only_ports) or (port_name in cima_output_only_ports)
            if is_output_only:
                self._output_only_rows.add(row)
            # Cache function kind for filtering
            if has_function_col:
                # Build a per-row map of function kinds
                if not hasattr(self, "_row_function_kind"):
                    self._row_function_kind = {}
                self._row_function_kind[row] = _classify_function(port_name)
            # Port
            name_item = QtWidgets.QTableWidgetItem(port_name)
            name_item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignVCenter | QtCore.Qt.AlignmentFlag.AlignLeft)
            self.table.setItem(row, self._columns["port"], name_item)

            # Function column (CIMA and BUCK)
            if has_function_col and self._columns["function"] is not None:
                func_item = QtWidgets.QTableWidgetItem(_classify_function(port_name))
                func_item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(row, self._columns["function"], func_item)

            # Current
            current_item = QtWidgets.QTableWidgetItem("N/A")
            current_item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, self._columns["current"], current_item)

            # Write Value (editable unless output-only field)
            if is_output_only:
                disabled_item = QtWidgets.QTableWidgetItem("—")
                disabled_item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(row, self._columns["write_val"], disabled_item)
            else:
                write_editor = ClearLineEdit(placeholder="enter value", align_center=True)
                write_editor.setMinimumHeight(26)               # <-- add height
                write_editor.setTextMargins(6, 0, 6, 0)         # <-- inner padding
                self.table.setCellWidget(row, self._columns["write_val"], write_editor)

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
            self.table.setCellWidget(row, self._columns["default"], default_container)

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
            # Add helpful note for CIMA ADCX_OUT row
            if is_cima_tab and (port_name in cima_note_ports):
                read_btn.setToolTip("Requires reading CWRAP_TF_REGs (64 pairs). Will populate all 64 ADCX_OUT<8:0> at once.")
            # Keep read cell plain to avoid halo around button
            # container_read.setObjectName("cellBox")
            self.table.setCellWidget(row, self._columns["read"], container_read)

            # Individual Write button (omit for output-only fields)
            if is_output_only:
                placeholder_item = QtWidgets.QTableWidgetItem("")
                placeholder_item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(row, self._columns["write"], placeholder_item)
            else:
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
                self.table.setCellWidget(row, self._columns["write"], container_write)

        header_view = self.table.horizontalHeader()
        if has_function_col:
            header_view.setSectionResizeMode(self._columns["port"], QtWidgets.QHeaderView.ResizeMode.Stretch)
            header_view.setSectionResizeMode(self._columns["function"], QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
            header_view.setSectionResizeMode(self._columns["current"], QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
            header_view.setSectionResizeMode(self._columns["write_val"], QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
            header_view.setSectionResizeMode(self._columns["default"], QtWidgets.QHeaderView.ResizeMode.Fixed)
            header_view.setSectionResizeMode(self._columns["read"], QtWidgets.QHeaderView.ResizeMode.Fixed)
            header_view.setSectionResizeMode(self._columns["write"], QtWidgets.QHeaderView.ResizeMode.Fixed)
            header_view.resizeSection(self._columns["default"], 79)
            header_view.resizeSection(self._columns["read"], 124)
            header_view.resizeSection(self._columns["write"], 124)
        else:
            header_view.setSectionResizeMode(self._columns["port"], QtWidgets.QHeaderView.ResizeMode.Stretch)
            header_view.setSectionResizeMode(self._columns["current"], QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
            header_view.setSectionResizeMode(self._columns["write_val"], QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
            header_view.setSectionResizeMode(self._columns["default"], QtWidgets.QHeaderView.ResizeMode.Fixed)
            header_view.setSectionResizeMode(self._columns["read"], QtWidgets.QHeaderView.ResizeMode.Fixed)
            header_view.setSectionResizeMode(self._columns["write"], QtWidgets.QHeaderView.ResizeMode.Fixed)
            header_view.resizeSection(self._columns["default"], 79)
            header_view.resizeSection(self._columns["read"], 124)
            header_view.resizeSection(self._columns["write"], 124)

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
            # Use dynamic column index for 'Current'
            col = self._columns["current"] if hasattr(self, "_columns") else 1
            self.table.item(r, col).setText("N/A")
        QtWidgets.QMessageBox.information(self, "Read All", f"[{self.title}] Read all (frontend only).")

    def on_write_all(self):
        for r in range(self.table.rowCount()):
            # Skip output-only rows (e.g., BUCK_HADC_VALID, BUCK_HADC_OUT<7:0>)
            if hasattr(self, "_output_only_rows") and r in getattr(self, "_output_only_rows", set()):
                continue
            editor = self.table.cellWidget(r, 2)  # ClearLineEdit
            value = editor.text() if isinstance(editor, QtWidgets.QLineEdit) else ""
            # No longer updating desired column since it's removed
        QtWidgets.QMessageBox.information(self, "Write All", f"[{self.title}] Wrote all (frontend only).")

    def on_check_hadc_clicked(self):
        QtWidgets.QMessageBox.information(self, "Check HADC", f"[{self.title}] Checking HADC... (placeholder)")

    def on_read_single(self, row: int):
        """Handle individual read button click for a specific row."""
        col_port = self._columns["port"] if hasattr(self, "_columns") else 0
        col_current = self._columns["current"] if hasattr(self, "_columns") else 1
        port_name = self.table.item(row, col_port).text()
        # Special handling for CIMA ADCX_OUT: requires reading 64 CWRAP_TF_REG pairs
        if str(self.title).upper() == "CIMA" and port_name == "ADCX_OUT<8:0>":
            QtWidgets.QMessageBox.information(
                self,
                "Read ADCX_OUT",
                "Requires reading CWRAP_TF_REGs (64 pairs).\nPlaceholder: would populate all 64 ADCX_OUT<8:0> values."
            )
            self.table.item(row, col_current).setText("pending 64x")
            return
        self.table.item(row, col_current).setText("N/A")  # Update current value
        QtWidgets.QMessageBox.information(self, "Read Single", f"[{self.title}] Read {port_name} (frontend only).")

    def on_write_single(self, row: int):
        """Handle individual write button click for a specific row."""
        col_port = self._columns["port"] if hasattr(self, "_columns") else 0
        col_write_val = self._columns["write_val"] if hasattr(self, "_columns") else 2
        port_name = self.table.item(row, col_port).text()
        editor = self.table.cellWidget(row, col_write_val)  # ClearLineEdit
        value = editor.text() if isinstance(editor, QtWidgets.QLineEdit) else ""
        # No longer updating desired column since it's removed
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

        # Accept forms like: 64'hFFFF_FFFF_FFFF_FFFF or 0xFFFF... or plain hex up to 16 nibbles
        if (re.match(r"^64'h[0-9A-Fa-f_]{1,19}$", mask_text)
            or re.match(r"^0x[0-9A-Fa-f_]{1,16}$", mask_text)
            or re.match(r"^[0-9A-Fa-f_]{1,16}$", mask_text)):
            self.mask_error.hide()
            self.write_all_btn.setEnabled(True)
        else:
            self.mask_error.show()
            self.write_all_btn.setEnabled(False)

    # Helpers to parse mask or index
    def _parsed_cima_mask(self) -> int:
        text = (self.cima_mask.text() or "").strip().replace("_", "")
        if not text:
            return 0
        if text.startswith("64'h"):
            text = text[4:]
        elif text.startswith("0x"):
            text = text[2:]
        try:
            value = int(text, 16)
        except Exception:
            value = 0
        return value & ((1 << 64) - 1)

    def _active_cima_mask(self) -> int:
        mask = self._parsed_cima_mask()
        if mask:
            return mask
        idx = int(self.cima_index.value())
        return 1 << idx

    def on_write_all(self):
        targets = self._active_cima_mask()
        wrote = []
        for r in range(self.table.rowCount()):
            editor = self.table.cellWidget(r, 2)  # ClearLineEdit
            value = editor.text() if isinstance(editor, QtWidgets.QLineEdit) else ""
            port_name = self.table.item(r, 0).text()
            wrote.append((port_name, value))
        # Summary dialog
        num = bin(targets).count("1")
        QtWidgets.QMessageBox.information(
            self,
            "Write All",
            f"[{self.title}] Write {len(wrote)} ports to {num} CIMA(s).\nMask = 0x{targets:016X}"
        )

    def on_write_single(self, row: int):
        port_name = self.table.item(row, 0).text()
        editor = self.table.cellWidget(row, 2)  # ClearLineEdit
        value = editor.text() if isinstance(editor, QtWidgets.QLineEdit) else ""
        mask = self._active_cima_mask()
        num = bin(mask).count("1")
        QtWidgets.QMessageBox.information(
            self,
            "Write Single",
            f"[{self.title}] {port_name} = {value} → {num} CIMA(s).\nMask = 0x{mask:016X}"
        )


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
        self.write_adcs_btn = QtWidgets.QPushButton("Write ADCs (by channel)")
        self.write_adcs_btn.setEnabled(False)
        self.write_adcs_btn.clicked.connect(self.on_write_adcs_clicked)
        bottom.addWidget(self.write_adcs_btn)
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

        # Helper to parse WT1 cell as either a single value or by-channel spec
        def parse_wt1_spec(txt: str):
            txt = (txt or "").strip()
            if not txt:
                return None
            # Accepted formats:
            #  - "7" → applies to all channels (single value)
            #  - "7,5,3,1" → values by channel index starting at 0
            #  - "c0=7,c1=5" or "0:7 1:5" → explicit channel/value pairs
            # Returns a dict: {channel_index: value} or {"*": value}
            # All values are integers 0..15
            def parse_int(s):
                return int(s.strip(), 0)
            # explicit channel pairs
            if any(ch in txt for ch in ["=", ":"]):
                mapping = {}
                # split by comma or whitespace
                parts = [p for p in txt.replace(",", " ").split() if p]
                for p in parts:
                    if ":" in p:
                        k, v = p.split(":", 1)
                    elif "=" in p:
                        k, v = p.split("=", 1)
                    else:
                        return None
                    k = k.strip().lower().lstrip("c")
                    try:
                        ch = int(k, 0)
                        val = parse_int(v)
                    except Exception:
                        return None
                    if not (0 <= val <= 15):
                        return None
                    mapping[ch] = val
                return mapping if mapping else None
            # list of values
            if "," in txt or " " in txt:
                try:
                    vals = [parse_int(x) for x in txt.replace(",", " ").split() if x]
                except Exception:
                    return None
                if not vals or any(v < 0 or v > 15 for v in vals):
                    return None
                return {i: v for i, v in enumerate(vals)}
            # single value
            try:
                v = parse_int(txt)
            except Exception:
                return None
            if not (0 <= v <= 15):
                return None
            return {"*": v}

        # WT1 requirement: if D[r] > 0 then WT1[r] must be non-empty and valid
        wt1_ok = True
        any_wt1 = False
        for r in range(rows):
            if colD[r] > 0:
                spec_txt = (self.table.item(r, 4).text() or "").strip()
                parsed = parse_wt1_spec(spec_txt)
                if not parsed:
                    wt1_ok = False
                    break
                any_wt1 = True

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
        # Allow ADC writing when the table is valid and at least one WT1 spec is present
        self.write_adcs_btn.setEnabled(valid and any_wt1)

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

    def on_write_adcs_clicked(self):
        rows = self.table.rowCount()

        # Reuse the local parser defined in validation by duplicating minimal logic here
        def parse_wt1_spec(txt: str):
            txt = (txt or "").strip()
            if not txt:
                return None
            def parse_int(s):
                return int(s.strip(), 0)
            if any(ch in txt for ch in ["=", ":"]):
                mapping = {}
                parts = [p for p in txt.replace(",", " ").split() if p]
                for p in parts:
                    if ":" in p:
                        k, v = p.split(":", 1)
                    elif "=" in p:
                        k, v = p.split("=", 1)
                    else:
                        return None
                    k = k.strip().lower().lstrip("c")
                    ch = int(k, 0)
                    val = parse_int(v)
                    if not (0 <= val <= 15):
                        return None
                    mapping[ch] = val
                return mapping if mapping else None
            if "," in txt or " " in txt:
                vals = [int(x, 0) for x in txt.replace(",", " ").split() if x]
                if not vals or any(v < 0 or v > 15 for v in vals):
                    return None
                return {i: v for i, v in enumerate(vals)}
            v = int(txt, 0)
            if not (0 <= v <= 15):
                return None
            return {"*": v}

        # Determine which column distributes to 576 to know which rows to consider
        colB = [int(self.table.item(r, 1).text() or "0") for r in range(rows)]
        colD = [int(self.table.item(r, 3).text() or "0") for r in range(rows)]

        sum_b = sum(colB)
        sum_d = sum(colD)
        def is_single_576(vec):
            return vec.count(576) == 1 and all((v == 0 or v == 576) for v in vec)

        differing_weights_mode = (sum_d == self.TOTAL) and is_single_576(colB)
        differing_activation_mode = (sum_b == self.TOTAL) and is_single_576(colD)

        # Aggregate per-channel values from WT1 cells for relevant rows
        channel_values = {}
        for r in range(rows):
            consider = False
            if differing_weights_mode and colD[r] > 0:
                consider = True
            if differing_activation_mode and colB[r] > 0:
                consider = True
            if not consider:
                continue
            spec = parse_wt1_spec(self.table.item(r, 4).text())
            if not spec:
                continue
            if "*" in spec:
                # broadcast single value to all present channels we have so far (or default to 2 channels)
                broadcast_val = spec["*"]
                if channel_values:
                    targets = list(channel_values.keys())
                else:
                    targets = [0, 1]
                for ch in targets:
                    channel_values.setdefault(ch, []).append((r, broadcast_val))
            else:
                for ch, val in spec.items():
                    channel_values.setdefault(ch, []).append((r, val))

        if not channel_values:
            QtWidgets.QMessageBox.warning(self, "Write ADCs", "No per-channel WT1 values parsed.")
            return

        # Summarize the writes we would perform (placeholder for actual HW writes)
        lines = [f"Selected CIMA index: {self.target_cima.value()}", "Per-channel WT1 programming (nibble values):"]
        for ch in sorted(channel_values.keys()):
            entries = ", ".join([f"row {r}: {v}" for r, v in channel_values[ch]])
            lines.append(f"  Channel {ch}: {entries}")
        QtWidgets.QMessageBox.information(self, "Write ADCs (by channel)", "\n".join(lines))

# ---------- Board Tab (APIs) ----------

class BoardTab(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        outer = QtWidgets.QVBoxLayout(self)
        outer.setContentsMargins(16, 16, 16, 16)
        outer.setSpacing(12)

        header = QtWidgets.QLabel("Board")
        header.setObjectName("sectionHeader")
        outer.addWidget(header)

        # Container for API rows inside a scroll area so the window can be resized smaller
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)

        content = QtWidgets.QWidget()
        content_layout = QtWidgets.QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(10)

        # Use a toolbox to organize APIs into tidy sections
        self.toolbox = QtWidgets.QToolBox()

        def add_section(title: str):
            page = QtWidgets.QWidget()
            v = QtWidgets.QVBoxLayout(page)
            v.setContentsMargins(6, 6, 6, 6)
            v.setSpacing(8)
            self.toolbox.addItem(page, title)
            return v

        layout_system   = add_section("System")
        layout_power    = add_section("Power & Rails")
        layout_cima     = add_section("CIMA / ADC")
        layout_buck     = add_section("BUCK")
        layout_resets   = add_section("Resets & Status")
        layout_gpio     = add_section("GPIO")
        layout_clocks   = add_section("Clocks")
        layout_csr      = add_section("FPGA CSR")
        layout_misc     = add_section("Misc")

        # Build rows into each section by temporarily pointing api_container
        self.api_container = layout_system
        self._add_system_info_row()          # 1.1
        self._add_i2c_scan_row()             # 1.2
        self.api_container.addStretch(1)

        self.api_container = layout_power
        self._add_powerup_row()              # 1.3
        self._add_powerdown_row()            # 1.4
        self._add_set_voltage_row()          # 1.5
        self._add_get_rail_voltage_row()     # 1.6
        self._add_get_rail_current_row()     # 1.7
        self.api_container.addStretch(1)

        self.api_container = layout_cima
        self._add_get_cima_adc_voltage_row() # 1.8
        self.api_container.addStretch(1)

        self.api_container = layout_buck
        self._add_buck_get_voltage_row()      # 1.21 (placeholder)
        self.api_container.addStretch(1)

        self.api_container = layout_resets
        self._add_dut_reset_row()            # 1.9
        self._add_fpga_reset_row()           # 1.10
        self._add_ftdi_reset_row()           # 1.11
        self._add_jtag_reset_status_row()    # 1.12
        self._add_get_dut_pinstatus_row()    # 1.15
        self.api_container.addStretch(1)

        self.api_container = layout_gpio
        self._add_gpio_write_row()           # 1.13
        self._add_gpio_read_row()            # 1.14
        self.api_container.addStretch(1)

        self.api_container = layout_clocks
        self._add_dut_clk_control_row()      # 1.16
        self._add_clock_config_row()         # 1.17
        self.api_container.addStretch(1)

        self.api_container = layout_csr
        self._add_csr_write_row()            # 1.18
        self._add_csr_read_row()             # 1.19
        self.api_container.addStretch(1)

        self.api_container = layout_misc
        self._add_exit_row()                 # 1.20
        self.api_container.addStretch(1)

        content_layout.addWidget(self.toolbox)
        scroll.setWidget(content)
        outer.addWidget(scroll, 1)

    # ---------- Helpers ----------
    def _add_row_shell(self, title_text: str) -> QtWidgets.QHBoxLayout:
        row = QtWidgets.QHBoxLayout()
        row.setSpacing(8)
        title = QtWidgets.QLabel(title_text)
        title.setWordWrap(True)
        title.setMinimumWidth(200)
        title.setStyleSheet("font-weight: 600; color: #e6e8eb;")
        row.addWidget(title)
        return row

    def _warn(self, title: str, message: str):
        QtWidgets.QMessageBox.warning(self, title, message)

    def _info(self, title: str, message: str):
        QtWidgets.QMessageBox.information(self, title, message)

    # ---------- 1.1 System_Info ----------
    def _add_system_info_row(self):
        row = self._add_row_shell("System Info")
        row.addStretch(1)
        btn = QtWidgets.QPushButton("System_Info()")
        btn.setProperty("kind", "primary")
        btn.clicked.connect(self.on_system_info_clicked)
        row.addWidget(btn)
        self.api_container.addLayout(row)

    def on_system_info_clicked(self):
        self._info("System_Info", "Query system versions (placeholder).")

    # ---------- 1.2 I2C_Dev_Scan ----------
    def _add_i2c_scan_row(self):
        row = self._add_row_shell("I2C Device Scan")
        row.addStretch(1)
        btn = QtWidgets.QPushButton("I2C_Dev_Scan()")
        btn.setProperty("kind", "primary")
        btn.clicked.connect(self.on_i2c_scan_clicked)
        row.addWidget(btn)
        self.api_container.addLayout(row)

    def on_i2c_scan_clicked(self):
        self._info("I2C_Dev_Scan", "Scanning I2C devices (placeholder).")

    # ---------- 1.3 Powerup_DUT ----------
    def _add_powerup_row(self):
        row = self._add_row_shell("Powerup DUT")
        row.addStretch(1)
        btn = QtWidgets.QPushButton("Powerup_DUT()")
        btn.setProperty("kind", "primary")
        btn.clicked.connect(self.on_powerup_clicked)
        row.addWidget(btn)
        self.api_container.addLayout(row)

    def on_powerup_clicked(self):
        self._info("Powerup_DUT", "Powering up DUT with default delays (placeholder).")

    # ---------- 1.4 Powerdown_DUT ----------
    def _add_powerdown_row(self):
        row = self._add_row_shell("Powerdown DUT")
        row.addStretch(1)
        btn = QtWidgets.QPushButton("Powerdown_DUT()")
        btn.setProperty("kind", "primary")
        btn.clicked.connect(self.on_powerdown_clicked)
        row.addWidget(btn)
        self.api_container.addLayout(row)

    def on_powerdown_clicked(self):
        self._info("Powerdown_DUT", "Powering down DUT (placeholder).")

    def _add_set_voltage_row(self):
        row = self._add_row_shell("Set Voltage")

        # railNumber (1-16)
        rail_label = QtWidgets.QLabel("railNumber:")
        row.addWidget(rail_label)
        self.rail_spin = QtWidgets.QSpinBox()
        self.rail_spin.setRange(1, 16)
        self.rail_spin.setToolTip("Rail index (1-16)")
        row.addWidget(self.rail_spin)

        # voltValue in mV (range varies by rail; placeholder bounds here)
        volt_label = QtWidgets.QLabel("voltValue (mV):")
        row.addWidget(volt_label)
        self.volt_spin = QtWidgets.QSpinBox()
        self.volt_spin.setRange(0, 5000)  # Placeholder bounds; varies by rail
        self.volt_spin.setSingleStep(10)
        self.volt_spin.setSuffix(" mV")
        self.volt_spin.setToolTip("Voltage in mV. Range depends on rail (placeholder 0..5000 mV).")
        row.addWidget(self.volt_spin)

        self.range_hint = QtWidgets.QLabel("Allowed: 0–5000 mV (per rail varies)")
        self.range_hint.setStyleSheet("color: #b9c0cc;")
        row.addWidget(self.range_hint)

        row.addStretch(1)

        self.set_voltage_btn = QtWidgets.QPushButton("Set Voltage")
        self.set_voltage_btn.setProperty("kind", "primary")
        self.set_voltage_btn.clicked.connect(self.on_set_voltage_clicked)
        row.addWidget(self.set_voltage_btn)

        self.api_container.addLayout(row)

        # If exact per-rail ranges are later provided, connect a handler to update hint/range
        self.rail_spin.valueChanged.connect(self._update_voltage_range_hint)
        self._update_voltage_range_hint()

    def _update_voltage_range_hint(self):
        rail = int(self.rail_spin.value())
        # Placeholder mapping; adjust when exact ranges are known
        default_min, default_max = 0, 5000
        min_mv, max_mv = default_min, default_max
        self.volt_spin.setRange(min_mv, max_mv)
        self.range_hint.setText(f"Allowed: {min_mv}–{max_mv} mV (rail {rail})")

    # Placeholder backend call for Set_Voltage
    def on_set_voltage_clicked(self):
        rail = int(self.rail_spin.value())
        mv = int(self.volt_spin.value())
        # In the absence of backend, show a status dialog summarizing the action
        QtWidgets.QMessageBox.information(
            self,
            "Set_Voltage",
            f"Set_Voltage(railNumber={rail}, voltValue={mv})\nStatus: placeholder (returns int status code)",
        )

    # ---------- 1.6 Get_Rail_Voltage ----------
    def _add_get_rail_voltage_row(self):
        row = self._add_row_shell("Get Rail Voltage")
        row.addStretch(1)
        btn = QtWidgets.QPushButton("Get_Rail_Voltage()")
        btn.setProperty("kind", "primary")
        btn.clicked.connect(self.on_get_rail_voltage_clicked)
        row.addWidget(btn)
        self.api_container.addLayout(row)

    def on_get_rail_voltage_clicked(self):
        self._info("Get_Rail_Voltage", "Read all rail voltages (placeholder).")

    # ---------- 1.7 Get_Rail_Current ----------
    def _add_get_rail_current_row(self):
        row = self._add_row_shell("Get Rail Current")
        row.addStretch(1)
        btn = QtWidgets.QPushButton("Get_Rail_Current()")
        btn.setProperty("kind", "primary")
        btn.clicked.connect(self.on_get_rail_current_clicked)
        row.addWidget(btn)
        self.api_container.addLayout(row)

    def on_get_rail_current_clicked(self):
        self._info("Get_Rail_Current", "Read all rail currents (placeholder).")

    # ---------- 1.8 Get_CIMA_ADC_Voltage(select) ----------
    def _add_get_cima_adc_voltage_row(self):
        row = self._add_row_shell("Get CIMA ADC Voltage")
        row.addWidget(QtWidgets.QLabel("select:"))
        self.cima_select = QtWidgets.QSpinBox()
        self.cima_select.setRange(0, 3)
        self.cima_select.setToolTip("0:CIMA0, 1:CIMA1, 2:CIMA2, 3:CIMA3")
        row.addWidget(self.cima_select)
        hint = QtWidgets.QLabel("0:CIMA0 1:CIMA1 2:CIMA2 3:CIMA3")
        hint.setWordWrap(True)
        hint.setStyleSheet("color: #b9c0cc;")
        row.addWidget(hint)
        row.addStretch(1)
        btn = QtWidgets.QPushButton("Get_CIMA_ADC_Voltage()")
        btn.setProperty("kind", "primary")
        btn.clicked.connect(self.on_get_cima_adc_voltage_clicked)
        row.addWidget(btn)
        self.api_container.addLayout(row)

    def on_get_cima_adc_voltage_clicked(self):
        sel = int(self.cima_select.value())
        self._info("Get_CIMA_ADC_Voltage", f"select={sel} (placeholder return status & values)")

    # ---------- 1.21 Get_BUCK_Voltage_of_BUCK_VSW_XX (placeholder) ----------
    def _add_buck_get_voltage_row(self):
        row = self._add_row_shell("Get BUCK Voltage of BUCK_VSW_XX")
        row.addWidget(QtWidgets.QLabel("XX:"))
        self.buck_vsw_sel = QtWidgets.QComboBox()
        self.buck_vsw_sel.addItems(["H", "L"])  # H or L
        self.buck_vsw_sel.setToolTip("Select XX (H or L)")
        row.addWidget(self.buck_vsw_sel)
        hint = QtWidgets.QLabel("Placeholder — API TBD")
        hint.setStyleSheet("color: #b9c0cc;")
        hint.setWordWrap(True)
        row.addWidget(hint)
        row.addStretch(1)
        btn = QtWidgets.QPushButton("Get_BUCK_Voltage()")
        btn.setProperty("kind", "primary")
        btn.clicked.connect(self.on_buck_get_voltage_clicked)
        row.addWidget(btn)
        self.api_container.addLayout(row)

    def on_buck_get_voltage_clicked(self):
        xx = self.buck_vsw_sel.currentText()
        self._info(
            "Get_BUCK_Voltage",
            f"Get BUCK Voltage of BUCK_VSW_{xx}\n(placeholder; backend API details TBD)",
        )

    # ---------- 1.9 DUT_Reset(resetMethod) ----------
    def _add_dut_reset_row(self):
        row = self._add_row_shell("DUT Reset")
        row.addWidget(QtWidgets.QLabel("resetMethod:"))
        self.reset_method = QtWidgets.QSpinBox()
        self.reset_method.setRange(0, 1)
        self.reset_method.setToolTip("0: RP5 reset, 1: FPGA reset")
        row.addWidget(self.reset_method)
        hint = QtWidgets.QLabel("0:RP5 1:FPGA")
        hint.setWordWrap(True)
        hint.setStyleSheet("color: #b9c0cc;")
        row.addWidget(hint)
        row.addStretch(1)
        btn = QtWidgets.QPushButton("DUT_Reset()")
        btn.setProperty("kind", "primary")
        btn.clicked.connect(self.on_dut_reset_clicked)
        row.addWidget(btn)
        self.api_container.addLayout(row)

    def on_dut_reset_clicked(self):
        method = int(self.reset_method.value())
        self._info("DUT_Reset", f"resetMethod={method} (placeholder)")

    # ---------- 1.10 FPGA_Reset ----------
    def _add_fpga_reset_row(self):
        row = self._add_row_shell("FPGA Reset")
        row.addStretch(1)
        btn = QtWidgets.QPushButton("FPGA_Reset()")
        btn.setProperty("kind", "primary")
        btn.clicked.connect(self.on_fpga_reset_clicked)
        row.addWidget(btn)
        self.api_container.addLayout(row)

    def on_fpga_reset_clicked(self):
        self._info("FPGA_Reset", "Resetting FPGA (placeholder).")

    # ---------- 1.11 FTDI_Reset ----------
    def _add_ftdi_reset_row(self):
        row = self._add_row_shell("FTDI Reset")
        row.addStretch(1)
        btn = QtWidgets.QPushButton("FTDI_Reset()")
        btn.setProperty("kind", "primary")
        btn.clicked.connect(self.on_ftdi_reset_clicked)
        row.addWidget(btn)
        self.api_container.addLayout(row)

    def on_ftdi_reset_clicked(self):
        self._info("FTDI_Reset", "Resetting FTDI (placeholder).")

    # ---------- 1.12 JTAG_Reset_Status ----------
    def _add_jtag_reset_status_row(self):
        row = self._add_row_shell("JTAG Reset Status")
        row.addStretch(1)
        btn = QtWidgets.QPushButton("JTAG_Reset_Status()")
        btn.setProperty("kind", "primary")
        btn.clicked.connect(self.on_jtag_reset_status_clicked)
        row.addWidget(btn)
        self.api_container.addLayout(row)

    def on_jtag_reset_status_clicked(self):
        self._info("JTAG_Reset_Status", "Reading JTAG reset pins (placeholder).")

    # ---------- 1.13 GPIO_Write(direction, writeValue) ----------
    def _add_gpio_write_row(self):
        row = self._add_row_shell("GPIO Write")
        row.addWidget(QtWidgets.QLabel("direction:"))
        self.gpio_dir = ClearLineEdit(placeholder="0xFFFFFFFF", align_center=False)
        self.gpio_dir.setToolTip("32-bit direction mask. 1=Output, 0=Input. Accepts decimal or 0xHEX.")
        self.gpio_dir.setMinimumWidth(140)
        row.addWidget(self.gpio_dir)
        row.addWidget(QtWidgets.QLabel("writeValue:"))
        self.gpio_wr = ClearLineEdit(placeholder="0x00000000", align_center=False)
        self.gpio_wr.setToolTip("32-bit value written to pins configured as outputs. Accepts decimal or 0xHEX.")
        self.gpio_wr.setMinimumWidth(140)
        row.addWidget(self.gpio_wr)
        row.addStretch(1)
        btn = QtWidgets.QPushButton("GPIO_Write()")
        btn.setProperty("kind", "primary")
        btn.clicked.connect(self.on_gpio_write_clicked)
        row.addWidget(btn)
        self.api_container.addLayout(row)

    def _parse_int_field(self, editor: QtWidgets.QLineEdit, bits: int, name: str) -> Optional[int]:
        text = (editor.text() or "").strip()
        if not text:
            self._warn(name, f"Enter a value for {name}.")
            return None
        try:
            value = int(text, 0)
        except Exception:
            self._warn(name, f"Invalid number for {name}. Use decimal or 0xHEX.")
            return None
        if value < 0 or value > ((1 << bits) - 1):
            self._warn(name, f"{name} out of range 0..0x{((1<<bits)-1):X}.")
            return None
        return value

    def on_gpio_write_clicked(self):
        direction = self._parse_int_field(self.gpio_dir, 32, "direction")
        if direction is None:
            return
        write_val = self._parse_int_field(self.gpio_wr, 32, "writeValue")
        if write_val is None:
            return
        self._info("GPIO_Write", f"direction=0x{direction:08X}, writeValue=0x{write_val:08X} (placeholder)")

    # ---------- 1.14 GPIO_Read ----------
    def _add_gpio_read_row(self):
        row = self._add_row_shell("GPIO Read")
        row.addStretch(1)
        btn = QtWidgets.QPushButton("GPIO_Read()")
        btn.setProperty("kind", "primary")
        btn.clicked.connect(self.on_gpio_read_clicked)
        row.addWidget(btn)
        self.api_container.addLayout(row)

    def on_gpio_read_clicked(self):
        self._info("GPIO_Read", "Reading 32 GPIOs (placeholder). Returns 32-bit value.")

    # ---------- 1.15 Get_DUT_PinStatus ----------
    def _add_get_dut_pinstatus_row(self):
        row = self._add_row_shell("Get DUT Pin Status")
        row.addStretch(1)
        btn = QtWidgets.QPushButton("Get_DUT_PinStatus()")
        btn.setProperty("kind", "primary")
        btn.clicked.connect(self.on_get_dut_pinstatus_clicked)
        row.addWidget(btn)
        self.api_container.addLayout(row)

    def on_get_dut_pinstatus_clicked(self):
        self._info("Get_DUT_PinStatus", "Reading DUT pin status (placeholder).")

    # ---------- 1.16 DUT_Clk_Control(enable) ----------
    def _add_dut_clk_control_row(self):
        row = self._add_row_shell("DUT Clk Control")
        row.addWidget(QtWidgets.QLabel("enable:"))
        self.clk_enable = QtWidgets.QSpinBox()
        self.clk_enable.setRange(0, 7)
        self.clk_enable.setToolTip("Bit2:PCIE, Bit1:LVCMOS, Bit0:NPU_LVDS")
        row.addWidget(self.clk_enable)
        hint = QtWidgets.QLabel("Bits: [2 PCIE][1 LVCMOS][0 NPU]")
        hint.setWordWrap(True)
        hint.setStyleSheet("color: #b9c0cc;")
        row.addWidget(hint)
        row.addStretch(1)
        btn = QtWidgets.QPushButton("DUT_Clk_Control()")
        btn.setProperty("kind", "primary")
        btn.clicked.connect(self.on_dut_clk_control_clicked)
        row.addWidget(btn)
        self.api_container.addLayout(row)

    def on_dut_clk_control_clicked(self):
        val = int(self.clk_enable.value())
        self._info("DUT_Clk_Control", f"enable=0x{val:X} (placeholder)")

    # ---------- 1.17 Clock Configuration (clkDevice) ----------
    def _add_clock_config_row(self):
        row = self._add_row_shell("Clock Configuration")
        row.addWidget(QtWidgets.QLabel("clkDevice:"))
        self.clk_device = QtWidgets.QSpinBox()
        self.clk_device.setRange(0, 1)
        self.clk_device.setToolTip("0:NPU_LVDS_CLK, 1:LVCMOS_CLK")
        row.addWidget(self.clk_device)
        hint = QtWidgets.QLabel("0:NPU_LVDS_CLK 1:LVCMOS_CLK")
        hint.setWordWrap(True)
        hint.setStyleSheet("color: #b9c0cc;")
        row.addWidget(hint)
        row.addStretch(1)
        btn = QtWidgets.QPushButton("Clock_Configuration()")
        btn.setProperty("kind", "primary")
        btn.clicked.connect(self.on_clock_configuration_clicked)
        row.addWidget(btn)
        self.api_container.addLayout(row)

    def on_clock_configuration_clicked(self):
        dev = int(self.clk_device.value())
        self._info("Clock Configuration", f"clkDevice={dev} (placeholder; uses en1_system_config.ini)")

    # ---------- 1.18 CSR_Write(regAddr, dataValue) ----------
    def _add_csr_write_row(self):
        row = self._add_row_shell("CSR Write")
        row.addWidget(QtWidgets.QLabel("regAddr:"))
        self.csr_addr_wr = QtWidgets.QSpinBox()
        self.csr_addr_wr.setRange(0, 0xFF)
        self.csr_addr_wr.setToolTip("Register address 0x00–0xFF")
        row.addWidget(self.csr_addr_wr)

        row.addWidget(QtWidgets.QLabel("dataValue:"))
        self.csr_data = ClearLineEdit(placeholder="0x00000000", align_center=False)
        self.csr_data.setMinimumWidth(140)
        self.csr_data.setToolTip("32-bit value. Accepts decimal or 0xHEX.")
        row.addWidget(self.csr_data)

        row.addStretch(1)
        btn = QtWidgets.QPushButton("CSR_Write()")
        btn.setProperty("kind", "primary")
        btn.clicked.connect(self.on_csr_write_clicked)
        row.addWidget(btn)
        self.api_container.addLayout(row)

    def on_csr_write_clicked(self):
        addr = int(self.csr_addr_wr.value())
        data = self._parse_int_field(self.csr_data, 32, "dataValue")
        if data is None:
            return
        self._info("CSR_Write", f"regAddr=0x{addr:02X}, dataValue=0x{data:08X} (placeholder)")

    # ---------- 1.19 CSR_Read(regAddr) ----------
    def _add_csr_read_row(self):
        row = self._add_row_shell("CSR Read")
        row.addWidget(QtWidgets.QLabel("regAddr:"))
        self.csr_addr_rd = QtWidgets.QSpinBox()
        self.csr_addr_rd.setRange(0, 0xFF)
        self.csr_addr_rd.setToolTip("Register address 0x00–0xFF")
        row.addWidget(self.csr_addr_rd)
        row.addStretch(1)
        btn = QtWidgets.QPushButton("CSR_Read()")
        btn.setProperty("kind", "primary")
        btn.clicked.connect(self.on_csr_read_clicked)
        row.addWidget(btn)
        self.api_container.addLayout(row)

    def on_csr_read_clicked(self):
        addr = int(self.csr_addr_rd.value())
        self._info("CSR_Read", f"regAddr=0x{addr:02X} (placeholder; returns readData)")

    # ---------- 1.20 Exit_Function ----------
    def _add_exit_row(self):
        row = self._add_row_shell("Exit Application")
        row.addStretch(1)
        btn = QtWidgets.QPushButton("Exit_Function()")
        btn.setProperty("kind", "accent")
        btn.clicked.connect(self.on_exit_function_clicked)
        row.addWidget(btn)
        self.api_container.addLayout(row)

    def on_exit_function_clicked(self):
        app = QtWidgets.QApplication.instance()
        if app:
            app.quit()

# ---------- Functions Tab (frontend with integration hooks) ----------

class FunctionsTab(QtWidgets.QWidget):
    """Frontend-only UI for function tests with simple integration hooks.

    Integration options:
      - Connect to the signal ``runRequested(str test_id, dict params)``.
      - Or pass an ``executor`` callable to the constructor or ``register_backend``.

    The executor signature should be: ``executor(test_id: str, params: dict) -> None``.
    """

    runRequested = QtCore.pyqtSignal(str, dict)

    def __init__(self, executor: Optional[Callable[[str, dict], None]] = None, parent=None):
        super().__init__(parent)
        self.executor: Optional[Callable[[str, dict], None]] = executor
        self._build_ui()

    # Public hook for later backend wiring
    def register_backend(self, executor: Callable[[str, dict], None]):
        self.executor = executor

    # ---------- UI ----------
    def _build_ui(self):
        outer = QtWidgets.QVBoxLayout(self)
        outer.setContentsMargins(16, 16, 16, 16)
        outer.setSpacing(12)

        header = QtWidgets.QLabel("Functions")
        header.setObjectName("sectionHeader")
        outer.addWidget(header)

        # Small hint explaining how to integrate
        hint = QtWidgets.QLabel(
            "Connect to runRequested(test_id, params) or call register_backend(executor). Frontend only for now."
        )
        hint.setStyleSheet("color: #b9c0cc;")
        hint.setWordWrap(True)
        outer.addWidget(hint)

        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)

        content = QtWidgets.QWidget()
        content_layout = QtWidgets.QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(10)

        self.toolbox = QtWidgets.QToolBox()

        # Helper to add pages
        def add_section(title: str):
            page = QtWidgets.QWidget()
            v = QtWidgets.QVBoxLayout(page)
            v.setContentsMargins(6, 6, 6, 6)
            v.setSpacing(8)
            self.toolbox.addItem(page, title)
            return v

        layout_cima   = add_section("CIMA")
        layout_mem    = add_section("Memory / CWRAP")
        layout_buck   = add_section("BUCK")

        # Build rows
        self._build_cima_rows(layout_cima)
        layout_cima.addStretch(1)

        self._build_memory_rows(layout_mem)
        layout_mem.addStretch(1)

        self._build_buck_rows(layout_buck)
        layout_buck.addStretch(1)

        content_layout.addWidget(self.toolbox)
        scroll.setWidget(content)
        outer.addWidget(scroll, 1)

    def _row_shell(self, title_text: str) -> QtWidgets.QHBoxLayout:
        row = QtWidgets.QHBoxLayout()
        row.setSpacing(8)
        title = QtWidgets.QLabel(title_text)
        title.setWordWrap(True)
        title.setMinimumWidth(240)
        title.setStyleSheet("font-weight: 600; color: #e6e8eb;")
        row.addWidget(title)
        return row

    # ---------- Field creators ----------
    def _spin(self, minimum: int, maximum: int, tooltip: str = "") -> QtWidgets.QSpinBox:
        sb = QtWidgets.QSpinBox()
        sb.setRange(minimum, maximum)
        if tooltip:
            sb.setToolTip(tooltip)
        return sb

    def _dspin(self, minimum: float, maximum: float, step: float = 0.01, suffix: str = "", tooltip: str = "") -> QtWidgets.QDoubleSpinBox:
        ds = QtWidgets.QDoubleSpinBox()
        ds.setRange(minimum, maximum)
        ds.setSingleStep(step)
        if suffix:
            ds.setSuffix(f" {suffix}")
        if tooltip:
            ds.setToolTip(tooltip)
        return ds

    def _text(self, placeholder: str = "", tooltip: str = "") -> QtWidgets.QLineEdit:
        ed = ClearLineEdit(placeholder=placeholder, align_center=False)
        if tooltip:
            ed.setToolTip(tooltip)
        ed.setMinimumWidth(140)
        return ed

    def _combo(self, items: List[str], tooltip: str = "") -> QtWidgets.QComboBox:
        cb = QtWidgets.QComboBox()
        cb.addItems(items)
        if tooltip:
            cb.setToolTip(tooltip)
        return cb

    # ---------- Build specific sections ----------
    def _build_cima_rows(self, container: QtWidgets.QVBoxLayout):
        # 1. CIMA Power on
        row = self._row_shell("CIMA Power on")
        row.addWidget(QtWidgets.QLabel("CIMA#:"))
        cima_idx = self._spin(0, 63, "0–63")
        row.addWidget(cima_idx)
        row.addWidget(QtWidgets.QLabel("Analog ATP:"))
        atp = self._combo(["Off", "On"]) 
        row.addWidget(atp)
        row.addWidget(QtWidgets.QLabel("Test point:"))
        tp = self._text("e.g. TP1")
        row.addWidget(tp)
        row.addStretch(1)
        btn = QtWidgets.QPushButton("Run")
        btn.setProperty("kind", "primary")
        btn.clicked.connect(lambda: self._emit("cima_power_on", {"cima": int(cima_idx.value()), "analog_atp": atp.currentText(), "test_point": tp.text()}))
        row.addWidget(btn)
        container.addLayout(row)

        # 2. Sweep register value
        row = self._row_shell("Sweep register value")
        row.addWidget(QtWidgets.QLabel("CIMA#:"))
        s_cima = self._spin(0, 63)
        row.addWidget(s_cima)
        row.addWidget(QtWidgets.QLabel("register:"))
        s_reg = self._text("REG_NAME")
        row.addWidget(s_reg)
        row.addWidget(QtWidgets.QLabel("values:"))
        s_vals = self._text("e.g. 0,1,2,3")
        row.addWidget(s_vals)
        row.addWidget(QtWidgets.QLabel("trigger:"))
        s_trig = self._combo(["manual", "signal"]) 
        row.addWidget(s_trig)
        row.addStretch(1)
        s_btn = QtWidgets.QPushButton("Run")
        s_btn.setProperty("kind", "primary")
        s_btn.clicked.connect(lambda: self._emit("sweep_register", {"cima": int(s_cima.value()), "register": s_reg.text(), "values": s_vals.text(), "trigger": s_trig.currentText()}))
        row.addWidget(s_btn)
        container.addLayout(row)

        # 3. CIMA HADC measurement
        row = self._row_shell("CIMA HADC measurement")
        row.addWidget(QtWidgets.QLabel("CIMA#:"))
        h_cima = self._spin(0, 63)
        row.addWidget(h_cima)
        row.addWidget(QtWidgets.QLabel("Analog ATP:"))
        h_atp = self._combo(["Off", "On"]) 
        row.addWidget(h_atp)
        row.addWidget(QtWidgets.QLabel("Test point:"))
        h_tp = self._text("e.g. TP1")
        row.addWidget(h_tp)
        row.addStretch(1)
        h_btn = QtWidgets.QPushButton("Run")
        h_btn.setProperty("kind", "primary")
        h_btn.clicked.connect(lambda: self._emit("cima_hadc_measure", {"cima": int(h_cima.value()), "analog_atp": h_atp.currentText(), "test_point": h_tp.text()}))
        row.addWidget(h_btn)
        container.addLayout(row)

        # 4. CIMA HADC self test
        row = self._row_shell("CIMA HADC self test")
        row.addWidget(QtWidgets.QLabel("CIMA#:"))
        hs_cima = self._spin(0, 63)
        row.addWidget(hs_cima)
        row.addWidget(QtWidgets.QLabel("Analog ATP:"))
        hs_atp = self._combo(["Off", "On"]) 
        row.addWidget(hs_atp)
        row.addWidget(QtWidgets.QLabel("Test point:"))
        hs_tp = self._text("e.g. TP1")
        row.addWidget(hs_tp)
        row.addStretch(1)
        hs_btn = QtWidgets.QPushButton("Run")
        hs_btn.setProperty("kind", "primary")
        hs_btn.clicked.connect(lambda: self._emit("cima_hadc_self_test", {"cima": int(hs_cima.value()), "analog_atp": hs_atp.currentText(), "test_point": hs_tp.text()}))
        row.addWidget(hs_btn)
        container.addLayout(row)

        # 5. CIMA Calibration
        row = self._row_shell("CIMA Calibration")
        row.addWidget(QtWidgets.QLabel("CIMA#:"))
        cal_cima = self._spin(0, 63)
        row.addWidget(cal_cima)
        row.addStretch(1)
        cal_btn = QtWidgets.QPushButton("Run")
        cal_btn.setProperty("kind", "primary")
        cal_btn.clicked.connect(lambda: self._emit("cima_calibration", {"cima": int(cal_cima.value())}))
        row.addWidget(cal_btn)
        container.addLayout(row)

        # 6. CIMA Transfer function
        row = self._row_shell("CIMA Transfer function")
        row.addWidget(QtWidgets.QLabel("CIMA#:"))
        tf_cima = self._spin(0, 63)
        row.addWidget(tf_cima)
        row.addWidget(QtWidgets.QLabel("Vref:"))
        tf_vref = self._dspin(0.0, 5.0, 0.01, "V")
        row.addWidget(tf_vref)
        row.addStretch(1)
        tf_btn = QtWidgets.QPushButton("Run")
        tf_btn.setProperty("kind", "primary")
        tf_btn.clicked.connect(lambda: self._emit("cima_transfer_function", {"cima": int(tf_cima.value()), "vref": float(tf_vref.value())}))
        row.addWidget(tf_btn)
        container.addLayout(row)

        # 9. MVM operation (note: requires compiler binary)
        row = self._row_shell("MVM operation")
        row.addWidget(QtWidgets.QLabel("CIMA#:"))
        mvm_cima = self._spin(0, 63)
        row.addWidget(mvm_cima)
        row.addWidget(QtWidgets.QLabel("ACT value:"))
        mvm_act = self._spin(0, 65535)
        row.addWidget(mvm_act)
        row.addStretch(1)
        mvm_note = QtWidgets.QLabel("requires compiler binary")
        mvm_note.setStyleSheet("color: #b9c0cc;")
        row.addWidget(mvm_note)
        mvm_btn = QtWidgets.QPushButton("Run")
        mvm_btn.setProperty("kind", "primary")
        mvm_btn.clicked.connect(lambda: self._emit("mvm_operation", {"cima": int(mvm_cima.value()), "act_value": int(mvm_act.value())}))
        row.addWidget(mvm_btn)
        container.addLayout(row)

    def _build_memory_rows(self, container: QtWidgets.QVBoxLayout):
        # 7. Memory write
        row = self._row_shell("Memory write")
        row.addWidget(QtWidgets.QLabel("CIMA#:"))
        mw_cima = self._spin(0, 63)
        row.addWidget(mw_cima)
        row.addWidget(QtWidgets.QLabel("bank addr:"))
        mw_bank = self._spin(0, 0xFFFF)
        row.addWidget(mw_bank)
        row.addWidget(QtWidgets.QLabel("weight value:"))
        mw_w = self._spin(0, 0xFFFF)
        row.addWidget(mw_w)
        row.addWidget(QtWidgets.QLabel("fault (UB):"))
        mw_fault = self._text("e.g. 0")
        row.addWidget(mw_fault)
        row.addStretch(1)
        mw_note = QtWidgets.QLabel("requires compiler binary")
        mw_note.setStyleSheet("color: #b9c0cc;")
        row.addWidget(mw_note)
        mw_btn = QtWidgets.QPushButton("Run")
        mw_btn.setProperty("kind", "primary")
        mw_btn.clicked.connect(lambda: self._emit("memory_write", {"cima": int(mw_cima.value()), "bank_addr": int(mw_bank.value()), "weight_value": int(mw_w.value()), "fault_setting": mw_fault.text()}))
        row.addWidget(mw_btn)
        container.addLayout(row)

        # 8. Memory read
        row = self._row_shell("Memory read")
        row.addWidget(QtWidgets.QLabel("CIMA#:"))
        mr_cima = self._spin(0, 63)
        row.addWidget(mr_cima)
        row.addWidget(QtWidgets.QLabel("bank addr:"))
        mr_bank = self._spin(0, 0xFFFF)
        row.addWidget(mr_bank)
        row.addWidget(QtWidgets.QLabel("fault (UB):"))
        mr_fault = self._text("e.g. 0")
        row.addWidget(mr_fault)
        row.addStretch(1)
        mr_btn = QtWidgets.QPushButton("Run")
        mr_btn.setProperty("kind", "primary")
        mr_btn.clicked.connect(lambda: self._emit("memory_read", {"cima": int(mr_cima.value()), "bank_addr": int(mr_bank.value()), "fault_setting": mr_fault.text()}))
        row.addWidget(mr_btn)
        container.addLayout(row)

        # 8b. Memory BIST
        row = self._row_shell("Memory BIST (back-to-back)")
        row.addWidget(QtWidgets.QLabel("CIMA#:"))
        mb_cima = self._spin(0, 63)
        row.addWidget(mb_cima)
        row.addWidget(QtWidgets.QLabel("bank addr:"))
        mb_bank = self._spin(0, 0xFFFF)
        row.addWidget(mb_bank)
        row.addWidget(QtWidgets.QLabel("fault (UB):"))
        mb_fault = self._text("e.g. 0")
        row.addWidget(mb_fault)
        row.addStretch(1)
        mb_btn = QtWidgets.QPushButton("Run")
        mb_btn.setProperty("kind", "primary")
        mb_btn.clicked.connect(lambda: self._emit("memory_bist", {"cima": int(mb_cima.value()), "bank_addr": int(mb_bank.value()), "fault_setting": mb_fault.text()}))
        row.addWidget(mb_btn)
        container.addLayout(row)

        # 10. CWRAP write
        row = self._row_shell("CWRAP write")
        row.addWidget(QtWidgets.QLabel("CIMA#:"))
        cw_cima = self._spin(0, 63)
        row.addWidget(cw_cima)
        row.addWidget(QtWidgets.QLabel("register:"))
        cw_reg = self._text("REG")
        row.addWidget(cw_reg)
        row.addWidget(QtWidgets.QLabel("space:"))
        cw_space = self._combo(["single", "entire space"])
        row.addWidget(cw_space)
        row.addStretch(1)
        cw_btn = QtWidgets.QPushButton("Run")
        cw_btn.setProperty("kind", "primary")
        cw_btn.clicked.connect(lambda: self._emit("cwrap_write", {"cima": int(cw_cima.value()), "register": cw_reg.text(), "space": cw_space.currentText()}))
        row.addWidget(cw_btn)
        container.addLayout(row)

        # 11. CWRAP read
        row = self._row_shell("CWRAP read")
        row.addWidget(QtWidgets.QLabel("CIMA#:"))
        cr_cima = self._spin(0, 63)
        row.addWidget(cr_cima)
        row.addWidget(QtWidgets.QLabel("register:"))
        cr_reg = self._text("REG")
        row.addWidget(cr_reg)
        row.addWidget(QtWidgets.QLabel("space:"))
        cr_space = self._combo(["single", "entire space"])
        row.addWidget(cr_space)
        row.addStretch(1)
        cr_btn = QtWidgets.QPushButton("Run")
        cr_btn.setProperty("kind", "primary")
        cr_btn.clicked.connect(lambda: self._emit("cwrap_read", {"cima": int(cr_cima.value()), "register": cr_reg.text(), "space": cr_space.currentText()}))
        row.addWidget(cr_btn)
        container.addLayout(row)

    def _build_buck_rows(self, container: QtWidgets.QVBoxLayout):
        # 12. BUCK HADC measurement
        row = self._row_shell("BUCK HADC measurement")
        row.addWidget(QtWidgets.QLabel("BUCK#:"))
        b_idx = self._spin(0, 1)
        row.addWidget(b_idx)
        row.addWidget(QtWidgets.QLabel("Analog ATP:"))
        b_atp = self._combo(["Off", "On"]) 
        row.addWidget(b_atp)
        row.addWidget(QtWidgets.QLabel("Test point:"))
        b_tp = self._text("e.g. TP_B1")
        row.addWidget(b_tp)
        row.addStretch(1)
        b_btn = QtWidgets.QPushButton("Run")
        b_btn.setProperty("kind", "primary")
        b_btn.clicked.connect(lambda: self._emit("buck_hadc_measure", {"buck": int(b_idx.value()), "analog_atp": b_atp.currentText(), "test_point": b_tp.text()}))
        row.addWidget(b_btn)
        container.addLayout(row)

        # 13. BUCK HADC self test
        row = self._row_shell("BUCK HADC self test")
        row.addWidget(QtWidgets.QLabel("BUCK#:"))
        bs_idx = self._spin(0, 1)
        row.addWidget(bs_idx)
        row.addWidget(QtWidgets.QLabel("Analog ATP:"))
        bs_atp = self._combo(["Off", "On"]) 
        row.addWidget(bs_atp)
        row.addWidget(QtWidgets.QLabel("Test point:"))
        bs_tp = self._text("e.g. TP_B1")
        row.addWidget(bs_tp)
        row.addStretch(1)
        bs_btn = QtWidgets.QPushButton("Run")
        bs_btn.setProperty("kind", "primary")
        bs_btn.clicked.connect(lambda: self._emit("buck_hadc_self_test", {"buck": int(bs_idx.value()), "analog_atp": bs_atp.currentText(), "test_point": bs_tp.text()}))
        row.addWidget(bs_btn)
        container.addLayout(row)

        # 14. BUCK reference calibration
        row = self._row_shell("BUCK reference calibration")
        row.addWidget(QtWidgets.QLabel("BUCK_TOP# (reference):"))
        br_ref = self._spin(0, 1)
        row.addWidget(br_ref)
        row.addStretch(1)
        br_btn = QtWidgets.QPushButton("Run")
        br_btn.setProperty("kind", "primary")
        br_btn.clicked.connect(lambda: self._emit("buck_reference_calibration", {"buck_top_ref": int(br_ref.value())}))
        row.addWidget(br_btn)
        container.addLayout(row)

        # 15. BUCK slave calibration
        row = self._row_shell("BUCK slave calibration")
        row.addWidget(QtWidgets.QLabel("BUCK_TOP# (slave):"))
        bs_slave = self._spin(0, 1)
        row.addWidget(bs_slave)
        row.addStretch(1)
        bs_cal_btn = QtWidgets.QPushButton("Run")
        bs_cal_btn.setProperty("kind", "primary")
        bs_cal_btn.clicked.connect(lambda: self._emit("buck_slave_calibration", {"buck_top_slave": int(bs_slave.value())}))
        row.addWidget(bs_cal_btn)
        container.addLayout(row)

        # 16. BUCK Power on
        row = self._row_shell("BUCK Power on")
        row.addWidget(QtWidgets.QLabel("BUCK#:"))
        bp_idx = self._spin(0, 1)
        row.addWidget(bp_idx)
        row.addWidget(QtWidgets.QLabel("Analog ATP:"))
        bp_atp = self._combo(["Off", "On"]) 
        row.addWidget(bp_atp)
        row.addWidget(QtWidgets.QLabel("Test point:"))
        bp_tp = self._text("e.g. TP_B1")
        row.addWidget(bp_tp)
        row.addStretch(1)
        bp_btn = QtWidgets.QPushButton("Run")
        bp_btn.setProperty("kind", "primary")
        bp_btn.clicked.connect(lambda: self._emit("buck_power_on", {"buck": int(bp_idx.value()), "analog_atp": bp_atp.currentText(), "test_point": bp_tp.text()}))
        row.addWidget(bp_btn)
        container.addLayout(row)

    # ---------- Emit helper ----------
    def _emit(self, test_id: str, params: dict):
        # Always emit the signal for external listeners
        self.runRequested.emit(test_id, params)
        # If no executor, show a friendly summary; otherwise delegate
        if self.executor is None:
            lines = [f"{k}: {v}" for k, v in params.items()]
            QtWidgets.QMessageBox.information(self, f"{test_id}", "\n".join(lines) or "(no params)")
            return
        try:
            self.executor(test_id, params)
        except Exception as exc:
            QtWidgets.QMessageBox.critical(self, "Execution error", str(exc))

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
        self.tab_cima = CimaTab("CIMA", CIMA_REGISTERS)
        self.tab_cima_mvm = CimaMvmTab()
        self.tab_board = BoardTab()
        self.tab_functions = FunctionsTab()

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
