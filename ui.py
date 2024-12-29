from functools import partial
from PySide6.QtWidgets import QHeaderView, QTableWidget, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFrame, QLineEdit, QScrollArea, QFileDialog, QTextEdit, QListWidget, QListWidgetItem, QCheckBox, QTableWidgetItem
from PySide6.QtGui import QFont, QTextCursor, QIcon
from PySide6.QtCore import Qt, QTimer, Signal, QObject
from event import Event
from read_config import read_config
from util import get_resource_path
from PySide6.QtCore import QMetaObject, Qt, QDateTime

# 定义全局信号类
class UISignals(QObject):
    log_update_client_signal = Signal(str)  # 用于更新客户端日志
    log_update_server_signal = Signal(str)  # 用于更新服务端日志

class MainUI(QWidget):

    # 定义信号
    log_update_client_signal = Signal(str)
    log_update_server_signal = Signal(str)

    def __init__(self):
        super().__init__()

        self.checkbox_kill_before_start = None
        self.server_log = None
        self.client_log = None

        self.config = read_config()
        self.eventHandler = Event(self)

        self.save_timer = QTimer()
        self.save_timer.setSingleShot(True)
        self.save_timer.timeout.connect(self.eventHandler.save_config)

        self.setWindowIcon(QIcon(get_resource_path('./icon.ico')))
        self.setWindowTitle("OverSky DayZ Debug Luanch [Author:Sky9th]")
        self.setGeometry(100, 100, 1500, 600)

        # Create the main layout (Vertical Layout)
        main_layout = QHBoxLayout()
        main_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)  # Align top-left

        main_set_widget = QWidget()
        main_set_widget.setFixedWidth(500)

        # Add error log layout
        main_set_layout = QVBoxLayout(main_set_widget)
        main_set_layout.addLayout(self.create_start_layout())
        main_set_layout.addWidget(self.create_divider())
        main_set_layout.addLayout(self.create_config_layout())
        main_set_layout.addLayout(self.create_error_log_layout())
        # main_layout.addLayout(main_set_layout)
        main_layout.addWidget(main_set_widget)

        main_log_layout = QHBoxLayout()

        self.max_log_size = 50000  # 设置日志框最大字符数（可根据需要调整）
        self.max_lines = 200  # 设置最大行数（可根据需要调整）
        self.log_update_client_signal.connect(self.update_client_log)
        self.log_update_server_signal.connect(self.update_server_log)

        main_log_layout.addLayout(self.create_mods_layout())
        main_log_layout.addLayout(self.create_log_layout("Client Log", "client"))
        main_log_layout.addLayout(self.create_log_layout("Server Log", "server"))

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

    def create_input(self, text="", value="", callback=None, *callback_args):
        """Creates an input box with a directory picker button and optional callback."""
        root_layout = QHBoxLayout()
        root_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        root_layout.setContentsMargins(0, 5, 0, 5)

        # Add label if text is provided
        if text:
            label = self.create_h3_label(text)
            root_layout.addWidget(label)

        # Create the input box
        input_box = QLineEdit()
        input_box.setText(value)
        input_box.setFixedWidth(280)
        input_box.setFixedHeight(30)
        input_box.textChanged.connect(partial(self.on_config_input, callback, *callback_args))

        root_layout.addWidget(input_box)
        return root_layout
    
    def on_config_input(self, callback, key, value):
        callback(value, key)

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
        button_dayz.clicked.connect(lambda: self.eventHandler.pack_pbo("DayZ"))
        # button_dayz_offline = QPushButton("DayZ Offline")
        # button_dayz_offline.clicked.connect(lambda: self.eventHandler.run_dayz("DayZ Offline"))
        button_dayzdiag = QPushButton("DayZDiag Offline")
        button_dayzdiag.clicked.connect(lambda: self.eventHandler.pack_pbo("DayZDiag Offline"))
        # button_workbench = QPushButton("Workbench")
        # button_workbench.clicked.connect(lambda: self.eventHandler.run_dayz("Workbench"))

        program_layout.addWidget(label_program)
        program_layout.addWidget(button_dayz)
        # program_layout.addWidget(button_dayz_offline)
        program_layout.addWidget(button_dayzdiag)
        # program_layout.addWidget(button_workbench)
        program_layout.setContentsMargins(0, 0, 50, 0)
        
        # check_layout = QHBoxLayout()
        # label_program = self.create_h3_label("")
        # checkbox_kill_before_start = QCheckBox("Kill task before run")
        # check_layout.addWidget(label_program)
        # check_layout.addWidget(checkbox_kill_before_start)
        # kill_status = self.str_to_bool(self.config["kill_before_start"])
        # checkbox_kill_before_start.setChecked(kill_status)
        # checkbox_kill_before_start.stateChanged.connect(self.update_status)
        # self.checkbox_kill_before_start = checkbox_kill_before_start
        
        # Create and add the second button group (Left and Right layout)
        mode_layout = QHBoxLayout()
        mode_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)  # Align top-left
        label_mode = self.create_h3_label("Mode")
        button_normal = QPushButton("MainMenu")
        button_normal.setCheckable(True)
        button_normal.setChecked(True)
        button_normal.clicked.connect(lambda: self.eventHandler.on_mode_select("MainMenu"))
        self.button_normal = button_normal
        button_mission = QPushButton("AutoConnect")
        button_mission.setCheckable(True)
        button_mission.clicked.connect(lambda: self.eventHandler.on_mode_select("AutoConnect"))
        self.button_mission = button_mission

        mode_layout.addWidget(label_mode)
        mode_layout.addWidget(button_normal)
        mode_layout.addWidget(button_mission)
        
        # Add the game label and button groups to the game layout
        game_layout.addWidget(self.create_h1_label("Game"))
        game_layout.addLayout(program_layout)
        # game_layout.addLayout(check_layout)
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
        button_dayz.clicked.connect(lambda: self.eventHandler.pack_pbo("DayZ", True))
        # button_dayzdiag = QPushButton("DayZDiag")
        # button_dayzdiag.clicked.connect(lambda: self.eventHandler.run_dayz("DayZDiag", True))

        program_layout.addWidget(label_program)
        program_layout.addWidget(button_dayz)
        # program_layout.addWidget(button_dayzdiag)

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
            ("Mikero Path", "MikeroDePboToolsMakePboPath"),
            ("Your Mod Path", "devMod"),
            ("Dependencies Mod Path", "dependeciesMod"),
            # ("Mission Path", "missionPath"),
            ("Offline Mission Path", "offlineMissoinPath")
        ]

        root_layout.addLayout(self.create_input(
            "Dev Mod Name",  # Label text
            self.config["devModName"],  # Initial path value
            self.eventHandler.on_config_update,  # Callback function
            "devModName"  # Additional argument for the callback
        ));
        # Loop through the configuration items and add them to the layout
        for label, config_key in config_items:
            root_layout.addLayout(self.create_input_with_directory_picker(
                label,  # Label text
                self.config[config_key],  # Initial path value
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
    
    def update_server_log(self, content):
        # 保证文本框内容不会超过最大长度
        max_length = 10000  # 限制最大字符数
        current_text = self.server_log.toPlainText()
        new_text = current_text + content
        
        # 只保留最大长度的日志
        if len(new_text) > max_length:
            self.server_log.setPlainText(new_text[-max_length:])  # 仅保留最新的日志
        else:
            self.server_log.setPlainText(new_text)

        # 确保滚动到最新位置
        self.server_log.ensureCursorVisible() 
        
        cursor = self.server_log.textCursor()
        cursor.movePosition(QTextCursor.End)  # 将光标移动到末尾
        self.server_log.setTextCursor(cursor)  # 更新文本框的光标位置

    def update_client_log(self, content):
        # 保证文本框内容不会超过最大长度
        max_length = 10000  # 限制最大字符数
        current_text = self.client_log.toPlainText()
        new_text = current_text + content
        
        # 只保留最大长度的日志
        if len(new_text) > max_length:
            self.client_log.setPlainText(new_text[-max_length:])  # 仅保留最新的日志
        else:
            self.client_log.setPlainText(new_text)

        # 确保滚动到最新位置
        self.client_log.ensureCursorVisible() 
        
        cursor = self.client_log.textCursor()
        cursor.movePosition(QTextCursor.End)  # 将光标移动到末尾
        self.client_log.setTextCursor(cursor)  # 更新文本框的光标位置
    
    def create_error_log_layout(self):
        """Creates the layout for displaying error logs."""
        root_layout = QVBoxLayout()
        root_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        # Create the scrollable text box for logs
        self.error_log = QTextEdit()
        self.error_log.setReadOnly(True)

        scroll_area = QScrollArea()
        scroll_area.setWidget(self.error_log)
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        root_layout.addWidget(scroll_area)

        return root_layout

    def update_error_log(self, content):
        """Append error content to the error log. If the content is too long, remove the oldest content."""
        # 获取当前的时间戳
        timestamp = QDateTime.currentDateTime().toString("yyyy-MM-dd hh:mm:ss")
        
        # 构建新的日志内容
        log_content = f"[{timestamp}] {content}\n"
        
        # 获取当前日志内容
        current_log = self.error_log.toPlainText()
        
        # 检查内容长度，超出最大长度则删除旧内容
        if len(current_log) + len(log_content) > 1000:
            # 计算需要删除的字符数
            excess_length = len(current_log) + len(log_content) - 1000
            # 删除多余的内容
            self.error_log.setPlainText(current_log[excess_length:])
        
        # 在日志末尾插入新内容
        cursor = self.error_log.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(log_content)
        self.error_log.setTextCursor(cursor)
        self.error_log.ensureCursorVisible()

    def create_mods_layout(self):
        root_layout = QVBoxLayout()

        self.depend_mod_list_widget = QListWidget()
        self.depend_mod_list_widget.setFixedWidth(200)

        # 表格显示目录和状态
        self.dev_mod_table = QTableWidget(self)
        self.dev_mod_table.setFixedWidth(200)
        self.dev_mod_table.setColumnCount(2)
        self.dev_mod_table.setHorizontalHeaderLabels(["Directory", "Status"])
        self.dev_mod_table.setColumnWidth(0, 147)
        self.dev_mod_table.setColumnWidth(1, 51)
        self.dev_mod_table.verticalHeader().setVisible(False)
        # self.dev_mod_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        button_refresh = QPushButton()
        button_refresh.setText("Fresh")
        button_refresh.clicked.connect(self.refresh_config)

        root_layout.addWidget(self.create_h1_label("Pack pbo"))
        root_layout.addWidget(self.dev_mod_table)
        root_layout.addWidget(self.create_h1_label("Extra Mods"))
        root_layout.addWidget(self.depend_mod_list_widget)
        root_layout.addWidget(button_refresh)

        self.update_mod_status()

        return root_layout
    
    # def update_status(self):
    #     self.eventHandler.on_config_update(self.checkbox_kill_before_start.isChecked(), "kill_before_start")

    def update_mod_status(self):
        """Clear and update the list widget with new mod names."""
        self.depend_mod_list_widget.clear()  # Clear the existing items

        depend_mod_names = self.config["depend_mods"]
        dev_mod_names = self.config["dev_mods"]
        selected = self.config["selected_mods"]

        for mod_name in depend_mod_names:
            item = QListWidgetItem()
            checkbox = QCheckBox(mod_name)

            # 正确的布尔判断
            isChecked = mod_name in selected

            checkbox.setChecked(isChecked)  # 设置复选框状态
            self.depend_mod_list_widget.addItem(item)
            self.depend_mod_list_widget.setItemWidget(item, checkbox)
            checkbox.stateChanged.connect(self.update_selected_mods)

        self.dev_mod_table.setRowCount(len(dev_mod_names))
        row = 0
        for mod_name in dev_mod_names:
            self.dev_mod_table.setItem(row, 0, QTableWidgetItem(mod_name))
            self.dev_mod_table.setItem(row, 1, QTableWidgetItem(""))
            row = row + 1

    def update_pack_status(self, folder, status):
        # 遍历表格的所有行
        for row in range(self.dev_mod_table.rowCount()):
            # 获取第一列的值（即目录）
            first_column_value = self.dev_mod_table.item(row, 0).text()
            # 根据第一列的值，更新第二列的状态（这里示范根据某种逻辑来修改第二列的值）
            if first_column_value == folder:  # 如果第一列有值
                self.dev_mod_table.setItem(row, 1, QTableWidgetItem(status))  # 更新第二列的状态
    
    def update_selected_mods(self):
        """Update selected_mods based on checkbox states."""
        self.config["selected_mods"] = []  # Clear the previous selection

        # Iterate through all checkboxes to update selected_mods
        for index in range(self.dev_mod_list_widget.count()):
            item = self.dev_mod_list_widget.item(index)
            checkbox = self.dev_mod_list_widget.itemWidget(item)
            if checkbox.isChecked():
                self.config["selected_mods"].append(checkbox.text())  # Add the mod to selected_mods if checked
        
        for index in range(self.depend_mod_list_widget.count()):
            item = self.depend_mod_list_widget.item(index)
            checkbox = self.depend_mod_list_widget.itemWidget(item)
            if checkbox.isChecked():
                self.config["selected_mods"].append(checkbox.text())  # Add the mod to selected_mods if checked

        # Start or reset the timer for saving config
        if self.save_timer.isActive():
            self.save_timer.stop()
        self.save_timer.start(300)  # Delay of 300ms

    def str_to_bool(self, value):
        true_values = {"true", "yes", "1"}
        false_values = {"false", "no", "0"}

        if value.lower() in true_values:
            return True
        elif value.lower() in false_values:
            return False
        return False

    def refresh_config(self):
        self.config = read_config()
        self.update_depend_mod_list()