"""This script captures an image from the webcam and can encode it as a base64 string.
"""

import base64
import os
import time
from typing import Optional

import cv2


def take_picture(
    output_dir: Optional[str | os.PathLike] = None,
    use_demo_data: bool = False,
    **kwargs,
) -> cv2.typing.MatLike:
    """Takes a picture using the webcam and saves it to the specified directory if provided.

    :param output_dir: Output directory for the image, defaults to None
    :type output_dir: Optional[str | os.PathLike], optional
    :param use_demo_data: Whether to load demo data, defaults to False
    :type use_demo_data: bool, optional
    :param ``**kwargs``: Keyword arguments for cv2.imread if use_demo_data is True
        (e.g., filename, flags)
    :raises exc: Any exception that occurs during the process
    :return: The captured image
    :rtype: cv2.typing.MatLike
    """
    if use_demo_data:
        im = cv2.imread(**kwargs)
        return im

    camera = cv2.VideoCapture(0)

    try:
        # Capture the picture
        _, frame = camera.read()

        if output_dir:
            timestamp = time.strftime("%Y%m%d%H%M")
            filename = f"image_{timestamp}.jpg"
            filepath = os.path.join(output_dir, filename)

            cv2.imwrite(filepath, frame)
            print(f"Picture taken and saved as {filepath}")
        return frame

    except Exception as exc:
        raise exc  # Handle the exception in the caller

    finally:
        camera.release()


def encode_image(frame: cv2.typing.MatLike) -> str:
    """Encodes an image into a base64 string.

    :param frame: The image to encode
    :type frame: cv2.typing.MatLike
    :return: Base64 encoded image
    :rtype: str
    """
    _, buffer = cv2.imencode(".jpg", frame)
    img_bytes = base64.b64encode(buffer).decode("utf-8")
    return img_bytes


if __name__ == "__main__":
    OUTPUT_DIR = "images"

    # Create the output directory if it doesn't exist
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"Created directory: {OUTPUT_DIR}")

    try:
        while True:
            take_picture(OUTPUT_DIR)
            # Sleep for 30 minutes (1800 seconds)
            time.sleep(1800)

    except KeyboardInterrupt:
        print("\nProgram terminated by user.")
