from flask import Flask, request, jsonify
from pathlib import Path
import google.generativeai as genai
from waitress import serve

# Initialize the Flask application
app = Flask(__name__)

# Configure the Google Generative AI
genai.configure(api_key="AIzaSyATPDTtRq7BAP027y-M2j2ztBjq3emqGfE")

# Set up the model configuration
generation_config = {
    "temperature": 0.4,
    "top_p": 1,
    "top_k": 32,
    "max_output_tokens": 8000,
}

safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_ONLY_HIGH"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_ONLY_HIGH"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_ONLY_HIGH"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_ONLY_HIGH"},
]

model = genai.GenerativeModel(model_name="gemini-1.0-pro-vision-latest",
                              generation_config=generation_config,
                              safety_settings=safety_settings)

# Define the API endpoint for content generation
@app.route('/generate_content', methods=['POST'])
def generate_content():
    if 'image' not in request.files:
        return jsonify({"error": "Image file is required"}), 400

    image_file = request.files['image']
    image_path = Path(image_file.filename)
    image_path.write_bytes(image_file.read())

    if not image_path.exists():
        return jsonify({"error": "Could not process the image"}), 500

    # Prepare the prompt with the image data
    image_parts = [{"mime_type": "image/jpeg", "data": image_path.read_bytes()}]
    prompt_parts = [
        " ",
        image_parts[0],
        "Analyze the image deeply, and after analyzing the image fully, suggest a detailed diet plan according to the analyzed image, in proper numbering and heading and subheadings, also suggest exercises according to the analyzed image, also I am giving you some textual data about the person. Now you have to analyze both the image and the textual data given of the person, and by understanding both the image and the textual data, Prepare a detailed diet and exercise plan with extra tips and suggestions. Write a detailed plan of aprox 1000 words.",
    ]

    # Generate content using the model
    response = model.generate_content(prompt_parts)
    return jsonify({"response": response.text})

if __name__ == '__main__':
    serve(app, host='0.0.0.0', port=8080)
