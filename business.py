import sys
import cv2
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton, QMessageBox, QInputDialog, QComboBox
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QImage, QPixmap
from imutils.video import VideoStream
import imutils
import os
import face_recognition


class BusinessPOSApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Business POS")
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout(self.central_widget)

        self.camera_label = QLabel(self)
        self.layout.addWidget(self.camera_label, alignment=Qt.AlignCenter)

        self.transaction_button = QPushButton("Transaction", self)
        self.transaction_button.clicked.connect(self.perform_transaction)
        self.layout.addWidget(self.transaction_button, alignment=Qt.AlignCenter)

        self.transfer_money_button = QPushButton("Transfer Money", self)
        self.transfer_money_button.clicked.connect(self.transfer_money)
        self.layout.addWidget(self.transfer_money_button, alignment=Qt.AlignCenter)

        self.business_name_label = QLabel(self)
        self.layout.addWidget(self.business_name_label, alignment=Qt.AlignCenter)

        self.balance_label = QLabel(self)
        self.layout.addWidget(self.balance_label, alignment=Qt.AlignCenter)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_camera)
        self.timer.start(100)  # Update every 100 milliseconds

        self.business_name = None
        self.business_balance = 0.0

        self.known_faces = self.load_known_faces("faces")

        self.video_stream = VideoStream(src=0).start()

        self.login_business()

    def load_known_faces(self, faces_folder):
        known_faces = []

        for filename in os.listdir(faces_folder):
            if filename.endswith(".jpg") or filename.endswith(".png"):
                face_name = os.path.splitext(filename)[0]
                face_image = face_recognition.load_image_file(os.path.join(faces_folder, filename))
                face_encoding = face_recognition.face_encodings(face_image)[0]
                known_faces.append({"encoding": face_encoding, "name": face_name})

        return known_faces

    def login_business(self):
        while True:
            username, ok = QInputDialog.getText(self, "Login Business", "Enter username:")
            if not ok:
                sys.exit()

            password, ok = QInputDialog.getText(self, "Login Business", "Enter password:")
            if not ok:
                sys.exit()

            business_files = [f for f in os.listdir("business") if f.endswith(".txt")]
            for business_file in business_files:
                with open(os.path.join("business", business_file), "r") as file:
                    data = file.read().splitlines()
                    if username == data[1] and password == data[2]:
                        self.business_name = data[0]
                        self.business_name_label.setText(f"Business: {self.business_name}")
                        self.business_balance = float(data[3])
                        self.update_balance_label()
                        return

            QMessageBox.warning(self, "Error", "Invalid credentials. Please try again.")

    def update_camera(self):
        frame = self.video_stream.read()
        frame = imutils.resize(frame, width=800)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        self.camera_label.setPixmap(QPixmap.fromImage(QImage(rgb_frame.data, rgb_frame.shape[1], rgb_frame.shape[0], QImage.Format_RGB888)))

    def perform_transaction(self):
        if not self.business_name:
            QMessageBox.warning(self, "Error", "Please log in to your business.")
            return

        match_found = False
        frame = self.video_stream.read()
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces([face["encoding"] for face in self.known_faces], face_encoding)
            if True in matches:
                match_found = True
                break

        if not match_found:
            QMessageBox.warning(self, "Error", "The person on the camera is not registered. Transaction cannot be performed.")
            return

        customer_name = None
        for face in self.known_faces:
            if face_recognition.compare_faces([face["encoding"]], face_encoding)[0]:
                customer_name = face["name"]
                break

        customer_balance = 0.0
        with open(os.path.join("../facebank2/balances", f"{customer_name}_balance.txt"), "r") as file:
            customer_balance = float(file.readline().strip())

        transaction_amount, ok = QInputDialog.getDouble(self, "Transaction", "Enter amount to subtract from customer:")
        if ok:
            if customer_balance >= transaction_amount:
                customer_balance -= transaction_amount
                self.business_balance += transaction_amount
                self.update_balance_label()

                with open(os.path.join("../facebank2/balances", f"{customer_name}_balance.txt"), "w") as file:
                    file.write(f"{customer_balance:.2f}")

                with open(os.path.join("../facebank2/business", f"{self.business_name}.txt"), "r+") as file:
                    lines = file.readlines()
                    lines[3] = f"{self.business_balance:.2f}\n"
                    file.seek(0)
                    file.writelines(lines)
            else:
                QMessageBox.warning(self, "Insufficient Funds", "The customer has insufficient funds for this transaction.")

    def transfer_money(self):
        if not self.business_name:
            QMessageBox.warning(self, "Error", "Please log in to your business.")
            return

        transfer_amount, ok = QInputDialog.getDouble(self, "Transfer Money", "Enter amount to transfer:")
        if not ok:
            return

        transfer_recipient_names = [face["name"] for face in self.known_faces]
        recipient, ok = QInputDialog.getItem(self, "Transfer Money", "Select recipient:", transfer_recipient_names, 0, False)
        if not ok:
            return

        recipient_balance = 0.0
        with open(os.path.join("../facebank2/balances", f"{recipient}_balance.txt"), "r") as file:
            recipient_balance = float(file.readline().strip())

        if self.business_balance >= transfer_amount:
            self.business_balance -= transfer_amount
            recipient_balance += transfer_amount
            self.update_balance_label()

            with open(os.path.join("../facebank2/balances", f"{recipient}_balance.txt"), "w") as file:
                file.write(f"{recipient_balance:.2f}")

            with open(os.path.join("../facebank2/business", f"{self.business_name}.txt"), "r+") as file:
                lines = file.readlines()
                lines[3] = f"{self.business_balance:.2f}\n"
                file.seek(0)
                file.writelines(lines)

            QMessageBox.information(self, "Transfer Money", f"${transfer_amount:.2f} transferred to {recipient}.")
        else:
            QMessageBox.warning(self, "Insufficient Funds", "You have insufficient funds for this transfer.")

    def update_balance_label(self):
        self.balance_label.setText(f"Balance: ${self.business_balance:.2f}")

    def closeEvent(self, event):
        self.video_stream.stop()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    pos_app = BusinessPOSApp()
    pos_app.show()
    sys.exit(app.exec_())
