import logging

from cryptshare.CryptshareTransferSecurityMode import SecurityModes

logger = logging.getLogger(__name__)


class CryptshareTransferPolicy:
    _policy: dict

    def __init__(self, policy: dict = None):
        self._policy = policy

    def get_allowed_security_modes(self) -> [SecurityModes, None]:
        """Returns the allowed security modes for the transfer"""
        security_modes: list = self.get_settings().get("securityModes", list())
        logger.debug(f"Security Modes raw: {security_modes}")
        modes = []
        for security_mode in security_modes:
            if security_mode["name"] == "ONE_TIME_PASSWORD":
                if "MANUAL" in security_mode.get("config", dict()).get("allowedPasswordModes", list()):
                    modes.append(SecurityModes.MANUAL)
                if "GENERATED" in security_mode.get("config", dict()).get("allowedPasswordModes", list()):
                    modes.append(SecurityModes.GENERATED)
                if "NONE" in security_mode.get("config", dict()).get("allowedPasswordModes", list()):
                    modes.append(SecurityModes.NONE)
        logger.debug(f"Allowed Security Modes: {modes}")
        return modes

    @property
    def maximum_retention_time(self) -> int:
        """Returns the maximum retention time for the transfer"""
        return self.get_settings().get("maxRetentionPeriod", 0)

    @property
    def is_allowed_editing_recipient_notification(self) -> bool:
        """Checks if the recipient notification is editable"""
        return self.get_settings().get("recipientNotificationEditable", False)

    @property
    def is_allowed(self) -> bool:
        """Checks if the transfer is allowed"""
        if not self._policy:
            return False
        return self._policy.get("allowed", False)

    def get_settings(self) -> dict:
        """Returns the policy settings"""
        if not self._policy:
            return {}
        return self._policy.get("settings", {})

    @property
    def policy(self):
        if not self._policy:
            return {}
        return self._policy

    def __repr__(self):
        return str(self.policy)
