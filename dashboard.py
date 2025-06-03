import json
import os
import sys

from PySide6.QtCore import QTimer, Qt, QSize, QUrl
from PySide6.QtGui import QFont, QPixmap, QColor, QPainter, QFontMetrics, QIcon
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from PySide6.QtWidgets import (QMainWindow, QApplication, QGridLayout, QScrollArea,
                               QWidget, QLabel, QVBoxLayout, QPushButton, QHBoxLayout,
                               QFrame, QSizePolicy, QLineEdit, QGraphicsDropShadowEffect)


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

        text = QLabel("E-PERPUSTAKAAN NASIONAL")
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
            # Check if windowHandle exists and is valid
            if hasattr(self.parent, 'windowHandle') and self.parent.windowHandle():
                self.parent.windowHandle().startSystemMove()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.MouseButton.LeftButton and self.drag_start_position is not None:
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

        self.image_nam = QNetworkAccessManager()
        self.image_nam.finished.connect(self._on_image_reply)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(8)

        self.cover_label = QLabel()
        self.cover_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.cover_label.setFixedSize(164, 180)
        self.set_cover_image(self.book_data.get('sampul_url'))
        main_layout.addWidget(self.cover_label)

        self.info_container_widget = QWidget()
        info_layout = QVBoxLayout(self.info_container_widget)
        info_layout.setContentsMargins(5, 5, 5, 5)
        info_layout.setSpacing(4)  # Reduced spacing for tighter info

        judul = self.book_data.get('judul', 'Judul Tidak Tersedia')
        self.title_label = QLabel()
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.title_label.setFont(bold_font())
        self.title_label.setStyleSheet("color: #222222;")
        self.title_label.setFixedHeight(QFontMetrics(self.title_label.font()).height() * 1.6)
        self.title_label.setWordWrap(False)
        self.title_label.setToolTip(judul)
        self.title_label.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)

        metrics = QFontMetrics(self.title_label.font())
        elided_title = metrics.elidedText(judul, Qt.TextElideMode.ElideRight, 150)
        self.title_label.setText(elided_title)

        self.author_code_label = QLabel(self.book_data.get('kode_pengarang', 'N/A'))
        self.author_code_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.author_code_label.setFont(small_font())
        self.author_code_label.setStyleSheet("color: #666666;")
        self.author_code_label.setWordWrap(True)  # Allow author to wrap

        self.year_label = QLabel(f"Tahun: {self.book_data.get('tahun_terbit', 'N/A')}")
        self.year_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.year_label.setFont(small_font())
        self.year_label.setStyleSheet("color: #666666;")

        info_layout.addWidget(self.title_label)
        info_layout.addWidget(self.author_code_label)
        info_layout.addWidget(self.year_label)
        info_layout.addStretch()

        main_layout.addWidget(self.info_container_widget)
        self.setLayout(main_layout)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(15)
        shadow.setOffset(0, 3)
        shadow.setColor(QColor(0, 0, 0, 100))
        self.setGraphicsEffect(shadow)

        self.setStyleSheet("""
            QWidget {
                background-color: #ffffff;
                border: 1px solid #cccccc;
                border-radius: 10px;
            }
            QWidget:hover {
                border: 1px solid #0078d7; /* Highlight border on hover */
                background-color: #f9f9f9; /* Slightly change background on hover */
            }
        """)

    def _load_fallback_image(self):
        """Loads a fallback image or placeholder."""
        fallback_path = resource_path("assets/book/null.png")
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

    def set_cover_image(self, url_string):
        if url_string and url_string.startswith("http"):
            url = QUrl(url_string)
            request = QNetworkRequest(url)
            self.image_nam.get(request)
        else:
            pixmap = QPixmap(url_string)
            if not pixmap.isNull():
                scaled = pixmap.scaled(self.cover_label.size(), Qt.AspectRatioMode.KeepAspectRatio,
                                       Qt.TransformationMode.SmoothTransformation)
                self.cover_label.setPixmap(scaled)
            else:
                self._load_fallback_image()

    def _on_image_reply(self, reply):
        if reply.error() == QNetworkReply.NoError:
            image_data = reply.readAll()
            pixmap = QPixmap()
            pixmap.loadFromData(image_data)
            if not pixmap.isNull():
                scaled = pixmap.scaled(self.cover_label.size(), Qt.AspectRatioMode.KeepAspectRatio,
                                       Qt.TransformationMode.SmoothTransformation)
                self.cover_label.setPixmap(scaled)
            else:
                print(f"Gagal memuat gambar dari data untuk: {self.book_data.get('judul')}")
                self._load_fallback_image()
        else:
            print(f"Network error saat mengambil gambar: {reply.errorString()} untuk {self.book_data.get('judul')}")
            self._load_fallback_image()
        reply.deleteLater()

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
            padding-left: 10px; /* Padding for text from icon */
        }
        QPushButton:hover {
            background-color: #44475a; /* Darker background on hover */
            border-radius: 5px;
        }
    """)
    button.setFont(QFont("Arial", 10))
    button.setIconSize(QSize(20, 20))
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
                border: 1px solid #0078d7; /* Highlight border when focused */
            }
        """)
        layout.addWidget(self.search_input)

        layout.addSpacing(20)

        add_nav_button(layout, "  Home", "assets/icon/home.png")
        add_nav_button(layout, "  Add New", "assets/icon/add.png")
        add_nav_button(layout, "  Categories", "assets/icon/category.png")
        add_nav_button(layout, "  Settings", "assets/icon/settings.png")
        add_nav_button(layout, "  About", "assets/icon/info.png")

        layout.addStretch()


