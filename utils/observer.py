# utils/observer.py
"""
Observer pattern implementation
"""

class Observer:
    """
    Observer class
    """
    def update(self, event: tuple[str, list[str], list[str]]):
        """
        Update method

        :param event: tuple containing the directory path, directory names, and filenames
        :return:
        """
        raise NotImplementedError("Subclass must implement abstract method")


class Observable:
    """
    Observable class
    """
    def __init__(self):
        self._observers = []

    def add_observer(self, observer):
        """
        Add observer

        :param observer:
        :return:
        """
        if observer not in self._observers:
            self._observers.append(observer)

    def remove_observer(self, observer):
        """
        Remove observer

        :param observer:
        :return:
        """
        self._observers.remove(observer)

    def notify_observers(self, event: tuple[str, list[str], list[str]]):
        """
        Notify observers

        :param event: tuple containing the directory path, directory names, and filenames
        :return:
        """
        for observer in self._observers:
            observer.update(event)
