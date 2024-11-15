import cv2
import google.generativeai as genai
import pyttsx3
import urllib.parse
import webbrowser

# Configure the Google Generative AI API
genai.configure(api_key="youkey")

# Choose a Gemini model.
model = genai.GenerativeModel(model_name="gemini-1.5-pro")

# Initialize text-to-speech engine
engine = pyttsx3.init()

# Set properties for the speech
engine.setProperty('rate', 180)    # Speed of speech
engine.setProperty('volume', 1)    # Volume level (0.0 to 1.0)

# Function to upload an image and get the medical condition response from the AI model
def identify_medical_condition(image_path):
    # Upload the image file to Google Generative AI API
    sample_file = genai.upload_file(path=image_path, display_name="Medical Image")
    
    # First query: Ask for a rough estimate of the medical condition
    medical_condition_response = model.generate_content([sample_file, "What medical condition is shown in this image? Just give a rough estimate, no need for exact diagnosis."])
    
    # Second query: Ask for only the name of the medical condition
    condition_name_response = model.generate_content([sample_file, "Name only the medical condition shown in this image."])
    
    return medical_condition_response.text, condition_name_response.text

# Function to search medical condition in the browser using Firefox
def search_in_browser(medical_condition):
    query = urllib.parse.quote(medical_condition)  # Properly encode the medical condition for the URL
    search_url = f"https://www.google.com/search?q={query}"
    search_url1 = f"https://www.google.com/search?q=medication for {query} amazon"

    # Get the Firefox browser (ensure it's installed in PATH)
    firefox_path = webbrowser.get('firefox')

    # Open the search URL in Firefox
    firefox_path.open(search_url)
    firefox_path.open(search_url1)

# Main logic to analyze a static image and identify medical condition
def main(image_path):
    # Detect the medical condition from the image
    full_response, medical_condition = identify_medical_condition(image_path)
    
    # Print both the full response and the medical condition name
    print("Full AI Response:", full_response)
    print("Medical Condition Detected:", medical_condition)
    
    # Search the detected medical condition in the browser
    search_in_browser(medical_condition)

    # Speak the detected medical condition
    engine.say(f"The detected medical condition is {medical_condition}")
    engine.runAndWait()

# Example usage
image_path = 'skin_cond4.jpeg'  # Replace with the path to your medical image file
main(image_path)
