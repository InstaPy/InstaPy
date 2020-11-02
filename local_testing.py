from instapy import InstaPy


def session_run():
  session = InstaPy(username="gunlukkiralikvilla_ist",
                    password="Gudeberk78",
                    headless_browser=False,
                    isChrome=True
                    )

  session.login()

  session.set_do_follow(True, percentage=60)
  
  session.set_comments(["Cok guzel!", "Vay bizim villalar da boyle!", "Guzel cekmissin @{}"])
  session.set_do_comment(True, percentage=85)

  session.set_mandatory_words(["Istanbul", "istanbul", "turkey", "Turkey"])
  session.set_relationship_bounds(enabled=True, max_followers=5000, min_followers=600)

  session.like_by_tags(["istanbulvilla", "villaistanbul"], amount=10)

  session.end()

session_run()