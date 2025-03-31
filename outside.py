# for urnning the code outside the TrackAPIweb directory

import cv2
import mediapipe as mp
import os

# Set up the correct path for the TrackAPIweb directory
base_path = os.path.join(".", "TrackAPIweb")

# Initialize MediaPipe Face Mesh
mp_face_mesh = mp.solutions.face_mesh
# For drawing landmarks on the face
mp_drawing = mp.solutions.drawing_utils
drawing_spec = mp_drawing.DrawingSpec(thickness=1, circle_radius=1, color=(0, 255, 0))

# Initialize Face Mesh with static_image_mode for single image processing
with mp_face_mesh.FaceMesh(static_image_mode=True,
                            max_num_faces=1,
                            refine_landmarks=True,
                            min_detection_confidence=0.5) as face_mesh:
    # Read the input image from TrackAPIweb directory
    input_path = os.path.join(base_path, "face_R.jpg")
    image = cv2.imread(input_path)
    if image is None:
        print(f"Could not read input image from {input_path}")
        exit(1)

    # Convert the image color space from BGR to RGB as MediaPipe expects RGB.
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Process the image to detect face landmarks
    results = face_mesh.process(rgb_image)

    # Check if any face is detected
    if results.multi_face_landmarks:
        # Loop over the face landmarks
        for face_landmarks in results.multi_face_landmarks:
            # Draw the landmarks on the original image
            mp_drawing.draw_landmarks(
                image=image,
                landmark_list=face_landmarks,
                connections=mp_face_mesh.FACEMESH_TESSELATION,
                landmark_drawing_spec=drawing_spec,
                connection_drawing_spec=drawing_spec)
    else:
        print("No face detected.")

    # Save the output image in TrackAPIweb directory
    output_path = os.path.join(base_path, "output_R.jpg")
    cv2.imwrite(output_path, image)
    print(f"Output saved to {output_path}")