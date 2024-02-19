import sys
import cv2
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton, QHBoxLayout, \
    QMessageBox, QInputDialog
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QImage, QPixmap
from imutils.video import VideoStream
import imutils
import os
import random
import string
import face_recognition


class POSApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("FacePOS")
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout(self.central_widget)

        self.camera_label = QLabel(self)
        self.layout.addWidget(self.camera_label, alignment=Qt.AlignCenter)

        self.button_layout = QHBoxLayout()

        self.register_button = QPushButton("Register Face", self)
        self.register_button.clicked.connect(self.register_face)
        self.button_layout.addWidget(self.register_button)

        self.transaction_button = QPushButton("Transaction", self)
        self.transaction_button.clicked.connect(self.perform_transaction)
        self.button_layout.addWidget(self.transaction_button)

        self.add_money_button = QPushButton("Add Money", self)
        self.add_money_button.clicked.connect(self.add_money)
        self.button_layout.addWidget(self.add_money_button)

        self.inquiry_button = QPushButton("Inquiry", self)
        self.inquiry_button.clicked.connect(self.inquire_balance)
        self.button_layout.addWidget(self.inquiry_button)

        self.layout.addLayout(self.button_layout)

        # Load known faces and balances from the "faces" and "balances" folders
        self.known_faces, self.face_balances = self.load_known_faces_and_balances("faces", "balances")

        # Initialize the video stream
        self.video_stream = VideoStream(src=0).start()

        # Set up a timer to update the camera feed
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_camera)
        self.timer.start(30)  # Update every 30 milliseconds

        # Variable to store the currently detected face
        self.current_face = None

    def load_known_faces_and_balances(self, faces_folder, balances_folder):
        known_faces = []
        face_balances = {}

        for filename in os.listdir(faces_folder):
            if filename.endswith(".jpg") or filename.endswith(".png"):
                face_name = os.path.splitext(filename)[0]
                face_image = cv2.imread(os.path.join(faces_folder, filename))

                # Check if face_encodings list is not empty before accessing its first element
                face_encodings = face_recognition.face_encodings(face_image)
                if not face_encodings:
                    print(f"No face found in {filename}")
                    continue

                encoding = face_encodings[0]
                known_faces.append({"encoding": encoding, "name": face_name})

                # Load face balances from the "balances" folder
                balance_filename = face_name + "_balance.txt"
                balance_path = os.path.join(balances_folder, balance_filename)
                if os.path.exists(balance_path):
                    with open(balance_path, 'r') as balance_file:
                        face_balances[face_name] = float(balance_file.read())
                else:
                    face_balances[face_name] = 0.0

        return known_faces, face_balances

    def update_camera(self):
        # Read a frame from the video stream
        frame = self.video_stream.read()

        # Resize the frame for better performance
        frame = imutils.resize(frame, width=800)

        # Convert the OpenCV frame to QImage
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = image.shape
        bytes_per_line = ch * w
        q_image = QImage(image.data, w, h, bytes_per_line, QImage.Format_RGB888)

        # Display the QImage in the QLabel
        pixmap = QPixmap.fromImage(q_image)
        self.camera_label.setPixmap(pixmap)

        # Recognize faces in the frame
        recognized_faces = self.recognize_faces(frame)

        # Process the recognized faces (link balances, etc.)
        self.process_faces(recognized_faces)

    def recognize_faces(self, frame):
        face_locations = face_recognition.face_locations(frame)
        face_encodings = face_recognition.face_encodings(frame, face_locations)

        recognized_faces = []
        for encoding in face_encodings:
            matches = face_recognition.compare_faces([face["encoding"] for face in self.known_faces], encoding)
            name = "Unknown"
            if True in matches:
                first_match_index = matches.index(True)
                name = self.known_faces[first_match_index]["name"]
                # Store the currently detected face
                self.current_face = name
            recognized_faces.append(name)
        return recognized_faces

    def process_faces(self, recognized_faces):
        # Placeholder for face processing logic
        for name in recognized_faces:
            if name == "Unknown":
                self.register_button.setEnabled(True)
                self.transaction_button.setEnabled(False)
                self.add_money_button.setEnabled(False)
                self.inquiry_button.setEnabled(False)
            else:
                self.register_button.setEnabled(False)
                self.transaction_button.setEnabled(True)
                self.add_money_button.setEnabled(True)
                self.inquiry_button.setEnabled(True)

    def register_face(self):
        # Disable buttons while processing
        self.register_button.setEnabled(False)
        self.transaction_button.setEnabled(False)
        self.add_money_button.setEnabled(False)
        self.inquiry_button.setEnabled(False)

        # Capture a frame for registration
        frame = self.video_stream.read()

        # Find faces in the frame
        face_locations = face_recognition.face_locations(frame)

        if face_locations:
            # Take the first face found
            top, right, bottom, left = face_locations[0]

            # Crop the face from the frame
            face_image = frame[top:bottom, left:right]

            # Generate a random 12-digit number starting with 42 as the filename
            filename = f"42{''.join(random.choices(string.digits, k=10))}.jpg"

            # Save the face image to the "faces" folder
            face_path = os.path.join("faces", filename)
            cv2.imwrite(face_path, cv2.cvtColor(face_image, cv2.COLOR_RGB2BGR))

            # Create a text file with the same name in the "balances" folder and set the default balance to zero
            balance_filename = os.path.splitext(filename)[0] + "_balance.txt"
            balance_path = os.path.join("balances", balance_filename)
            with open(balance_path, 'w') as balance_file:
                balance_file.write("0")

            # Show a confirmation popup
            self.show_popup("Success", f"Face registered: {filename}")

        else:
            # Show a failure popup
            self.show_popup("Failure", "No face detected for registration")

        # Re-enable buttons
        self.register_button.setEnabled(True)
        self.transaction_button.setEnabled(True)
        self.add_money_button.setEnabled(True)
        self.inquiry_button.setEnabled(True)

    def perform_transaction(self):
        self.handle_money_operation("Transaction", -1)

    def add_money(self):
        self.handle_money_operation("Add Money", 1)

    def handle_money_operation(self, operation_type, sign):
        # Disable buttons while processing
        self.register_button.setEnabled(False)
        self.transaction_button.setEnabled(False)
        self.add_money_button.setEnabled(False)
        self.inquiry_button.setEnabled(False)

        if self.current_face is not None:
            # Get the transaction amount as a string
            amount_str, ok_pressed = QInputDialog.getText(self, operation_type,
                                                          f"Enter {operation_type} amount (e.g., 12+4):")

            if ok_pressed:
                # Evaluate the expression and get the result as a float
                try:
                    amount = eval(amount_str)
                    amount = float(amount)
                except Exception as e:
                    # If evaluation fails, show an error message
                    self.show_popup("Error", "Invalid expression. Please enter a valid numerical expression.")
                    return

                # Update the face balance
                self.face_balances[self.current_face] += sign * amount

                # Update the text file in the "balances" folder
                balance_filename = self.current_face + "_balance.txt"
                balance_path = os.path.join("balances", balance_filename)
                with open(balance_path, 'w') as balance_file:
                    balance_file.write(str(self.face_balances[self.current_face]))

                # Show a transaction completed popup
                self.show_popup(f"{operation_type} Completed",
                                f"{operation_type} completed for {self.current_face}: +{amount}")

        # Re-enable buttons
        self.register_button.setEnabled(True)
        self.transaction_button.setEnabled(True)
        self.add_money_button.setEnabled(True)
        self.inquiry_button.setEnabled(True)

    def inquire_balance(self):
        if self.current_face is not None:
            # Show the balance in a popup
            balance = self.face_balances[self.current_face]
            self.show_popup("Balance Inquiry", f"Balance for {self.current_face}: {balance}")
        else:
            # Show a message if no face is detected
            self.show_popup("No Face Detected", "No face detected for balance inquiry")

    def show_popup(self, title, message):
        msg_box = QMessageBox()
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.exec_()

    def closeEvent(self, event):
        # Release the video stream when closing the application
        self.video_stream.stop()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    pos_app = POSApp()
    pos_app.show()
    sys.exit(app.exec_())
