import sys
import tempfile
import urllib.request
from pathlib import Path
from typing import Optional, Dict, Any
from enum import Enum

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFileDialog, QMessageBox, QProgressBar,
    QCheckBox, QSizePolicy, QFrame, QSplitter
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QPropertyAnimation, QEasingCurve, QRect, QUrl
from PyQt6.QtGui import QPixmap, QFont, QColor
from PyQt6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply

from analyzer import analyze_image
from namer import generate_name


class Theme(Enum):
    LIGHT = "light"
    DARK = "dark"


class ThemeManager:
    LIGHT_COLORS = {
        "bg_primary": "#e8eef4", "bg_secondary": "#f0f4f8", "bg_tertiary": "#dbe4ec",
        "border": "#cbd5e1", "border_focus": "#006699",
        "text_primary": "#0f172a", "text_secondary": "#334155", "text_muted": "#64748b",
        "accent": "#006699", "accent_hover": "#005580", "accent_pressed": "#004466",
        "accent_light": "#eef5fa", "success": "#059669", "error": "#dc2626",
        "card_bg": "#ffffff", "card_border": "#e2e8f0",
        "drop_idle_border": "#cbd5e1", "drop_idle_bg": "#f1f5f9",
        "drop_active_border": "#006699", "drop_active_bg": "#eef5fa",
        "drop_loaded_border": "#e2e8f0", "drop_loaded_bg": "#ffffff",
    }
    DARK_COLORS = {
        "bg_primary": "#050a14", "bg_secondary": "#0a1220", "bg_tertiary": "#121a2e",
        "border": "#1e2a3e", "border_focus": "#3b82f6",
        "text_primary": "#f8fafc", "text_secondary": "#e2e8f0", "text_muted": "#94a3b8",
        "accent": "#3b82f6", "accent_hover": "#60a5fa", "accent_pressed": "#2563eb",
        "accent_light": "#121a2e", "success": "#10b981", "error": "#ef4444",
        "card_bg": "#0a1220", "card_border": "#1e2a3e",
        "drop_idle_border": "#1e2a3e", "drop_idle_bg": "#0a1220",
        "drop_active_border": "#3b82f6", "drop_active_bg": "#121a2e",
        "drop_loaded_border": "#1e2a3e", "drop_loaded_bg": "#0a1220",
    }

    def __init__(self):
        self._theme = Theme.LIGHT
        self._colors = self.LIGHT_COLORS.copy()

    @property
    def theme(self) -> Theme:
        return self._theme

    @property
    def colors(self) -> Dict[str, str]:
        return self._colors

    def toggle(self):
        self._theme = Theme.DARK if self._theme == Theme.LIGHT else Theme.LIGHT
        self._colors = self.DARK_COLORS.copy() if self._theme == Theme.DARK else self.LIGHT_COLORS.copy()

    def get(self, key: str) -> str:
        return self._colors.get(key, "#000000")

    def stylesheet(self) -> str:
        c = self._colors
        return f"""
            QMainWindow {{ background-color: {c["bg_primary"]}; }}
            QWidget#centralWidget {{ background-color: {c["bg_primary"]}; }}
            QWidget {{ color: {c["text_primary"]}; }}
            QFrame {{ background-color: transparent; }}
            QLabel {{ background-color: transparent; color: {c["text_primary"]}; }}
            QCheckBox {{ spacing: 8px; color: {c["text_secondary"]}; }}
            QCheckBox::indicator {{ width: 18px; height: 18px; border: 2px solid {c["border"]}; border-radius: 4px; background: {c["bg_primary"]}; }}
            QCheckBox::indicator:checked {{ background-color: {c["accent"]}; border-color: {c["accent"]}; }}
            QCheckBox::indicator:hover {{ border-color: {c["accent"]}; }}
            QPushButton {{ background-color: {c["bg_tertiary"]}; color: {c["text_primary"]}; border: 1px solid {c["border"]}; border-radius: 8px; padding: 8px 20px; font-weight: 500; font-size: 13px; }}
            QPushButton:hover {{ background-color: {c["border"]}; border-color: {c["border"]}; }}
            QPushButton:pressed {{ background-color: {c["accent_light"]}; }}
            QPushButton:disabled {{ background-color: {c["bg_secondary"]}; color: {c["text_muted"]}; border-color: {c["bg_tertiary"]}; }}
            QPushButton[primary="true"] {{ background-color: {c["accent"]}; color: white; border-color: {c["accent"]}; }}
            QPushButton[primary="true"]:hover {{ background-color: {c["accent_hover"]}; border-color: {c["accent_hover"]}; }}
            QPushButton[primary="true"]:pressed {{ background-color: {c["accent_pressed"]}; border-color: {c["accent_pressed"]}; }}
            QProgressBar {{ border: none; background-color: {c["bg_tertiary"]}; border-radius: 1.5px; }}
            QProgressBar::chunk {{ background-color: {c["accent"]}; border-radius: 1.5px;}}
            QSplitter::handle {{ background-color: {c["border"]}; width: 1px; margin-left: 10px; }}
            QScrollArea {{ border: none; background-color: transparent; }}
            QScrollBar:vertical {{ background: {c["bg_secondary"]}; width: 8px; border-radius: 4px; }}
            QScrollBar::handle:vertical {{ background: {c["border"]}; border-radius: 4px; min-height: 30px; }}
            QScrollBar::handle:vertical:hover {{ background: {c["text_muted"]}; }}
            QMessageBox {{ background-color: {c["card_bg"]};}}
            QMessageBox QLabel {{ color: {c["text_primary"]}; }}
        """

    def apply_to_app(self, app: QApplication):
        app.setStyleSheet(self.stylesheet())


