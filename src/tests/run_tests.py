"""Runs all tests in the tests directory."""

import unittest

from tests import data_collection, fog_inference


def main():
    """Main function to run all tests in the tests directory."""
    data_collection_suite = data_collection.suite()
    fog_inference_suite = fog_inference.suite()
    runner = unittest.TextTestRunner()
    runner.run(data_collection_suite)
    runner.run(fog_inference_suite)


if __name__ == "__main__":
    main()
