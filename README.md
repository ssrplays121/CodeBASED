# codeBASED: Codebase Compiler 📦

A simple desktop application for compiling your entire codebase into a single, organized text file. Perfect for AI analysis, code review, archiving, or sharing complete project context.

## ✨ Features

### 📁 **Smart File Management**
- **Visual File Tree**: Interactive checkbox treeview to select specific files/folders
- **Asynchronous Loading**: Load large codebases without freezing the UI
- **File Type Recognition**: Automatic icons for different programming languages
- **Real-time Statistics**: Live file and folder count tracking

### 🎨 **Modern GUI Design**
- **Dark Theme Interface**: Easy-on-the-eyes dark color scheme
- **Custom Dialog System**: Beautiful, themed confirmation and information dialogs
- **Responsive Layout**: Adapts to different window sizes
- **Progress Tracking**: Real-time progress bars for long operations

### ⚡ **Powerful Compilation**
- **Selective Compilation**: Choose exactly which files to include
- **Structured Output**: Organized with headers, metadata, and separators
- **Error Handling**: Graceful handling of file reading errors
- **File Metadata**: Includes file size, modification dates, and line counts

### 🔧 **Advanced Controls**
- **Check/Uncheck All**: Quick selection controls
- **Cancel Operations**: Stop long-running processes at any time
- **Custom Output Paths**: Choose where to save compiled files
- **Refresh Functionality**: Reload directory structure

## 🚀 Installation

### Prerequisites
- Python 3.7 or higher
- Tkinter (usually comes with Python)

### Quick Start
1. Clone the repository:
```bash
git clone https://github.com/yourusername/codebased.git
cd codebased
```

2. Run the application:
```bash
python codebaser.py
```

Or make it executable:
```bash
chmod +x codebaser.py
./codebaser.py
```

## 📖 Usage Guide

### Basic Workflow
1. **Select Source Folder**: Click "Select Folder" to choose your project directory
2. **Review File Tree**: Browse through your codebase structure
3. **Select Files**: Check the boxes next to files you want to include
4. **Configure Output**: Choose output directory and filename
5. **Compile**: Click "Compile Selected Files" to generate the output

### Advanced Features
- **Folder Navigation**: Double-click folders to expand/collapse
- **Batch Selection**: Use "Check All" / "Uncheck All" for bulk operations
- **Output Customization**: Customize the output filename and location
- **Status Tracking**: Monitor progress through the status bar

## 🏗️ Architecture

### Core Components
- **`CodebaseCompilerApp`**: Main application class managing the GUI and workflows
- **`CheckboxTreeview`**: Custom treeview widget with checkbox functionality
- **`CustomDialog` Classes**: Themed dialog boxes (Info, Warning, Error, Confirm)
- **Thread Management**: Asynchronous file loading and compilation

### Key Design Patterns
- **Model-View-Controller**: Separated GUI, business logic, and data
- **Observer Pattern**: Queue-based communication between threads
- **Factory Pattern**: Custom dialog creation
- **Composite Pattern**: File tree structure representation

## 🛠️ Technical Details

### Supported File Types
The application recognizes and provides appropriate icons for:
- **Programming Languages**: Python, JavaScript, TypeScript, Java, C/C++, Go, Rust, Swift, Kotlin, PHP, Ruby, Dart
- **Web Technologies**: HTML, CSS, SCSS, JSX, TSX
- **Data Formats**: JSON, XML, YAML, CSV, SQL
- **Documents**: Markdown, Text, PDF, Word, Excel
- **Media**: Images (JPG, PNG, GIF)
- **Archives**: ZIP, TAR, GZ, 7Z
- **Executables**: EXE, DLL, SO, DYLIB

### Output Format
The compiled file includes:
- Project metadata and timestamp
- Individual file headers with paths and statistics
- Original file contents with line preservation
- Compilation summary with error reporting
- Error log for problematic files

## 🎨 Customization

### Color Scheme
The application uses a custom dark theme that can be modified by editing the `colors` dictionary:
```python
self.colors = {
    'background': '#1B211A',
    'primary': '#628141',
    'secondary': '#8BAE66',
    'accent': '#EBD5AB',
    # ... additional colors
}
```

### Extending Functionality
1. **Add File Icons**: Modify the `_get_file_icon()` method in `CodebaseCompilerApp`
2. **Custom Dialogs**: Extend the `CustomDialog` base class
3. **Additional Features**: Add new methods to the main application class

## ⚙️ Performance

### Optimization Features
- **Lazy Loading**: Files are loaded only when needed
- **Background Processing**: Heavy operations run in separate threads
- **Memory Efficient**: Processes files one at a time during compilation
- **Progress Feedback**: Real-time updates for long operations

### System Requirements
- **Minimum**: 4GB RAM, Dual-core processor
- **Recommended**: 8GB RAM, Quad-core processor for large codebases
- **Storage**: Minimal, only stores temporary data during processing

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. **Report Bugs**: Open an issue with detailed descriptions
2. **Suggest Features**: Propose new functionality or improvements
3. **Submit Pull Requests**: Follow the existing code style and add tests
4. **Improve Documentation**: Help enhance this README or add examples

### Development Setup
```bash
# Fork and clone the repository
git clone https://github.com/yourusername/codebased.git

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements.txt
```

## 📄 License

This project is available under the MIT License. See the LICENSE file for details.

## 🙏 Acknowledgments

- **Tkinter**: For providing the GUI framework
- **Python Community**: For extensive libraries and tools
- **Contributors**: Everyone who has helped improve codeBASED

## 📞 Support

Having issues or questions?
- **Check Issues**: Look for existing solutions in the issue tracker
- **Create Issue**: Report bugs or request features
- **Email**: For direct contact (if provided)

---

**codeBASED** - Code based in reality for all your context needs.
