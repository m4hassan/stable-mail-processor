from abc import ABC, abstractmethod

class DriveService(ABC):
    @abstractmethod
    def list_folders(self):
        pass

    @abstractmethod
    def create_folder(self, folder_name):
        pass

    @abstractmethod
    def upload_file(self, file_name, file_content, folder_id):
        pass

    @abstractmethod
    def delete_all_folders(self):
        """Delete all folders in the drive"""
        pass

class DatabaseService(ABC):
    @abstractmethod
    def get_processed_mail_ids(self):
        pass

    @abstractmethod
    def save_processed_mail_id(self, mail_id, recipient_name):
        pass

class MailService(ABC):
    @abstractmethod
    def fetch_mail_items(self, status="completed"):
        pass

    @abstractmethod
    def extract_recipient_name(self, mail_item):
        pass
