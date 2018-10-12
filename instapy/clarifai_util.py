"""Module which handles the clarifai api and checks
the image for invalid content"""
from clarifai.rest import ClarifaiApp


def check_image(browser, clarifai_api_key, img_tags, img_tags_skip_if_contain, logger,
                clarifai_models, full_match=False, picture_url=None):
    """Uses the link to the image to check for invalid content in the image"""
    clarifai_api = ClarifaiApp(api_key=clarifai_api_key)
    # set req image to given one or get it from current page
    if picture_url is None:
        img_link = get_imagelink(browser)
    else:
        img_link = picture_url
    # Get list of tags from Clarifai API by checking link against provided model(s)
    clarifai_tags = get_clarifai_response(clarifai_api, clarifai_models, img_link)

    # Will not comment on an image if any of the tags in img_tags_skip_if_contain are matched
    if given_tags_in_result(img_tags_skip_if_contain, clarifai_tags):
        logger.info('Not Commenting, image contains concept: "{}".'.format(
            ', '.join(list(set(clarifai_tags) & set(img_tags_skip_if_contain)))))
        return False, []

    for (tags, should_comment, comments) in img_tags:
        if should_comment and given_tags_in_result(tags, clarifai_tags, full_match):
            return True, comments
        elif given_tags_in_result(tags, clarifai_tags, full_match):
            logger.info('Not Commenting, image contains concept(s): "{}".'.format(
                ', '.join(list(set(clarifai_tags) & set(tags)))))
            return False, []

    return True, []


def given_tags_in_result(search_tags, clarifai_tags, full_match=False):
    """Checks the clarifai tags if it contains one (or all) search tags """
    if full_match:
        return all([tag in clarifai_tags for tag in search_tags])
    else:
        return any((tag in clarifai_tags for tag in search_tags))


def get_imagelink(browser):
    """Gets the imagelink from the given webpage open in the browser"""
    return browser.find_element_by_xpath('//img[@class = "FFVAD" or @class="_8jZFn"]') \
        .get_attribute('src')


def get_clarifai_response(clarifai_api, models, img_link):
    """Compiles a list of tags from Clarifai using the
    chosen models"""
    results = []

    for model in models:
        model = get_model(clarifai_api, model)
        clarifai_response = model.predict_by_url(img_link)
        # Use get_clarifai_tags function to filter results returned from Clarifai
        clarifai_tags = get_clarifai_tags(clarifai_response)
        results.extend(clarifai_tags)

    return results


def get_clarifai_tags(clarifai_response):
    """Get the response from the Clarifai API and return results filtered by
    models with 50% or higher confidence"""
    results = []
    concepts = [{concept.get('name').lower(): concept.get('value')}
                for concept in clarifai_response['outputs'][0]['data']['concepts']]
    for concept in concepts:
        if float([x for x in concept.values()][0]) > 0.50:
            results.append(str([x for x in concept.keys()][0]))

    return results


def get_model(clarifai_api, model):
    """Selects model(s) from publics models provided by
    Clarifai. Includes support for custom models"""
    selector = model.lower()

    if 'general' == selector:
        return clarifai_api.public_models.general_model
    elif 'nsfw' == selector:
        return clarifai_api.models.get('nsfw-v1.0')
    elif 'apparel' == selector:
        return clarifai_api.models.get('apparel')
    elif 'celebrity' == selector:
        return clarifai_api.models.get('celeb-v1.3')
    elif 'color' == selector:
        return clarifai_api.models.get('color')
    elif 'demographics' == selector:
        return clarifai_api.models.get('demographics')
    elif 'face detection' == selector:
        return clarifai_api.models.get('face-v1.3')
    elif 'food' == selector:
        return clarifai_api.models.get('food-items-v1.0')
    elif 'moderation' == selector:
        return clarifai_api.models.get("moderation")
    elif 'textures' == selector:
        return clarifai_api.models.get("Textures & Patterns")
    elif 'travel' == selector:
        return clarifai_api.models.get('travel-v1.0')
    elif 'weddings' == selector:
        return clarifai_api.models.get('weddings-v1.0')
    else:
        # When using custom models, provide a value for
        # model different from the options given above
        return clarifai_api.models.get(model)
