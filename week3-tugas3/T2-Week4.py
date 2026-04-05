import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QStackedWidget, QRadioButton, QButtonGroup, QDateEdit,
    QTextEdit, QProgressBar, QFrame, QGraphicsDropShadowEffect
)
from PyQt5.QtCore import pyqtSignal, QDate, Qt, QPropertyAnimation, QEasingCurve, QRect
from PyQt5.QtGui import QColor, QFont, QPainter, QPen, QBrush, QLinearGradient, QPalette, QFontDatabase


DARK_BG       = "#0D0F14"
CARD_BG       = "#13161E"
BORDER_COLOR  = "#1E2330"
ACCENT        = "#4F8EF7"
ACCENT_GLOW   = "#3B6FCC"
SUCCESS       = "#34D399"
ERROR         = "#F87171"
TEXT_PRIMARY  = "#E8ECF4"
TEXT_MUTED    = "#5A6278"
TEXT_LABEL    = "#8A93A8"
INPUT_BG      = "#0D0F14"
STEP_INACTIVE = "#1E2330"


GLOBAL_STYLE = f"""
QWidget {{
    background-color: {DARK_BG};
    color: {TEXT_PRIMARY};
    font-family: 'Segoe UI', 'SF Pro Display', sans-serif;
    font-size: 13px;
}}

QLineEdit {{
    background-color: {INPUT_BG};
    border: 1.5px solid {BORDER_COLOR};
    border-radius: 10px;
    padding: 12px 16px;
    color: {TEXT_PRIMARY};
    font-size: 13px;
    selection-background-color: {ACCENT};
}}
QLineEdit:focus {{
    border: 1.5px solid {ACCENT};
    background-color: #0F1219;
}}
QLineEdit:hover {{
    border: 1.5px solid #2A3048;
}}

QTextEdit {{
    background-color: {INPUT_BG};
    border: 1.5px solid {BORDER_COLOR};
    border-radius: 10px;
    padding: 12px 16px;
    color: {TEXT_PRIMARY};
    font-size: 13px;
}}
QTextEdit:focus {{
    border: 1.5px solid {ACCENT};
}}

QDateEdit {{
    background-color: {INPUT_BG};
    border: 1.5px solid {BORDER_COLOR};
    border-radius: 10px;
    padding: 12px 16px;
    color: {TEXT_PRIMARY};
    font-size: 13px;
}}
QDateEdit:focus {{
    border: 1.5px solid {ACCENT};
}}
QDateEdit::drop-down {{
    border: none;
    width: 30px;
}}

QCalendarWidget {{
    background-color: {CARD_BG};
    color: {TEXT_PRIMARY};
    border: 1px solid {BORDER_COLOR};
    border-radius: 10px;
}}
QCalendarWidget QAbstractItemView {{
    background-color: {CARD_BG};
    selection-background-color: {ACCENT};
    color: {TEXT_PRIMARY};
}}

QScrollBar:vertical {{
    background: {DARK_BG};
    width: 6px;
    border-radius: 3px;
}}
QScrollBar::handle:vertical {{
    background: {BORDER_COLOR};
    border-radius: 3px;
    min-height: 20px;
}}
QScrollBar::handle:vertical:hover {{
    background: {ACCENT};
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}
"""


def styled_label(text, size=12, color=TEXT_LABEL, bold=False):
    lbl = QLabel(text)
    weight = "600" if bold else "400"
    lbl.setStyleSheet(f"color: {color}; font-size: {size}px; font-weight: {weight}; background: transparent;")
    return lbl


def create_field(placeholder, echo_mode=None):
    field = QLineEdit()
    field.setPlaceholderText(placeholder)
    field.setMinimumHeight(46)
    if echo_mode:
        field.setEchoMode(echo_mode)
    return field


def set_field_state(field, state):
    """state: 'normal', 'valid', 'error'"""
    colors = {
        'normal': BORDER_COLOR,
        'valid': SUCCESS,
        'error': ERROR
    }
    c = colors.get(state, BORDER_COLOR)
    field.setStyleSheet(f"""
        QLineEdit {{
            background-color: {INPUT_BG};
            border: 1.5px solid {c};
            border-radius: 10px;
            padding: 12px 16px;
            color: {TEXT_PRIMARY};
            font-size: 13px;
        }}
        QLineEdit:focus {{ border: 1.5px solid {ACCENT}; }}
    """)


