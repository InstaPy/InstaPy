"""
Yandex Translate and MeaningCloud Sentiment Analysis services
Official Documentations:
    Yandex: https://tech.yandex.com/translate/doc/dg/concepts/api-overview
    -docpage/
    MeaningCloud: https://www.meaningcloud.com/developer/sentiment-analysis/doc
"""

import json
import requests
from meaningcloud import SentimentResponse, SentimentRequest

from .util import deform_emojis
from .util import has_any_letters
from .util import get_time_until_next_month
from .util import truncate_float
from .settings import Settings
from .time_util import sleep

from requests.exceptions import SSLError
from requests.exceptions import ConnectionError

YANDEX_API_VERSION = "v1.5"
YANDEX_HOST = "https://translate.yandex.net"

YANDEX_CONFIG = Settings.yandex_config
MEANINGCLOUD_CONFIG = Settings.meaningcloud_config

YANDEX_FAILURE_MSG = "Oh no! Yandex Translate failed :/"
MEANINGCLOUD_FAILURE_MSG = "Oh no! MeaningCloud Sentiment Analysis failed :/"


def text_analysis(text, text_type, logger):
    """
    Analyse text by sentiment analysis & language detection

    :return:
        Boolean indicating if the text is appropriate (after analysis) or
        None (if analysis isn't enabled)
    """

    # convert emojis in text into plain words for better analysis
    text, emojiless_text = deform_emojis(text)
    text_type_c = text_type.capitalize()
    inap_msg = "--> Content is inappropriate!"  # generic negative result
    # message
    language_of_text = None
    text_is_printed = None

    if (not YANDEX_CONFIG or YANDEX_CONFIG["enabled"] is not True or
            (YANDEX_CONFIG["match_language"] is not True and
             (not MEANINGCLOUD_CONFIG or MEANINGCLOUD_CONFIG[
                 "enabled"] is not True))):

        # No analysis will be held
        print('')
        logger.info(
            "{} text: \"{}\"".format(text_type_c, text.encode("utf-8")))
        return None

    if YANDEX_CONFIG["match_language"] is True:
        # Language detection & match will take place
        if has_any_letters(emojiless_text):
            language_of_text = detect_language(emojiless_text)
        else:
            # text contains only emojis
            language_of_text = "en"

        # output the text to be analysed
        print('')
        logger.info(
            "{} text ['{}']: \"{}\"".format(text_type_c, language_of_text,
                                            text.encode("utf-8")))
        text_is_printed = True

        if language_of_text and YANDEX_CONFIG[
            "language_code"] != language_of_text:
            logger.info("{}\t~language of the text is '{}'".format(inap_msg,
                                                                   language_of_text))
            return False

        elif not language_of_text:
            logger.info(
                "{}\t~language of text couldn't be detected!".format(inap_msg))
            return False

    if MEANINGCLOUD_CONFIG["enabled"] is True:
        # Text language normalization for accuracy & efficiency
        if not language_of_text:
            if has_any_letters(emojiless_text):
                language_of_text = detect_language(emojiless_text)
            else:
                # text contains only emojis
                language_of_text = "en"

            # output the text to be analysed [if not printed above]
            if text_is_printed is not True:
                print('')
                logger.info("{} text ['{}']: \"{}\"".format(text_type_c,
                                                            language_of_text,
                                                            text.encode(
                                                                "utf-8")))

            if not language_of_text:
                logger.info(
                    "{}\t~language of text couldn't be detected!".format(
                        inap_msg))
                return False

        # if language of text is not supported by MeaningCloud, translate it
        # into english by Yandex
        if language_of_text not in ["en", "es", "fr", "it", "pt", "ca"]:
            translation_direction = "{}-en".format(language_of_text)
            text = translate_text(translation_direction, text)
            language_of_text = "en"

        # Sentiment Analysis
        sentiment = sentiment_analysis(text, language_of_text, logger)

        if sentiment is None:
            logger.info("{}\t~sentiment of text couldn't be detected!".format(
                inap_msg))
            return False

        # polarity verification
        if MEANINGCLOUD_CONFIG["score_tag"]:
            if not sentiment["score_tag"]:
                logger.info(
                    "{}\t~polarity of text couldn't be detected!".format(
                        inap_msg))
                return False

            else:
                # get polarity & desired polarity levels to match towards
                # positivity
                pol = sentiment["score_tag"]
                des_pol = MEANINGCLOUD_CONFIG["score_tag"]

                polarity_level = (3 if pol == "P+" else 2 if pol == 'P' else
                1 if pol == "NEU" else
                -2 if pol == "N+" else -1 if pol == 'N' else
                0 if pol == "NONE" else None)

                desired_polarity_level = (
                    3 if des_pol == "P+" else 2 if des_pol == 'P' else
                    1 if des_pol == "NEU" else
                    -2 if des_pol == "N+" else -1 if des_pol == 'N' else
                    0 if des_pol == "NONE" else None)

                if desired_polarity_level > polarity_level:
                    logger.info(
                        "{}\t~polarity of text is '{}' with {}% confidence"
                        .format(inap_msg,
                                sentiment["score_tag"],
                                sentiment["confidence"]))
                    return False

        # agreement verification
        if MEANINGCLOUD_CONFIG["agreement"]:
            if not sentiment["agreement"]:
                logger.info(
                    "{}\t~expressions' agreement of text couldn't be "
                    "detected!".format(
                        inap_msg))
                return False

            elif MEANINGCLOUD_CONFIG["agreement"] != sentiment["agreement"]:
                logger.info("{}\t~expressions in text has {}"
                            .format(inap_msg, sentiment["agreement"].lower()))
                return False

        # subjectivity verification
        if MEANINGCLOUD_CONFIG["subjectivity"]:
            if not sentiment["subjectivity"]:
                logger.info(
                    "{}\t~subjectivity of text couldn't be detected!".format(
                        inap_msg))
                return False

            elif MEANINGCLOUD_CONFIG["subjectivity"] != sentiment[
                "subjectivity"]:
                logger.info("{}\t~text is {}"
                            .format(inap_msg,
                                    sentiment["subjectivity"].lower()))
                return False

        # confidence verification
        if MEANINGCLOUD_CONFIG["confidence"]:
            if not sentiment["confidence"]:
                logger.info(
                    "{}\t~sentiment confidence of text couldn't be "
                    "detected!".format(
                        inap_msg))
                return False

            elif MEANINGCLOUD_CONFIG["confidence"] > int(
                    sentiment["confidence"]):
                logger.info("{}\t~sentiment confidence of text is {}"
                            .format(inap_msg, sentiment["confidence"]))
                return False

    return True


