import cv2
import time
import os

def take_picture(output_dir=None, save=True):
    camera = cv2.VideoCapture(0)

    try:
        # Capture the picture
        _, frame = camera.read()

        if save:
            timestamp = time.strftime("%Y%m%d%H%M")
            filename = f"image_{timestamp}.jpg"
            filepath = os.path.join(output_dir, filename)

            cv2.imwrite(filepath, frame)
            print(f"Picture taken and saved as {filepath}")
        else:
            print("Picture taken")
            return frame

    finally:
        camera.release()

if __name__ == "__main__":
    output_directory = "images"

    # Create the output directory if it doesn't exist
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
        print(f"Created directory: {output_directory}")

    try:
        while True:
            take_picture(output_directory)
            # Sleep for 30 minutes (1800 seconds)
            time.sleep(1800)  

    except KeyboardInterrupt:
        print("\nProgram terminated by user.")