class StepWidget(QWidget):
    stepCompleted = pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        self.valid = False

    def set_valid(self, is_valid):
        self.valid = is_valid
        self.stepCompleted.emit(is_valid)


class StepIndicator(QWidget):
    def __init__(self, steps, parent=None):
        super().__init__(parent)
        self.steps = steps
        self.current = 0
        self.setFixedHeight(70)

    def set_current(self, idx):
        self.current = idx
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w = self.width()
        h = self.height()
        n = len(self.steps)
        spacing = w / (n + 1)
        cy = h // 2
        r = 16

        for i in range(n - 1):
            x1 = int(spacing * (i + 1)) + r
            x2 = int(spacing * (i + 2)) - r
            if i < self.current:
                pen = QPen(QColor(ACCENT), 2)
            else:
                pen = QPen(QColor(BORDER_COLOR), 2)
            painter.setPen(pen)
            painter.drawLine(x1, cy, x2, cy)

        for i, label in enumerate(self.steps):
            cx = int(spacing * (i + 1))

            if i < self.current:
                # Completed
                painter.setBrush(QBrush(QColor(ACCENT)))
                painter.setPen(Qt.NoPen)
                painter.drawEllipse(cx - r, cy - r, r * 2, r * 2)
                painter.setPen(QPen(QColor("#FFFFFF"), 2))
                painter.setFont(QFont("Segoe UI", 9, QFont.Bold))
                painter.drawText(cx - r, cy - r, r * 2, r * 2, Qt.AlignCenter, "✓")
            elif i == self.current:
                # Active
                glow = QBrush(QColor(ACCENT))
                painter.setBrush(glow)
                painter.setPen(Qt.NoPen)
                painter.setOpacity(0.15)
                painter.drawEllipse(cx - r - 5, cy - r - 5, (r + 5) * 2, (r + 5) * 2)
                painter.setOpacity(1.0)
                painter.setBrush(QBrush(QColor(ACCENT)))
                painter.drawEllipse(cx - r, cy - r, r * 2, r * 2)
                painter.setPen(QPen(QColor("#FFFFFF"), 1))
                painter.setFont(QFont("Segoe UI", 9, QFont.Bold))
                painter.drawText(cx - r, cy - r, r * 2, r * 2, Qt.AlignCenter, str(i + 1))
            else:
                # Inactive
                painter.setBrush(QBrush(QColor(CARD_BG)))
                painter.setPen(QPen(QColor(BORDER_COLOR), 1.5))
                painter.drawEllipse(cx - r, cy - r, r * 2, r * 2)
                painter.setPen(QPen(QColor(TEXT_MUTED), 1))
                painter.setFont(QFont("Segoe UI", 9))
                painter.drawText(cx - r, cy - r, r * 2, r * 2, Qt.AlignCenter, str(i + 1))

            # Label below
            painter.setPen(QPen(QColor(ACCENT if i == self.current else TEXT_MUTED), 1))
            painter.setFont(QFont("Segoe UI", 8, QFont.Bold if i == self.current else QFont.Normal))
            painter.drawText(cx - 40, cy + r + 4, 80, 20, Qt.AlignCenter, label)


