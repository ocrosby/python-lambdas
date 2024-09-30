# utils/scanner.py
"""
This module contains the DirectoryScanner class
"""
import os

from utils.observer import Observable
from utils.lambda_observer import LambdaObserver
from utils.layer_observer import LayerObserver

class DirectoryScanner(Observable):
    """
    Directory scanner class
    """
    def scan(self, root_directory):
        """
        Scan the directory

        It notifies all observers with a tuple containing the directory path, directory names, and filenames

        :param root_directory:
        :return:
        """
        for dirpath, dirnames, filenames in os.walk(root_directory):
            self.notify_observers((dirpath, dirnames, filenames))

if __name__ == "__main__":
    scanner = DirectoryScanner()
    scanner.add_observer(LambdaObserver())
    scanner.add_observer(LayerObserver())
    scanner.scan("../")
