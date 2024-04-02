from ultralytics import YOLO
from PIL import Image
import torch
import os

# Function to perform object detection
def detect(image):
    # Check if GPU is available, otherwise use CPU
    device = "cuda" if torch.cuda.is_available() else "cpu"
    
    # Load YOLO model
    model = YOLO("yolov8s.pt").to(device)
    
    # Perform object detection on the image
    return model(image)

# Function to count the number of people detected in the image
def getPeopleCount(results):
    for result in results:
        count = 0
        boxes = result.boxes.cpu().numpy()
        for box in boxes:
            cls = int(box.cls[0])
            if cls == 0:  
                count += 1
        return count

# Function to open image
def open_image(image_path):
    return Image.open(image_path)

# Function to load images, perform object detection, and save results to a CSV file
def training_output():
    # Defining path and collectors as constants
    DATA_PATH = './data'
    COLLECTORS = ['bryan', 'chris', 'jiayu', 'jurgen']

    total_images = 0
    image_failed = []
    
    # Clear the file and write header
    with open("bbox_results.csv", "w") as f:
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
                count = getPeopleCount(detect(img))

                # Save results to CSV
                with open("bbox_results.csv", "a") as f:
                    f.write(f"{image[6:-4]},{COLLECTORS.index(collector)},{count}\n")
            except Exception as e:
                # Record failed images
                image_failed.append(f"{DATA_PATH}/{collector}/images/{image}")
                print(e)
    
    # Print summary
    print(f"Total images processed: {total_images}")
    print(f"Images failed: {image_failed}")


def main():
    training_output()

if __name__ == "__main__":
    main()
