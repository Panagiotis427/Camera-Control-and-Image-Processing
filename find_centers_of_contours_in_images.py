"""Find and draw center of each contour in a given image using OpenCV."""

import cv2
import numpy as np
import matplotlib.pyplot as plt

def find_draw_center_of_contours(image_path):

    # Read image
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if image is None:
        print(f"Error: Unable to open image file {image_path}")
        return

    # Find contours
    contours, _ = cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Draw center of each object
    for i, contour in enumerate(contours):
        # Get center of mass
        M = cv2.moments(contour)
        if M["m00"] == 0:
            continue
        cX = int(M["m10"] / M["m00"])
        cY = int(M["m01"] / M["m00"])

        # Draw center
        cv2.circle(image, (cX, cY), 80, (0, 0, 255), -1)

        # Draw text
        textx, texty = cv2.getTextSize(f"Contour #{i+1}", cv2.FONT_HERSHEY_SIMPLEX, 10, 28)
        cv2.rectangle(image, (cX - 30, cY + 360), (cX - 30 + textx[0], cY + 360 - textx[1]), (0, 0, 255), -1)
        cv2.putText(image, f"Contour #{i+1}", (cX - 30, cY + 360), cv2.FONT_HERSHEY_SIMPLEX, 10, (255, 255, 255), 28)

    # Show image
    plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    plt.show()

    # Save image
    cv2.imwrite("/sample_contours_centers.png", image)


if __name__ == "__main__":

    image_path = "/sample.png"
    find_draw_center_of_contours(image_path)
