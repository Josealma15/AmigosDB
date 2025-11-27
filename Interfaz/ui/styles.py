def load_styles():
    return """
        QWidget {
            background-color: #f3f4f6;
            font-family: 'Segoe UI';
            font-size: 14px;
        }

        QTabWidget::pane {
            border: 2px solid #9ca3af;
            background: #e5e7eb;
            border-radius: 8px;
        }

        QTabBar::tab {
            background: #9ca3af;
            color: white;
            padding: 8px;
            border-top-left-radius: 6px;
            border-top-right-radius: 6px;
            margin-right: 2px;
        }
        QTabBar::tab:selected {
            background: #1f2937;
            font-weight: bold;
        }

        QLineEdit, QComboBox {
            background: white;
            padding: 6px;
            border: 1px solid #9ca3af;
            border-radius: 6px;
        }

        QPushButton {
            background-color: #10b981;
            color: white;
            border-radius: 6px;
            padding: 8px;
            font-size: 14px;
        }
        QPushButton:hover {
            background-color: #059669;
        }

        QTableWidget {
            background: white;
            border: 2px solid #6b7280;
            border-radius: 6px;
        }

        QHeaderView::section {
            background-color: #1f2937;
            color: white;
            padding: 5px;
            font-size: 14px;
        }
    """
