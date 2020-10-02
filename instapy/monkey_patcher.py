from selenium.webdriver.common.action_chains import ActionChains


def patch_move_to_element():
    """Patch move_to_element method in Class ActionChain"""
    ref_move_to_element = ActionChains.move_to_element

    def override_move_to_element(self, to_element):
        if "firefox" in self._driver.name:
            to_element.location_once_scrolled_into_view
        return self.__move_to_element(to_element)

    setattr(ActionChains, "__move_to_element", ref_move_to_element)
    setattr(ActionChains, "move_to_element", override_move_to_element)


def patch_all():
    patch_move_to_element()
