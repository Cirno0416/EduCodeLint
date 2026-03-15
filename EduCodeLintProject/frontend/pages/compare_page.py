from datetime import datetime

import pytz
from PyQt6.QtCore import QThread
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QMessageBox
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

        # 监听历史记录删除事件，如果对比的记录被删除了，自动清除选择
        self.record_page = record_page
        self.record_page.record_deleted.connect(self.on_record_deleted)

        self.compare_controller = CompareController()
        self.record_controller = RecordController()

        self.page = 1
        self.page_size = 10

        # 防重复请求
        self.loading_records = False

        # 当前选择的ID
        self.analysis_a = None
        self.analysis_b = None

        # 当前选择的按钮（用于高亮显示）
        self.btn_a_selected = None
        self.btn_b_selected = None

        self.compare_data = None

        layout = QVBoxLayout(self)

        title = QLabel("批次对比")
        title.setObjectName("pageTitle")
        layout.addWidget(title)

        # ===== 历史记录列表 =====
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(
            ["ID", "文件数量", "创建时间", "状态", "选择批次A", "选择批次B"]
        )

        self.table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)

        layout.addWidget(self.table)

        # ===== 分页控件 =====
        self.pagination = Pagination(self.page, self.page_size)
        self.pagination.page_changed.connect(self.on_page_changed)
        self.pagination.page_size_changed.connect(self.on_page_size_changed)

        layout.addWidget(self.pagination)

        # ===== 当前选择显示和Compare按钮 =====
        btn_layout = QHBoxLayout()

        self.selection_label = QLabel("A: 未选择    B: 未选择")

        self.btn_compare = QPushButton("对比选中批次")
        self.btn_compare.clicked.connect(self.compare_selected)

        btn_layout.addWidget(self.selection_label)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_compare)

        layout.addLayout(btn_layout)

        # 这里是空隙
        layout.addSpacing(30)

        # ===== 对比摘要 =====
        summary_title = QLabel("对比结果")
        font = QFont()
        font.setBold(True)
        summary_title.setFont(font)
        layout.addWidget(summary_title)

        self.summary_label = QLabel("还未进行对比")
        layout.addWidget(self.summary_label)

        # ===== 详细报告按钮 =====
        self.btn_report = QPushButton("查看对比分析报告")
        self.btn_report.setEnabled(False)
        self.btn_report.clicked.connect(self.open_report)

        layout.addWidget(self.btn_report)

        # 初始化加载
        self.load_records()

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
            QMessageBox.warning(self, "错误", result.get("msg"))
            return

        data = result["data"]
        records = data["records"]

        self.page = data["page"]
        self.page_size = data["page_size"]
        self.total_records = data.get("total", 0)

        if self.total_records > 0:
            self.total_pages = (self.total_records + self.page_size - 1) // self.page_size
        else:
            self.total_pages = 1

        self.table.setRowCount(len(records))

        for row, r in enumerate(records):
            analysis_id = r["id"]
            formatted_time = self.time_format(r["created_at"])

            self.table.setItem(row, 0, QTableWidgetItem(r["id"]))
            self.table.setItem(row, 1, QTableWidgetItem(str(r["file_count"])))
            self.table.setItem(row, 2, QTableWidgetItem(formatted_time))
            self.table.setItem(row, 3, QTableWidgetItem(r["status"]))

            btn_a = QPushButton("A")
            btn_b = QPushButton("B")

            btn_a.clicked.connect(
                lambda _, aid=r["id"]: self.select_a(aid)
            )

            btn_b.clicked.connect(
                lambda _, aid=r["id"]: self.select_b(aid)
            )

            # 如果已经是选中的A/B就高亮
            if analysis_id == self.analysis_a:
                btn_a.setText("✓")
                btn_a.setStyleSheet("background:#4CAF50;color:white")

            if analysis_id == self.analysis_b:
                btn_b.setText("✓")
                btn_b.setStyleSheet("background:#4CAF50;color:white")

            self.table.setCellWidget(row, 4, btn_a)
            self.table.setCellWidget(row, 5, btn_b)

        self.pagination.update_pagination(
            self.page,
            self.total_pages,
            self.total_records
        )

    def on_load_finished(self):
        self.loading_records = False

    def on_page_changed(self, page):
        self.page = page
        self.load_records()

    def on_page_size_changed(self, page_size):
        if page_size != self.page_size:
            self.page_size = page_size
            self.page = 1
            self.load_records()

    def select_a(self, analysis_id):
        if self.analysis_b == analysis_id:
            DialogUtil.warning(self, "A 和 B 不能重复")
            return

        self.analysis_a = analysis_id

        self.update_current_page_buttons()
        self.update_selection_label()

    def select_b(self, analysis_id):
        if self.analysis_a == analysis_id:
            DialogUtil.warning(self, "A 和 B 不能重复")
            return

        self.analysis_b = analysis_id

        self.update_current_page_buttons()
        self.update_selection_label()

    def update_current_page_buttons(self):
        for row in range(self.table.rowCount()):
            analysis_id = self.table.item(row, 0).text()

            btn_a = self.table.cellWidget(row, 4)
            btn_b = self.table.cellWidget(row, 5)

            # A
            if analysis_id == self.analysis_a:
                btn_a.setText("✓")
                btn_a.setStyleSheet("background:#4CAF50;color:white")
            else:
                btn_a.setText("A")
                btn_a.setStyleSheet("")

            # B
            if analysis_id == self.analysis_b:
                btn_b.setText("✓")
                btn_b.setStyleSheet("background:#4CAF50;color:white")
            else:
                btn_b.setText("B")
                btn_b.setStyleSheet("")

    def update_selection_label(self):
        a_text = self.analysis_a if self.analysis_a else "未选择"
        b_text = self.analysis_b if self.analysis_b else "未选择"

        self.selection_label.setText(
            f"Batch A: {a_text}    |    Batch B: {b_text}"
        )

    def on_record_deleted(self, deleted_id):
        changed = False

        if self.analysis_a == deleted_id:
            self.analysis_a = None
            changed = True

        if self.analysis_b == deleted_id:
            self.analysis_b = None
            changed = True

        if changed:
            self.update_selection_label()

    def compare_selected(self):
        if not self.analysis_a or not self.analysis_b:
            DialogUtil.warning(self, "请选择两条记录进行对比")
            return

        result = self.compare_controller.compare(self.analysis_a, self.analysis_b)

        if result["code"] != 0:
            DialogUtil.warning(self, result["msg"])
            return

        self.compare_data = result["data"]

        summary = self.compare_data["overall_summary"]
        text = (
            f"Batch Score: {summary['batch1_weighted_score']} → {summary['batch2_weighted_score']}\n"
            f"Weighted Difference: {summary['weighted_difference']}\n"
            f"Trend: {summary['trend']}"
        )
        self.summary_label.setText(text)
        self.btn_report.setEnabled(True)

    def open_report(self):
        dialog = CompareReportWindow(self.compare_data)
        dialog.exec()

    def on_error(self, message):
        DialogUtil.error(self, f"获取记录失败: {message}")

    def time_format(self, created_at):
        """将ISO格式的时间戳转换为本地时间并格式化显示"""
        local_tz = pytz.timezone('Asia/Shanghai')

        try:
            # 解析ISO格式的时间戳
            dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))

            # 如果时间是UTC，转换为本地时间
            if dt.tzinfo is not None:
                # 转换为本地时间
                local_dt = dt.astimezone(local_tz)
                # 格式化
                formatted_time = local_dt.strftime('%Y-%m-%d %H:%M:%S')
            else:
                # 如果没有时区信息，直接使用
                formatted_time = dt.strftime('%Y-%m-%d %H:%M:%S')
        except:
            # 解析失败时使用原始字符串
            formatted_time = created_at

        return formatted_time
