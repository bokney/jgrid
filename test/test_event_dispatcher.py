
import pytest
from src.event_dispatcher import EventDispatcher, KeyedEventDispatcher


@pytest.fixture
def event_dispatcher():
    return EventDispatcher[str]()



@pytest.fixture
def keyed_event_dispatcher():
    return KeyedEventDispatcher[str, str]()


@pytest.fixture
def observer_list():
    return []


@pytest.fixture
def dummy_observer(observer_list):
    def observer(event_data: str):
        observer_list.append(event_data)
    return observer


@pytest.fixture
def failing_observer():
    def observer(event_data: str):
        raise ValueError("Intentional observer failure")
    return observer


class TestEventDispatcher:
    def test_register_adds_observer_to_list(
        self, event_dispatcher, dummy_observer
    ):
        event_dispatcher.register(dummy_observer)
        assert len(event_dispatcher._observers) == 1
        assert dummy_observer in event_dispatcher._observers

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
        assert dummy_observer not in event_dispatcher._observers

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
        event_dispatcher.notify("Test Event")
        assert observer_list == ["Test Event"]

    def test_notify_passes_correct_data(
        self, event_dispatcher, dummy_observer, observer_list
    ):
        event_dispatcher.register(dummy_observer)
        event_dispatcher.notify("Correct Data")
        assert observer_list == ["Correct Data"]

    def test_notify_with_no_observers_does_not_fail(
        self, event_dispatcher
    ):
        try:
            event_dispatcher.notify("No Listeners")
        except Exception as e:
            pytest.fail(
                f"Notify with no observers raised an error: {e}"
            )

    def test_observers_notified_in_order_of_registration(
        self, event_dispatcher, observer_list
    ):
        def observer1(event_data: str):
            observer_list.append(f"Observer1: {event_data}")

        def observer2(event_data: str):
            observer_list.append(f"Observer2: {event_data}")

        event_dispatcher.register(observer1)
        event_dispatcher.register(observer2)
        event_dispatcher.notify("Ordered Event")

        assert observer_list == [
            "Observer1: Ordered Event",
            "Observer2: Ordered Event"
        ]

    def test_exception_in_observer_propagates_if_required(
        self, event_dispatcher, failing_observer
    ):
        event_dispatcher.register(failing_observer)

        with pytest.raises(ValueError, match="Intentional observer failure"):
            event_dispatcher.notify("Trigger Exception")


class TestKeyedEventDispatcher:
    def test_register_adds_keyed_observer_to_list(
        self, keyed_event_dispatcher, dummy_observer
    ):
        key = "orderkey123"
        keyed_event_dispatcher.register(key, dummy_observer)
        assert dummy_observer in keyed_event_dispatcher._observers[key]

    def test_register_keyed_observer_ignores_duplicates(
        self, keyed_event_dispatcher, dummy_observer
    ):
        key = "orderkey123"
        keyed_event_dispatcher.register(key, dummy_observer)
        keyed_event_dispatcher.register(key, dummy_observer)
        assert keyed_event_dispatcher._observers[key].count(
            dummy_observer
        ) == 1

    def test_unregister_removes_keyed_observer(
        self, keyed_event_dispatcher, dummy_observer
    ):
        key = "orderkey123"
        keyed_event_dispatcher.register(key, dummy_observer)
        keyed_event_dispatcher.unregister(key, dummy_observer)
        assert dummy_observer not in keyed_event_dispatcher._observers[key]

    def test_unregister_non_existent_keyed_observer_does_nothing(
        self, keyed_event_dispatcher, dummy_observer
    ):
        key = "orderkey123"
        try:
            keyed_event_dispatcher.unregister(key, dummy_observer)
        except Exception as e:
            pytest.fail(
                f"Unregistering a non-existent observer raised an error: {e}"
            )

    def test_notify_calls_all_registered_keyed_observers(
        self, keyed_event_dispatcher, dummy_observer, observer_list
    ):
        key = "orderkey123"
        keyed_event_dispatcher.register(key, dummy_observer)
        keyed_event_dispatcher.notify(key, "Test Event")
        assert observer_list == ["Test Event"]

    def test_notify_does_not_call_observer_with_wrong_key(
        self, keyed_event_dispatcher, dummy_observer, observer_list
    ):
        keyed_event_dispatcher.register("orderkey123", dummy_observer)
        keyed_event_dispatcher.notify("order456", "Test Event")
        assert observer_list == []

    def test_notify_with_no_keyed_observers_does_not_fail(
        self, keyed_event_dispatcher
    ):
        try:
            keyed_event_dispatcher.notify("orderkey123", "No Listeners")
        except Exception as e:
            pytest.fail(f"Notify with no observers raised an error: {e}")

    def test_keyed_observers_notified_in_order_of_registration(
        self, keyed_event_dispatcher, observer_list
    ):
        key = "orderkey123"

        def observer1(event_data: str):
            observer_list.append(f"Observer1: {event_data}")

        def observer2(event_data: str):
            observer_list.append(f"Observer2: {event_data}")

        keyed_event_dispatcher.register(key, observer1)
        keyed_event_dispatcher.register(key, observer2)
        keyed_event_dispatcher.notify(key, "Ordered Event")
        assert observer_list == [
            "Observer1: Ordered Event",
            "Observer2: Ordered Event"
        ]

    def test_exception_in_observer_propagates_for_key(
        self, keyed_event_dispatcher, failing_observer
    ):
        key = "orderkey123"
        keyed_event_dispatcher.register(key, failing_observer)
        with pytest.raises(ValueError, match="Intentional observer failure"):
            keyed_event_dispatcher.notify(key, "Trigger Exception")
