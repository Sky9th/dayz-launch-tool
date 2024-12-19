from functools import partial
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFrame, QLineEdit, QScrollArea, QFileDialog, QTextEdit
from PySide6.QtGui import QFont, QTextCursor, QIcon
from PySide6.QtCore import Qt
from event import Event
from util import get_resource_path

class MainUI(QWidget):

    def __init__(self):
        super().__init__()

        self.server_log = None
        self.client_log = None

        self.eventHandler = Event(self)

        self.setWindowIcon(QIcon(get_resource_path('./icon.ico')))
        self.setWindowTitle("OverSky DayZ Debug Luanch [Author:Sky9th]")
        self.setGeometry(100, 100, 500, 600)

        # Create the main layout (Vertical Layout)
        main_layout = QHBoxLayout()
        main_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)  # Align top-left

        main_set_widget = QWidget()
        main_set_widget.setFixedWidth(450)

        # Add error log layout
        main_layout.addLayout(self.create_error_log_layout())
        main_set_layout = QVBoxLayout(main_set_widget)
        main_set_layout.addLayout(self.create_start_layout())
        main_set_layout.addWidget(self.create_divider())
        main_set_layout.addLayout(self.create_config_layout())
        main_layout.addLayout(main_set_layout)

        main_layout.addWidget(main_set_widget)

        main_log_layout = QHBoxLayout()
        # main_log_layout.addLayout(self.create_log_layout("Client Log", "client"))
        # main_log_layout.addLayout(self.create_log_layout("Server Log", "server"))
        main_layout.addLayout(main_log_layout)

        # Set the main layout for the window
        self.setLayout(main_layout)

    def create_divider(self, h = True, length = None):
        divider = QFrame()
        if (h):
            divider.setFrameShape(QFrame.HLine)  # Set the frame to be a horizontal line
        else :
            divider.setFrameShape(QFrame.VLine)  # Set the frame to be a horizontal line
        divider.setFrameShadow(QFrame.Sunken)  # Set the shadow of the line
        if (length != None):
            divider.setFixedWidth(length)
        return divider;

    def create_label(self, text, font_size, fixed_height, fixed_width):
        """Creates a styled label with specified font size, height, and width."""
        label = QLabel(text)
        label.setWordWrap(True)  # Enable word wrap

        font = QFont()
        font.setPointSize(font_size)  # Set the font size
        label.setFont(font)

        label.setMinimumHeight(fixed_height)  # Set fixed height for the label
        label.setFixedWidth(fixed_width)  # Set fixed width for the label

        return label

    def create_h1_label(self, text):
        """Creates and styles a label with size H1."""
        return self.create_label(text, 16, 30, 120)

    def create_h2_label(self, text):
        """Creates and styles a label with size H2."""
        return self.create_label(text, 12, 25, 120)

    def create_h3_label(self, text):
        """Creates and styles a label with size H3."""
        return self.create_label(text, 10, 20, 120)

    def create_input(self, text = "", placeholder = ""):

        root_layout = QHBoxLayout()
        root_layout.setContentsMargins(0, 5, 0, 5)
        
        if (text):
            label = self.create_h3_label(text)
            root_layout.addWidget(label)

        input = QLineEdit()
        input.setPlaceholderText(placeholder)  # Placeholder text when the input is empty
        input.setFixedWidth(200)  # Set the width of the input box
        root_layout.addWidget(input)

        return root_layout
    
    def create_input_with_directory_picker(self, text="", value="", callback=None, *callback_args):
        """Creates an input box with a directory picker button and optional callback."""
        root_layout = QHBoxLayout()
        root_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        root_layout.setContentsMargins(0, 5, 0, 5)

        # Add label if text is provided
        if text:
            label = self.create_h3_label(text)
            root_layout.addWidget(label)

        # Layout for the input box and the browse button
        pick_layout = QVBoxLayout()
        pick_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        # Create the input box
        input_box = QLineEdit()
        input_box.setText(value)
        input_box.setFixedWidth(280)
        input_box.setFixedHeight(30)
        pick_layout.addWidget(input_box)

        # Create the button to select a directory
        browse_button = QPushButton("Browse")
        if callback:
            # Use partial to pass the callback and any additional parameters
            browse_button.clicked.connect(partial(self.select_directory, input_box, callback, *callback_args))
        browse_button.setFixedWidth(100)
        pick_layout.addWidget(browse_button)

        root_layout.addLayout(pick_layout)

        return root_layout

    def select_directory(self, input_box, callback, *callback_args):
        """Handle directory selection and trigger the callback with additional arguments."""
        # Open the directory selection dialog
        directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        if directory:
            input_box.setText(directory)  # Update the input box with the selected directory
            # Call the callback function with the directory and additional arguments
            callback(directory, *callback_args)

    def create_start_layout(self):
        start_layout = QVBoxLayout()
        start_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)  # Align top-left

        game_layout = self.create_game_layout()
        start_layout.addLayout(game_layout)

        server_layout = self.create_server_layout()
        start_layout.addLayout(server_layout)

        start_layout.addLayout(self.create_kill_layout())

        return start_layout

    def create_game_layout(self):
        """Creates the game layout with program and mode buttons."""

        game_layout = QVBoxLayout()
        game_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)  # Align top-left

        # Create and add the first button group (Left and Right layout)
        program_layout = QHBoxLayout()
        program_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)  # Align top-left
        label_program = self.create_h3_label("Program")
        button_dayz = QPushButton("DayZ")
        button_dayz.clicked.connect(lambda: self.eventHandler.run_dayz("DayZ"))
        button_dayzdiag = QPushButton("DayZDiag")
        button_dayzdiag.clicked.connect(lambda: self.eventHandler.run_dayz("DayZDiag"))
        button_workbench = QPushButton("Workbench")
        button_workbench.clicked.connect(lambda: self.eventHandler.run_dayz("Workbench"))

        program_layout.addWidget(label_program)
        program_layout.addWidget(button_dayz)
        program_layout.addWidget(button_dayzdiag)
        program_layout.addWidget(button_workbench)
        program_layout.setContentsMargins(0, 0, 50, 0)
        
        # Create and add the second button group (Left and Right layout)
        mode_layout = QHBoxLayout()
        mode_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)  # Align top-left
        label_mode = self.create_h3_label("Mode")
        button_normal = QPushButton("Normal")
        button_normal.setCheckable(True)
        button_normal.setChecked(True)
        button_normal.clicked.connect(lambda: self.eventHandler.on_mode_select("normal"))
        self.button_normal = button_normal
        button_mission = QPushButton("Mission")
        button_mission.setCheckable(True)
        button_mission.clicked.connect(lambda: self.eventHandler.on_mode_select("mission"))
        self.button_mission = button_mission

        mode_layout.addWidget(label_mode)
        mode_layout.addWidget(button_normal)
        mode_layout.addWidget(button_mission)
        
        # Add the game label and button groups to the game layout
        game_layout.addWidget(self.create_h1_label("Game"))
        game_layout.addLayout(program_layout)
        game_layout.addLayout(mode_layout)

        return game_layout
    
    def create_server_layout(self):
        """Creates the game layout with program and mode buttons."""

        game_layout = QVBoxLayout()
        game_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)  # Align top-left

        # Create and add the first button group (Left and Right layout)
        program_layout = QHBoxLayout()
        program_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)  # Align top-left
        label_program = self.create_h3_label("Program")

        button_dayz = QPushButton("DayZ")
        button_dayz.clicked.connect(lambda: self.eventHandler.run_dayz("DayZ", True))
        button_dayzdiag = QPushButton("DayZDiag")
        button_dayzdiag.clicked.connect(lambda: self.eventHandler.run_dayz("DayZDiag", True))

        program_layout.addWidget(label_program)
        program_layout.addWidget(button_dayz)
        program_layout.addWidget(button_dayzdiag)

        # Add the game label and button groups to the game layout
        game_layout.addWidget(self.create_h1_label("Server"))
        game_layout.addLayout(program_layout)

        return game_layout
    
    def create_kill_layout(self):
        """Creates the game layout with program and mode buttons."""

        game_layout = QVBoxLayout()
        game_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)  # Align top-left

        button_kg = QPushButton("Kill Game")
        button_kg.clicked.connect(self.eventHandler.kill_dayz)
        button_ks = QPushButton("Kill Server")
        button_ks.clicked.connect(self.eventHandler.kill_dayz_server)
        button_ka = QPushButton("Kill All")
        button_ka.clicked.connect(self.eventHandler.kill_dayz_processes)

        game_btn_layout = QHBoxLayout()
        game_btn_layout.addWidget(self.create_h3_label("Command"))
        game_btn_layout.addWidget(button_kg)
        game_btn_layout.addWidget(button_ks)
        game_btn_layout.addWidget(button_ka)

        # Add the game label and button groups to the game layout
        game_layout.addWidget(self.create_h1_label("Server"))
        game_layout.addLayout(game_btn_layout)

        return game_layout
    
    def create_config_layout(self):
        """Creates the game layout with program and mode buttons."""

        root_layout = QVBoxLayout()
        root_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)  # Align top-left
        
        # Add the game label and button groups to the game layout
        root_layout.addWidget(self.create_h1_label("Config"))
        #root_layout.addLayout(self.create_input_with_directory_picker("Mount Driver", "", self.eventHandler.set))

        # Define configuration items in an array
        config_items = [
            ("Mount Driver", "mountDriverPath"),
            ("DayZ Install Path", "dayZInstallPath"),
            ("DayZ Server Install Path", "dayZServerInstallPath"),
            ("Your Mod Path", "devMod"),
            ("Dependencies Mod Path", "dependeciesMod"),
            # ("Mission Path", "missionPath"),
            ("Offline Mission Path", "offlineMissoinPath")
        ]

        # Loop through the configuration items and add them to the layout
        for label, config_key in config_items:
            root_layout.addLayout(self.create_input_with_directory_picker(
                label,  # Label text
                self.eventHandler.config[config_key],  # Initial path value
                self.eventHandler.on_config_update,  # Callback function
                config_key  # Additional argument for the callback
            ))

        return root_layout

    def create_log_layout(self, text, type):
        """Creates the layout for the logger with scrollable text box."""
        root_layout = QVBoxLayout()
        root_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        # Create the title label
        root_layout.addWidget(self.create_h1_label(text))

        # Create the scrollable text box for logs
        view = QTextEdit()
        view.setReadOnly(True)  # Make the text box read-only
        view.setPlaceholderText("Logs will appear here...")

        if (type == "client"):
            self.client_log = view
        else:
            self.server_log = view

        # Create a scroll area to make the text box scrollable
        scroll_area = QScrollArea()
        scroll_area.setWidget(view)
        scroll_area.setWidgetResizable(True)

        # Add the scroll area to the layout
        root_layout.addWidget(scroll_area)

        return root_layout

    def update_log(self, log_type, content):
        """
        更新客户端或服务端日志组件内容。
        :param log_type: 日志类型 ("client" 或 "server")
        :param content: 日志内容
        """
        if log_type == "client":
            cursor = self.client_log.textCursor()  # 获取当前文本光标
            cursor.movePosition(QTextCursor.End)  # 将光标移动到末尾
            cursor.insertText(content)  # 插入新的日志信息
            self.client_log.setTextCursor(cursor)  # 更新文本框的光标位置
            self.client_log.ensureCursorVisible()  # 确保滚动到最新位置
        elif log_type == "server":
            cursor = self.server_log.textCursor()  # 获取当前文本光标
            cursor.movePosition(QTextCursor.End)  # 将光标移动到末尾
            cursor.insertText(content)  # 插入新的日志信息
            self.server_log.setTextCursor(cursor)  # 更新文本框的光标位置
            self.server_log.ensureCursorVisible()  # 确保滚动到最新位置

    def create_error_log_layout(self):
        """Creates the layout for displaying error logs."""
        root_layout = QVBoxLayout()
        root_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        # Create the title label
        label = QLabel("Error Log")
        label.setAlignment(Qt.AlignLeft)
        root_layout.addWidget(label)

        # Create the scrollable text box for logs
        self.error_log = QTextEdit()
        self.error_log.setReadOnly(True)
        self.error_log.setPlaceholderText("Errors will appear here...")

        scroll_area = QScrollArea()
        scroll_area.setWidget(self.error_log)
        scroll_area.setWidgetResizable(True)

        root_layout.addWidget(scroll_area)

        return root_layout

    def update_error_log(self, content):
        print(content)
        """Append error content to the error log."""
        cursor = self.error_log.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(content + "\n")
        self.error_log.setTextCursor(cursor)
        self.error_log.ensureCursorVisible()