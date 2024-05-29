import logging
from datetime import datetime

from cryptshare import CryptshareSender
from cryptshare.CryptshareNotificationMessage import CryptshareNotificationMessage
from cryptshare.CryptshareTransferSecurityMode import CryptshareTransferSecurityMode

logger = logging.getLogger(__name__)


class CryptshareTransferSettings:
    sender: CryptshareSender
    _expiration_date: datetime
    notification_message: CryptshareNotificationMessage
    security_mode: CryptshareTransferSecurityMode
    other_settings: dict

    def __init__(
        self,
        sender: CryptshareSender,
        expiration_date: datetime = None,
        notification_message: CryptshareNotificationMessage = None,
        security_mode: CryptshareTransferSecurityMode = None,
        **kwargs,
    ) -> None:
        """Initialises the TransferSettings object

        :param sender: The sender of the transfer
        :param expiration_date: The expiration date of the transfer
        :param notification_message: The notification message of the transfer
        :param security_mode: The security mode of the transfer
        :param fileChecksumAlgorithm: The file checksum algorithm of the transfer
        :param showZipFileContent: The show zip file content of the transfer
        :param sendDownloadNotifications: The send download notifications of the transfer
        :param sendDownloadSummary: The send download summary of the transfer
        :param sendRecipientNotification: The send recipient notification of the transfer
        :param sendUploadSummary: The send upload summary of the transfer
        :param senderLanguage: The sender language of the transfer
        :param showFileNames: The show file names of the transfer
        :param recipientLanguage: The recipient language of the transfer
        :param classificationId: The classification id of the transfer
        :param confidentialMessageFileId: The confidential message file id of the transfer
        """
        logger.debug("Initialising TransferSettings")
        self._expiration_date = expiration_date
        self.notification_message = notification_message
        self.security_mode = security_mode
        self.sender = sender
        self.security_mode = security_mode
        self.other_settings = kwargs

    @property
    def expiration_date_str(self) -> str:
        # Expiration date format in REST API: "2020-10-09T11:51:46+02:00"
        return self.format_expiration_date()

    @property
    def expiration_date(self) -> datetime:
        # Expiration date format in REST API: "2020-10-09T11:51:46+02:00"
        return self._expiration_date

    def format_expiration_date(self) -> str:
        formatted_expiration_date = self._expiration_date.astimezone().strftime("%Y-%m-%dT%H:%M:%S%z")
        expiration_date = formatted_expiration_date[:-2] + ":" + formatted_expiration_date[-2:]
        return expiration_date

    def data(self) -> dict:
        logger.debug("Returning TransferSettings data as dict")
        return_dict = {
            "notificationMessage": self.notification_message.data(),
            "securityMode": self.security_mode.data(),
            "sender": self.sender.data(),
            "expirationDate": self.expiration_date_str,
        } | {key: value for (key, value) in self.other_settings.items() if value != ""}

        return return_dict