def sentiment_analysis(text, language_of_text, logger):
    """
    Perform a detailed multilingual sentiment analysis of texts from
    different sources
    Available responses:
        https://github.com/MeaningCloud/meaningcloud-python/blob/master
        /meaningcloud/Response.py

    :return:
        Dictionary with the sentiment results or None
    """

    try:
        # make a request to the Sentiment Analysis API
        sentiment_response = SentimentResponse(
            SentimentRequest(
                key=MEANINGCLOUD_CONFIG["license_key"],
                lang=language_of_text,
                txt=text,
                txtf='plain')
                .sendReq()
        )
        # check if there are any errors in the request
        request_state = lift_meaningcloud_request(sentiment_response)
        if request_state is not True:
            return None

        # get results
        sentiment = sentiment_response.getResults()
        if sentiment and "score_tag" in sentiment.keys() and sentiment[
            "score_tag"]:
            # if text has a question mark & its polarity is neither negative
            # nor none, then label it neutral
            # @todo: polarity is assigned but never used
            if sentiment["score_tag"] not in ["N", "N+", "NONE"]:
                if '?' in text:
                    polarity = "NEU"
            return sentiment

        else:
            status_message = sentiment_response.getStatusMsg()
            print('')
            logger.error("{}\t~there was an unexpected error :|"
                         "\n{}\n".format(MEANINGCLOUD_FAILURE_MSG,
                                         status_message))
            return None

    except (ValueError, ConnectionError) as exc:
        print('')
        logger.exception("{}\t~{}\n"
                         .format(MEANINGCLOUD_FAILURE_MSG,
                                 str(exc).encode("utf-8")))
        return None