class WorkerThread(QThread):
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)
    progress = pyqtSignal(int, str)

    def __init__(self, image_path: str, verbose: bool = False):
        super().__init__()
        self.image_path = image_path
        self.verbose = verbose

    def run(self):
        try:
            self.progress.emit(10, "Carregando imagem...")
            self.progress.emit(30, "Analisando cores...")
            features = analyze_image(self.image_path)
            self.progress.emit(60, "Gerando nome surreal...")
            name, debug_info = generate_name(features, verbose=self.verbose)
            self.progress.emit(90, "Finalizando...")
            result = {"name": name, "features": features, "debug": debug_info if self.verbose else {}}
            self.progress.emit(100, "Concluído!")
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))


class ImageDownloadWorker(QThread):
    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    progress = pyqtSignal(int, str)

    def __init__(self, url: str):
        super().__init__()
        self.url = url

    def run(self):
        try:
            self.progress.emit(10, "Baixando imagem...")

            with tempfile.NamedTemporaryFile(delete=False, suffix='.tmp') as tmp:
                temp_path = tmp.name

            req = urllib.request.Request(
                self.url,
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            )

            with urllib.request.urlopen(req, timeout=30) as response:
                self.progress.emit(50, "Salvando imagem...")
                content_type = response.headers.get('Content-Type', '')

                ext = self._get_extension_from_content_type(content_type)
                if not ext:
                    ext = self._get_extension_from_url(self.url)

                final_path = temp_path + ext
                import os
                os.rename(temp_path, final_path)

                with open(final_path, 'wb') as f:
                    f.write(response.read())

                self.progress.emit(100, "Download concluído!")
                self.finished.emit(final_path)

        except Exception as e:
            self.error.emit(f"Erro ao baixar imagem: {str(e)}")

    def _get_extension_from_content_type(self, content_type: str) -> str:
        mime_to_ext = {
            'image/jpeg': '.jpg',
            'image/png': '.png',
            'image/gif': '.gif',
            'image/bmp': '.bmp',
            'image/tiff': '.tiff',
            'image/webp': '.webp',
        }
        return mime_to_ext.get(content_type.lower(), '')

    def _get_extension_from_url(self, url: str) -> str:
        path = QUrl(url).path()
        ext = Path(path).suffix.lower()
        valid_exts = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', '.webp', '.gif')
        return ext if ext in valid_exts else '.jpg'


