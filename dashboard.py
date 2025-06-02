import os
import sys

from PySide6.QtCore import QTimer, Qt, QSize
from PySide6.QtGui import QFont, QPixmap, QColor, QPainter, QFontMetrics, QIcon
from PySide6.QtWidgets import (QMainWindow, QApplication, QGridLayout, QScrollArea,
                               QWidget, QLabel, QVBoxLayout, QPushButton, QHBoxLayout,
                               QFrame, QSizePolicy, QLineEdit)


def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


class TitleBar(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.drag_start_position = None
        self.parent = parent
        self.setFixedSize(800, 40)
        self.setContentsMargins(0, 0, 0, 0)
        self.setStyleSheet("background-color: #2A2A40;")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        icon = QLabel()
        icon_pixmap = QPixmap(resource_path("assets/icon/ikon.ico")).scaled(20, 20, Qt.KeepAspectRatio,
                                                                       Qt.SmoothTransformation)
        icon.setPixmap(icon_pixmap)
        icon.setStyleSheet("padding-left: 10px")
        layout.addWidget(icon)

        text = QLabel("PASSWORD MANAGER")
        text.setStyleSheet("color: white; font-weight: bold; padding-left: 1px")
        layout.addWidget(text)

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout.addWidget(spacer)

        frame_min = QFrame()
        frame_min.setFrameShape(QFrame.NoFrame)
        frame_min.setStyleSheet("background-color: #2A2A40;")

        layout_min_frame = QVBoxLayout()
        layout_min_frame.setContentsMargins(0, 0, 0, 0)
        layout_min_frame.setAlignment(Qt.AlignmentFlag.AlignCenter)

        tombol_min = QPushButton("⛔️")
        tombol_min.setFixedSize(30, 30)
        tombol_min.setFont(QFont("Arial", 14))
        tombol_min.setStyleSheet("""
                            QPushButton {
                                color: white;
                                border: none;
                            }
                            QPushButton:hover {
                                background-color: #44475a;
                            }
                        """)
        tombol_min.clicked.connect(self.parent.showMinimized)
        layout_min_frame.addWidget(tombol_min)
        frame_min.setLayout(layout_min_frame)
        layout.addWidget(frame_min)

        frame_ex = QFrame()
        frame_ex.setFrameShape(QFrame.NoFrame)
        frame_ex.setStyleSheet("background-color: #2A2A40;")

        layout_ex_frame = QHBoxLayout()
        layout_ex_frame.setContentsMargins(0, 0, 5, 0)
        layout_ex_frame.setAlignment(Qt.AlignmentFlag.AlignCenter)

        tombol_ex = QPushButton("❌")
        tombol_ex.setFixedSize(30, 30)
        tombol_ex.setFont(QFont("Arial", 14))
        tombol_ex.setStyleSheet("""
                            QPushButton {
                                color: white;
                                border: none;
                            }
                            QPushButton:hover {
                                background-color: #44475a;
                            }
                        """)
        tombol_ex.clicked.connect(self.parent.close)
        layout_ex_frame.addWidget(tombol_ex)
        frame_ex.setLayout(layout_ex_frame)
        layout.addWidget(frame_ex)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_start_position = event.globalPosition().toPoint()
            if hasattr(self.parent, 'windowHandle') and self.parent.windowHandle():
                self.parent.windowHandle().startSystemMove()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.MouseButton.LeftButton:
            if hasattr(self, 'drag_start_position'):
                delta = event.globalPosition().toPoint() - self.drag_start_position
                self.parent.move(self.parent.pos() + delta)
                self.drag_start_position = event.globalPosition().toPoint()
                event.accept()


def bold_font():
    font = QFont()
    font.setBold(True)
    return font


def small_font():
    font = QFont()
    font.setPointSize(font.pointSize() - 2)
    return font


class BookCardWidget(QWidget):
    def __init__(self, book_data, parent=None):
        super().__init__(parent)
        self.book_data = book_data
        self.setFixedSize(180, 280)

        # --- Layout Utama ---
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(8)

        # --- Sampul Buku ---
        self.cover_label = QLabel()
        self.cover_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.cover_label.setFixedSize(164, 180)

        self.set_cover_image(self.book_data.get('sampul_url'))
        main_layout.addWidget(self.cover_label)

        # --- Informasi Buku ---
        self.info_container_widget = QWidget()
        info_layout = QVBoxLayout(self.info_container_widget)
        info_layout.setContentsMargins(5, 5, 5, 5)
        info_layout.setSpacing(8)

        # Judul
        judul = self.book_data.get('judul', 'Judul Tidak Tersedia')
        self.title_label = QLabel()
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.title_label.setWordWrap(True)
        self.title_label.setFont(bold_font())
        self.title_label.setStyleSheet("color: #222222;")

        # Hitung batas tinggi maksimal untuk 2 baris
        metrics = QFontMetrics(self.title_label.font())
        line_height = metrics.lineSpacing()
        max_height = line_height * 1

        # Potong teks agar tidak lebih dari 2 baris
        available_width = 150  # Sesuai dengan lebar cover atau container
        elided_text = metrics.elidedText(judul, Qt.TextElideMode.ElideRight, available_width * 1)
        self.title_label.setText(elided_text)
        self.title_label.setMaximumHeight(max_height)

        # Kode Pengarang
        self.author_code_label = QLabel(self.book_data.get('kode_pengarang', 'N/A'))
        self.author_code_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.author_code_label.setFont(small_font())
        self.author_code_label.setStyleSheet("color: #666666;")

        # Tahun Terbit
        self.year_label = QLabel(f"Tahun: {self.book_data.get('tahun_terbit', 'N/A')}")
        self.year_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.year_label.setFont(small_font())
        self.year_label.setStyleSheet("color: #666666;")

        # Tambahkan ke layout info
        info_layout.addWidget(self.title_label)
        info_layout.addWidget(self.author_code_label)
        info_layout.addWidget(self.year_label)
        info_layout.addStretch()

        main_layout.addWidget(self.info_container_widget)
        self.setLayout(main_layout)

        # Stylesheet kartu
        self.setStyleSheet("""
            QWidget {
                background-color: #ffffff;
                border: 1px solid #cccccc;
                border-radius: 10px;
            }
            QWidget:hover {
                border: 1px solid #0078d7;
                background-color: #f9f9f9;
            }
        """)

    def set_cover_image(self, url):
        if url:
            pixmap = QPixmap(url)
        else:
            pixmap = QPixmap()

        if not pixmap or pixmap.isNull():
            fallback_path = "assets/book/null.png"
            fallback_pixmap = QPixmap(fallback_path)
            if not fallback_pixmap.isNull():
                scaled = fallback_pixmap.scaled(self.cover_label.size(), Qt.AspectRatioMode.KeepAspectRatio,
                                                Qt.TransformationMode.SmoothTransformation)
                self.cover_label.setPixmap(scaled)
            else:
                placeholder = QPixmap(self.cover_label.size())
                placeholder.fill(QColor("#e0e0e0"))
                painter = QPainter(placeholder)
                painter.setPen(QColor("#888888"))
                painter.setFont(QFont("Arial", 10, QFont.Weight.Normal))
                painter.drawText(placeholder.rect(), Qt.AlignmentFlag.AlignCenter, "Sampul\nTidak Tersedia")
                painter.end()
                self.cover_label.setPixmap(placeholder)
        else:
            scaled = pixmap.scaled(self.cover_label.size(), Qt.AspectRatioMode.KeepAspectRatio,
                                   Qt.TransformationMode.SmoothTransformation)
            self.cover_label.setPixmap(scaled)

    def mousePressEvent(self, event):
        print(f"Kartu diklik: {self.book_data.get('judul')}")
        super().mousePressEvent(event)


def add_nav_button(layout, text, icon_path):
    button = QPushButton(QIcon(resource_path(icon_path)), text)
    button.setFixedSize(150, 40)
    button.setStyleSheet("""
        QPushButton {
            background-color: transparent;
            color: white;
            border: none;
            text-align: left;
            padding-left: 10px;
        }
        QPushButton:hover {
            background-color: #44475a;
            border-radius: 5px;
        }
    """)
    button.setFont(QFont("Arial", 10))
    button.setIconSize(QSize(20, 20)) # Adjust icon size
    layout.addWidget(button)


class SidebarWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(170)
        self.setStyleSheet("background-color: #2A2A40; border-radius: 10px;")
        self.setContentsMargins(0, 0, 0, 0)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 20, 10, 10)
        layout.setSpacing(10)

        # Search Bar
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: #44475a;
                color: white;
                border: 1px solid #555566;
                border-radius: 5px;
                padding: 5px 10px;
            }
            QLineEdit:focus {
                border: 1px solid #0078d7;
            }
        """)
        layout.addWidget(self.search_input)

        layout.addSpacing(20) # Add some space before buttons

        # Navigation Buttons
        add_nav_button(layout, "  Home", "assets/icon/home.png")
        add_nav_button(layout, "  Add New", "assets/icon/add.png")
        add_nav_button(layout, "  Categories", "assets/icon/category.png")
        add_nav_button(layout, "  Settings", "assets/icon/settings.png")
        add_nav_button(layout, "  About", "assets/icon/info.png")

        layout.addStretch()


class HalamanUtama(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Window)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(800, 600)

        self.container = QWidget()
        self.container.setStyleSheet("background-color: #2A2A40; border-radius: 10px;")
        self.setCentralWidget(self.container)

        wrapper_layout = QVBoxLayout(self.container)
        wrapper_layout.setContentsMargins(0, 0, 0, 0)
        wrapper_layout.setSpacing(0)

        # Title bar
        self.title_bar = TitleBar(self)
        wrapper_layout.addWidget(self.title_bar)

        # Main horizontal layout for sidebar and content
        self.main_h_layout = QHBoxLayout()
        self.main_h_layout.setContentsMargins(0, 0, 0, 0)
        self.main_h_layout.setSpacing(0)

        # Sidebar
        self.sidebar = SidebarWidget(self)
        self.main_h_layout.addWidget(self.sidebar)

        # Area utama untuk konten (termasuk buku)
        self.main_content_area = QWidget()
        main_content_layout = QVBoxLayout(self.main_content_area)
        main_content_layout.setContentsMargins(13, 0, 15, 15)
        main_content_layout.setSpacing(10)

        # ScrollArea for book grid
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet(
            "QScrollArea { border: none; background-color: transparent; }")

        self.scroll_content_widget = QWidget()
        self.scroll_area.setWidget(self.scroll_content_widget)
        self.scroll_content_widget.setStyleSheet("background-color: #282838;")

        self.grid_layout = QGridLayout(self.scroll_content_widget)
        self.grid_layout.setSpacing(15)
        self.grid_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        main_content_layout.addWidget(self.scroll_area)

        self.main_h_layout.addWidget(self.main_content_area)
        wrapper_layout.addLayout(self.main_h_layout)


        QTimer.singleShot(100, self.load_initial_books)

    def load_initial_books(self):
        dummy_books = [
            {'judul': 'Belajar PySide6 dari Nol hingga Mahir Sekali', 'kode_pengarang': 'PEN001',
             'tahun_terbit': '2023', 'sampul_url': ''},
            {'judul': 'FastAPI untuk Backend Andal', 'kode_pengarang': 'PEN002', 'tahun_terbit': '2022',
             'sampul_url': ''},
            {'judul': 'Desain UI/UX Modern', 'kode_pengarang': 'PEN003', 'tahun_terbit': '2024',
             'sampul_url': 'path/to/your/sample_cover1.jpg'},
            {'judul': 'Algoritma dan Struktur Data', 'kode_pengarang': 'PEN004', 'tahun_terbit': '2021',
             'sampul_url': ''},
            {'judul': 'Pemrograman Paralel dengan Python', 'kode_pengarang': 'PEN005', 'tahun_terbit': '2023',
             'sampul_url': 'path/to/your/sample_cover2.jpg'},
            {'judul': 'Kecerdasan Buatan Terapan', 'kode_pengarang': 'PEN006', 'tahun_terbit': '2024'},
            {'judul': 'Manajemen Proyek Agile', 'kode_pengarang': 'PEN007', 'tahun_terbit': '2022'},
            {'judul': 'Basis Data NoSQL', 'kode_pengarang': 'PEN008', 'tahun_terbit': '2023'},
        ]
        self.display_books(dummy_books)

    def display_books(self, books_data):
        while self.grid_layout.count():
            child = self.grid_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        num_columns = max(1, self.scroll_content_widget.width() // (180 + 15))

        for index, book_item_data in enumerate(books_data):
            card = BookCardWidget(book_item_data)
            row = index // num_columns
            col = index % num_columns
            self.grid_layout.addWidget(card, row, col)

        self.scroll_content_widget.setLayout(self.grid_layout)

    def fetch_and_display_books(self):
        print("Fungsi fetch_and_display_books() perlu diimplementasikan untuk mengambil data dari API.")
        self.load_initial_books()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = HalamanUtama()
    main_window.show()
    sys.exit(app.exec())
