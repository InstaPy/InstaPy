"""Module which handles the clarifai api and checks
the image for invalid content"""
from clarifai.rest import ClarifaiApp, Workflow
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

from .xpath import read_xpath


def check_image(
    browser,
    clarifai_api_key,
    img_tags,
    img_tags_skip_if_contain,
    logger,
    clarifai_models,
    workflow,
    probability,
    full_match=False,
    check_video=False,
    proxy=None,
    picture_url=None,
):
    try:
        """Uses the link to the image to check for invalid content in the
        image.
        If a workflow has been selected, get list of tags from Clarifai API
        by checking link against models included in the workflow. If a workflow
        hasn't been provided, InstaPy will check images against given model(
        s)"""
        clarifai_api = ClarifaiApp(api_key=clarifai_api_key)
        clarifai_tags = []

        if proxy is not None:
            clarifai_api.api.session.proxies = {"https": proxy}
        # Set req image or video source URL to given one or get it from
        # current page
        if picture_url is None:
            source_link = get_source_link(browser)
        else:
            source_link = [picture_url]

        # No image in page
        if not source_link:
            return True, [], []

        # Check image using workflow if provided. If no workflow,
        # check image using model(s)
        if workflow:
            clarifai_workflow = Workflow(clarifai_api.api, workflow_id=workflow[0])
            # If source is video, checks keyframe against models as video
            # inputs not supported when using workflows
            if source_link[0].endswith("mp4"):
                clarifai_response = clarifai_workflow.predict_by_url(source_link[1])
            else:
                clarifai_response = clarifai_workflow.predict_by_url(source_link[0])

            for response in clarifai_response["results"][0]["outputs"]:
                results = get_clarifai_tags(response, probability)
                clarifai_tags.extend(results)
        else:
            for model in clarifai_models:
                clarifai_response = get_clarifai_response(
                    clarifai_api, model, source_link, check_video
                )
                results = get_clarifai_tags(
                    clarifai_response["outputs"][0], probability
                )
                clarifai_tags.extend(results)

        logger.info(
            "source_link {} got predicted result(s):\n{}".format(
                source_link, clarifai_tags
            )
        )

        # Will not comment on an image if any of the tags in
        # img_tags_skip_if_contain are matched
        if given_tags_in_result(img_tags_skip_if_contain, clarifai_tags):
            logger.info(
                'Not Commenting, image contains concept(s): "{}".'.format(
                    ", ".join(list(set(clarifai_tags) & set(img_tags_skip_if_contain)))
                )
            )
            return False, [], clarifai_tags

        for (tags, should_comment, comments) in img_tags:
            if should_comment and given_tags_in_result(tags, clarifai_tags, full_match):
                return True, comments, clarifai_tags
            elif given_tags_in_result(tags, clarifai_tags, full_match):
                logger.info(
                    'Not Commenting, image contains concept(s): "{}".'.format(
                        ", ".join(list(set(clarifai_tags) & set(tags)))
                    )
                )
                return False, [], clarifai_tags

        return True, [], clarifai_tags

    except Exception as err:
        logger.error("Image check error: {}".format(err))


def given_tags_in_result(search_tags, clarifai_tags, full_match=False):
    """Checks the clarifai tags if it contains one (or all) search tags"""
    if full_match:
        return all([tag in clarifai_tags for tag in search_tags])
    else:
        return any((tag in clarifai_tags for tag in search_tags))


def get_source_link(browser):
    """Checks to see if a post is an image. If so, returns list with image
    source URL.
    If a NoSuchElement exception occurs, checks post for video and returns
    the source URLs
    for both the video and the video's keyframe."""
    source = []

    try:
        source.append(
            browser.find_element(
                By.XPATH, read_xpath(get_source_link.__name__, "image")
            ).get_attribute("src")
        )
    except NoSuchElementException:
        source.append(
            browser.find_element(
                By.XPATH, read_xpath(get_source_link.__name__, "video")
            ).get_attribute("src")
        )
        source.append(
            browser.find_element(
                By.XPATH, read_xpath(get_source_link.__name__, "image_alt")
            ).get_attribute("src")
        )

    return source


def get_clarifai_response(clarifai_api, clarifai_model, source_link, check_video):
    """Compiles a list of tags from Clarifai using the chosen models.
    First checks the value of each item in the models list against a
    dictionary. If the model value provided does not match one of the
    keys in the dictionary below, model value is used in
    clarifai_api.models.get(). Useful for custom models."""
    # List of models which support video inputs
    video_models = ["apparel", "food", "general", "nsfw", "travel", "wedding"]
    clarifai_models = {
        "general": "general-v1.3",
        "nsfw": "nsfw-v1.0",
        "apparel": "apparel",
        "celebrity": "celeb-v1.3",
        "color": "color",
        "demographics": "demographics",
        "food": "food-items-v1.0",
        "landscape quality": "Landscape Quality",
        "logo": "logo",
        "moderation": "moderation",
        "portrait quality": "Portrait Quality",
        "textures": "Textures & Patterns",
        "travel": "travel-v1.0",
        "weddings": "weddings-v1.0",
    }

    model = clarifai_api.models.get(
        clarifai_models.get(clarifai_model.lower(), clarifai_model)
    )
    # Get response from Clarifai API
    # If source is video, model accepts video inputs and check_video is
    # True, analyze content of frames in video
    if (
        check_video
        and source_link[0].endswith("mp4")
        and clarifai_model.lower() in video_models
    ):
        response = model.predict_by_url(source_link[0], is_video=True)
    # If source is video but model does not accept video inputs or
    # check_video is False, analyze content of keyframe
    elif source_link[0].endswith("mp4"):
        response = model.predict_by_url(source_link[1])
    else:
        response = model.predict_by_url(source_link[0])

    return response


def get_clarifai_tags(clarifai_response, probability):
    """Get the response from the Clarifai API and return results filtered by
    concepts with a confidence set by probability parameter (default 50%)"""
    results = []
    concepts = []

    # Parse response for Color model
    try:
        concepts = [
            {concept.get("w3c", {}).get("name").lower(): concept.get("value")}
            for concept in clarifai_response["data"]["colors"]
        ]
    except KeyError:
        pass

    # Parse response for Celebrity and Demographics models
    try:
        for value in clarifai_response["data"]["regions"]:
            for face in value["data"]["face"].values():
                concepts.extend(
                    [
                        {concept.get("name").lower(): concept.get("value")}
                        for concept in face["concepts"]
                    ]
                )
    except KeyError:
        pass

    # Parse response for Logo model
    try:
        concepts = [
            {concept.get("name").lower(): concept.get("value")}
            for concept in clarifai_response["data"]["regions"][0]["data"]["concepts"]
        ]
    except KeyError:
        pass

    # Parse response for General model and similarly structured responses
    try:
        concepts = [
            {concept.get("name").lower(): concept.get("value")}
            for concept in clarifai_response["data"]["concepts"]
        ]
    except KeyError:
        pass

    # Parse response for Video input
    try:
        for frame in clarifai_response["data"]["frames"]:
            concepts.extend(
                [
                    {concept.get("name").lower(): concept.get("value")}
                    for concept in frame["data"]["concepts"]
                ]
            )
    except KeyError:
        pass

    # Filter concepts based on probability threshold
    for concept in concepts:
        if float([x for x in concept.values()][0]) > probability:
            results.append(str([x for x in concept.keys()][0]))

    return results
