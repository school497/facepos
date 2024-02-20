import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QMessageBox, QInputDialog, QLineEdit
import os

class SelectorWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Edition Selector")
        self.setGeometry(100, 100, 400, 300)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout(self.central_widget)

        self.business_button = QPushButton("Business Edition", self)
        self.business_button.clicked.connect(self.select_business_edition)
        self.layout.addWidget(self.business_button)

        self.bank_button = QPushButton("Bank Edition", self)
        self.bank_button.clicked.connect(self.select_bank_edition)
        self.layout.addWidget(self.bank_button)

        self.civilian_button = QPushButton("Civilian Edition", self)
        self.civilian_button.clicked.connect(self.select_civilian_edition)
        self.layout.addWidget(self.civilian_button)

        self.create_folders()  # Create necessary folders

    def select_business_edition(self):
        choice = QMessageBox.question(self, "Business Edition", "Do you already have a business?",
                                       QMessageBox.Yes | QMessageBox.No)
        if choice == QMessageBox.Yes:
            self.login_business()
        else:
            self.register_business()

    def select_bank_edition(self):
        username, password, ok = self.get_login_credentials("Bank Edition")
        if ok and username == "milo" and password == "milo":
            os.system("python3 bank.py")
            self.close()
        else:
            QMessageBox.warning(self, "Error", "Invalid credentials.")

    def select_civilian_edition(self):
        os.system("python3 civilian.py")
        self.close()

    def get_login_credentials(self, edition):
        username, ok1 = QInputDialog.getText(self, edition, "Enter Username:")
        password, ok2 = QInputDialog.getText(self, edition, "Enter Password:", QLineEdit.Password)
        return username, password, ok1 and ok2

    def login_business(self):
        os.system("python3 business.py")
        self.close()

    def register_business(self):
        business_name, ok = QInputDialog.getText(self, "Register Business", "Enter Business Name:")
        if ok:
            username, ok1 = QInputDialog.getText(self, "Register Business", "Enter Username:")
            password, ok2 = QInputDialog.getText(self, "Register Business", "Enter Password:", QLineEdit.Password)
            if ok1 and ok2:
                # Save business information to a file
                business_file = os.path.join("business", f"{business_name}.txt")
                with open(business_file, "w") as file:
                    file.write(f"{business_name}\n{username}\n{password}\n0")  # Default balance is 0
                QMessageBox.information(self, "Registration Successful", f"Business '{business_name}' registered successfully.")

    def create_folders(self):
        # Create necessary folders if they don't exist
        folders = ["faces", "balances", "business"]
        for folder in folders:
            if not os.path.exists(folder):
                os.makedirs(folder)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    selector_window = SelectorWindow()
    selector_window.show()
    sys.exit(app.exec_())
