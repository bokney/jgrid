
import pytest
from src.event_dispatcher import EventDispatcher, KeyedEventDispatcher


@pytest.fixture
def event_dispatcher():
    return EventDispatcher()


@pytest.fixture
def keyed_event_dispatcher():
    return KeyedEventDispatcher()


@pytest.fixture
def observer_list():
    return []


@pytest.fixture
def dummy_observer(observer_list):
    def observer():
        observer_list.append("called")
    return observer


@pytest.fixture
def failing_observer():
    def observer():
        raise ValueError("Intentional observer failure")
    return observer


class TestEventDispatcher:
    def test_register_adds_observer_to_list(
        self, event_dispatcher, dummy_observer
    ):
        event_dispatcher.register(dummy_observer)
        assert event_dispatcher.has_observer(dummy_observer)

    def test_register_observer_ignores_duplicates(
        self, event_dispatcher, dummy_observer
    ):
        event_dispatcher.register(dummy_observer)
        event_dispatcher.register(dummy_observer)
        assert event_dispatcher._observers.count(dummy_observer) == 1

    def test_unregister_removes_observer(
        self, event_dispatcher, dummy_observer
    ):
        event_dispatcher.register(dummy_observer)
        event_dispatcher.unregister(dummy_observer)
        assert not event_dispatcher.has_observer(dummy_observer)

    def test_unregister_non_existent_observer_does_nothing(
        self, event_dispatcher, dummy_observer
    ):
        try:
            event_dispatcher.unregister(dummy_observer)
        except Exception as e:
            pytest.fail(
                f"Unregistering a non-existent observer raised an error: {e}"
            )

    def test_notify_calls_all_registered_observers(
        self, event_dispatcher, dummy_observer, observer_list
    ):
        event_dispatcher.register(dummy_observer)
        event_dispatcher.notify()
        assert observer_list == ["called"]

    def test_notify_with_no_observers_does_not_fail(
        self, event_dispatcher
    ):
        try:
            event_dispatcher.notify()
        except Exception as e:
            pytest.fail(f"Notify with no observers raised an error: {e}")

    def test_observers_notified_in_order_of_registration(
            self, event_dispatcher, observer_list
        ):
        def observer1():
            observer_list.append("Observer1 called")

        def observer2():
            observer_list.append("Observer2 called")

        event_dispatcher.register(observer1)
        event_dispatcher.register(observer2)
        event_dispatcher.notify()

        assert observer_list == ["Observer1 called", "Observer2 called"]

    def test_exception_in_observer_propagates_if_required(
            self, event_dispatcher, failing_observer
        ):
        event_dispatcher.register(failing_observer)
        with pytest.raises(ValueError, match="Intentional observer failure"):
            event_dispatcher.notify()


class TestKeyedEventDispatcher:
    def test_register_adds_keyed_observer(
        self, keyed_event_dispatcher, dummy_observer
    ):
        key = "uniqueKey"
        keyed_event_dispatcher.register(key, dummy_observer)
        assert key in keyed_event_dispatcher._observers
        assert keyed_event_dispatcher._observers[key] == dummy_observer

    def test_register_keyed_observer_overrides_previous(
        self, keyed_event_dispatcher, dummy_observer
    ):
        key = "uniqueKey"
        keyed_event_dispatcher.register(key, dummy_observer)
        def another_observer():
            pass
        keyed_event_dispatcher.register(key, another_observer)
        assert keyed_event_dispatcher._observers[key] == another_observer

    def test_unregister_removes_keyed_observer(
        self, keyed_event_dispatcher, dummy_observer
    ):
        key = "uniqueKey"
        keyed_event_dispatcher.register(key, dummy_observer)
        keyed_event_dispatcher.unregister(key)
        assert key not in keyed_event_dispatcher._observers

    def test_unregister_non_existent_key_does_nothing(
        self, keyed_event_dispatcher
    ):
        try:
            keyed_event_dispatcher.unregister("nonExistentKey")
        except Exception as e:
            pytest.fail(
                f"Unregistering a non-existent key raised an error: {e}"
            )

    def test_notify_calls_registered_keyed_observer(
        self, keyed_event_dispatcher, dummy_observer, observer_list
    ):
        key = "uniqueKey"
        def observer():
            observer_list.append("keyed called")
        keyed_event_dispatcher.register(key, observer)
        keyed_event_dispatcher.notify(key)
        assert observer_list == ["keyed called"]

    def test_notify_does_not_call_observer_with_wrong_key(
        self, keyed_event_dispatcher, dummy_observer, observer_list
    ):
        key = "uniqueKey"
        def observer():
            observer_list.append("keyed called")
        keyed_event_dispatcher.register(key, observer)
        keyed_event_dispatcher.notify("wrongKey")
        assert observer_list == []

    def test_notify_with_no_keyed_observer_does_not_fail(
        self, keyed_event_dispatcher
    ):
        try:
            keyed_event_dispatcher.notify("nonExistentKey")
        except Exception as e:
            pytest.fail(f"Notify with no keyed observer raised an error: {e}")

    def test_exception_in_keyed_observer_propagates(
        self, keyed_event_dispatcher, failing_observer
    ):
        key = "uniqueKey"
        keyed_event_dispatcher.register(key, failing_observer)
        with pytest.raises(ValueError, match="Intentional observer failure"):
            keyed_event_dispatcher.notify(key)
