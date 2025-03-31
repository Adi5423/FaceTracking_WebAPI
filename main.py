import cv2
import mediapipe as mp
import numpy as np
import base64
import io
from fastapi import FastAPI, WebSocket
from fastapi.responses import JSONResponse
import uvicorn
from starlette.websockets import WebSocketDisconnect

app = FastAPI()

# Initialize MediaPipe FaceMesh and drawing utilities.
mp_face_mesh = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils
drawing_spec = mp_drawing.DrawingSpec(thickness=1, circle_radius=1, color=(0, 255, 0))

# Use live mode for continuous processing.
face_mesh = mp_face_mesh.FaceMesh(
    static_image_mode=False,
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5
)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # Receive a base64-encoded image from the client.
            data = await websocket.receive_text()
            image_bytes = base64.b64decode(data)
            np_arr = np.frombuffer(image_bytes, np.uint8)
            image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

            # Convert BGR to RGB for MediaPipe processing.
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = face_mesh.process(rgb_image)

            # Draw landmarks on the original image if detected.
            if results.multi_face_landmarks:
                for face_landmarks in results.multi_face_landmarks:
                    mp_drawing.draw_landmarks(
                        image=image,
                        landmark_list=face_landmarks,
                        connections=mp_face_mesh.FACEMESH_TESSELATION,
                        landmark_drawing_spec=drawing_spec,
                        connection_drawing_spec=drawing_spec
                    )
            else:
                # Optionally, you can annotate the image with an error message.
                cv2.putText(image, "No face detected", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

            # Encode the processed image to JPEG.
            ret, buffer = cv2.imencode('.jpg', image)
            if not ret:
                await websocket.send_json({"error": "Image encoding failed"})
                continue

            # Convert JPEG buffer to base64 string.
            processed_image_base64 = base64.b64encode(buffer).decode('utf-8')

            # Send back the processed image.
            await websocket.send_json({"processed_image": processed_image_base64})
    except WebSocketDisconnect:
        print("Client disconnected")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
