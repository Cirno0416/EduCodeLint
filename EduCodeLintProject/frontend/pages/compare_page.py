from datetime import datetime
import pytz

from PyQt6.QtCore import QThread, Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QListWidget, QListWidgetItem, QSizePolicy
)

from frontend.components.pagination import Pagination
from frontend.controllers.compare_controller import CompareController
from frontend.components.compare_report_window import CompareReportWindow
from frontend.controllers.record_controller import RecordController
from frontend.core.record_worker import RecordWorker
from frontend.pages.record_page import RecordPage
from frontend.utils.dialog_util import DialogUtil


class ComparePage(QWidget):

    def __init__(self, record_page: RecordPage, parent=None):
        super().__init__(parent)

        self.record_page = record_page
        self.record_page.record_deleted.connect(self.on_record_deleted)

        self.compare_controller = CompareController()
        self.record_controller = RecordController()

        self.page = 1
        self.page_size = 10
        self.loading_records = False

        # 多选列表
        self.selected_analyses = []

        self.compare_data = None

        title = QLabel("批次对比")
        title.setObjectName("pageTitle")

        # =============================
        # 表格
        # =============================
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(
            ["批次ID", "文件数量", "创建时间", "操作"]
        )
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setStyleSheet("""
            QTableWidget::item:selected {
                background-color: #f0f0f0;    /* 背景色 */
                color: #000000; 
            }
            QTableWidget::item {
                border: none;                 /* 移除每个格子前的蓝线 */
            }
            QHeaderView::section {
                font-weight: bold;
                font-size: 10pt;
            }
        """)

        # 禁止编辑
        self.table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )

        # 去掉焦点
        self.table.setFocusPolicy(
            Qt.FocusPolicy.NoFocus
        )

        # 整行选中
        self.table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )

        # 一次只选中一行
        self.table.setSelectionMode(
            QTableWidget.SelectionMode.SingleSelection
        )

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)

        # =============================
        # 分页
        # =============================
        self.pagination = Pagination(self.page, self.page_size)
        self.pagination.page_changed.connect(self.on_page_changed)
        self.pagination.page_size_changed.connect(self.on_page_size_changed)

        # =============================
        # 选中列表 + 按钮
        # =============================
        label_font = QFont()
        label_font.setPointSize(12)
        label_font.setBold(True)

        # 列表展示选择批次ID
        # 标题
        self.selection_title = QLabel(f"已选择批次")
        self.selection_title.setFont(label_font)

        # 列表
        self.selection_list = QListWidget()
        self.selection_list.setFixedHeight(200)     # 固定高度
        self.selection_list.setMinimumWidth(500)    # 最小宽度
        self.selection_list.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )
        self.selection_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #ddd;
                border-radius: 6px;
                padding: 4px;
            }
        """)

        selection_layout = QVBoxLayout()
        selection_layout.addWidget(self.selection_title)
        selection_layout.addWidget(self.selection_list)
        selection_layout.addStretch()

        # 按钮
        btn_font = QFont()
        btn_font.setPointSize(10)
        btn_font.setBold(True)

        self.btn_compare = QPushButton("对比选中批次")
        self.btn_compare.setFont(btn_font)
        self.btn_compare.clicked.connect(self.compare_selected)
        self.btn_compare.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)

        self.btn_report = QPushButton("查看对比分析报告")
        self.btn_report.setFont(btn_font)
        self.btn_report.setEnabled(False)
        self.btn_report.clicked.connect(self.open_report)
        self.btn_report.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)

        # 分析状态
        self.status_label = QLabel("尚未进行对比")
        self.status_label.setFont(label_font)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignRight)

        status_layout = QHBoxLayout()
        status_layout.addStretch()
        status_layout.addWidget(self.status_label)

        btn_layout = QVBoxLayout()
        btn_layout.addWidget(self.btn_compare, alignment=Qt.AlignmentFlag.AlignRight)
        btn_layout.addSpacing(20)
        btn_layout.addWidget(self.btn_report, alignment=Qt.AlignmentFlag.AlignRight)
        btn_layout.addSpacing(30)
        btn_layout.addLayout(status_layout)

        bottom_layout = QHBoxLayout()
        bottom_layout.addLayout(selection_layout)
        bottom_layout.addStretch()
        bottom_layout.addLayout(btn_layout)

        layout = QVBoxLayout(self)
        layout.addWidget(title)
        layout.addWidget(self.table, stretch=1)
        layout.addWidget(self.pagination)
        layout.addSpacing(30)
        layout.addLayout(bottom_layout)

        self.load_records()

    # =============================
    # 加载数据
    # =============================
    def load_records(self):
        if self.loading_records:
            return

        self.loading_records = True

        self.record_thread = QThread()
        self.worker = RecordWorker(
            self.record_controller,
            self.page,
            self.page_size
        )

        self.worker.moveToThread(self.record_thread)

        self.record_thread.started.connect(self.worker.run)

        self.worker.finished.connect(self.on_records_loaded)
        self.worker.error.connect(self.on_error)

        self.worker.finished.connect(self.record_thread.quit)
        self.worker.error.connect(self.record_thread.quit)

        self.worker.finished.connect(self.worker.deleteLater)
        self.record_thread.finished.connect(self.record_thread.deleteLater)

        self.record_thread.finished.connect(self.on_load_finished)

        self.record_thread.start()

    def on_records_loaded(self, result):
        if result.get("code") != 0:
            DialogUtil.warning(self, result.get("msg"))
            return

        data = result["data"]
        records = data["records"]

        self.page = data["page"]
        self.page_size = data["page_size"]
        self.total_records = data.get("total", 0)

        self.total_pages = max(1, (self.total_records + self.page_size - 1) // self.page_size)

        self.table.setRowCount(len(records))

        for row, r in enumerate(records):
            analysis_id = r["id"]
            formatted_time = self.time_format(r["created_at"])

            self.table.setItem(row, 0, QTableWidgetItem(r["id"]))
            self.table.setItem(row, 1, QTableWidgetItem(str(r["file_count"])))
            self.table.setItem(row, 2, QTableWidgetItem(formatted_time))

            btn = QPushButton("选择")

            btn.clicked.connect(
                lambda _, aid=analysis_id, ct=formatted_time, fc=str(r["file_count"]):
                self.toggle_select(aid, ct, fc)
            )

            # 已选高亮
            if any(a["id"] == analysis_id for a in self.selected_analyses):
                btn.setText("✓")
                btn.setStyleSheet("background:#4CAF50;color:white")

            self.table.setCellWidget(row, 3, btn)

        self.pagination.update_pagination(
            self.page,
            self.total_pages,
            self.total_records
        )

    def on_load_finished(self):
        self.loading_records = False

    def toggle_select(self, analysis_id, created_at, file_count):
        existing = next((a for a in self.selected_analyses if a["id"] == analysis_id), None)

        if existing:
            self.selected_analyses.remove(existing)
        else:
            if len(self.selected_analyses) >= 5:
                DialogUtil.warning(self, "最多只能选择5个批次")
                return

            self.selected_analyses.append({
                "id": analysis_id,
                "created_at": created_at,
                "file_count": file_count
            })

        self.update_current_page_buttons()
        self.update_selection_label()

    def update_current_page_buttons(self):
        for row in range(self.table.rowCount()):
            analysis_id = self.table.item(row, 0).text()
            btn = self.table.cellWidget(row, 3)

            if any(a["id"] == analysis_id for a in self.selected_analyses):
                btn.setText("✓")
                btn.setStyleSheet("background:#4CAF50;color:white")
            else:
                btn.setText("选择")
                btn.setStyleSheet("")

    def update_selection_label(self):
        self.selection_list.clear()

        if not self.selected_analyses:
            item = QListWidgetItem("无")
            self.selection_list.addItem(item)
            return

        for a in self.selected_analyses:
            text = f'{a["id"]}  {a["created_at"]} ({a["file_count"]}个文件)'
            item = QListWidgetItem(text)
            self.selection_list.addItem(item)

    # =============================
    # 删除同步
    # =============================
    def on_record_deleted(self, deleted_id):
        self.selected_analyses = [
            a for a in self.selected_analyses if a["id"] != deleted_id
        ]
        self.update_selection_label()

    # =============================
    # 对比
    # =============================
    def compare_selected(self):
        if len(self.selected_analyses) < 2:
            DialogUtil.warning(self, "至少选择两个批次")
            return

        if len(self.selected_analyses) > 5:
            DialogUtil.warning(self, "最多选择5个批次")
            return

        ids = [a["id"] for a in self.selected_analyses]

        result = self.compare_controller.compare(ids)

        if result["code"] != 0:
            DialogUtil.warning(self, result["msg"])
            return

        self.compare_data = result["data"]

        self.btn_report.setEnabled(True)

        self.status_label.setText("对比分析完成")

    def open_report(self):
        dialog = CompareReportWindow(self.compare_data)
        dialog.exec()

    # =============================
    # 分页
    # =============================
    def on_page_changed(self, page):
        self.page = page
        self.load_records()

    def on_page_size_changed(self, page_size):
        if page_size != self.page_size:
            self.page_size = page_size
            self.page = 1
            self.load_records()

    def on_error(self, message):
        DialogUtil.error(self, f"获取记录失败: {message}")

    def time_format(self, created_at):
        local_tz = pytz.timezone('Asia/Shanghai')

        try:
            dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            if dt.tzinfo:
                dt = dt.astimezone(local_tz)
            return dt.strftime('%Y-%m-%d %H:%M:%S')
        except:
            return created_at
