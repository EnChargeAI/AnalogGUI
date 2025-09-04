Analog Team GUI
================

A minimal, beautiful Tkinter GUI scaffold with tabs for BUCK0, BUCK1, CIMA, Board, and Functions. Each tab shows a scrollable list of analog ports with columns for Name, Read Value, Write, Read, and Default. Actions currently stub to show interaction; values are populated with N/A by default.

How to run
----------

1. Ensure Python 3.9+ is installed.
2. Install PyQt6 (required dependency):
   ```bash
   pip3 install PyQt6
   ```
   Or alternatively using brew:
   ```bash
   brew install pyqt
   ```
3. From this directory run:

```
python3 app.py
```

Notes
-----

- The UI uses a custom dark theme with accent buttons. Modify the sample port list in `app.py` inside `_build_tab_contents`.
- Hook up real hardware by replacing the `on_write`, `on_read`, and `_on_check_hadc` stubs.


