"""Runs tests for the fog subscriber methods.
"""

import datetime
import os
import unittest

import pandas as pd

from deployment.fog_subscriber import CrowdStatus, DataFromEdge, model_inference
from util.wifi_bt_processing import get_bbox_counts_column_index, get_demo_data


class TestFogSubscriberMethods(unittest.TestCase):
    """Test case for fog subscriber methods."""

    def test_inference(self) -> None:
        """Tests the inference method for the fog subscriber."""
        koufu_file_path = os.path.join(os.path.dirname(__file__), "test_data/koufu.csv")
        df = pd.read_csv(koufu_file_path).drop(columns=["timestamp", "count"])
        ndarray = df.to_numpy()[-1].reshape(1, -1)
        crowd_status = CrowdStatus(
            status=0,
            err=None,
            timestamp=datetime.datetime.fromtimestamp(0.0),
            data={},
            numpy_data=ndarray,
        )

        for device_idx in range(4):
            wifi_data, bt_data = get_demo_data(device_idx, koufu_file_path, index=-1)
            bbox_col = get_bbox_counts_column_index(device_idx, column_offset=0)
            image_data = crowd_status["numpy_data"][0, bbox_col]
            data_from_edge = DataFromEdge(
                device_id=device_idx,
                return_image=False,
                image=image_data,
                wifi_data=wifi_data,
                bt_data=bt_data,
            )
            crowd_status["data"][device_idx] = data_from_edge

        deployment_dir = os.path.join(
            os.path.dirname(__file__), "..", "deployment", "models"
        )
        preds = model_inference(crowd_status, deployment_dir, "gpr")

        self.assertEqual(preds[0], 281)  # Known value from the training predictions.


def suite() -> unittest.TestSuite:
    """Returns a test suite for fog subscriber methods.

    :return: Test suite for fog subscriber methods
    :rtype: unittest.TestSuite
    """
    s = unittest.TestSuite()
    s.addTest(TestFogSubscriberMethods("test_inference"))
    return s


if __name__ == "__main__":
    unittest.main()
