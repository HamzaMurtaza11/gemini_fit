from flask import Flask, request, jsonify
# Removed pathlib import as it's no longer needed for file path management
import google.generativeai as genai

# Initialize the Flask application
app = Flask(__name__)

# Configure the Google Generative AI
genai.configure(api_key="AIzaSyATPDTtRq7BAP027y-M2j2ztBjq3emqGfE")  # Make sure to secure your API key properly

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
    # Directly read the image file bytes, avoiding file system writes
    image_bytes = image_file.read()

    # Since we're not writing to the disk, we check if the bytes are not empty
    if not image_bytes:
        return jsonify({"error": "Could not process the image"}), 500

    # Prepare the prompt with the image data
    image_parts = [{"mime_type": image_file.mimetype, "data": image_bytes}]
    prompt_parts = [
        " ",
        image_parts[0],
        "Analyze the image deeply, and after analyzing the image fully, suggest a detailed diet plan according to the analyzed image, in proper numbering and heading and subheadings, also suggest exercises according to the analyzed image, also I am giving you some textual data about the person. Now you have to analyze both the image and the textual data given of the person, and by understanding both the image and the textual data, Prepare a detailed diet and exercise plan with extra tips and suggestions. Write a detailed plan of aprox 1000 words.",
    ]

    # Generate content using the model
    response = model.generate_content(prompt_parts)
    return jsonify({"response": response.text})

if __name__ == '__main__':
    app.run(debug=True)
