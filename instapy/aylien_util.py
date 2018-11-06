""" AYLIEN Text Analysis API
"""
from aylienapiclient import textapi

from .util import deform_emojis
from .util import truncate_float



def aylien_text_analysis(user_data, text, text_type, logger):
    """ Return a solid information about the content of the text """
    client = textapi.Client(user_data["app_id"], user_data["key"])
    """Convert emojis in text into plain words for Aylien to better analyse..
    """
    text = deform_emojis(text)
    # sentiment analysis
    sentiment = client.Sentiment({"text": text})
    # language detection
    language = client.Language({"text": text})

    text_type_c = text_type.capitalize()
    # generic negative result message
    inap_msg = "--> Content is inappropriate!"

    # analysis output
    print('')
    logger.info("{} text: \"{}\"".format(text_type_c, text.encode("utf-8")))

    # polarity verification
    if user_data["polarity"]:
        if user_data["polarity"] != sentiment["polarity"]:
            logger.info("{}\t~polarity of the text is '{}' with {} confidence"
                            .format(inap_msg,
                                    sentiment["polarity"],
                                    truncate_float(sentiment["polarity_confidence"], 2)))
            return False

        elif (user_data["polarity_confidence"] and
              user_data["polarity_confidence"] > sentiment["polarity_confidence"]):
            logger.info("{}\t~polarity confidence of the text- {} is below {}"
                            .format(inap_msg,
                                    truncate_float(sentiment["polarity_confidence"], 2),
                                    user_data["polarity_confidence"]))
            return False

    # language verification
    if user_data["lang"]:
        if language["lang"] == "unknown":
            logger.info("{}\t~language of the text couldn't be detected"
                            .format(inap_msg))
            return False

        elif user_data["lang"] != language["lang"]:
            logger.info("{}\t~language of the text is '{}' with {} confidence"
                            .format(inap_msg,
                                    language["lang"],
                                    truncate_float(language["confidence"], 2)))
            return False

        elif (user_data["lang_confidence"] and
              user_data["lang_confidence"] > language["confidence"]):
            logger.info("{}\t~language confidence of the text- {} is below {}!"
                            .format(inap_msg,
                                    truncate_float(language["confidence"], 2),
                                    user_data["lang_confidence"]))
            return False

    return True



