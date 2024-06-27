import sys
import os
import pydicom
import numpy as np
import cv2
from PyQt5.QtWidgets import (
    QApplication,
    QMessageBox,
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
    QGraphicsView,
    QGraphicsScene,
    QGraphicsPixmapItem,
    QGraphicsItem,
    QGraphicsDropShadowEffect,
)
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QImage, QPixmap, QIcon, QWheelEvent, QColor


class DICOMViewer(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Visualizador DICOM")
        self.setGeometry(100, 100, 1000, 700)

        
        self.setWindowIcon(
            QIcon("ruta/al/icono.ico")
        )  
        self.initUI()

        self.original_image = None
        self.modified_image = None

    def initUI(self):
        # Configurar la interfaz moderna
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
            QPushButton:checked {
                background-color: #ff6347; 
            }
            QPushButton:hover {
                background-color: #777777;
            }
            QPushButton:disabled {
                background-color: #444444; 
                color: #888888;
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
            QFrame#controls_frame {
                background-color: #3c3c3c; 
                border-radius: 10px;
                padding: 10px;
            }
            QGraphicsView {
                background-color: #1c1c1c; 
            }
        """
        )

        self.graphics_view = GraphicsView(self)
        self.graphics_scene = QGraphicsScene(self)
        self.graphics_view.setScene(self.graphics_scene)
        self.image_item = QGraphicsPixmapItem()
        self.graphics_scene.addItem(self.image_item)

        self.open_button = QPushButton("Abrir Imagen", self)
        self.open_button.clicked.connect(self.open_image)

        self.contrast_slider = QSlider(Qt.Horizontal, self)
        self.contrast_slider.setMinimum(-50)
        self.contrast_slider.setMaximum(50)
        self.contrast_slider.setValue(0)
        self.contrast_slider.valueChanged.connect(self.update_image)

        self.contrast_label = QLabel("Contraste: 0%", self)

        self.negative_button = QPushButton("Aplicar Negativo", self)
        self.negative_button.setCheckable(True)
        self.negative_button.clicked.connect(self.update_image)

        self.color_map_box = QComboBox(self)
        self.color_map_box.addItems(["Ninguno", "Jet", "Hot", "Bone", "Winter"])
        self.color_map_box.currentIndexChanged.connect(self.update_image)

        self.save_button = QPushButton("Guardar Imagen", self)
        self.save_button.clicked.connect(self.save_image)
        self.save_button.setEnabled(False)

        # Cuantificador de zoom
        self.zoom_label = QLabel("Zoom: 100%", self)
        self.zoom_factor = 1.0

        controls_layout = QVBoxLayout()
        controls_layout.addWidget(self.open_button)
        controls_layout.addWidget(self.contrast_label)
        controls_layout.addWidget(self.contrast_slider)
        controls_layout.addWidget(self.negative_button)
        controls_layout.addWidget(QLabel("Mapa de Color"))
        controls_layout.addWidget(self.color_map_box)
        controls_layout.addStretch()
        controls_layout.addWidget(self.save_button)

        controls_frame = QFrame()
        controls_frame.setObjectName("controls_frame")
        controls_frame.setLayout(controls_layout)

        right_layout = QVBoxLayout()
        right_layout.addWidget(self.graphics_view)
        right_layout.addWidget(self.zoom_label, alignment=Qt.AlignRight)

        main_layout = QHBoxLayout()
        main_layout.addWidget(controls_frame, 1)
        main_layout.addLayout(right_layout, 4)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def open_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Abrir Imagen", "", "Archivos DICOM (*.dcm)"
        )
        if file_path:
            self.load_dicom_image(file_path)
            self.update_image()
            self.save_button.setEnabled(
                True
            )  

    def load_dicom_image(self, file_path):
        dicom = pydicom.dcmread(file_path)
        self.original_image = dicom.pixel_array.astype(np.float32)
        self.modified_image = self.original_image.copy()

    def update_image(self):
        if self.original_image is not None:
            image = self.original_image.copy()

            
            contrast = (self.contrast_slider.value() + 50) / 50.0
            image = cv2.convertScaleAbs(image, alpha=contrast, beta=0)

           
            self.contrast_label.setText(f"Contraste: {self.contrast_slider.value()}%")

            
            if self.negative_button.isChecked():
                image = cv2.bitwise_not(image)

            
            color_map = self.color_map_box.currentText()
            if (color_map != "Ninguno") and (
                len(image.shape) == 2
            ):  
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
        if len(image.shape) == 2:  # Grayscale image
            qimage = QImage(
                image.data, image.shape[1], image.shape[0], QImage.Format_Grayscale8
            )
        else:  # Color image
            qimage = QImage(
                image.data, image.shape[1], image.shape[0], QImage.Format_RGB888
            )
            qimage = qimage.rgbSwapped()
        pixmap = QPixmap.fromImage(qimage)
        self.image_item.setPixmap(pixmap)
        self.graphics_scene.setSceneRect(QRectF(pixmap.rect()))

    def save_image(self):
        if self.modified_image is not None:
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Guardar Imagen ",
                "",
                "PNG Files (*.png);;JPEG Files (*.jpg);;All Files (*)",
            )
            if file_path:
                directory = os.path.dirname(file_path)
                if not os.access(directory, os.W_OK):
                    QMessageBox.critical(
                        self,
                        "Error",
                        f"No tienes permisos de escritura en: {directory}",
                    )
                    return

                try:
                    if file_path.lower().endswith(".jpg") or file_path.lower().endswith(
                        ".jpeg"
                    ):
                        cv2.imwrite(
                            file_path,
                            self.modified_image,
                            [int(cv2.IMWRITE_JPEG_QUALITY), 90],
                        )
                    else:
                        cv2.imwrite(file_path, self.modified_image)
                    QMessageBox.information(
                        self, "Exito", f"Imagen exitosamente guardada en {file_path}"
                    )
                except Exception as e:
                    QMessageBox.critical(
                        self, "Error", f"Error al guardar la imagen: {e}"
                    )

    def update_zoom_label(self):
        self.zoom_label.setText(f"Zoom: {int(self.zoom_factor * 100)}%")


class GraphicsView(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.parent = parent

    def wheelEvent(self, event: QWheelEvent):
        zoom_in_factor = 1.25
        zoom_out_factor = 1 / zoom_in_factor

        if event.angleDelta().y() > 0:
            zoom_factor = zoom_in_factor
        else:
            zoom_factor = zoom_out_factor

        self.parent.zoom_factor *= zoom_factor
        self.parent.update_zoom_label()

        self.scale(zoom_factor, zoom_factor)


def main():
    app = QApplication(sys.argv)
    
    app.setWindowIcon(
        QIcon("ruta/al/icono.ico")
    )  
    viewer = DICOMViewer()
    viewer.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
