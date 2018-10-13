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
    """Compiles a list of tags from Clarifai using the chosen models.
    First checks the value of each item in the models list against a
    dictionary. If the model value provided does not match one of the
    keys in the dictionary below, model value is used in
    clarifai_api.models.get(). Useful for custom models."""
    results = []
    clarifai_model = {
        'general': 'general-v1.5',
        'nsfw': 'nsfw-v1.0',
        'apparel': 'apparel',
        'celebrity': 'celeb-v1.3',
        'color': 'color',
        'demographics': 'demographics',
        'face detection': 'face-v1.3',
        'food': 'food-items-v1.0',
        'moderation': 'moderation',
        'textures': 'Textures & Patterns',
        'travel': 'travel-v1.0',
        'weddings': 'weddings-v1.0'
    }

    for model in models:
        model = clarifai_api.models.get(clarifai_model.get(model.lower(), model))
        # Get response from Clarifai API
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
