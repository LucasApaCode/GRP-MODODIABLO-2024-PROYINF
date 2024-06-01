import sys
import pydicom
import numpy as np
import cv2
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QFileDialog,
    QLabel,
    QSlider,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QComboBox,
    QFrame,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap


class DICOMViewer(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Procesador de Imagenes DICOM")
        self.setGeometry(100, 100, 1000, 700)

        self.initUI()

        self.original_image = None
        self.modified_image = None

    def initUI(self):
        self.setStyleSheet(
            """
            QWidget {
                background-color: #2c2c2c;
                color: #ffffff;
                font-size: 14px;
            }
            QPushButton {
                background-color: #5c5c5c;
                border: none;
                padding: 10px;
                border-radius: 5px;
                color: white;
            }
            QPushButton:hover {
                background-color: #777777;
            }
            QSlider::groove:horizontal {
                height: 10px;
                background: #444444;
                border-radius: 5px;
            }
            QSlider::handle:horizontal {
                background: #777777;
                border: 2px solid #444444;
                width: 20px;
                height: 20px;
                margin: -5px 0;
                border-radius: 10px;
            }
            QComboBox {
                background-color: #444444;
                border: 1px solid #777777;
                border-radius: 5px;
                padding: 5px;
                min-width: 100px;
            }
            QComboBox QAbstractItemView {
                background-color: #444444;
                selection-background-color: #777777;
            }
        """
        )

        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setFrameShape(QFrame.Box)
        self.image_label.setStyleSheet("QLabel { background-color: #000000; }")

        self.open_button = QPushButton("Abrir Imagen DICOM", self)
        self.open_button.clicked.connect(self.open_image)

        self.contrast_slider = QSlider(Qt.Horizontal, self)
        self.contrast_slider.setMinimum(1)
        self.contrast_slider.setMaximum(100)
        self.contrast_slider.setValue(50)
        self.contrast_slider.valueChanged.connect(self.update_image)

        self.negative_button = QPushButton("Aplicar Negativo", self)
        self.negative_button.setCheckable(True)
        self.negative_button.clicked.connect(self.update_image)

        self.color_map_box = QComboBox(self)
        self.color_map_box.addItems(["Ninguno", "Jet", "Hot", "Bone", "Winter"])
        self.color_map_box.currentIndexChanged.connect(self.update_image)

        self.save_button = QPushButton("Guardar Imagen", self)
        self.save_button.clicked.connect(self.save_image)

        controls_layout = QVBoxLayout()
        controls_layout.addWidget(self.open_button)
        controls_layout.addWidget(QLabel("Contraste"))
        controls_layout.addWidget(self.contrast_slider)
        controls_layout.addWidget(self.negative_button)
        controls_layout.addWidget(QLabel("Mapa de Color"))
        controls_layout.addWidget(self.color_map_box)
        controls_layout.addWidget(self.save_button)
        controls_layout.addStretch()

        main_layout = QHBoxLayout()
        main_layout.addLayout(controls_layout, 1)
        main_layout.addWidget(self.image_label, 4)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def open_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Abrir Imagen DICOM", "", "DICOM Files (*.dcm)"
        )
        if file_path:
            self.load_dicom_image(file_path)
            self.update_image()

    def load_dicom_image(self, file_path):
        dicom = pydicom.dcmread(file_path)
        self.original_image = dicom.pixel_array.astype(np.float32)
        self.modified_image = self.original_image.copy()

    def update_image(self):
        if self.original_image is not None:
            image = self.original_image.copy()

            contrast = self.contrast_slider.value() / 50.0
            image = cv2.convertScaleAbs(image, alpha=contrast, beta=0)

            if self.negative_button.isChecked():
                image = cv2.bitwise_not(image)

            color_map = self.color_map_box.currentText()
            if color_map != "Ninguno":
                colormaps = {
                    "Jet": cv2.COLORMAP_JET,
                    "Hot": cv2.COLORMAP_HOT,
                    "Bone": cv2.COLORMAP_BONE,
                    "Winter": cv2.COLORMAP_WINTER,
                }
                image_8bit = cv2.convertScaleAbs(image, alpha=255.0 / image.max())
                image = cv2.applyColorMap(image_8bit, colormaps[color_map])

            self.modified_image = image
            self.display_image(image)

    def display_image(self, image):
        if len(image.shape) == 2:
            qimage = QImage(
                image.data, image.shape[1], image.shape[0], QImage.Format_Grayscale8
            )
        else:
            qimage = QImage(
                image.data, image.shape[1], image.shape[0], QImage.Format_RGB888
            )
            qimage = qimage.rgbSwapped()
        pixmap = QPixmap.fromImage(qimage)
        self.image_label.setPixmap(pixmap)

    def save_image(self):
        if self.modified_image is not None:
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Guardar Imagen",
                "",
                "PNG Files (*.png);;JPEG Files (*.jpg);;All Files (*)",
            )
            if file_path:
                cv2.imwrite(file_path, self.modified_image)


def main():
    app = QApplication(sys.argv)
    viewer = DICOMViewer()
    viewer.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
