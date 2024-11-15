import cv2
import google.generativeai as genai
import pyttsx3
import webbrowser
import urllib.parse

# Configure the Google Generative AI API
genai.configure(api_key="AIzaSyAKi62cSIUc6fVt5XH0MZWN9G3WDkDCuCs")

# Choose a Gemini model.
model = genai.GenerativeModel(model_name="gemini-1.5-pro")

engine = pyttsx3.init()

# Set properties for the speech
engine.setProperty('rate', 180)    # Speed of speech
engine.setProperty('volume', 1)    # Volume level (0.0 to 1.0)

# Check if espeak is available and set properties
if 'espeak' in engine.getProperty('voices')[0].id:
    engine.setProperty('voice', 'en-us')
    engine.setProperty('pitch', 70)  # Set pitch (0-100)

# Function to capture a frame and save it as an image
def capture_frame():
    ret, frame = cap.read()
    if ret:
        image_path = "captured_frame.jpg"
        cv2.imwrite(image_path, frame)
        return image_path
    return None

# Function to upload an image and get the response from the AI model
def identify_object(image_path):
    sample_file = genai.upload_file(path=image_path, display_name="Captured Frame")
    
    # First query to get a brief description of the product (limited to 1-2 sentences)
    response = model.generate_content([sample_file, "What product is this and where can I buy it? Limit the description to one or two sentences."])
    
    # Second query to get just the product name in fewer words
    product_name_response = model.generate_content([sample_file, "Give me only the product name in 5 words or less."])
    
    return response.text, product_name_response.text

# Function to search product in the browser using Firefox
def search_in_browser(product_name):
    query = urllib.parse.quote(product_name)  # Properly encode the product name for the URL
    search_url = f"https://www.google.com/search?q={query}"
    
    # Get the Firefox browser (ensure it's installed in PATH)
    firefox_path = webbrowser.get('firefox')
    
    # Open the search URL in Firefox
    firefox_path.open(search_url)

# Initialize webcam
esp32_cam_url = "http://192.168.208.229:81/stream"
cap = cv2.VideoCapture(0)

# Main loop to check for 's' key press and capture frames
def main_loop():
    while True:
        ret, frame = cap.read()
        if ret:
            cv2.imshow("ESP32 Cam Stream", frame)

        # Check for 's' key press to capture frame
        if cv2.waitKey(1) & 0xFF == ord('s'):
            image_path = capture_frame()
            if image_path:
                full_result, product_name = identify_object(image_path)
                
                # Print limited response (1-2 sentences)
                print("Brief Identified Information:", full_result)

                # Open browser and search for the product name only (before speaking)
                print("Product Name Identified:", product_name)
                search_in_browser(product_name)

                # Convert text-to-speech (for limited response)

                # Speak the product name (after browser opens)
                engine.say(f"The product name is {product_name}")
                engine.runAndWait()

        # Break loop if 'q' is pressed to quit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

# Start the main loop
main_loop()

# When everything is done, release the capture
cap.release()
cv2.destroyAllWindows()
