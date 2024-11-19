import cv2
import google.generativeai as genai
from gtts import gTTS
import urllib.parse
import webbrowser
import os
import pygame
import smtplib
from email.message import EmailMessage

# Configure the Google Generative AI API
genai.configure(api_key="your_key")

# Choose a Gemini model
model = genai.GenerativeModel(model_name="gemini-1.5-pro")

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

    # Open the search URLs in Firefox
    firefox_path.open(search_url)
    firefox_path.open(search_url1)

# Function to speak the detected medical condition using gTTS and pygame
def speak_text(text):
    try:
        tts = gTTS(text=text, lang='en')
        audio_file = "speech.mp3"
        tts.save(audio_file)
        
        # Initialize pygame mixer
        pygame.mixer.init()
        pygame.mixer.music.load(audio_file)
        pygame.mixer.music.play()

        # Wait until playback finishes
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)

        # Cleanup
        os.remove(audio_file)
    except Exception as e:
        print("Error in text-to-speech:", e)

# Function to send an email with the captured image and medical condition
def send_email(image_path, medical_condition):
    try:
        # Email details
        sender_email = "xyz@gmail.com"  # Replace with your email
        sender_password = "bla bla"  # Replace with your email password
        recipient_email = "xys@gmail.com"  # Replace with recipient email

        # Create email message
        msg = EmailMessage()
        msg["Subject"] = "Medical Condition Identified"
        msg["From"] = sender_email
        msg["To"] = recipient_email
        msg.set_content(f"The detected medical condition is: {medical_condition}\n\nPlease find the attached image for reference.")

        # Attach the image file
        with open(image_path, "rb") as img_file:
            img_data = img_file.read()
            img_name = os.path.basename(image_path)
            msg.add_attachment(img_data, maintype="image", subtype="jpeg", filename=img_name)

        # Send the email using SMTP
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()  # Secure the connection
            server.login(sender_email, sender_password)
            server.send_message(msg)
            print("Email sent successfully.")
    except Exception as e:
        print(f"Error sending email: {e}")

# Main logic to analyze a frame captured from the camera
def main():
    # Open the video capture from the default camera
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Error: Could not open video capture.")
        return

    print("Press 's' to capture an image and analyze it, or 'q' to quit.")

    while True:
        # Capture frame-by-frame
        ret, frame = cap.read()
        
        # Check if frame was captured successfully
        if not ret:
            print("Failed to grab frame.")
            break

        # Display the resulting frame
        cv2.imshow('Video Feed', frame)

        # Wait for key press
        key = cv2.waitKey(1) & 0xFF

        # If 's' is pressed, save the current frame and analyze it
        if key == ord('s'):
            image_path = "captured_frame.jpg"
            cv2.imwrite(image_path, frame)
            print("Image captured and saved as 'captured_frame.jpg'")

            # Detect the medical condition from the image
            full_response, medical_condition = identify_medical_condition(image_path)

            # Print both the full response and the medical condition name
            print("Full AI Response:", full_response)
            print("Medical Condition Detected:", medical_condition)

            # Search the detected medical condition in the browser
            search_in_browser(medical_condition)

            # Speak the detected medical condition
            speak_text(f"The detected medical condition is {medical_condition}")

            # Send an email with the captured image and medical condition
            send_email(image_path, medical_condition)

            # Remove the captured frame file after processing
            os.remove(image_path)

        # If 'q' is pressed, exit the loop
        elif key == ord('q'):
            print("Exiting the video capture.")
            break

    # Release the video capture and close all OpenCV windows
    cap.release()
    cv2.destroyAllWindows()

# Start the continuous video feed and wait for key commands
main()