class AnimatedButton(QPushButton):
    def __init__(self, text: str, primary: bool = False):
        super().__init__(text)
        self._primary = primary
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        if primary:
            self.setProperty("primary", True)
        self._anim = QPropertyAnimation(self, b"geometry")
        self._anim.setDuration(100)
        self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._anim.stop()
            self._anim.setStartValue(self.geometry())
            r = self.geometry()
            self._anim.setEndValue(QRect(r.x() + 1, r.y() + 1, r.width() - 2, r.height() - 2))
            self._anim.start()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._anim.stop()
            self._anim.setStartValue(self.geometry())
            r = self.geometry()
            self._anim.setEndValue(QRect(r.x() - 1, r.y() - 1, r.width() + 2, r.height() + 2))
            self._anim.start()
        super().mouseReleaseEvent(event)


class ImageDropZone(QFrame):
    image_selected = pyqtSignal(str)

    def __init__(self, theme_manager: ThemeManager):
        super().__init__()
        self.theme = theme_manager
        self._pixmap: Optional[QPixmap] = None
        self._has_image = False
        self._drag_active = False
        self._downloading = False
        self._download_worker: Optional[ImageDownloadWorker] = None
        self.setAcceptDrops(True)
        self.setMinimumSize(320, 320)
        self.setMaximumSize(480, 480)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setMinimumSize(320, 320)
        layout.addWidget(self.image_label)
        self._update_style()

    def _update_style(self):
        c = self.theme.colors
        if self._has_image:
            border, bg, text = c["drop_loaded_border"], c["drop_loaded_bg"], ""
        elif self._drag_active:
            border, bg, text = c["drop_active_border"], c["drop_active_bg"], "Solte a imagem aqui"
        elif self._downloading:
            border, bg, text = c["drop_active_border"], c["drop_active_bg"], "Baixando imagem..."
        else:
            border, bg, text = c["drop_idle_border"], c["drop_idle_bg"], "Arraste uma imagem aqui\nou clique para selecionar"

        self.setStyleSheet(f"QFrame {{ border: 2px dashed {border}; border-radius: 16px; background-color: {bg}; }} QLabel {{ border: none; background: transparent; color: {c['text_muted']}; font-size: 14px; }}")
        if not self._has_image and not self._downloading:
            self.image_label.setText(text)

    def dragEnterEvent(self, event):
        if self._can_accept_mime_data(event.mimeData()):
            event.acceptProposedAction()
            if not self._has_image and not self._downloading:
                self._drag_active = True
                self._update_style()

    def dragMoveEvent(self, event):
        if self._can_accept_mime_data(event.mimeData()):
            event.acceptProposedAction()

    def dragLeaveEvent(self, event):
        if not self._has_image and not self._downloading:
            self._drag_active = False
            self._update_style()

    def _can_accept_mime_data(self, mime_data) -> bool:
        if mime_data.hasUrls():
            for url in mime_data.urls():
                if self._is_valid_image_url(url):
                    return True
        if mime_data.hasImage():
            return True
        return False

    def dropEvent(self, event):
        self._drag_active = False
        mime_data = event.mimeData()

        if mime_data.hasImage():
            image = mime_data.imageData()
            if image and not image.isNull():
                self._save_and_process_image(image)
                return

        if mime_data.hasUrls():
            for url in mime_data.urls():
                local_path = url.toLocalFile()

                if local_path and self._is_image_file(local_path):
                    self.load_image(local_path)
                    self.image_selected.emit(local_path)
                    return

                elif url.isValid() and url.scheme() in ('http', 'https'):
                    final_url = self._extract_direct_image_url(url.toString())
                    self._download_image(final_url)
                    return

        self._update_style()

    def _extract_direct_image_url(self, url: str) -> str:
        from urllib.parse import urlparse, parse_qs

        parsed = urlparse(url)

        if 'google.com' in parsed.netloc and parsed.path == '/imgres':
            query = parse_qs(parsed.query)
            if 'imgurl' in query:
                return query['imgurl'][0]

        if 'bing.com' in parsed.netloc and 'images' in parsed.path:
            query = parse_qs(parsed.query)
            if 'mediaurl' in query:
                return query['mediaurl'][0]

        return url

    def _save_and_process_image(self, image):
        import tempfile
        from PyQt6.QtCore import QBuffer, QIODevice

        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
            temp_path = tmp.name

        buffer = QBuffer()
        buffer.open(QIODevice.OpenModeFlag.WriteOnly)
        image.save(buffer, "PNG")
        buffer.close()

        with open(temp_path, 'wb') as f:
            f.write(buffer.data().data())

        self.load_image(temp_path)
        self.image_selected.emit(temp_path)

    def _is_valid_image_url(self, url: QUrl) -> bool:
        if url.isLocalFile():
            return self._is_image_file(url.toLocalFile())
        elif url.scheme() in ('http', 'https'):
            path = url.path()
            ext = Path(path).suffix.lower()
            valid_exts = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', '.webp', '.gif')
            return ext in valid_exts or ext == ''
        return False

    def _is_image_file(self, path: str) -> bool:
        return Path(path).suffix.lower() in ('.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', '.webp')

    def _download_image(self, url: str):
        if self._downloading and self._download_worker and self._download_worker.isRunning():
            self._download_worker.quit()
            self._download_worker.wait(1000)

        self._downloading = True
        self._update_style()

        self._download_worker = ImageDownloadWorker(url)
        self._download_worker.finished.connect(self._on_download_finished)
        self._download_worker.error.connect(self._on_download_error)
        self._download_worker.progress.connect(self._on_download_progress)
        self._download_worker.start()

    def _on_download_finished(self, local_path: str):
        self._downloading = False
        if self._download_worker:
            self._download_worker.deleteLater()
            self._download_worker = None
        self.load_image(local_path)
        self.image_selected.emit(local_path)

    def _on_download_error(self, error: str):
        self._downloading = False
        if self._download_worker:
            self._download_worker.deleteLater()
            self._download_worker = None
        self._update_style()
        self.image_label.setToolTip(error)

    def _on_download_progress(self, value: int, message: str):
        self.image_label.setText(message)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and not self._has_image and not self._downloading:
            self.select_image()

    def select_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Selecionar Imagem", "", "Imagens (*.jpg *.jpeg *.png *.bmp *.tiff *.tif *.webp)")
        if file_path:
            self.load_image(file_path)
            self.image_selected.emit(file_path)

    def load_image(self, path: str):
        pixmap = QPixmap(path)
        if not pixmap.isNull():
            self._pixmap = pixmap
            self._has_image = True
            self._update_style()
            self._update_pixmap()

    def _update_pixmap(self):
        if self._pixmap:
            scaled = self._pixmap.scaled(self.image_label.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.image_label.setPixmap(scaled)

    def clear_image(self):
        if self._downloading and self._download_worker:
            self._download_worker.quit()
            self._download_worker.wait(1000)
            self._download_worker = None

        self._downloading = False
        self._pixmap = None
        self._has_image = False
        self.image_label.clear()
        self._update_style()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self._pixmap:
            self._update_pixmap()

    def theme_changed(self):
        self._update_style()


class ResultCard(QFrame):
    def __init__(self, theme_manager: ThemeManager):
        super().__init__()
        self.theme = theme_manager
        self.setFixedHeight(72)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 10, 16, 10)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.name_label = QLabel("—")
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.name_label.setWordWrap(True)
        self.name_label.setFont(QFont("Segoe UI", 20, QFont.Weight.Medium))
        self.name_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        layout.addWidget(self.name_label)

        self._current_name = ""
        self._current_seed = None
        self._apply_style()

    def _apply_style(self):
        c = self.theme.colors
        self.setStyleSheet(f'''
            QFrame {{ background-color: {c["card_bg"]}; border: 1px solid {c["card_border"]}; border-radius: 10px; }}
            QLabel {{ color: {c["text_primary"]}; background: transparent; border: none; }}
        ''')

    def set_name(self, name: str, seed: int = None):
        self._current_name = name
        self._current_seed = seed
        self.name_label.setText(name)
        self.setToolTip(f"Seed: {seed}" if seed else "")

    def clear_name(self):
        self._current_name = ""
        self._current_seed = None
        self.name_label.setText("—")
        self.setToolTip("")

    def get_name(self) -> str:
        return self._current_name

    def theme_changed(self):
        self._apply_style()