def detect_language(text):
    """
    Detect the language of the specified text

    :return:
        String with the language of text or None
    """

    POST = "/api/{}/tr.json/detect?key={}&text={}".format(
        YANDEX_API_VERSION, YANDEX_CONFIG["API_key"], text)
    logger = Settings.logger

    try:
        req = requests.get(YANDEX_HOST + POST)
    except SSLError as exc:
        print('')
        logger.exception("{}\t~there was a connection error :<"
                         "\n{}\n".format(YANDEX_FAILURE_MSG,
                                         str(exc).encode("utf-8")))
        return None

    data = json.loads(req.text)
    # check if there are any errors in the request
    request_state = lift_yandex_request(data)
    if request_state is not True:
        return None

    # get the result
    if "lang" in data.keys() and data["lang"]:
        language_of_text = data["lang"]
        return language_of_text

    else:
        return None


def yandex_supported_languages(language_code="en"):
    """
    Get the list of translation directions supported by the service
    Overview of supported langugages:
        https://tech.yandex.com/translate/doc/dg/concepts/api-overview
        -docpage/#api-overview__languages

    :return:
        dict.keys() object containing language codes or None
    """

    POST = "/api/{}/tr.json/getLangs?key={}&ui={}".format(
        YANDEX_API_VERSION, YANDEX_CONFIG["API_key"], language_code)
    logger = Settings.logger

    try:
        req = requests.get(YANDEX_HOST + POST)
    except SSLError:
        # try again one more time
        sleep(2)

        try:
            req = requests.get(YANDEX_HOST + POST)
        except SSLError as exc:
            print('')
            logger.exception("{}\t~there was a connection error :<"
                             "\n{}\n".format(YANDEX_FAILURE_MSG,
                                             str(exc).encode("utf-8")))
            return None

    data = json.loads(req.text)
    if "langs" in data.keys() and data["langs"]:
        language_codes = data["langs"].keys()
        return language_codes

    else:
        return None


def translate_text(translation_direction, text_to_translate):
    """
    Translate the text to the specified language

    :param translation_direction:
        "en-ru"   [from english to russian]
        "en"   [to english, auto-detect source lang]

    :return:
        String with the translated text or None
    """

    # if the text doesn't have an end mark, add a dot to get a better
    # translation
    if not text_to_translate.endswith(('.', '?', '!', ';')):
        text_to_translate += '.'

    POST = "/api/{}/tr.json/translate?key={}&text={}&lang={}".format(
        YANDEX_API_VERSION, YANDEX_CONFIG["API_key"],
        text_to_translate, translation_direction)
    logger = Settings.logger

    try:
        req = requests.get(YANDEX_HOST + POST)
    except SSLError as exc:
        print('')
        logger.exception("{}\t~there was a connection error :<"
                         "\n{}\n".format(YANDEX_FAILURE_MSG,
                                         str(exc).encode("utf-8")))
        return None

    data = json.loads(req.text)
    # check if there are any errors in the request
    request_state = lift_yandex_request(data)
    if request_state is not True:
        return None

    # get the result
    if "text" in data.keys() and data["text"]:
        translated_text = data["text"][0]
        return translated_text

    else:
        return None


def lift_yandex_request(request):
    """
    Handle the Yandex status code from requests

    :return:
        Boolean indicating the state of request
    """

    status_code = request["code"]
    logger = Settings.logger

    # handle per status code
    if status_code in [401, 402, 404]:
        # turn off Yandex service
        YANDEX_CONFIG.update(enabled=False)
        service_turnoff_msg = "turned off Yandex service"

        if status_code == 401:
            error_msg = "API key provided is invalid"
        elif status_code == 402:
            error_msg = "API key provided is blocked"
        elif status_code == 404:
            error_msg = "you've reached the request limit"

        print('')
        logger.error("{}\t~{} [{}]\n".format(YANDEX_FAILURE_MSG,
                                             error_msg,
                                             service_turnoff_msg))
        return False

    elif status_code in [413, 422, 501]:
        if status_code == 413:
            error_msg = "given text exceeds the maximum size :<"
        elif status_code == 422:
            error_msg = "given text couldn't be translated :("
        elif status_code == 501:
            error_msg = "the specified translation direction is not " \
                        "supported ~.~"

        print('')
        logger.error("{}\t~{}\n".format(YANDEX_FAILURE_MSG,
                                        error_msg))
        return False

    return True


