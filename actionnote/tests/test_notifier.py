from modules.notifier import Notifier, PLYER_AVAILABLE


def test_plyer_available_is_exposed_as_instance_attribute():
    # app.py reads notifier.PLYER_AVAILABLE off the instance (e.g. in
    # /api/config and the startup banner) -- it must not only exist as a
    # module-level global, or every such access raises AttributeError.
    notifier = Notifier()
    assert notifier.PLYER_AVAILABLE == PLYER_AVAILABLE
