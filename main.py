import cv2
import mediapipe as mp
import numpy as np
import base64
from fastapi import FastAPI, WebSocket
import uvicorn
from starlette.websockets import WebSocketDisconnect

app = FastAPI()

# Initialize MediaPipe FaceMesh
mp_face_mesh = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils
drawing_spec = mp_drawing.DrawingSpec(thickness=1, circle_radius=1, color=(0, 255, 0))

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
            data = await websocket.receive_text()
            image_bytes = base64.b64decode(data)
            np_arr = np.frombuffer(image_bytes, np.uint8)
            image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = face_mesh.process(rgb_image)

            if results.multi_face_landmarks:
                landmark_data = []
                for face_landmarks in results.multi_face_landmarks:
                    for idx, landmark in enumerate(face_landmarks.landmark):
                        landmark_data.append({
                            "id": idx,
                            "x": landmark.x,
                            "y": landmark.y,
                            "z": landmark.z
                        })

                await websocket.send_json({"landmarks": landmark_data})
            else:
                await websocket.send_json({"error": "No face detected"})

    except WebSocketDisconnect:
        print("Client disconnected")

# Run the server
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
