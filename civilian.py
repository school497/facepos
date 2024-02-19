import sys
import cv2
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QMessageBox, QPushButton, QInputDialog, QLineEdit
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QImage, QPixmap
from imutils.video import VideoStream
import imutils
import os
import face_recognition


class CivilianPOSApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Civilian POS")
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout(self.central_widget)

        self.camera_label = QLabel(self)
        self.layout.addWidget(self.camera_label, alignment=Qt.AlignCenter)

        self.business_name_label = QLabel(self)
        self.layout.addWidget(self.business_name_label, alignment=Qt.AlignCenter)

        self.balance_label = QLabel(self)
        self.layout.addWidget(self.balance_label, alignment=Qt.AlignCenter)

        self.transfer_button = QPushButton("Transfer Money", self)
        self.transfer_button.clicked.connect(self.transfer_money)
        self.layout.addWidget(self.transfer_button, alignment=Qt.AlignCenter)

        self.deregister_button = QPushButton("Deregister", self)
        self.deregister_button.clicked.connect(self.deregister)
        self.layout.addWidget(self.deregister_button, alignment=Qt.AlignCenter)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_camera)
        self.timer.start(100)  # Update every 100 milliseconds

        self.civilian_name = None
        self.civilian_balance = 0.0

        self.known_faces = self.load_known_faces("./faces")

        self.video_stream = VideoStream(src=0).start()

        self.login_civilian()

    def load_known_faces(self, faces_folder):
        known_faces = []

        for filename in os.listdir(faces_folder):
            if filename.endswith(".jpg") or filename.endswith(".png"):
                civilian_name = os.path.splitext(filename)[0]
                face_image = face_recognition.load_image_file(os.path.join(faces_folder, filename))
                face_encoding = face_recognition.face_encodings(face_image)[0]
                known_faces.append({"encoding": face_encoding, "name": civilian_name})

        return known_faces

    def login_civilian(self):
        match_found = False
        while not match_found:
            frame = self.video_stream.read()
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(rgb_frame)
            face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

            if not face_encodings:
                self.show_register_popup()
                sys.exit()

            for face_encoding in face_encodings:
                matches = face_recognition.compare_faces([face["encoding"] for face in self.known_faces], face_encoding)
                if True in matches:
                    match_found = True
                    break

            if match_found:
                self.civilian_name = [face["name"] for face in self.known_faces if face_recognition.compare_faces([face["encoding"]], face_encoding)][0]
                self.business_name_label.setText(f"Civilian: {self.civilian_name}")
                self.load_civilian_balance()
                break

    def load_civilian_balance(self):
        balance_file = os.path.join("./balances", f"{self.civilian_name}_balance.txt")
        if os.path.exists(balance_file):
            with open(balance_file, "r") as file:
                self.civilian_balance = float(file.read().strip())
                self.balance_label.setText(f"Balance: ${self.civilian_balance:.2f}")
        else:
            self.balance_label.setText("Balance: $0.00")
            QMessageBox.warning(self, "Error", "Balance file not found. Please contact support.")

    def update_camera(self):
        frame = self.video_stream.read()
        frame = imutils.resize(frame, width=800)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        self.camera_label.setPixmap(QPixmap.fromImage(QImage(rgb_frame.data, rgb_frame.shape[1], rgb_frame.shape[0], QImage.Format_RGB888)))

    def transfer_money(self):
        recipient, ok = QInputDialog.getItem(self, "Transfer Money", "Select recipient:", [face["name"] for face in self.known_faces])
        if ok:
            amount, ok = QInputDialog.getDouble(self, "Transfer Money", "Enter amount to transfer:")
            if ok:
                if amount > self.civilian_balance:
                    QMessageBox.warning(self, "Insufficient Funds", "You don't have enough funds for this transfer.")
                else:
                    self.civilian_balance -= amount
                    self.balance_label.setText(f"Balance: ${self.civilian_balance:.2f}")
                    self.update_civilian_balance_file()
                    recipient_balance_file = os.path.join("./balances", f"{recipient}_balance.txt")
                    if os.path.exists(recipient_balance_file):
                        with open(recipient_balance_file, "r+") as file:
                            recipient_balance = float(file.read().strip())
                            recipient_balance += amount
                            file.seek(0)
                            file.write(f"{recipient_balance:.2f}")
                    QMessageBox.information(self, "Transfer Successful", f"${amount:.2f} transferred to {recipient}.")

    def deregister(self):
        if self.civilian_balance == 0.0:
            face_file = os.path.join("./faces", f"{self.civilian_name}.jpg")
            balance_file = os.path.join("./balances", f"{self.civilian_name}_balance.txt")
            if os.path.exists(face_file):
                os.remove(face_file)
            if os.path.exists(balance_file):
                os.remove(balance_file)
            QMessageBox.information(self, "Deregistration Successful", "You have been deregistered successfully.")
            sys.exit()
        else:
            QMessageBox.warning(self, "Error", "You cannot deregister while you still have funds in your account.")

    def update_civilian_balance_file(self):
        balance_file = os.path.join("./balances", f"{self.civilian_name}_balance.txt")
        with open(balance_file, "w") as file:
            file.write(f"{self.civilian_balance:.2f}")

    def show_register_popup(self):
        QMessageBox.warning(self, "Unregistered User", "To use the service, you must register with the bank.")
        sys.exit()

    def closeEvent(self, event):
        self.video_stream.stop()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    pos_app = CivilianPOSApp()
    pos_app.show()
    sys.exit(app.exec_())
