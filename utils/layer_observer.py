# utils/layer_observer.py
"""
This module contains the LayerObserver class
"""
import os

from .observer import Observer

class LayerObserver(Observer):
    """
    Layer observer
    """

    def update(self, event: tuple[str, list[str], list[str]]):
        """
        Update method

        :param directory:
        :return:
        """
        directory, _, _ = event
        if self.is_layer_directory(directory):
            print(f"Layer directory detected: {directory}")

    def is_layer_directory(self, directory):
        """
        Determine if the directory is a Layer directory
        """
        # Implement logic to determine if the directory is a Layer directory
        if not os.path.isdir(directory):
            return False

        if not "layers" in directory:
            return False

        return True
