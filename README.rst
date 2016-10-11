 # InstaPy

.. raw:: html

   <h2>

Instagram Like, Comment and Follow Automation Script

.. raw:: html

   </h2>

.. raw:: html

   <p>

Automation Script for "farming" Likes, Comments and Followers on
Instagram. Implemented in Python using the selenium module.

.. raw:: html

   </p>

.. raw:: html

   <h4>

Example

.. raw:: html

   </h4>

.. code:: python

    from instapy import InstaPy

    InstaPy(username='test', password='test')\
      .login()\
      .set_do_comment(True, percentage=10)\
      .set_comments(['Cool!', 'Awesome!', 'Nice!'])\
      .set_dont_include(['friend1', 'friend2', 'friend3'])\
      .set_dont_like(['food', 'girl', 'hot'])\
      .set_ignore_if_contains(['pizza'])\
      .like_by_tags(['dog', '#cat'], amount=100)\
      .end()

.. raw:: html

   <h2>

It's easy to use and the built in delays prevet your account from
getting banned

.. raw:: html

   </h2>

.. raw:: html

   <h5>

Getting started

.. raw:: html

   </h5>

.. code:: bash

    pip install selenium

.. raw:: html

   <p>

If you want the script to get the username and password for your
environment, you can do:

.. raw:: html

   </p>

::

    export INSTA_USER="<Your username>"
    export INSTA_PW="<Your password>"

.. raw:: html

   <hr />

.. code:: python

    from instapy import InstaPy

    #if you don't provide arguments, the script will look for INSTA_USER and INSTA_PW in the environment

    session = InstaPy(username='test', password='test')
    session.login()

    #likes 100 posts of dogs

    session.like_by_tags(['#dog'], amount=100)
    session.like_from_image(url='www.instagram.com/image', amount=100)

    session.end()

.. raw:: html

   <h5>

Restricting Likes

.. raw:: html

   </h5>

.. code:: python

    #searches the description for the given words and won't
    # like the image if one of the words are in there

    session.set_dont_like(['food', 'eat', 'meal'])

.. raw:: html

   <h5>

Ignoring Restrictions

.. raw:: html

   </h5>

.. code:: python

    #will ignore the don't like if the description contains
    # one of the given words

    session.set_ignore_if_contains(['glutenfree', 'french', 'tasty'])

.. raw:: html

   <h5>

Commenting

.. raw:: html

   </h5>

.. code:: python

    #default enabled=False, ~ every 4th image will be commented on

    session.set_do_comment(enabled=True, percentage=25)
    session.set_comments(['Awesome', 'Really Cool', 'I like your stuff'])

.. raw:: html

   <h5>

Following

.. raw:: html

   </h5>

.. code:: python

    #default enabled=False, follows ~ every 10th user from the images

    session.set_do_follow(enabled=True, percentage=10)

.. raw:: html

   <h5>

Excluding friends

.. raw:: html

   </h5>

.. code:: python

    #will prevent commenting on and unfollowing your good friends (the images will still be liked)

    session.set_dont_include(['friend1', 'friend2', 'friend3'])

.. raw:: html

   <h5>

Unfollowing

.. raw:: html

   </h5>

.. code:: python

    #unfollows 10 of the accounts your following -> instagram will only unfollow 10 before you'll be 'blocked for 10 minutes' (if you enter a higher number than 10 it will unfollow 10, then wait 10 minutes and will continue then)

    session.unfollow_users(amount=10) 

.. raw:: html

   <h3>

Clarifai ImageAPI

.. raw:: html

   </h3>

.. raw:: html

   <h6>

Note: Head over to https://developer.clarifai.com/signup/ and create a
free account, once you're logged in go to
https://developer.clarifai.com/account/applications/ and create a new
application. You can find the client ID and Secret there. You get 5000
API-calls free/month.

.. raw:: html

   </h6>

.. raw:: html

   <p>

If you want the script to get your Clarifai\_ID and Clarifai\_Secret for
your environment, you can do:

.. raw:: html

   </p>

::

    export CLARIFAI_ID="<ProjectID>"
    export CLARIFAI_SECRET="<Project Secret>"

.. raw:: html

   <h5>

Getting started

.. raw:: html

   </h5>

.. code:: bash

    pip install pip install git+git://github.com/Clarifai/clarifai-python.git

.. raw:: html

   <h4>

Example with Imagecontent handling

.. raw:: html

   </h4>

.. code:: python

    from instapy import InstaPy

    InstaPy(username='test', password='test')\
      .login()\
      .set_do_comment(True, percentage=10)\
      .set_comments(['Cool!', 'Awesome!', 'Nice!'])\
      .set_dont_include(['friend1', 'friend2', 'friend3'])\
      .set_dont_like(['food', 'girl', 'hot'])\
      .set_ignore_if_contains(['pizza'])\
      .set_use_clarifai(enabled=True)\
      .clarifai_check_img_for(['nsfw'])\
      .clarifai_check_img_for(['food', 'lunch', 'dinner'], comment=True, comments=['Tasty!', 'Nice!', 'Yum!'])\
      .like_by_tags(['dog', '#cat'], amount=100)\
      .end()

.. raw:: html

   <h5>

Enabling Imagechecking

.. raw:: html

   </h5>

.. code:: python

    #default enabled=False , enables the checking with the clarifai api (image tagging)
    #if secret and proj_id are not set, it will get the environment Variables
    # 'Clarifai_SECRET' and 'CLARIFAI_ID'

    session.set_use_clarifai(enabled=True, secret='xyz', proj_id='123')

.. raw:: html

   <h5>

Filtering inappropriate images

.. raw:: html

   </h5>

.. code:: python

    # uses the clarifai api to check if the image contains nsfw content
    # -> won't comment if image is nsfw

    session.check_image_for(['nsfw'])

.. raw:: html

   <h5>

Specialized comments for images with specific content

.. raw:: html

   </h5>

.. code:: python

    #checks the image for keywords food and lunch, if found,
    #comments with the given comments

    session.check_image_for(['food', 'lunch'], comment=True, comments=['Tasty!', 'Yum!'])

.. raw:: html

   <h6>

Check out https://clarifai.com/demo to see some of the available tags.

.. raw:: html

   </h6>

.. raw:: html

   <hr />

.. raw:: html

   <h6>

Have Fun & Feel Free to report any issues

.. raw:: html

   </h6>
