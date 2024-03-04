import sys
import csv
import os
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QPushButton, QLabel, QFileDialog
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("System Management GUI")
        self.setGeometry(100, 100, 800, 600)

        self.home_layout = QVBoxLayout()
        self.setLayout(self.home_layout)

        # Creating home screen option buttons
        self.installation_button = QPushButton("Installation: Set Parameters for New System")
        self.installation_button.clicked.connect(self.installation_screen)
        self.home_layout.addWidget(self.installation_button)

        self.view_data_button = QPushButton("View Downloaded Data")
        self.view_data_button.clicked.connect(self.view_data_screen)
        self.home_layout.addWidget(self.view_data_button)

        self.download_data_button = QPushButton("Download Data")
        self.home_layout.addWidget(self.download_data_button)

        self.select_system_button = QPushButton("Select Existing System")
        self.home_layout.addWidget(self.select_system_button)

        self.create_system_button = QPushButton("Create New System")
        self.create_system_button.clicked.connect(self.installation_screen)
        self.home_layout.addWidget(self.create_system_button)

        self.home_layout.addStretch(1)  # Add stretch to push buttons to the top

    def installation_screen(self):
        # Implementation of installation screen
        pass

    def view_data_screen(self):
        self.clear_layout()
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.dropdown = QComboBox()
        self.dropdown.activated.connect(self.plot_data)
        layout.addWidget(self.dropdown)

        self.plot_button = QPushButton("Plot Data")
        self.plot_button.clicked.connect(self.plot_data)
        layout.addWidget(self.plot_button)

        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        self.load_csv_files()

    def load_csv_files(self):
        # Change this path to your directory where CSV files are stored
        directory = '/path/to/your/csv/files/'

        # Add CSV files to dropdown menu
        csv_files = [file for file in os.listdir(directory) if file.endswith('.csv')]
        self.dropdown.addItems(csv_files)

    def plot_data(self):
        filename = self.dropdown.currentText()
        if filename:
            # Clear previous plot
            self.figure.clear()
            ax = self.figure.add_subplot(111)

            with open(filename, 'r') as csvfile:
                csv_reader = csv.DictReader(csvfile)
                data = {'OutsideAir': [], 'MixedAir': []}
                for row in csv_reader:
                    data['OutsideAir'].append(float(row['OutsideAir']))
                    data['MixedAir'].append(float(row['MixedAir']))

                ax.plot(data['OutsideAir'], data['MixedAir'], 'o', label='Data')
                ax.set_xlabel('Outside Air (°C)')
                ax.set_ylabel('Mixed Air (°C)')
                ax.set_title('Outside Air vs Mixed Air Temperature')
                ax.legend()
                self.canvas.draw()

    def clear_layout(self):
        for i in reversed(range(self.layout().count())):
            self.layout().itemAt(i).widget().setParent(None)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())
