from datetime import datetime

import pytz
from PyQt6.QtCore import QThread, Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout,
    QLabel, QTableWidget,
    QTableWidgetItem,
    QHeaderView, QSpinBox, QPushButton, QComboBox, QHBoxLayout, QMessageBox
)

from frontend.components.score_dashboard import ScoreDashboard
from frontend.controllers.record_controller import RecordController
from frontend.core.analysis_detail_worker import AnalysisDetailWorker
from frontend.core.delete_record_worker import DeleteRecordWorker
from frontend.core.record_worker import RecordWorker
from frontend.utils.dialog_util import DialogUtil


class RecordPage(QWidget):
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
        header.setFont(font)

        layout.addWidget(self.table)

        # ==============================
        # 分页控件
        # ==============================
        pagination_layout = QHBoxLayout()

        # 上一页按钮
        self.prev_btn = QPushButton("上一页")
        self.prev_btn.clicked.connect(self.go_to_prev_page)
        self.prev_btn.setEnabled(False)  # 初始时禁用

        # 页码显示
        self.page_label = QLabel(f"第 {self.page} 页")
        self.page_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 下一页按钮
        self.next_btn = QPushButton("下一页")
        self.next_btn.clicked.connect(self.go_to_next_page)
        self.next_btn.setEnabled(False)  # 初始时禁用

        # 跳转页码输入
        self.jump_label = QLabel("跳转到:")
        self.jump_spinbox = QSpinBox()
        self.jump_spinbox.setRange(1, 1)  # 初始范围只有第1页
        self.jump_spinbox.setFixedWidth(50)
        self.jump_spinbox.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)
        self.jump_btn = QPushButton("Go")
        self.jump_btn.clicked.connect(self.jump_to_page)

        # 每页显示数量选择
        self.page_size_label = QLabel("每页显示:")
        self.page_size_combo = QComboBox()
        self.page_size_combo.addItems(["10", "20", "50"])
        self.page_size_combo.setCurrentText(str(self.page_size))
        self.page_size_combo.currentTextChanged.connect(self.on_page_size_changed)

        # 总记录数显示
        self.total_label = QLabel("共 0 条记录")

        pagination_layout.addWidget(self.prev_btn)
        pagination_layout.addWidget(self.page_label)
        pagination_layout.addWidget(self.next_btn)
        pagination_layout.addStretch()
        pagination_layout.addWidget(self.jump_label)
        pagination_layout.addWidget(self.jump_spinbox)
        pagination_layout.addWidget(self.jump_btn)
        pagination_layout.addStretch()
        pagination_layout.addWidget(self.page_size_label)
        pagination_layout.addWidget(self.page_size_combo)
        pagination_layout.addWidget(self.total_label)

        layout.addLayout(pagination_layout)

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

        self.loading_records = True

        # 禁用分页按钮，防止重复点击
        self.set_pagination_enabled(False)

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
            btn_delete.clicked.connect(lambda checked, rid=r["id"]: self.delete_record(rid))
            self.table.setCellWidget(row, 4, btn_delete)

        # 更新分页控件状态
        self.update_pagination_controls()

    def on_load_finished(self):
        """线程结束后重置状态"""
        self.loading_records = False
        self.set_pagination_enabled(True)

    def set_pagination_enabled(self, enabled):
        """设置分页控件的启用状态"""
        self.prev_btn.setEnabled(enabled and self.page > 1)
        self.next_btn.setEnabled(enabled and self.page < self.total_pages)
        self.jump_btn.setEnabled(enabled)
        self.jump_spinbox.setEnabled(enabled)
        self.page_size_combo.setEnabled(enabled)

    def update_pagination_controls(self):
        """更新分页控件显示"""
        self.page_label.setText(f"第 {self.page} 页 / 共 {self.total_pages} 页")
        self.total_label.setText(f"共 {self.total_records} 条记录")

        # 更新跳转输入框的范围
        self.jump_spinbox.setRange(1, self.total_pages)
        self.jump_spinbox.setValue(self.page)

        # 更新按钮状态
        self.prev_btn.setEnabled(self.page > 1)
        self.next_btn.setEnabled(self.page < self.total_pages)

    def go_to_prev_page(self):
        """前往上一页"""
        if self.page > 1:
            self.page -= 1
            self.load_records()

    def go_to_next_page(self):
        """前往下一页"""
        if self.page < self.total_pages:
            self.page += 1
            self.load_records()

    def jump_to_page(self):
        """跳转到指定页"""
        target_page = self.jump_spinbox.value()
        if target_page != self.page:
            self.page = target_page
            self.load_records()

    def on_page_size_changed(self, page_size_text):
        """每页显示数量改变"""
        new_page_size = int(page_size_text)
        if new_page_size != self.page_size:
            self.page_size = new_page_size
            self.page = 1  # 重置到第一页
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
