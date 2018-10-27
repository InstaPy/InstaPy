"""Module which handles the clarifai api and checks
the image for invalid content"""
from clarifai.rest import ClarifaiApp
from clarifai.rest import Workflow


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
    picture_url=None,
    proxy=None,
):

    try:
        """Uses the link to the image to check for invalid content in the image.
        If a workflow has been selected, get list of tags from Clarifai API
        by checking link against models included in the workflow. If a workflow
        hasn't been provided, InstaPy will check images against given model(s)"""
        clarifai_api = ClarifaiApp(api_key=clarifai_api_key)
        clarifai_tags = []

        if proxy is not None:
            clarifai_api.api.session.proxies = {'https': proxy}
        # set req image to given one or get it from current page
        if picture_url is None:
            img_link = get_imagelink(browser)
        else:
            img_link = picture_url

        # no image in page
        if img_link is None:
            return True, [], []

        # Check image using workflow if provided. If no workflow, check image using model(s)
        if workflow:
            clarifai_workflow = Workflow(clarifai_api.api, workflow_id=workflow[0])
            clarifai_response = clarifai_workflow.predict_by_url(img_link)
            for response in clarifai_response['results'][0]['outputs']:
                results = get_clarifai_tags(response, probability)
                clarifai_tags.extend(results)
        else:
            for model in clarifai_models:
                clarifai_response = get_clarifai_response(clarifai_api, model, img_link)
                results = get_clarifai_tags(clarifai_response['outputs'][0], probability)
                clarifai_tags.extend(results)

        # Will not comment on an image if any of the tags in img_tags_skip_if_contain are matched
        if given_tags_in_result(img_tags_skip_if_contain, clarifai_tags):
            logger.info(
                'Not Commenting, image contains concept(s): "{}".'.format(
                    ', '.join(list(set(clarifai_tags) & set(img_tags_skip_if_contain)))
            )
        )
        return False, [], clarifai_tags
        
        logger.info('img_link {} got predicted result:\n{}'.format(img_link, clarifai_tags))

        for (tags, should_comment, comments) in img_tags:
            if should_comment and given_tags_in_result(tags, clarifai_tags, full_match):
                return True, comments, clarifai_tags
            elif given_tags_in_result(tags, clarifai_tags, full_match):
                logger.info(
                    'Not Commenting, image contains concept(s): "{}".'.format(
                        ', '.join(list(set(clarifai_tags) & set(tags)))
                    )
                )
                return False, [], clarifai_tags

        return True, [], clarifai_tags
        
    except Exception as err:
        logger.error(
            'Image check error: {}'.format(err))


def given_tags_in_result(search_tags, clarifai_tags, full_match=False):
    """Checks the clarifai tags if it contains one (or all) search tags """
    if full_match:
        return all([tag in clarifai_tags for tag in search_tags])
    else:
        return any((tag in clarifai_tags for tag in search_tags))


def get_imagelink(browser):
    """Gets the imagelink from the given webpage open in the browser"""
    return browser.find_element_by_xpath(
        '//img[@class = "FFVAD" or @class="_8jZFn"]'
    ).get_attribute('src')


def get_clarifai_response(clarifai_api, clarifai_model, img_link):
    """Compiles a list of tags from Clarifai using the chosen models.
    First checks the value of each item in the models list against a
    dictionary. If the model value provided does not match one of the
    keys in the dictionary below, model value is used in
    clarifai_api.models.get(). Useful for custom models."""
    clarifai_models = {
        'general': 'general-v1.3',
        'nsfw': 'nsfw-v1.0',
        'apparel': 'apparel',
        'celebrity': 'celeb-v1.3',
        'color': 'color',
        'demographics': 'demographics',
        'food': 'food-items-v1.0',
        'landscape quality': 'Landscape Quality',
        'logo': 'logo',
        'moderation': 'moderation',
        'portrait quality': 'Portrait Quality',
        'textures': 'Textures & Patterns',
        'travel': 'travel-v1.0',
        'weddings': 'weddings-v1.0',
    }

    model = clarifai_api.models.get(
        clarifai_models.get(clarifai_model.lower(), clarifai_model)
    )
    # Get response from Clarifai API
    clarifai_response = model.predict_by_url(img_link)
    return clarifai_response


def get_clarifai_tags(clarifai_response, probability):
    """Get the response from the Clarifai API and return results filtered by
    concepts with a confidence set by probability parameter (default 50%)"""
    results = []
    concepts = []

    # Parse response for Color model
    try:
        concepts = [
            {concept.get('w3c', {}).get('name').lower(): concept.get('value')}
            for concept in clarifai_response['data']['colors']
        ]
    except KeyError:
        pass

    # Parse response for Celebrity model
    try:
        for value in clarifai_response['data']['regions']:
            concepts = [
                {concept.get('name').lower(): concept.get('value')}
                for concept in value['data']['face']['identity']['concepts']
            ]
    except KeyError:
        pass

    # Parse response for Demographics model
    try:
        for value in clarifai_response['data']['regions'][0]['data']['face'].values():
            concepts = [
                {concept.get('name').lower(): concept.get('value')}
                for concept in value['concepts']
            ]
    except KeyError:
        pass

    # Parse response for Logo model
    try:
        concepts = [
            {concept.get('name').lower(): concept.get('value')}
            for concept in clarifai_response['data']['regions'][0]['data']['concepts']
        ]
    except KeyError:
        pass

    # Parse response for General model and similarly structured responses
    try:
        concepts = [
            {concept.get('name').lower(): concept.get('value')}
            for concept in clarifai_response['data']['concepts']
        ]
    except KeyError:
        pass

    # Filter concepts based on probability threshold
    for concept in concepts:
        if float([x for x in concept.values()][0]) > probability:
            results.append(str([x for x in concept.keys()][0]))

    return results
