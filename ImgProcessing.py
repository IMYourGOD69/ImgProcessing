import streamlit as st
import cv2
import numpy as np
import random
import matplotlib.pyplot as plt
from io import BytesIO

# Global variable for minimum area in rectangle detection
min_area = 1000

def upload_image():
    uploaded_file = st.file_uploader("Upload an Image", type=["jpg", "jpeg", "png", "bmp", "tiff"])
    if uploaded_file is not None:
        bytes_data = uploaded_file.read()
        image = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
        return image
    else:
        return None

def upload_image_rectangle_detection(image, min_area):
    if image is None:
        st.error("Failed to load image.")
        return

    window_width, window_height = 800, 600
    aspect_ratio = image.shape[1] / image.shape[0]

    if image.shape[1] > window_width or image.shape[0] > window_height:
        if aspect_ratio > 1:
            new_width = window_width
            new_height = int(new_width / aspect_ratio)
        else:
            new_height = window_height
            new_width = int(new_height * aspect_ratio)
        resized_img = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
    else:
        resized_img = image.copy()

    frame_gray = cv2.cvtColor(resized_img, cv2.COLOR_BGR2GRAY)
    _, binary_image = cv2.threshold(frame_gray, 100, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    contours, _ = cv2.findContours(binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    rectangle_count = 0
    output_img = resized_img.copy()

    for contour in contours:
        epsilon = 0.02 * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)

        if len(approx) == 4 and cv2.contourArea(contour) > min_area:
            cv2.drawContours(output_img, [approx], 0, (0, 255, 0), 2)
            rectangle_count += 1

    cv2.putText(output_img, f"Total Rectangles: {rectangle_count}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    st.subheader("Image with Rectangle Detection")
    st.image(output_img, channels="BGR")
    st.write(f"Total Rectangles Detected: {rectangle_count}")

def live_rectangle_detection():
    st.subheader("Live Rectangle Detection (Webcam)")
    WEBCAM_ID = st.number_input("Enter Webcam ID (usually 0 or 1):", value=1, step=1)
    live_detection = st.checkbox("Start Live Detection")
    video_placeholder = st.empty()

    if live_detection:
        cap = cv2.VideoCapture(WEBCAM_ID)
        if not cap.isOpened():
            st.error("Failed to open webcam. Please check the webcam ID.")
            return

        while live_detection:
            ret, frame = cap.read()
            if not ret:
                st.warning("Failed to capture frame from webcam.")
                break

            frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            _, binary_image = cv2.threshold(frame_gray, 100, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
            contours, _ = cv2.findContours(binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            rectangle_count = 0
            output_frame = frame.copy()

            for contour in contours:
                epsilon = 0.02 * cv2.arcLength(contour, True)
                approx = cv2.approxPolyDP(contour, epsilon, True)

                if len(approx) == 4 and cv2.contourArea(contour) > min_area:
                    cv2.drawContours(output_frame, [approx], 0, (0, 255, 0), 2)
                    rectangle_count += 1

            cv2.putText(output_frame, f"Total Rectangles: {rectangle_count}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

            video_placeholder.image(output_frame, channels="BGR")

            if st.button("Stop Live Detection"):
                live_detection = False

        cap.release()
        cv2.destroyAllWindows()

def upload_image_coin_counting(image):
    if image is None:
        st.error("Failed to load image.")
        return

    window_width, window_height = 800, 600
    aspect_ratio = image.shape[1] / image.shape[0]

    if image.shape[1] > window_width or image.shape[0] > window_height:
        if aspect_ratio > 1:
            new_width = window_width
            new_height = int(new_width / aspect_ratio)
        else:
            new_height = window_height
            new_width = int(new_height * aspect_ratio)
        resized_img = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
    else:
        resized_img = image.copy()

    input_img_gray = cv2.cvtColor(resized_img, cv2.COLOR_BGR2GRAY)
    _, binary_image = cv2.threshold(input_img_gray, 100, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    contours, _ = cv2.findContours(binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    input_img_color = cv2.cvtColor(input_img_gray, cv2.COLOR_GRAY2BGR)
    object_count = 0
    total_value = 0
    count_50sen, count_20sen, count_10sen, count_5sen = 0, 0, 0, 0

    for contour in contours:
        contour_area = cv2.contourArea(contour)
        if 500 <= contour_area <= 5000:
            (x, y), radius = cv2.minEnclosingCircle(contour)
            center = (int(x), int(y))
            radius = int(radius)

            if 34 <= radius <= 36:
                coin_value, coin_label = 0.50, "50 sen"
                count_50sen += 1
            elif 31 <= radius <= 33:
                coin_value, coin_label = 0.20, "20 sen"
                count_20sen += 1
            elif 28 <= radius <= 30:
                coin_value, coin_label = 0.10, "10 sen"
                count_10sen += 1
            elif 25 <= radius <= 27:
                coin_value, coin_label = 0.05, "5 sen"
                count_5sen += 1
            else:
                coin_value, coin_label = 0, "Unknown"

            total_value += coin_value
            cv2.circle(input_img_color, center, radius, (0, 255, 0), 2)
            cv2.putText(input_img_color, coin_label, (center[0] - 20, center[1]), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            object_count += 1

    st.subheader("Image with Coin Classification")
    st.image(input_img_color, channels="BGR")
    st.write(f"Total number of coins found: {object_count}")
    st.write(f"Total value of the coins: RM {total_value:.2f}")
    st.write(f"50 sen coins: {count_50sen}, 20 sen coins: {count_20sen}, 10 sen coins: {count_10sen}, 5 sen coins: {count_5sen}")

def count_manyObjects(image, threshold_value=1, min_area_val=4000):
    if image is None:
        st.error("Failed to load image. Please check the file.")
        return

    window_width, window_height = 800, 600
    h, w = image.shape[:2]
    aspect_ratio = w / h

    if w > window_width or h > window_height:
        if aspect_ratio > 1:
            new_width = window_width
            new_height = int(new_width / aspect_ratio)
        else:
            new_height = window_height
            new_width = int(new_height * aspect_ratio)
        image_resized = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
    else:
        image_resized = image.copy()

    foreground = image_resized.copy()
    seed = (10, 10)
    mask = np.zeros((foreground.shape[0] + 2, foreground.shape[1] + 2), np.uint8)
    cv2.floodFill(foreground, mask, seedPoint=seed, newVal=(0, 0, 0), loDiff=(5, 5, 5), upDiff=(5, 5, 5))

    gray = cv2.cvtColor(foreground, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, threshold_value, 255, cv2.THRESH_BINARY)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5)))
    cntrs, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    filtered_contours = [cnt for cnt in cntrs if cv2.contourArea(cnt) > min_area_val]
    object_count = len(filtered_contours)

    output_image = image_resized.copy()
    for cnt in filtered_contours:
        cv2.drawContours(output_image, [cnt], 0, (0, 255, 0), 2)

    output_image_rgb = cv2.cvtColor(output_image, cv2.COLOR_BGR2RGB)

    st.subheader("Image with Object Detection")
    fig, ax = plt.subplots()
    ax.imshow(output_image_rgb)
    ax.axis('off')
    ax.set_title(f"Total Objects: {object_count}")
    st.pyplot(fig)
    st.write(f"Total Objects Detected: {object_count}")

def process_dynamicImage(image):
    if image is None:
        st.error("Failed to load image.")
        return

    max_width = 800
    height, width = image.shape[:2]
    if width > max_width:
        scaling_factor = max_width / width
        new_size = (int(width * scaling_factor), int(height * scaling_factor))
        image = cv2.resize(image, new_size)

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (7, 7), 0)
    _, thresh = cv2.threshold(blurred, 100, 255, cv2.THRESH_BINARY)
    edges = cv2.Canny(thresh, 50, 200)
    kernel = np.ones((3, 3), np.uint8)
    thresh = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    size_groups = []
    min_area_threshold = 100

    for contour in contours:
        area = cv2.contourArea(contour)
        if area < min_area_threshold:
            continue

        found_group = False
        for idx, (group_area, count) in enumerate(size_groups):
            mean_area = group_area / count
            if abs(mean_area - area) <= 500:
                size_groups[idx] = (group_area + area, count + 1)
                found_group = True
                break

        if not found_group:
            size_groups.append((area, 1))

    colors = [tuple(random.sample(range(256), 3)) for _ in range(len(size_groups))]

    output_image = image.copy()
    for i, contour in enumerate(contours):
        area = cv2.contourArea(contour)
        if area < min_area_threshold:
            continue

        for idx, (group_area, count) in enumerate(size_groups):
            mean_area = group_area / count
            if abs(mean_area - area) <= 800:
                cv2.drawContours(output_image, [contour], -1, colors[idx], 2)
                M = cv2.moments(contour)
                if M["m00"] != 0:
                    cX = int(M["m10"] / M["m00"])
                    cY = int(M["m01"] / M["m00"])
                else:
                    cX, cY = 0, 0
                label = chr(65 + idx)
                cv2.putText(output_image, label, (cX, cY), cv2.FONT_HERSHEY_SIMPLEX, 0.5, colors[idx], 2)
                break

    y0, dy = 30, 30
    for i, (group_area, count) in enumerate(size_groups):
        mean_area = group_area / count
        size_label = f"Size {chr(65 + i)}: {count} (Mean Area: {mean_area:.1f})"
        cv2.putText(output_image, size_label, (10, y0 + i * dy), cv2.FONT_HERSHEY_SIMPLEX, 0.8, colors[i], 2)

    output_image_rgb = cv2.cvtColor(output_image, cv2.COLOR_BGR2RGB)

    st.subheader("Dynamic Object Classification")
    fig, ax = plt.subplots()
    ax.imshow(output_image_rgb)
    ax.axis('off')
    ax.set_title("Dynamic Object Classification")
    st.pyplot(fig)

def dynamicDetection():
    image = upload_image()
    process_dynamicImage(image)

stable_colors = [
    (255, 0, 0),     # Red
    (0, 255, 0),     # Green
    (0, 0, 255),     # Blue
    (255, 255, 0),   # Cyan
    (255, 0, 255),   # Magenta
    (0, 255, 255),   # Yellow
    (128, 0, 128),   # Purple
    (128, 128, 0)    # Olive
]

def process_liveDynamic(frame):
    max_width = 800
    height, width = frame.shape[:2]
    if width > max_width:
        scaling_factor = max_width / width
        new_size = (int(width * scaling_factor), int(height * scaling_factor))
        frame = cv2.resize(frame, new_size)

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (7, 7), 0)
    _, thresh = cv2.threshold(blurred, 100, 255, cv2.THRESH_BINARY)
    edges = cv2.Canny(thresh, 50, 200)
    kernel = np.ones((3, 3), np.uint8)
    thresh = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    size_groups = []
    min_area_threshold = 100

    for contour in contours:
        area = cv2.contourArea(contour)
        if area < min_area_threshold:
            continue

        found_group = False
        for idx, (group_area, count) in enumerate(size_groups):
            mean_area = group_area / count
            if abs(mean_area - area) <= 500:
                size_groups[idx] = (group_area + area, count + 1)
                found_group = True
                break

        if not found_group:
            size_groups.append((area, 1))

    output_frame = frame.copy()
    for i, contour in enumerate(contours):
        area = cv2.contourArea(contour)
        if area < min_area_threshold:
            continue

        for idx, (group_area, count) in enumerate(size_groups):
            mean_area = group_area / count
            if abs(mean_area - area) <= 800:
                color = stable_colors[idx % len(stable_colors)]
                cv2.drawContours(output_frame, [contour], -1, color, 2)
                break

    y0, dy = 50, 30
    for i, (group_area, count) in enumerate(size_groups):
        mean_area = group_area / count
        size_label = f"Size {chr(65 + i)}: {count} (Mean Area: {mean_area:.1f})"
        color = stable_colors[i % len(stable_colors)]
        cv2.putText(output_frame, size_label, (10, y0 + i * dy), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 3)

    return output_frame

def liveDynamic():
    st.subheader("Live Dynamic Shape Detection (Webcam)")
    WEBCAM_ID = st.number_input("Enter Webcam ID (usually 0 or 1):", value=1, step=1, key="live_dynamic_webcam_id")
    live_detection = st.checkbox("Start Live Dynamic Shape Detection")
    video_placeholder = st.empty()

    if live_detection:
        cap = cv2.VideoCapture(WEBCAM_ID)
        if not cap.isOpened():
            st.error("Failed to open webcam. Please check the webcam ID.")
            return

        while live_detection:
            ret, frame = cap.read()
            if not ret:
                st.warning("Failed to capture frame from webcam.")
                break

            processed_frame = process_liveDynamic(frame)
            video_placeholder.image(processed_frame, channels="BGR")

            if st.button("Stop Live Dynamic Detection"):
                live_detection = False

        cap.release()
        cv2.destroyAllWindows()

def main():
    st.title("OpenCV Operations in Streamlit")
    operation_type = st.sidebar.selectbox(
        "Choose an Operation:",
        (
            "Select an option",
            "Upload Image for Coin Counting",
            "Upload Image for Rectangle Detection",
            "Live Detection of Rectangles (Webcam)",
            "Upload Image for Object Detection",
            "Upload Image for Dynamic Shape Classification",
            "Live Detection of Dynamic Shapes (Webcam)",
        ),
    )

    if operation_type == "Upload Image for Coin Counting":
        image = upload_image()
        if image is not None:
            upload_image_coin_counting(image)

    elif operation_type == "Upload Image for Rectangle Detection":
        image = upload_image()
        if image is not None:
            min_area = st.sidebar.slider("Minimum Area for Rectangles", 100, 10000, 1000)
            upload_image_rectangle_detection(image, min_area)

    elif operation_type == "Live Detection of Rectangles (Webcam)":
        live_rectangle_detection()

    elif operation_type == "Upload Image for Object Detection":
        image = upload_image()
        if image is not None:
            st.subheader("Object Detection")
            count_manyObjects(image)

    elif operation_type == "Upload Image for Dynamic Shape Classification":
        dynamicDetection()

    elif operation_type == "Live Detection of Dynamic Shapes (Webcam)":
        liveDynamic()

if __name__ == "__main__":
    main()