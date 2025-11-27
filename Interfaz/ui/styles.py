def load_styles():
    return """
        /* ============================================================
           GLOBAL STYLES
           ============================================================ */
        
        QWidget {
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 35px;
            color: #1e293b;
        }
        
        QMainWindow {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                       stop:0 #667eea, stop:0.5 #764ba2, stop:1 #f093fb);
        }

        /* ============================================================
           TAB WIDGET STYLES
           ============================================================ */
        
        QTabWidget {
            background: transparent;
        }

        QTabWidget::pane {
            border: 2px solid #cbd5e1;
            background: rgba(255, 255, 255, 0.6); /* Semi-transparent to show gradient */
            border-radius: 12px;
            padding: 10px;
        }

        QTabBar::tab {
            background: rgba(255, 255, 255, 0.7);
            color: #475569;
            padding: 18px 40px;
            border-top-left-radius: 12px;
            border-top-right-radius: 12px;
            margin-right: 8px;
            font-weight: bold;
            font-size: 22px;
        }
        
        QTabBar::tab:selected {
            background: #3b82f6;
            color: white;
        }
        
        QTabBar::tab:hover:!selected {
            background: rgba(255, 255, 255, 0.9);
        }

        /* ============================================================
           INPUT FIELDS
           ============================================================ */
        
        QLineEdit, QComboBox {
            background: white;
            padding: 16px 20px;
            border: 2px solid #cbd5e1;
            border-radius: 12px;
            font-size: 35px;
            color: #1e293b;
        }
        
        QLineEdit:focus, QComboBox:focus {
            border: 3px solid #3b82f6;
            background: #f8fafc;
        }
        
        QComboBox::drop-down {
            border: none;
            padding-right: 10px;
        }
        
        QComboBox::down-arrow {
            image: none;
            border-left: 8px solid transparent;
            border-right: 8px solid transparent;
            border-top: 10px solid #64748b;
            margin-right: 12px;
        }

        /* ============================================================
           BUTTONS
           ============================================================ */
        
        QPushButton {
            background-color: #3b82f6;
            color: white;
            border-radius: 12px;
            padding: 16px 32px;
            font-size: 35px;
            font-weight: bold;
            border: none;
            min-height: 60px;
        }
        
        QPushButton:hover {
            background-color: #2563eb;
        }
        
        QPushButton:pressed {
            background-color: #1d4ed8;
        }
        
        QPushButton:disabled {
            background-color: #cbd5e1;
            color: #94a3b8;
        }
        
        /* Success Button */
        QPushButton[class="success"] {
            background-color: #10b981;
        }
        
        QPushButton[class="success"]:hover {
            background-color: #059669;
        }
        
        /* Danger Button */
        QPushButton[class="danger"] {
            background-color: #ef4444;
        }
        
        QPushButton[class="danger"]:hover {
            background-color: #dc2626;
        }
        
        /* Warning Button */
        QPushButton[class="warning"] {
            background-color: #f59e0b;
        }
        
        QPushButton[class="warning"]:hover {
            background-color: #d97706;
        }
        
        /* Secondary Button */
        QPushButton[class="secondary"] {
            background-color: #64748b;
        }
        
        QPushButton[class="secondary"]:hover {
            background-color: #475569;
        }

        /* ============================================================
           TABLES
           ============================================================ */
        
        QTableWidget {
            background: rgba(255, 255, 255, 0.9);
            border: 2px solid #e2e8f0;
            border-radius: 12px;
            gridline-color: #f3f4f6;
            selection-background-color: #e9d5ff;
            selection-color: #4c1d95;
            alternate-background-color: #faf5ff;
            font-size: 22px;
        }

        QHeaderView::section {
            background-color: #8b5cf6;
            color: white;
            padding: 18px 14px;
            font-size: 35px;
            font-weight: bold;
            border: none;
            border-right: 1px solid #7c3aed;
        }
        
        QHeaderView::section:first {
            border-top-left-radius: 10px;
        }
        
        QHeaderView::section:last {
            border-top-right-radius: 10px;
            border-right: none;
        }
        
        QTableWidget::item {
            padding: 12px;
            border-bottom: 1px solid #f3f4f6;
        }
        
        QTableWidget::item:selected {
            background-color: #e9d5ff;
            color: #4c1d95;
        }

        /* ============================================================
           LABELS
           ============================================================ */
        
        QLabel {
            color: #1e293b;
            font-size: 35px;
            background: transparent;
        }
        
        QLabel[class="title"] {
            font-size: 42px;
            font-weight: bold;
            color: #1e293b;
            padding: 20px 0;
        }
        
        QLabel[class="subtitle"] {
            font-size: 28px;
            font-weight: 600;
            color: #475569;
            padding: 14px 0;
        }
        
        QLabel[class="description"] {
            font-size: 22px;
            color: #64748b;
            font-style: italic;
        }
        
        QLabel[class="section-title"] {
            font-size: 28px;
            font-weight: bold;
            color: #1e293b;
            padding: 22px 0 14px 0;
        }

        /* ============================================================
           FRAMES AND SEPARATORS
           ============================================================ */
        
        QFrame[frameShape="4"] {  /* HLine */
            background-color: #e2e8f0;
            max-height: 3px;
            margin: 16px 0;
        }
        
        QFrame[frameShape="5"] {  /* VLine */
            background-color: #e2e8f0;
            max-width: 3px;
            margin: 0 16px;
        }

        /* ============================================================
           SCROLLBARS
           ============================================================ */
        
        QScrollBar:vertical {
            border: none;
            background: #f1f5f9;
            width: 18px;
            border-radius: 9px;
        }
        
        QScrollBar::handle:vertical {
            background: #cbd5e1;
            border-radius: 9px;
            min-height: 30px;
        }
        
        QScrollBar::handle:vertical:hover {
            background: #94a3b8;
        }
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            height: 0px;
        }
        
        QScrollBar::horizontal {
            border: none;
            background: #f1f5f9;
            height: 18px;
            border-radius: 9px;
        }
        
        QScrollBar::handle:horizontal {
            background: #cbd5e1;
            border-radius: 9px;
            min-width: 30px;
        }
        
        QScrollBar::handle:horizontal:hover {
            background: #94a3b8;
        }
        
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
            width: 0px;
        }

        /* ============================================================
           MESSAGE BOXES
           ============================================================ */
        
        QMessageBox {
            background-color: white;
        }
        
        QMessageBox QPushButton {
            min-width: 120px;
        }
    """
