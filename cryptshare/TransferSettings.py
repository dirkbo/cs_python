import logging

logger = logging.getLogger(__name__)


class TransferSettings:
    def __init__(
        self,
        sender,
        expiration_date=None,
        notification_message=None,
        file_checksum_algorithm=None,
        show_zip_file_content=None,
        send_download_notifications=None,
        send_download_summary=None,
        send_recipient_notification=None,
        send_upload_summary=None,
        sender_language=None,
        show_file_names=None,
        recipient_language=None,
        classification_id=None,
        confidential_message_file_id=None,
        security_mode=None,
    ):
        logger.debug("Initialising TransferSettings")
        self.expiration_date = expiration_date
        self.notification_message = notification_message
        self.security_mode = security_mode
        self.file_checksum_algorithm = file_checksum_algorithm
        self.show_zip_file_content = show_zip_file_content
        self.send_download_notifications = send_download_notifications
        self.send_download_summary = send_download_summary
        self.send_recipient_notification = send_recipient_notification
        self.send_upload_summary = send_upload_summary
        self.sender = sender
        self.sender_language = sender_language
        self.show_file_names = show_file_names
        self.recipient_language = recipient_language
        self.classification_id = classification_id
        self.confidential_message_file_id = confidential_message_file_id
        self.security_mode = security_mode

    def data(self):
        logger.debug("Returning TransferSettings data")
        return_dict = {
            "notificationMessage": self.notification_message.data(),
            "recipientLanguage": self.recipient_language,
            "securityMode": self.security_mode.data(),
            "sendDownloadNotifications": self.send_download_notifications,
            "sendDownloadSummary": self.send_download_summary,
            "sendRecipientNotification": self.send_recipient_notification,
            "sendUploadSummary": self.send_upload_summary,
            "sender": self.sender.data(),
            "senderLanguage": self.sender_language,
            "showFileNames": self.show_file_names,
            "showZipFileContent": self.show_zip_file_content,
            "expirationDate": self.expiration_date,
            "fileChecksumAlgorithm": self.file_checksum_algorithm,
            "classificationId": self.classification_id,
            "confidentialMessageFileId": self.confidential_message_file_id,
        }
        return return_dict
