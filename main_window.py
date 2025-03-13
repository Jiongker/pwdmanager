from PyQt6.QtWidgets import QMainWindow, QTabWidget, QWidget, QVBoxLayout, QMessageBox,QTableWidgetItem,QPushButton,QLineEdit, QComboBox,QTableWidget,QHeaderView,QTabBar,QGroupBox
from PyQt6.QtGui import QIcon
from database import PasswordDatabase
import os
from PyQt6.QtWidgets import QFileDialog

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('密码管理器')
        self.setGeometry(100, 100, 800, 600)
        self.setWindowIcon(QIcon(':/icons/app_icon.png'))
        
        # 创建标签页
        self.tabs = QTabWidget()
        self.storage_tab = QWidget()
        self.search_tab = QWidget()
        
        self.tabs.addTab(self.storage_tab, QIcon(':/icons/save.png'), '存储密码')
        self.tabs.addTab(self.search_tab, QIcon(':/icons/search.png'), '查询密码')
        
        self.init_storage_tab()
        self.init_search_tab()
        
        self.setCentralWidget(self.tabs)
        
        # 初始化数据库
        self.db = PasswordDatabase()

    def save_password(self):
        try:
            if not hasattr(self, 'db') or not self.db.db_path:
                QMessageBox.critical(self, '错误', '请先选择存储目录')
                return

            website = self.website_input.text().strip()
            username = self.username_input.text().strip()
            password = self.password_input.text().strip()
            tags = [t.strip() for t in self.tags_input.text().split(',') if t.strip()]

            if not website or not username or not password:
                QMessageBox.warning(self, '警告', '网站、用户名和密码为必填项')
                return

            self.db.save_password(website, username, password, tags)
            QMessageBox.information(self, '成功', '密码保存成功！')
            
            # 清空输入框
            self.website_input.clear()
            self.username_input.clear()
            self.password_input.clear()
            self.tags_input.clear()
        except Exception as e:
            QMessageBox.critical(self, '错误', f'保存失败: {str(e)}')

    def init_storage_tab(self):
        from PyQt6.QtWidgets import (QFormLayout, QLineEdit, QPushButton, 
                                  QFileDialog, QHBoxLayout, QGroupBox)
        
        # 创建表单组
        group = QGroupBox('密码信息')
        form_layout = QFormLayout()
        
        self.website_input = QLineEdit()
        self.username_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.tags_input = QLineEdit()
        
        form_layout.addRow('网站:', self.website_input)
        form_layout.addRow('用户名:', self.username_input)
        form_layout.addRow('密码:', self.password_input)
        form_layout.addRow('标签(逗号分隔):', self.tags_input)
        group.setLayout(form_layout)
        
        # 目录选择按钮
        dir_layout = QHBoxLayout()
        self.dir_label = QLineEdit('选择存储目录')
        self.dir_label.setReadOnly(True)
        dir_btn = QPushButton('选择...')
        dir_btn.setIcon(QIcon(':/icons/folder.png'))
        dir_btn.clicked.connect(self.select_directory)
        dir_layout.addWidget(self.dir_label)
        dir_layout.addWidget(dir_btn)
        
        # 保存按钮
        save_btn = QPushButton('保存密码')
        save_btn.setIcon(QIcon(':/icons/save.png'))
        save_btn.clicked.connect(self.save_password)
        
        # 主布局
        main_layout = QVBoxLayout()
        main_layout.addWidget(group)
        main_layout.addLayout(dir_layout)
        main_layout.addWidget(save_btn)
        self.storage_tab.setLayout(main_layout)

    def init_search_tab(self):
        from PyQt6.QtWidgets import (QHBoxLayout, QLineEdit, QPushButton, 
                                  QTableWidget, QTableWidgetItem, QGroupBox,
                                  QVBoxLayout, QHeaderView)
        
        # 创建搜索组
        search_group = QGroupBox('搜索条件')
        search_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText('输入网站或标签进行搜索')
        search_btn = QPushButton('搜索')
        search_btn.setIcon(QIcon(':/icons/search.png'))
        search_btn.clicked.connect(self.search_passwords)
        
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(search_btn)
        search_group.setLayout(search_layout)
        
        # 创建结果表格
        self.result_table = QTableWidget()
        self.result_table.setColumnCount(4)
        self.result_table.setHorizontalHeaderLabels(['网站', '用户名', '密码', '标签'])
        self.result_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.result_table.verticalHeader().setVisible(False)
        
        # 主布局
        main_layout = QVBoxLayout()
        main_layout.addWidget(search_group)
        main_layout.addWidget(self.result_table)
        self.search_tab.setLayout(main_layout)
    
    def show_password(self, item):
        if item.column() == 2:
            real_password = item.data(256)
            msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setWindowTitle('密码')
        msg.setText(f'真实密码：{real_password}')
        msg.setStyleSheet('QLabel{color: #000000; background: white;} QPushButton{background: #4A90E2; color: white;}')
        msg.exec()

    def search_passwords(self):
        keyword = self.search_input.text()
        results = self.db.search_passwords(keyword)
        
        self.result_table.setRowCount(len(results))
        for row_idx, item in enumerate(results):
            self.result_table.setItem(row_idx, 0, QTableWidgetItem(item['website']))
            self.result_table.setItem(row_idx, 1, QTableWidgetItem(item['username']))
            
            # 显示隐藏密码
            password_item = QTableWidgetItem('******')
            password_item.setData(256, item['password'])  # 256是UserRole
            self.result_table.setItem(row_idx, 2, password_item)
        self.result_table.itemDoubleClicked.connect(self.show_password)
            
        self.result_table.setItem(row_idx, 3, QTableWidgetItem(', '.join(item['tags'])))


    def select_directory(self):
        selected_dir = QFileDialog.getExistingDirectory(self, "选择存储目录")
        if selected_dir:
            self.dir_label.setText(selected_dir)
            self.db = PasswordDatabase(os.path.join(selected_dir, 'passwords.db'))