class RadioCard(QWidget):
    toggled = pyqtSignal(bool)

    def __init__(self, text, icon=""):
        super().__init__()
        self.text = text
        self.icon = icon
        self._checked = False
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(48)
        self._update_style()

    def set_checked(self, val):
        self._checked = val
        self._update_style()
        self.update()

    def is_checked(self):
        return self._checked

    def mousePressEvent(self, event):
        self.toggled.emit(True)

    def _update_style(self):
        if self._checked:
            self.setStyleSheet(f"""
                RadioCard {{
                    background-color: #0F1A2E;
                    border: 1.5px solid {ACCENT};
                    border-radius: 10px;
                }}
            """)
        else:
            self.setStyleSheet(f"""
                RadioCard {{
                    background-color: {INPUT_BG};
                    border: 1.5px solid {BORDER_COLOR};
                    border-radius: 10px;
                }}
                RadioCard:hover {{
                    border: 1.5px solid #2A3048;
                }}
            """)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Radio circle
        cr = 8
        cx, cy = 20, self.height() // 2
        if self._checked:
            painter.setBrush(QBrush(QColor(ACCENT)))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(cx - cr, cy - cr, cr * 2, cr * 2)
            painter.setBrush(QBrush(QColor("#FFFFFF")))
            painter.drawEllipse(cx - 3, cy - 3, 6, 6)
        else:
            painter.setBrush(Qt.NoBrush)
            painter.setPen(QPen(QColor(TEXT_MUTED), 1.5))
            painter.drawEllipse(cx - cr, cy - cr, cr * 2, cr * 2)

        # Label
        color = TEXT_PRIMARY if self._checked else TEXT_MUTED
        painter.setPen(QPen(QColor(color), 1))
        painter.setFont(QFont("Segoe UI", 11, QFont.Medium if self._checked else QFont.Normal))
        painter.drawText(cx + cr + 10, 0, self.width() - cx - cr - 20, self.height(), Qt.AlignVCenter, f"{self.icon}  {self.text}")


