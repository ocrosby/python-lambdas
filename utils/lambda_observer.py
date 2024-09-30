# utils/lambda_observer.py
"""
This module contains the LambdaFunctionObserver class
"""
import os

from .observer import Observer

class LambdaObserver(Observer):
    """
    Lambda Function observer
    """
    def update(self, event: tuple[str, list[str], list[str]]):
        """
        Update method

        :param directory:
        :return:
        """
        dirpath, _, _ = event
        if self.is_lambda_function_directory(dirpath):
            print(f"Lambda Function directory detected: {dirpath}")


    def is_lambda_function_directory(self, directory):
        """
        Determine if the directory is a Lambda Function directory

        :param directory:
        :return:
        """
        # Implement logic to determine if the directory is a Lambda Function directory
        if not os.path.isdir(directory):
            return False

        if not "handler.py" in os.listdir(directory):
            return False

        return True
