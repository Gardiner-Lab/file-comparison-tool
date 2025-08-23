# Screenshots and Media

This directory contains screenshots, demo GIFs, and other media files for the File Comparison Tool documentation.

## File Organization

- `screenshots/` - Application screenshots
- `demos/` - Demo GIFs and videos
- `diagrams/` - Architecture and workflow diagrams
- `icons/` - Application icons and UI elements

## Screenshots Needed

### Main Application Interface
- [ ] Main window with all panels visible
- [ ] File selection panel with files loaded
- [ ] Column mapping interface with dropdowns
- [ ] Operation configuration panel
- [ ] Results display with sample data
- [ ] Export dialog

### Workflow Demonstration
- [ ] Step-by-step workflow screenshots
- [ ] Before/after comparison examples
- [ ] Error handling examples
- [ ] Help system screenshots

### Demo GIFs
- [ ] Complete workflow demonstration (30-60 seconds)
- [ ] File selection and preview
- [ ] Column mapping process
- [ ] Operation execution with progress
- [ ] Results export

## Guidelines for Screenshots

1. **Resolution**: Use high-resolution screenshots (at least 1920x1080)
2. **Format**: PNG for screenshots, GIF for animations
3. **Content**: Use sample data that demonstrates features clearly
4. **Privacy**: Ensure no sensitive data is visible
5. **Consistency**: Use consistent window sizes and themes

## Sample Data for Screenshots

Use the test files in `test_data/` directory:
- `customers.csv` and `subscribers.csv` for basic demonstrations
- Larger files for performance demonstrations
- Files with different column structures for mapping examples

## Tools for Creating Screenshots

### Recommended Tools
- **Windows**: Snipping Tool, Greenshot, ShareX
- **macOS**: Screenshot utility (Cmd+Shift+4), CleanShot X
- **Linux**: GNOME Screenshot, Flameshot, Shutter

### GIF Creation Tools
- **Cross-platform**: OBS Studio, ScreenToGif
- **Online**: Giphy Capture, LICEcap
- **Command line**: ffmpeg

## File Naming Convention

Use descriptive names with prefixes:
- `main-window-overview.png`
- `file-selection-panel.png`
- `column-mapping-dropdown.png`
- `results-display-table.png`
- `demo-complete-workflow.gif`
- `demo-file-selection.gif`

## Adding Screenshots to Documentation

When adding screenshots to README.md or other documentation:

```markdown
![Main Window](docs/images/screenshots/main-window-overview.png)
*The main application window showing all panels*

![Demo](docs/images/demos/complete-workflow.gif)
*Complete workflow demonstration*
```

## TODO

- [ ] Create main application screenshots
- [ ] Record workflow demonstration GIFs
- [ ] Add error handling screenshots
- [ ] Create help system screenshots
- [ ] Update README.md with actual screenshots
- [ ] Create application icon and logo