def lift_meaningcloud_request(request):
    """
    Handle the MeaningCloud status code from requests
    Error Codes:
        https://www.meaningcloud.com/developer/documentation/error-codes

    :return:
        Boolean indicating the state of request
    """

    status_code = request.getStatusCode()
    logger = Settings.logger

    # handle per status code
    if status_code == '0':
        # request is successful
        return True

    elif status_code in ["100", "101", "102"]:
        # turn off MeaningCloud service
        MEANINGCLOUD_CONFIG.update(enabled=False)
        service_turnoff_msg = "turned off MeaningCloud service"

        if status_code == "100":
            error_msg = ("operation denied: license key is either incorrect,"
                         " unauthorized to make requests or you've been "
                         "banned from using service")

        elif status_code == "101":
            error_msg = "license expired: license key you're sending to use " \
                        "the API has expired"

        elif status_code == "102":
            consumed_credits = request.getConsumedCredits() or "unknown"
            time_until_next_month = get_time_until_next_month()

            error_msg = (
                "credits per subscription exceeded: ran out of credits for "
                "current month"
                " (spent: {}) - wait for credits to be reset at month end ({}"
                " days)".format(consumed_credits,
                                truncate_float(
                                    time_until_next_month / 60 / 60 / 24,
                                    2)))

        print('')
        logger.error("{}\t~{} [{}]\n".format(MEANINGCLOUD_FAILURE_MSG,
                                             error_msg,
                                             service_turnoff_msg))

    elif status_code in ["103", "104", "105", "200", "201", "202", "203",
                         "204", "205", "206", "207", "212", "214", "215"]:

        if status_code == "103":
            error_msg = (
                "request too large: exceeded the limit on the number of words"
                " that can be analyzed in a single request (max 50000)")

        elif status_code == "104":
            error_msg = (
                "request rate limit exceeded: hit the limit set for number of"
                " requests can be carried out concurrently (per second)")

        elif status_code == "105":
            error_msg = (
                "resource access denied: no access to a resource or language "
                "either cos haven't subscribed to any packs or trial ended")

        elif status_code == "200":
            error_msg = (
                "missing required parameter(s): you haven't specified one of"
                " the required parameters")

        elif status_code == "201":
            error_msg = (
                "resource not supported: you've sent an incorrect value for"
                " the 'model' or 'ud' parameters")

        elif status_code == "202":
            error_msg = (
                "engine internal error: internal error has occurred in"
                " service engines (wait a few minutes and try again)")

        elif status_code == "203":
            error_msg = (
                "can't connect to service: unable to serve the request due to"
                " high load in servers (wait a few minutes & try again)")

        elif status_code == "204":
            error_msg = (
                "resource not compatible for the language automatically"
                " identified from the text")

        elif status_code == "205":
            error_msg = (
                "language not supported: you've sent an incorrect value "
                "for the lang parameter")

        elif status_code == "212":
            error_msg = (
                "no content to analyze: content provided to analyze couldn't "
                "be"
                " accessed or converted into HTML (make sure value is "
                "supported)")

        elif status_code == "214":
            error_msg = (
                "wrong format: one of the parameters sent does not have"
                " the accepted format")

        elif status_code == "215":
            error_msg = (
                "timeout exceeded for service response: it's taken too long"
                " to respond & exceeded the timeout set for the system")

        print('')
        logger.error("{}\t~{}\n".format(MEANINGCLOUD_FAILURE_MSG,
                                        error_msg))

    else:
        response = request.getResponse()
        if response is None:
            error_msg = "the request sent did not return a JSON :/"
        else:
            status_message = request.getStatusMsg()
            error_msg = ("there was an unusual error :|"
                         "\n{}".format(status_message))

        print('')
        logger.error("{}\t~{}\n".format(MEANINGCLOUD_FAILURE_MSG,
                                        error_msg))

    return False
