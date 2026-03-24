from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas


class ScrollableCanvas(FigureCanvas):

    def wheelEvent(self, event):
        parent = self.parent()
        while parent:
            if hasattr(parent, "verticalScrollBar"):
                parent.wheelEvent(event)
                return
            parent = parent.parent()

        super().wheelEvent(event)