class FeatureRow(QWidget):
    def __init__(self, label: str, value: str = "—", theme_manager: ThemeManager = None):
        super().__init__()
        self.theme = theme_manager
        self.setFixedHeight(30)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        self.label_widget = QLabel(label)
        self.label_widget.setFont(QFont("Segoe UI", 9))
        self.label_widget.setFixedWidth(100)

        self.value_widget = QLabel(value)
        self.value_widget.setFont(QFont("Segoe UI", 9, QFont.Weight.Medium))
        self.value_widget.setWordWrap(True)

        layout.addWidget(self.label_widget)
        layout.addWidget(self.value_widget, 1)

        if self.theme:
            self.theme_changed()

    def set_value(self, value: str):
        self.value_widget.setText(value)

    def theme_changed(self):
        c = self.theme.colors
        self.label_widget.setStyleSheet(f"color: {c['text_muted']}; background: transparent;")
        self.value_widget.setStyleSheet(f"color: {c['text_primary']}; background: transparent;")


class ThemeToggle(QPushButton):
    def __init__(self, theme_manager: ThemeManager, on_toggle):
        super().__init__()
        self.theme = theme_manager
        self._on_toggle = on_toggle
        self.setFixedSize(36, 36)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.clicked.connect(self._toggle)
        self._update_icon()

    def _toggle(self):
        self.theme.toggle()
        self._update_icon()
        self._on_toggle()

    def _update_icon(self):
        self.setText("☀" if self.theme.theme == Theme.DARK else "🌙")
        self.setFont(QFont("Segoe UI", 13))
        c = self.theme.colors
        self.setStyleSheet(f'QPushButton {{ background-color: {c["bg_tertiary"]}; border: 1px solid {c["border"]}; border-radius: 18px; color: {c["text_secondary"]}; }} QPushButton:hover {{ background-color: {c["border"]}; }}')


