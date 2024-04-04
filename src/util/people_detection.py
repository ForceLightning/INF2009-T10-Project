"""Detect people in images and save the results to a CSV file.
"""

import os
from pathlib import Path

import torch
import cv2
from PIL import Image
from ultralytics import YOLO

DATA_PATH = "./data"
COLLECTORS = ["bryan", "chris", "jiayu", "jurgen"]


def detect(image: cv2.typing.MatLike | Image.Image) -> list:
    """Function to perform object detection on an image.

    :param image: Image to perform object detection on
    :type image: cv2.typing.MatLike
    :return: List of results from object detection
    :rtype: list
    """
    # Check if GPU is available, otherwise use CPU
    device = "cuda" if torch.cuda.is_available() else "cpu"

    # Load YOLO model
    model = YOLO("yolov8s.pt").to(device)

    # Perform object detection on the image
    return model.predict(image, classes=[0])  # type: ignore


# Function to count the number of people detected in the image
def get_people_count(results: list) -> int:
    """Function to count the number of people detected in the image.

    :param results: Results from object detection
    :type results: list
    :return: Number of people detected
    :rtype: int
    """
    for result in results:
        count = 0
        boxes = result.boxes.cpu().numpy()
        for box in boxes:
            cls = int(box.cls[0])
            if cls == 0:
                count += 1
        return count
    return 0


def open_image(image_path: str | bytes | Path) -> Image.Image:
    """Function to open an image.

    :param image_path: Path to the image
    :type image_path: str | bytes | Path
    :return: Image object
    :rtype: Image.Image
    """
    return Image.open(image_path)


# Function to load images, perform object detection, and save results to a CSV file
def training_output() -> None:
    """Function to load images, perform object detection, and save results to a CSV file.

    :return: None
    :rtype: None

    :raises Exception: If an error occurs during processing
    """

    # Defining path and collectors as constants
    total_images = 0
    image_failed = []

    # Clear the file and write header
    with open("bbox_results.csv", "w", encoding="utf-8") as f:
        f.write("Timestamp,Device_ID,Bbox Count\n")

    # Loop through each collector
    for collector in COLLECTORS:
        images = os.listdir((f"{DATA_PATH}/{collector}/images/"))
        total_images += len(images)
        # Loop through each image in the collector's directory
        for image in images:
            try:
                # Load image
                img = open_image(f"{DATA_PATH}/{collector}/images/{image}")

                # Perform object detection and count people
                count = get_people_count(detect(img))

                # Save results to CSV
                with open("bbox_results.csv", "a", encoding="utf-8") as f:
                    f.write(f"{image[6:-4]},{COLLECTORS.index(collector)},{count}\n")
            except Exception as e:
                # Record failed images
                image_failed.append(f"{DATA_PATH}/{collector}/images/{image}")
                raise e

    # Print summary
    print(f"Total images processed: {total_images}")
    print(f"Images failed: {image_failed}")


def main():
    """The main function for training the YOLO model and saving the results to a CSV file."""
    training_output()


if __name__ == "__main__":
    main()
