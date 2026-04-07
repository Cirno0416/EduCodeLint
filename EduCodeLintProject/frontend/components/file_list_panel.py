from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QTabWidget, QLabel


class FileListPanel(QWidget):
    """右侧文件列表面板，显示问题Tab及对应的文件路径列表"""

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # 顶部说明标签
        self.label = QLabel()
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("""
            font-size: 14px; 
            font-weight: bold; 
            padding: 5px; 
            background-color: #f0f0f0; 
            border-radius: 4px;
        """)
        layout.addWidget(self.label)

        # Tab 组件
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.TabPosition.North)
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #ccc;
                background: #fafafa;
            }
            QTabBar::tab:selected {
                background: #ffffff;
            }
            QTabBar::tab:hover {
                background: #d0d0d0;
            }
        """)
        layout.addWidget(self.tab_widget)

    def set_data(self, metric_list, metric_to_files, title="点击问题查看涉及的文件"):
        """
        设置面板数据
        :param metric_list: 所有可能的指标名称列表（如 CATEGORY_MAPPING[category]）
        :param metric_count: 字典，指标 -> 问题数量
        :param metric_to_files: 字典，指标 -> 文件路径列表（全局映射）
        :param title: 面板标题
        """
        self.label.setText(title)
        self.tab_widget.clear()

        for metric in metric_list:
            tab_title = metric

            # 文件列表控件
            file_list_widget = QListWidget()
            file_list_widget.setWordWrap(True)
            file_list_widget.setAlternatingRowColors(True)
            # 禁用选中高亮
            file_list_widget.setSelectionMode(QListWidget.SelectionMode.NoSelection)
            # 禁用焦点框
            file_list_widget.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            file_list_widget.setStyleSheet("""
                QListWidget {
                    font-size: 12px;
                }
                QListWidget::item {
                    padding: 4px;
                    border-bottom: 1px solid #eee;
                }
            """)

            file_paths = metric_to_files.get(metric, [])
            if file_paths:
                for idx, fp in enumerate(file_paths, start=1):
                    file_list_widget.addItem(f"{idx}. {fp}")
            else:
                file_list_widget.addItem("该问题没有出现在任何文件中")

            # 将列表放入容器
            tab_content = QWidget()
            tab_layout = QVBoxLayout(tab_content)
            tab_layout.setContentsMargins(5, 5, 5, 5)
            tab_layout.addWidget(file_list_widget)

            self.tab_widget.addTab(tab_content, tab_title)
