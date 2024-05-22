import logging
from decimal import Decimal

from langdetect import detect, detect_langs

logger = logging.getLogger(__name__)


class CryptshareNotificationMessage:
    def __init__(self, body: str = None, subject: str = None, language: str = None) -> None:
        logger.debug("Initialising NotificationMessage")
        self.body = body if body else ""
        self.subject = subject if subject else ""
        self.language = language if language else "en"
        if not language and (body or subject):
            self.detect_language()

    def detect_language(self) -> None:
        logger.debug("Detecting language from Notification Message subject and body")
        # Implement language detection here
        use_text_for_detection = f"{self.body} {self.subject}"

        try:
            probs = detect_langs(use_text_for_detection)
            lang = detect(use_text_for_detection)
        except Exception as e:
            logger.warning("Unable to detect language from text!\n %s", e)
            return

        if len(probs) > 0:
            logger.debug("Probabilities: {}".format(probs))
            probability = Decimal(0)

            try:
                if len(str(probs[0]).split(":")) > 0:
                    probability = str(probs[0]).split(":")[1]
                else:
                    probability = str(probs[0]).replace(lang + ":", "")
                probability = Decimal(probability)
            except Decimal.InvalidDecimalOperation:
                logger.warning("Invalid decimal conversion: %s", probability)
            except ValueError:
                logger.warning("Value error: %s", probability)
            except Exception as e:
                logger.warning("Decimal conversion failed: %s %s", probability, e)

            if probability > 0.8:
                logger.info(f"Detected recipient language: {lang.lower()} Probability: {probability}")
                self.language = lang.lower()
                return
            logger.debug(f"Recipient language detection probability too low: {lang.lower()} {probability}")
        return

    def data(self) -> dict:
        logger.debug("Returning NotificationMessage data")
        return {"body": self.body, "subject": self.subject}