class HalamanUtama(QMainWindow):
    BASE_API_URL = "http://127.0.0.1:8000"

    def __init__(self):

        self.current_page = 1
        self.total_pages = 1
        self.books_per_page = 9

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

        self.title_bar = TitleBar(self)
        wrapper_layout.addWidget(self.title_bar)

        self.main_h_layout = QHBoxLayout()
        self.main_h_layout.setContentsMargins(0, 0, 0, 0)
        self.main_h_layout.setSpacing(0)

        self.sidebar = SidebarWidget(self)
        self.main_h_layout.addWidget(self.sidebar)

        self.main_content_area = QWidget()
        main_content_layout = QVBoxLayout(self.main_content_area)
        main_content_layout.setContentsMargins(13, 0, 15, 15)
        main_content_layout.setSpacing(10)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet(
            "QScrollArea { border: none; background-color: transparent; }")

        self.scroll_content_widget = QWidget()
        self.scroll_area.setWidget(self.scroll_content_widget)
        self.scroll_content_widget.setStyleSheet("background-color: #1F1F30;")

        self.grid_layout = QGridLayout(self.scroll_content_widget)
        self.grid_layout.setSpacing(15)
        self.grid_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        main_content_layout.addWidget(self.scroll_area)

        self.pagination_layout = QHBoxLayout()
        self.pagination_layout.setContentsMargins(0, 0, 0, 0)
        self.pagination_layout.setSpacing(10)
        self.pagination_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.prev_button = QPushButton("« Sebelumnya")
        self.prev_button.clicked.connect(self.prev_page)
        self.next_button = QPushButton("Berikutnya »")
        self.next_button.clicked.connect(self.next_page)
        self.page_label = QLabel("Halaman 1 dari 1")
        self.page_label.setStyleSheet("color: white;")

        for btn in [self.prev_button, self.next_button]:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #44475a;
                    color: white;
                    padding: 5px 10px;
                    border: none;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #5a5a7a;
                }
            """)

        self.pagination_layout.addWidget(self.prev_button)
        self.pagination_layout.addWidget(self.page_label)
        self.pagination_layout.addWidget(self.next_button)

        main_content_layout.addLayout(self.pagination_layout)

        self.main_h_layout.addWidget(self.main_content_area)
        wrapper_layout.addLayout(self.main_h_layout)

        self.nam = QNetworkAccessManager()
        self.nam.finished.connect(self.on_book_list_reply)

        QTimer.singleShot(100, self.fetch_books_from_api)

    def fetch_books_from_api(self, page=None):
        if page is not None:
            self.current_page = page
        skip = (self.current_page - 1) * self.books_per_page
        url = QUrl(f"{self.BASE_API_URL}/books/list/all?skip={skip}&limit={self.books_per_page}")
        request = QNetworkRequest(url)
        print(f"Requesting book list from: {url.toString()}")
        self.nam.get(request)

    def on_book_list_reply(self, reply):
        """Handles the reply for the book list request."""
        if reply.error() == QNetworkReply.NoError:
            data = bytes(reply.readAll()).decode('utf-8')
            try:
                parsed = json.loads(data)
                books_json = parsed.get("items", [])
                total_books = parsed.get("total", 0)

                self.total_pages = (total_books + self.books_per_page - 1) // self.books_per_page

                transformed_books = []
                for book_api in books_json:
                    cover_path = book_api.get('cover', '')
                    full_cover_url = f"{self.BASE_API_URL}{cover_path}" if cover_path.startswith('/') else cover_path

                    transformed_books.append({
                        'judul': book_api.get('name', 'Judul Tidak Tersedia'),
                        'kode_pengarang': book_api.get('author', 'Pengarang Tidak Diketahui'),
                        'tahun_terbit': book_api.get('date', '----').split('-')[0] if book_api.get('date') else 'N/A',
                        'sampul_url': full_cover_url
                    })
                self.display_books(transformed_books)

                self.page_label.setText(f"Halaman {self.current_page} dari {self.total_pages}")
                self.prev_button.setEnabled(self.current_page > 1)
                self.next_button.setEnabled(self.current_page < self.total_pages)

            except json.JSONDecodeError as e:
                print(f"Error decoding JSON: {e}")
                self.display_books([])
            except Exception as e:
                print(f"An unexpected error occurred during book processing: {e}")
                self.display_books([])
        else:
            print(f"Network error fetching book list: {reply.errorString()}")
            self.display_books([])
        reply.deleteLater()

    def next_page(self):
        if self.current_page < self.total_pages:
            self.fetch_books_from_api(self.current_page + 1)

    def prev_page(self):
        if self.current_page > 1:
            self.fetch_books_from_api(self.current_page - 1)

    def display_books(self, books_data):
        while self.grid_layout.count():
            child = self.grid_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        if not books_data:
            no_books_label = QLabel("Tidak ada buku untuk ditampilkan.")
            no_books_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            no_books_label.setStyleSheet("color: white; font-size: 16px;")
            self.grid_layout.addWidget(no_books_label, 0, 0, 1, -1)
            return

        content_width = self.scroll_content_widget.width()
        card_width_plus_spacing = 180 + self.grid_layout.spacing()

        if content_width <= 0:
            num_columns = 3
        else:
            num_columns = max(1, content_width // card_width_plus_spacing)

        for index, book_item_data in enumerate(books_data):
            card = BookCardWidget(book_item_data)
            row = index // num_columns
            col = index % num_columns
            self.grid_layout.addWidget(card, row, col)

        self.scroll_content_widget.setLayout(self.grid_layout)
        self.scroll_content_widget.adjustSize()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = HalamanUtama()
    main_window.show()
    sys.exit(app.exec())