class LeftPanel(QWidget):
    def __init__(self, theme_manager: ThemeManager):
        super().__init__()
        self.theme = theme_manager
        self.setMinimumWidth(380)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)

        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(12)

        title_layout = QVBoxLayout()
        title_layout.setSpacing(2)
        title = QLabel("surreal-namer")
        title.setFont(QFont("Segoe UI", 20, QFont.Weight.Light))
        title_layout.addWidget(title)
        subtitle = QLabel("Gere nomes surreais a partir de imagens")
        subtitle.setFont(QFont("Segoe UI", 9))
        title_layout.addWidget(subtitle)
        header_layout.addLayout(title_layout, 1)

        self.theme_toggle = ThemeToggle(self.theme, lambda: None)
        header_layout.addWidget(self.theme_toggle, 0, Qt.AlignmentFlag.AlignTop)
        layout.addWidget(header)

        self.drop_zone = ImageDropZone(self.theme)
        drop_container = QWidget()
        drop_layout = QHBoxLayout(drop_container)
        drop_layout.setContentsMargins(0, 0, 0, 0)
        drop_layout.addWidget(self.drop_zone, 0, Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(drop_container)

        layout.addStretch()

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(3)
        layout.addWidget(self.progress_bar)

        self.status_label = QLabel("Pronto")
        self.status_label.setFont(QFont("Segoe UI", 9))
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)

        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(10)
        controls_layout.setContentsMargins(0, 8, 0, 0)

        self.verbose_check = QCheckBox("Modo detalhado")
        self.verbose_check.setFont(QFont("Segoe UI", 9))
        controls_layout.addWidget(self.verbose_check)
        controls_layout.addStretch()

        self.copy_btn = AnimatedButton("Copiar nome", primary=True)
        self.copy_btn.setFixedHeight(38)
        self.copy_btn.setEnabled(False)
        controls_layout.addWidget(self.copy_btn)

        self.clear_btn = AnimatedButton("Limpar")
        self.clear_btn.setFixedHeight(38)
        self.clear_btn.setEnabled(False)
        controls_layout.addWidget(self.clear_btn)

        layout.addLayout(controls_layout)

    def theme_changed(self):
        self.drop_zone.theme_changed()
        c = self.theme.colors
        self.status_label.setStyleSheet(f"color: {c['text_muted']}; background: transparent;")


