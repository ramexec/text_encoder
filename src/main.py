
import sys
import subprocess

from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QTextEdit,
    QComboBox,
    QPushButton,
    QLabel,
    QHBoxLayout,
    QVBoxLayout,
    QMessageBox
)

from dict_1 import index_1


class Home(QWidget):

    def __init__(self):
        super().__init__()

        self.init_ui()
        self.settings()
        self.connect_events()

        # Ensure initial selections are different
        if self.option_1.count() > 1:
            self.option_2.setCurrentIndex(1)

    # --------------------------------------------------
    # UI
    # --------------------------------------------------

    def init_ui(self):

        self.title = QLabel("Text Converter")
        self.title.setStyleSheet("""
            font-size: 22px;
            font-weight: bold;
        """)

        # Input
        self.input_box_1 = QTextEdit()
        self.input_box_1.setPlaceholderText(
            "Enter text to convert..."
        )

        # Output
        self.output_box_1 = QTextEdit()
        self.output_box_1.setPlaceholderText(
            "Converted output will appear here..."
        )
        self.output_box_1.setReadOnly(True)

        # Button
        self.calculate_output = QPushButton("Convert")

        # Options
        self.option_1_label = QLabel("From:")
        self.option_2_label = QLabel("To:")

        self.option_1 = QComboBox()
        self.option_2 = QComboBox()

        self.option_1.addItems(index_1)
        self.option_2.addItems(index_1)

        # Layouts
        master_layout = QHBoxLayout()

        left_layout = QVBoxLayout()
        right_layout = QVBoxLayout()

        # Left side
        left_layout.addWidget(self.title)
        left_layout.addStretch()

        left_layout.addWidget(self.calculate_output)

        left_layout.addWidget(self.option_1_label)
        left_layout.addWidget(self.option_1)

        left_layout.addWidget(self.option_2_label)
        left_layout.addWidget(self.option_2)

        left_layout.addStretch()

        # Right side
        right_layout.addWidget(QLabel("Input:"))
        right_layout.addWidget(self.input_box_1)

        right_layout.addWidget(QLabel("Output:"))
        right_layout.addWidget(self.output_box_1)

        master_layout.addLayout(left_layout, 2)
        master_layout.addLayout(right_layout, 8)

        self.setLayout(master_layout)

    # --------------------------------------------------
    # Window Settings
    # --------------------------------------------------

    def settings(self):

        self.setWindowTitle("Converter")
        self.setGeometry(300, 300, 900, 500)

        self.setStyleSheet("""
            QWidget {
                font-size: 14px;
            }

            QPushButton {
                padding: 8px;
                font-weight: bold;
            }

            QComboBox {
                padding: 6px;
            }

            QTextEdit {
                padding: 5px;
            }
        """)

    # --------------------------------------------------
    # Application Directory
    # --------------------------------------------------

    def get_app_directory(self):

        if getattr(sys, "frozen", False):
            # Running as a packaged EXE
            return Path(sys.executable).resolve().parent

        # Running as a normal Python script
        return Path(__file__).resolve().parent

    # --------------------------------------------------
    # Events
    # --------------------------------------------------

    def connect_events(self):

        self.option_1.currentIndexChanged.connect(
            lambda: self.update_options(1)
        )

        self.option_2.currentIndexChanged.connect(
            lambda: self.update_options(2)
        )

        self.calculate_output.clicked.connect(
            self.convert_click
        )

    # --------------------------------------------------
    # Prevent Same Options
    # --------------------------------------------------

    def update_options(self, changed):

        if self.option_1.count() < 2:
            return

        if changed == 1:

            selected = self.option_1.currentText()

            if selected == self.option_2.currentText():

                next_index = (
                    self.option_2.currentIndex() + 1
                ) % self.option_2.count()

                self.option_2.blockSignals(True)
                self.option_2.setCurrentIndex(next_index)
                self.option_2.blockSignals(False)

        else:

            selected = self.option_2.currentText()

            if selected == self.option_1.currentText():

                next_index = (
                    self.option_1.currentIndex() + 1
                ) % self.option_1.count()

                self.option_1.blockSignals(True)
                self.option_1.setCurrentIndex(next_index)
                self.option_1.blockSignals(False)

    # --------------------------------------------------
    # Execute Converter EXE
    # --------------------------------------------------

    def setup_exe(self, text, option_from, option_to):

        exe_name = f"{option_from}-{option_to}.exe"

        # Get folder containing Converter.exe
        app_directory = self.get_app_directory()

        # Find converter executable beside Converter.exe
        exe_path = app_directory / exe_name

        print("Looking for:", exe_path)

        if not exe_path.is_file():

            raise FileNotFoundError(
                f"Converter executable not found:\n{exe_path}"
            )

        result = subprocess.run(
            [str(exe_path), text],
            capture_output=True,
            text=True,
            check=True,
            timeout=30
        )

        return result.stdout.strip()

    # --------------------------------------------------
    # Convert Button
    # --------------------------------------------------

    def convert_click(self):

        text_to_convert = self.input_box_1.toPlainText()

        if not text_to_convert.strip():

            QMessageBox.warning(
                self,
                "Empty Input",
                "Please enter some text to convert."
            )
            return

        selected_1 = self.option_1.currentText()
        selected_2 = self.option_2.currentText()

        if selected_1 == selected_2:

            QMessageBox.warning(
                self,
                "Invalid Selection",
                "Please select two different options."
            )
            return

        self.calculate_output.setEnabled(False)
        self.calculate_output.setText("Converting...")

        try:

            converted_text = self.setup_exe(
                text_to_convert,
                selected_1,
                selected_2
            )

            self.output_box_1.setPlainText(
                converted_text
            )

        except FileNotFoundError as e:

            QMessageBox.critical(
                self,
                "File Not Found",
                str(e)
            )

        except subprocess.TimeoutExpired:

            QMessageBox.critical(
                self,
                "Timeout",
                "Conversion took too long."
            )

        except subprocess.CalledProcessError as e:

            QMessageBox.critical(
                self,
                "Conversion Error",
                e.stderr or str(e)
            )

        except Exception as e:

            QMessageBox.critical(
                self,
                "Error",
                str(e)
            )

        finally:

            self.calculate_output.setEnabled(True)
            self.calculate_output.setText("Convert")


# --------------------------------------------------
# Main
# --------------------------------------------------

if __name__ == "__main__":

    app = QApplication(sys.argv)

    main = Home()
    main.show()

    sys.exit(app.exec())
