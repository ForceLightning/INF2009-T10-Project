"""Runs all tests in the tests directory."""

import unittest

import tests.data_collection


def main():
    """Main function to run all tests in the tests directory."""
    data_collection_suite = tests.data_collection.suite()
    runner = unittest.TextTestRunner()
    runner.run(data_collection_suite)


if __name__ == "__main__":
    main()