class RightPanel(QWidget):
    def __init__(self, theme_manager: ThemeManager):
        super().__init__()
        self.theme = theme_manager
        self.setMinimumWidth(340)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        self.result_card = ResultCard(self.theme)
        layout.addWidget(self.result_card)

        features_frame = QFrame()
        features_layout = QVBoxLayout(features_frame)
        features_layout.setContentsMargins(0, 0, 0, 0)
        features_layout.setSpacing(12)

        features_title = QLabel("Características da Imagem")
        features_title.setFont(QFont("Segoe UI", 11, QFont.Weight.Medium))
        features_layout.addWidget(features_title)

        grid_widget = QWidget()
        grid_layout = QHBoxLayout(grid_widget)
        grid_layout.setContentsMargins(0, 0, 0, 0)
        grid_layout.setSpacing(24)

        left_col = QVBoxLayout()
        left_col.setSpacing(6)
        self.feat_dimensions = FeatureRow("Dimensões", "—", self.theme)
        self.feat_orientation = FeatureRow("Orientação", "—", self.theme)
        self.feat_aspect = FeatureRow("Proporção", "—", self.theme)
        left_col.addWidget(self.feat_dimensions)
        left_col.addWidget(self.feat_orientation)
        left_col.addWidget(self.feat_aspect)

        right_col = QVBoxLayout()
        right_col.setSpacing(6)
        self.feat_brightness = FeatureRow("Brilho", "—", self.theme)
        self.feat_colors = FeatureRow("Cores", "—", self.theme)
        self.feat_colors.value_widget.setWordWrap(True)
        right_col.addWidget(self.feat_brightness)
        right_col.addWidget(self.feat_colors)

        grid_layout.addLayout(left_col, 1)
        grid_layout.addLayout(right_col, 1)
        features_layout.addWidget(grid_widget)

        layout.addWidget(features_frame)
        layout.addStretch()

    def theme_changed(self):
        self.result_card.theme_changed()
        for feat in (self.feat_dimensions, self.feat_orientation, self.feat_aspect, self.feat_brightness, self.feat_colors):
            feat.theme_changed()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("surreal-namer")
        self.setMinimumSize(900, 560)
        self.resize(1000, 620)

        self.theme = ThemeManager()
        self.current_image_path: Optional[str] = None
        self.worker: Optional[WorkerThread] = None

        self.setup_ui()
        self.apply_theme()

    def setup_ui(self):
        central = QWidget()
        central.setObjectName("centralWidget")
        self.setCentralWidget(central)

        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(self.splitter)

        self.left_panel = LeftPanel(self.theme)
        self.splitter.addWidget(self.left_panel)

        self.right_panel = RightPanel(self.theme)
        self.splitter.addWidget(self.right_panel)

        self.splitter.setSizes([420, 580])
        self.splitter.setHandleWidth(1)

        self.left_panel.drop_zone.image_selected.connect(self.on_image_selected)
        self.left_panel.copy_btn.clicked.connect(self.copy_name)
        self.left_panel.clear_btn.clicked.connect(self.clear_all)
        self.left_panel.theme_toggle._on_toggle = self.on_theme_changed

    def apply_theme(self):
        self.theme.apply_to_app(QApplication.instance())
        self.left_panel.theme_changed()
        self.right_panel.theme_changed()

    def on_theme_changed(self):
        self.apply_theme()

    def on_image_selected(self, path: str):
        self.load_image(path)

    def load_image(self, path: str):
        self.current_image_path = path
        self.left_panel.clear_btn.setEnabled(True)
        self.left_panel.status_label.setText(f"Processando: {Path(path).name}")
        self.analyze_image()

    def clear_all(self):
        self.current_image_path = None
        self.left_panel.drop_zone.clear_image()
        self.left_panel.clear_btn.setEnabled(False)
        self.left_panel.copy_btn.setEnabled(False)
        self.left_panel.status_label.setText("Pronto")
        self.right_panel.result_card.clear_name()
        self.reset_features()

    def reset_features(self):
        for feat in (self.right_panel.feat_dimensions, self.right_panel.feat_orientation, self.right_panel.feat_aspect, self.right_panel.feat_brightness, self.right_panel.feat_colors):
            feat.set_value("—")

    def analyze_image(self):
        if not self.current_image_path:
            return

        self.left_panel.progress_bar.setVisible(True)
        self.left_panel.progress_bar.setValue(0)
        self.left_panel.copy_btn.setEnabled(False)
        self.left_panel.clear_btn.setEnabled(False)

        self.worker = WorkerThread(self.current_image_path, self.left_panel.verbose_check.isChecked())
        self.worker.finished.connect(self.on_analysis_finished)
        self.worker.error.connect(self.on_analysis_error)
        self.worker.progress.connect(self.on_progress)
        self.worker.start()

    def on_progress(self, value: int, message: str):
        self.left_panel.progress_bar.setValue(value)
        self.left_panel.status_label.setText(message)

    def on_analysis_finished(self, result: Dict[str, Any]):
        self.left_panel.progress_bar.setVisible(False)
        self.left_panel.clear_btn.setEnabled(True)
        self.left_panel.copy_btn.setEnabled(True)

        name = result["name"]
        features = result["features"]

        seed = result.get("debug", {}).get("seed") if result.get("debug") else None
        self.right_panel.result_card.set_name(name, seed)

        self.right_panel.feat_dimensions.set_value(f"{features['width']} × {features['height']} px")
        self.right_panel.feat_orientation.set_value(features['orientation'].capitalize())
        self.right_panel.feat_aspect.set_value(f"{features['aspect_ratio']:.2f}")
        self.right_panel.feat_brightness.set_value(f"{features['brightness']:.0%} ({features['brightness_category']})")
        self.right_panel.feat_colors.set_value(", ".join(features['color_names'][:5]))

        self.left_panel.status_label.setText(f"Nome gerado: {name}")

    def on_analysis_error(self, error: str):
        self.left_panel.progress_bar.setVisible(False)
        self.left_panel.clear_btn.setEnabled(True)
        self.left_panel.status_label.setText("Erro")
        QMessageBox.critical(self, "Erro", f"Falha ao processar imagem:\n{error}")

    def copy_name(self):
        name = self.right_panel.result_card.get_name()
        if name and name != "—":
            QApplication.clipboard().setText(name)
            self.left_panel.status_label.setText("Nome copiado para a área de transferência")
            QTimer.singleShot(2000, lambda: self.left_panel.status_label.setText(f"Nome gerado: {name}"))


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("surreal-namer")
    app.setApplicationVersion("1.0")

    font = QFont("Segoe UI", 9)
    app.setFont(font)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()