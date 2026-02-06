
import requests
import os

# Define the backend URL
BACKEND_URL = "http://localhost:8000/upload-answer-sheet"

# Path to the image file (using one of the user's uploaded images)
image_path = r"C:\Users\sonys\.gemini\antigravity\brain\f974865a-d60b-4a43-9b79-364738fb5789\uploaded_image_1767262711717.png"

def test_upload():
    if not os.path.exists(image_path):
        print(f"File not found: {image_path}")
        return

    print(f"Uploading {image_path} to {BACKEND_URL}...")
    
    try:
        with open(image_path, "rb") as f:
            files = {"file": f}
            response = requests.post(BACKEND_URL, files=files)
        
        print(f"Status Code: {response.status_code}")
        try:
            print("Response JSON:", response.json())
        except:
            print("Response Text:", response.text)
            
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    test_upload()