class Step1(StepWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.setSpacing(14)
        layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(styled_label("NAMA LENGKAP", 10, TEXT_MUTED, True))
        self.name = create_field("Masukkan nama lengkap")
        self.name.textChanged.connect(self.validate)
        layout.addWidget(self.name)

        layout.addWidget(styled_label("TANGGAL LAHIR", 10, TEXT_MUTED, True))
        self.date = QDateEdit()
        self.date.setCalendarPopup(True)
        self.date.setDate(QDate.currentDate())
        self.date.setMinimumHeight(46)
        layout.addWidget(self.date)

        layout.addWidget(styled_label("JENIS KELAMIN", 10, TEXT_MUTED, True))
        gender_row = QHBoxLayout()
        gender_row.setSpacing(10)
        self.male_card = RadioCard("Laki-laki", "♂")
        self.female_card = RadioCard("Perempuan", "♀")
        self.male_card.toggled.connect(lambda: self._select_gender(self.male_card, self.female_card))
        self.female_card.toggled.connect(lambda: self._select_gender(self.female_card, self.male_card))
        gender_row.addWidget(self.male_card)
        gender_row.addWidget(self.female_card)
        layout.addLayout(gender_row)

        layout.addStretch()
        self.setLayout(layout)
        self._gender_selected = False

    def _select_gender(self, selected, other):
        selected.set_checked(True)
        other.set_checked(False)
        self._gender_selected = True
        self.validate()

    def validate(self):
        has_name = bool(self.name.text().strip())
        set_field_state(self.name, 'valid' if has_name else ('error' if self.name.text() else 'normal'))
        self.set_valid(has_name and self._gender_selected)


class Step2(StepWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.setSpacing(14)
        layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(styled_label("ALAMAT EMAIL", 10, TEXT_MUTED, True))
        self.email = create_field("nama@email.com")
        self.email.textChanged.connect(self.validate)
        layout.addWidget(self.email)

        layout.addWidget(styled_label("NOMOR TELEPON", 10, TEXT_MUTED, True))
        self.phone = create_field("08xx xxxx xxxx")
        self.phone.textChanged.connect(self.validate)
        layout.addWidget(self.phone)

        layout.addWidget(styled_label("ALAMAT LENGKAP", 10, TEXT_MUTED, True))
        self.address = QTextEdit()
        self.address.setPlaceholderText("Jl. Contoh No. 1, Kota, Provinsi")
        self.address.setMinimumHeight(90)
        self.address.setMaximumHeight(110)
        self.address.textChanged.connect(self.validate)
        layout.addWidget(self.address)

        layout.addStretch()
        self.setLayout(layout)

    def validate(self):
        email_ok = "@" in self.email.text() and "." in self.email.text()
        phone_ok = self.phone.text().replace(" ", "").replace("-", "").isdigit() and len(self.phone.text()) >= 9
        addr_ok = bool(self.address.toPlainText().strip())

        set_field_state(self.email, 'valid' if email_ok else ('error' if self.email.text() else 'normal'))
        set_field_state(self.phone, 'valid' if phone_ok else ('error' if self.phone.text() else 'normal'))
        self.set_valid(email_ok and phone_ok and addr_ok)


class Step3(StepWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.setSpacing(14)
        layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(styled_label("USERNAME", 10, TEXT_MUTED, True))
        self.username = create_field("username unik anda")
        self.username.textChanged.connect(self.validate)
        layout.addWidget(self.username)

        layout.addWidget(styled_label("PASSWORD", 10, TEXT_MUTED, True))
        self.password = create_field("Min. 6 karakter", QLineEdit.Password)
        self.password.textChanged.connect(self.validate)
        layout.addWidget(self.password)

        # Strength bar
        self.strength_bar = QProgressBar()
        self.strength_bar.setMaximum(3)
        self.strength_bar.setValue(0)
        self.strength_bar.setFixedHeight(4)
        self.strength_bar.setTextVisible(False)
        self.strength_bar.setStyleSheet(f"""
            QProgressBar {{ background: {BORDER_COLOR}; border-radius: 2px; border: none; }}
            QProgressBar::chunk {{ background: {ACCENT}; border-radius: 2px; }}
        """)
        layout.addWidget(self.strength_bar)

        layout.addWidget(styled_label("KONFIRMASI PASSWORD", 10, TEXT_MUTED, True))
        self.confirm = create_field("Ulangi password anda", QLineEdit.Password)
        self.confirm.textChanged.connect(self.validate)
        layout.addWidget(self.confirm)

        self.match_label = styled_label("", 10, TEXT_MUTED)
        layout.addWidget(self.match_label)

        layout.addStretch()
        self.setLayout(layout)

    def validate(self):
        pwd = self.password.text()
        strength = 0
        if len(pwd) >= 6: strength += 1
        if any(c.isdigit() for c in pwd): strength += 1
        if any(not c.isalnum() for c in pwd): strength += 1
        self.strength_bar.setValue(strength)

        colors = ["#F87171", "#FBBF24", "#34D399"]
        bar_color = colors[strength - 1] if strength > 0 else BORDER_COLOR
        self.strength_bar.setStyleSheet(f"""
            QProgressBar {{ background: {BORDER_COLOR}; border-radius: 2px; border: none; }}
            QProgressBar::chunk {{ background: {bar_color}; border-radius: 2px; }}
        """)

        user_ok = bool(self.username.text().strip())
        pwd_ok = len(pwd) >= 6
        confirm_ok = pwd == self.confirm.text() and bool(self.confirm.text())

        set_field_state(self.username, 'valid' if user_ok else ('error' if self.username.text() else 'normal'))
        set_field_state(self.password, 'valid' if pwd_ok else ('error' if pwd else 'normal'))
        set_field_state(self.confirm, 'valid' if confirm_ok else ('error' if self.confirm.text() else 'normal'))

        if self.confirm.text():
            if confirm_ok:
                self.match_label.setText("✓  Password cocok")
                self.match_label.setStyleSheet(f"color: {SUCCESS}; font-size: 11px; background: transparent;")
            else:
                self.match_label.setText("✗  Password tidak cocok")
                self.match_label.setStyleSheet(f"color: {ERROR}; font-size: 11px; background: transparent;")
        else:
            self.match_label.setText("")

        self.set_valid(user_ok and pwd_ok and confirm_ok)


class ReviewStep(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(0, 0, 0, 0)

        title = styled_label("Konfirmasi Data Anda", 16, TEXT_PRIMARY, True)
        layout.addWidget(title)
        sub = styled_label("Periksa kembali informasi sebelum mendaftar.", 11, TEXT_MUTED)
        layout.addWidget(sub)

        self.rows_layout = QVBoxLayout()
        self.rows_layout.setSpacing(8)
        layout.addLayout(self.rows_layout)
        layout.addStretch()
        self.setLayout(layout)

    def set_data(self, data):
        while self.rows_layout.count():
            item = self.rows_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        icons = {
            "Nama": "👤", "Tanggal Lahir": "🗓", "Jenis Kelamin": "⚥",
            "Email": "✉", "Telepon": "📞", "Alamat": "📍",
            "Username": "🔖"
        }

        for k, v in data.items():
            row = QFrame()
            row.setStyleSheet(f"""
                QFrame {{
                    background-color: {CARD_BG};
                    border: 1px solid {BORDER_COLOR};
                    border-radius: 10px;
                    padding: 2px;
                }}
            """)
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(14, 10, 14, 10)

            icon = icons.get(k, "•")
            key_lbl = styled_label(f"{icon}  {k}", 11, TEXT_MUTED)
            key_lbl.setFixedWidth(140)
            val_lbl = styled_label(str(v), 12, TEXT_PRIMARY, True)
            val_lbl.setWordWrap(True)

            row_layout.addWidget(key_lbl)
            row_layout.addWidget(val_lbl, 1)
            self.rows_layout.addWidget(row)


class MainWindow(QWidget):
    stepChanged = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pendaftaran Akun")
        self.setFixedSize(500, 660)
        self.setStyleSheet(GLOBAL_STYLE)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # Header
        header = QWidget()
        header.setFixedHeight(72)
        header.setStyleSheet(f"background: {CARD_BG}; border-bottom: 1px solid {BORDER_COLOR};")
        hdr_layout = QHBoxLayout(header)
        hdr_layout.setContentsMargins(28, 0, 28, 0)
        app_title = QLabel("PENDAFTARAN")
        app_title.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 16px; font-weight: 700; letter-spacing: 3px; background: transparent;")
        app_sub = QLabel("Buat akun baru")
        app_sub.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 11px; background: transparent;")
        t_col = QVBoxLayout()
        t_col.setSpacing(2)
        t_col.addWidget(app_title)
        t_col.addWidget(app_sub)
        hdr_layout.addLayout(t_col)
        hdr_layout.addStretch()
        outer.addWidget(header)

        # Step indicator
        self.steps_label = ["Pribadi", "Kontak", "Akun", "Review"]
        self.step_indicator = StepIndicator(self.steps_label)
        self.step_indicator.setStyleSheet(f"background: {DARK_BG};")
        outer.addWidget(self.step_indicator)

        # Divider
        div = QFrame()
        div.setFrameShape(QFrame.HLine)
        div.setStyleSheet(f"color: {BORDER_COLOR};")
        outer.addWidget(div)

        # Content card
        content_wrapper = QWidget()
        content_wrapper.setStyleSheet(f"background: {DARK_BG};")
        cw_layout = QVBoxLayout(content_wrapper)
        cw_layout.setContentsMargins(28, 24, 28, 24)

        self.stack = QStackedWidget()
        self.step1 = Step1()
        self.step2 = Step2()
        self.step3 = Step3()
        self.review = ReviewStep()
        self.stack.addWidget(self.step1)
        self.stack.addWidget(self.step2)
        self.stack.addWidget(self.step3)
        self.stack.addWidget(self.review)
        cw_layout.addWidget(self.stack)
        outer.addWidget(content_wrapper, 1)

        # Footer
        footer = QWidget()
        footer.setFixedHeight(80)
        footer.setStyleSheet(f"background: {CARD_BG}; border-top: 1px solid {BORDER_COLOR};")
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(28, 0, 28, 0)

        self.step_counter = styled_label("Langkah 1 dari 4", 11, TEXT_MUTED)

        self.back_btn = QPushButton("← Kembali")
        self.back_btn.setFixedSize(110, 42)
        self.back_btn.setCursor(Qt.PointingHandCursor)
        self.back_btn.setVisible(False)
        self.back_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                border: 1.5px solid {BORDER_COLOR};
                border-radius: 10px;
                color: {TEXT_LABEL};
                font-size: 13px;
            }}
            QPushButton:hover {{
                border-color: {ACCENT};
                color: {ACCENT};
            }}
        """)

        self.next_btn = QPushButton("Lanjut →")
        self.next_btn.setFixedSize(130, 42)
        self.next_btn.setCursor(Qt.PointingHandCursor)
        self.next_btn.setEnabled(False)
        self.next_btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {ACCENT}, stop:1 {ACCENT_GLOW});
                border: none;
                border-radius: 10px;
                color: white;
                font-size: 13px;
                font-weight: 600;
            }}
            QPushButton:disabled {{
                background: {BORDER_COLOR};
                color: {TEXT_MUTED};
            }}
            QPushButton:hover:enabled {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #6AA3FF, stop:1 {ACCENT});
            }}
        """)

        footer_layout.addWidget(self.step_counter)
        footer_layout.addStretch()
        footer_layout.addWidget(self.back_btn)
        footer_layout.addSpacing(10)
        footer_layout.addWidget(self.next_btn)
        outer.addWidget(footer)

        self.current_step = 0
        self.back_btn.clicked.connect(self.prev_step)
        self.next_btn.clicked.connect(self.next_step)

        self.step1.stepCompleted.connect(self.next_btn.setEnabled)
        self.step2.stepCompleted.connect(self.next_btn.setEnabled)
        self.step3.stepCompleted.connect(self.next_btn.setEnabled)

    def next_step(self):
        self.current_step += 1
        self.stack.setCurrentIndex(self.current_step)
        self.step_indicator.set_current(self.current_step)
        self.step_counter.setText(f"Langkah {self.current_step + 1} dari 4")
        self.back_btn.setVisible(True)

        if self.current_step == 3:
            data = {
                "Nama": self.step1.name.text(),
                "Tanggal Lahir": self.step1.date.date().toString("dd MMMM yyyy"),
                "Jenis Kelamin": "Laki-laki" if self.step1.male_card.is_checked() else "Perempuan",
                "Email": self.step2.email.text(),
                "Telepon": self.step2.phone.text(),
                "Alamat": self.step2.address.toPlainText().strip(),
                "Username": self.step3.username.text(),
            }
            self.review.set_data(data)
            self.next_btn.setText("✓  Daftar Sekarang")
            self.next_btn.setEnabled(True)
            self.next_btn.setStyleSheet(f"""
                QPushButton {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #059669, stop:1 #34D399);
                    border: none;
                    border-radius: 10px;
                    color: white;
                    font-size: 13px;
                    font-weight: 600;
                }}
                QPushButton:hover {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #10B981, stop:1 #6EE7B7);
                }}
            """)
        else:
            self.next_btn.setEnabled(False)
            self.next_btn.setText("Lanjut →")

    def prev_step(self):
        self.current_step -= 1
        self.stack.setCurrentIndex(self.current_step)
        self.step_indicator.set_current(self.current_step)
        self.step_counter.setText(f"Langkah {self.current_step + 1} dari 4")

        if self.current_step == 0:
            self.back_btn.setVisible(False)

        self.next_btn.setText("Lanjut →")
        self.next_btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {ACCENT}, stop:1 {ACCENT_GLOW});
                border: none;
                border-radius: 10px;
                color: white;
                font-size: 13px;
                font-weight: 600;
            }}
            QPushButton:disabled {{
                background: {BORDER_COLOR};
                color: {TEXT_MUTED};
            }}
            QPushButton:hover:enabled {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #6AA3FF, stop:1 {ACCENT});
            }}
        """)

        steps = [self.step1, self.step2, self.step3]
        self.next_btn.setEnabled(steps[self.current_step].valid)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(DARK_BG))
    palette.setColor(QPalette.WindowText, QColor(TEXT_PRIMARY))
    palette.setColor(QPalette.Base, QColor(INPUT_BG))
    palette.setColor(QPalette.AlternateBase, QColor(CARD_BG))
    palette.setColor(QPalette.Text, QColor(TEXT_PRIMARY))
    palette.setColor(QPalette.Button, QColor(CARD_BG))
    palette.setColor(QPalette.ButtonText, QColor(TEXT_PRIMARY))
    palette.setColor(QPalette.Highlight, QColor(ACCENT))
    palette.setColor(QPalette.HighlightedText, QColor("#FFFFFF"))
    app.setPalette(palette)

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())