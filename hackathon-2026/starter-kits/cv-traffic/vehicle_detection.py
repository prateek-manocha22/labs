import cv2
from ultralytics import YOLO

def detect_vehicles(image_path):
    # Load a pre-trained YOLOv8 model
    model = YOLO('yolov8n.pt') 

    # Run inference
    results = model(image_path)

    # Show results
    for r in results:
        print(f"Detected {len(r.boxes)} objects.")
        # Open results in a window (won't work on headless systems)
        # r.show() 
        
        # Save output image
        r.save(filename='detected_vehicles.jpg')

if __name__ == "__main__":
    print("CV Traffic Starter Kit")
    # detect_vehicles('path_to_your_image.jpg')
    print("Uncomment the line above with a valid image path to run detection.")
