from datetime import datetime
from functools import partial

import pytz
from PyQt6.QtCore import QThread, Qt, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout,
    QLabel, QTableWidget,
    QTableWidgetItem,
    QHeaderView, QPushButton, QMessageBox
)

from frontend.components.pagination import Pagination
from frontend.components.score_dashboard import ScoreDashboard
from frontend.controllers.record_controller import RecordController
from frontend.core.analysis_detail_worker import AnalysisDetailWorker
from frontend.core.delete_record_worker import DeleteRecordWorker
from frontend.core.record_worker import RecordWorker
from frontend.utils.dialog_util import DialogUtil


class RecordPage(QWidget):
    record_deleted = pyqtSignal(str)

    def __init__(self):
        super().__init__()

        self.page = 1
        self.page_size = 10

        self.controller = RecordController()

        # 防重复请求
        self.loading_records = False
        self.loading_detail = False

        # 当前选中的记录
        self.current_analysis_id = None

        layout = QVBoxLayout()

        title = QLabel("历史分析记录")
        title.setObjectName("pageTitle")
        layout.addWidget(title)

        # ==============================
        # 历史记录表格
        # ==============================
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(
            ["ID", "文件数量", "创建时间", "状态", "操作"]
        )

        # 禁止编辑
        self.table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )
        # 整行选中（自动高亮）
        self.table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        # 一次只选中一行
        self.table.setSelectionMode(
            QTableWidget.SelectionMode.SingleSelection
        )
        # 去掉方框焦点
        self.table.setFocusPolicy(
            Qt.FocusPolicy.NoFocus
        )

        self.table.setStyleSheet("""
            QTableWidget::item:selected {
                background-color: #3399FF;    /* 高亮背景色 */
                color: white;                 /* 高亮文字颜色 */
            }
            QTableWidget::item {
                border: none;                 /* 移除每个格子前的蓝线 */
            }
        """)

        # 监听点击事件
        self.table.cellClicked.connect(self.on_record_clicked)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)

        font = QFont()
        font.setBold(True)
        font.setPointSize(10)
        header.setFont(font)

        layout.addWidget(self.table)

        # ==============================
        # 分页控件
        # ==============================
        self.pagination = Pagination(self.page, self.page_size)
        self.pagination.page_changed.connect(self.on_page_changed)
        self.pagination.page_size_changed.connect(self.on_page_size_changed)

        layout.addWidget(self.pagination)

        # 这里是空隙
        layout.addSpacing(30)

        # ==============================
        # 分析记录展示区域
        # ==============================
        self.dashboard = ScoreDashboard()
        layout.addWidget(self.dashboard)

        self.setLayout(layout)

        # 初始化加载
        self.load_records()

    def load_records(self):
        """加载记录"""
        if self.loading_records:
            return

        self.table.clearSelection()

        self.loading_records = True

        self.record_thread = QThread()
        self.worker = RecordWorker(
            self.controller,
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
        """数据加载完成"""
        if result.get("code") != 0:
            DialogUtil.error(self, result.get("msg"))
            return

        data = result["data"]
        records = data["records"]

        # 更新分页信息
        self.page = data["page"]
        self.page_size = data["page_size"]
        self.total_records = data.get("total", 0)

        # 计算总页数
        if self.total_records > 0:
            self.total_pages = (self.total_records + self.page_size - 1) // self.page_size
        else:
            self.total_pages = 1

        self.table.setRowCount(len(records))

        for row, r in enumerate(records):
            formatted_time = self.time_format(r["created_at"])

            self.table.setItem(row, 0, QTableWidgetItem(r["id"]))
            self.table.setItem(row, 1, QTableWidgetItem(str(r["file_count"])))
            self.table.setItem(row, 2, QTableWidgetItem(formatted_time))
            self.table.setItem(row, 3, QTableWidgetItem(r["status"]))

            btn_delete = QPushButton("删除")
            btn_delete.clicked.connect(
                partial(self.delete_record, r["id"])
            )
            self.table.setCellWidget(row, 4, btn_delete)

        self.pagination.update_pagination(
            self.page,
            self.total_pages,
            self.total_records
        )

        # 重置选择高亮
        self.restore_selection()

    def on_load_finished(self):
        """线程结束后重置状态"""
        self.loading_records = False

    def restore_selection(self):
        """根据 analysis_id 恢复选中状态"""
        if not self.current_analysis_id:
            return

        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)

            if not item:
                continue

            if item.text() == self.current_analysis_id:
                self.table.selectRow(row)
                return

        # 当前页没有该记录则取消选中
        self.table.clearSelection()

    def on_page_changed(self, page):
        self.page = page
        self.load_records()

    def on_page_size_changed(self, page_size):
        if page_size != self.page_size:
            self.page_size = page_size
            self.page = 1
            self.load_records()

    def on_record_clicked(self, row, column):
        """点击记录"""
        item = self.table.item(row, 0)

        if not item:
            return

        analysis_id = item.text()

        # 防止重复点击正在加载或已加载完的的记录
        if self.loading_detail or analysis_id == self.current_analysis_id:
            return

        self.current_analysis_id = analysis_id
        self.load_analysis_detail(analysis_id)

    def load_analysis_detail(self, analysis_id):
        """加载分析详情"""
        self.loading_detail = True

        self.detail_thread = QThread()
        self.worker = AnalysisDetailWorker(
            self.controller,
            analysis_id
        )
        self.worker.moveToThread(self.detail_thread)

        self.detail_thread.started.connect(self.worker.run)

        self.worker.finished.connect(self.on_analysis_loaded)
        self.worker.error.connect(self.on_error)

        # 正常结束
        self.worker.finished.connect(self.detail_thread.quit)
        # 出错也结束线程
        self.worker.error.connect(self.detail_thread.quit)

        # 清理对象
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker.error.connect(self.worker.deleteLater)

        self.detail_thread.finished.connect(self.detail_thread.deleteLater)
        self.detail_thread.finished.connect(self.on_detail_load_finished)

        self.detail_thread.start()

    def on_analysis_loaded(self, result):
        """加载完成更新dashboard"""
        if result.get("code") != 0:
            DialogUtil.error(self, result.get("msg", "获取分析失败"))
            return

        data = result["data"]
        self.dashboard.update_score(data)

    def on_detail_load_finished(self):
        """线程结束后隐藏LoadingOverlay并重置状态"""
        self.loading_detail = False

    def delete_record(self, analysis_id):
        reply = QMessageBox.question(
            self,
            "删除确认",
            f"确定要删除记录 {analysis_id} 吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.No:
            return

        # 记录删除的id，用于回调
        self.deleted_analysis_id = analysis_id

        self.delete_thread = QThread()
        self.worker = DeleteRecordWorker(
            self.controller,
            analysis_id
        )
        self.worker.moveToThread(self.delete_thread)

        self.delete_thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.on_record_deleted)
        self.worker.error.connect(self.on_error)

        self.worker.finished.connect(self.delete_thread.quit)
        self.worker.error.connect(self.delete_thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.delete_thread.finished.connect(self.delete_thread.deleteLater)

        self.delete_thread.start()

    def on_record_deleted(self, result):
        """点击删除按钮"""
        if result.get("code") != 0:
            DialogUtil.error(self, result.get("msg"))
            return

        deleted_id = getattr(self, "deleted_analysis_id", None)
        if deleted_id:
            # 发出记录删除信号，通知其他组件更新
            self.record_deleted.emit(deleted_id)

        # 如果删除的是当前选中的记录可能导致状态异常
        self.current_analysis_id = None

        # 清空dashboard
        self.dashboard.reset()

        # 清空表格选中
        self.table.clearSelection()

        # 重新加载
        self.load_records()

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
