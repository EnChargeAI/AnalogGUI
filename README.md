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
python3 analog_gui.py
```

Notes
-----

- The UI uses a custom dark theme with accent buttons. Modify the sample port list in `analog_gui.py` inside `_build_tab_contents`.
- Hook up real hardware by replacing the `on_write`, `on_read`, and `_on_check_hadc` stubs.

## Contributing

We welcome contributions to AnalogGUI! Here's how you can help:

### For Repository Collaborators
To add someone as a collaborator to this repository:
1. Go to the repository **Settings** tab on GitHub
2. Click on **"Manage access"** in the left sidebar  
3. Click **"Invite a collaborator"**
4. Enter the GitHub username or email of the person to add
5. Select the appropriate permission level (Read, Write, or Admin)

*Note: Only repository owners and admins can add new collaborators.*

### For Contributors
- Check out our [Contributing Guidelines](CONTRIBUTING.md) for detailed information
- See [CONTRIBUTORS.md](CONTRIBUTORS.md) for our list of contributors
- Report bugs or suggest features using our [issue templates](.github/ISSUE_TEMPLATE/)
- Submit pull requests following our [pull request template](.github/PULL_REQUEST_TEMPLATE.md)

## Project Structure

```
AnalogGUI/
├── analog_gui.py          # Main GUI application
├── README.md             # This file
├── CONTRIBUTING.md       # Contribution guidelines
├── CONTRIBUTORS.md       # List of contributors
├── CODEOWNERS           # Code ownership configuration
└── .github/             # GitHub templates and configuration
    ├── ISSUE_TEMPLATE/  # Bug report and feature request templates
    └── PULL_REQUEST_TEMPLATE.md
```

