import google.generativeai as genai
import PIL.Image
import os
import json
import time
from datetime import datetime
import re

def extract_json_from_response(response_text):
    """Extract and parse JSON from the response text"""
    try:
        # Find JSON string between ```json and ``` markers
        json_match = re.search(r'```json\n(.*?)\n```', response_text, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
            # Parse the JSON string into a Python object
            return json.loads(json_str)
        else:
            print("❌ No JSON found in response")
            return None
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing JSON: {str(e)}")
        return None

def append_to_json(filename, data):
    """Append or update data in JSON file"""
    try:
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
        else:
            existing_data = {}
        
        existing_data.update(data)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, indent=4, ensure_ascii=False)
            
        print(f"✓ Successfully updated {filename}")
    except Exception as e:
        print(f"❌ Error updating JSON file: {str(e)}")

# Configure the API key
print("\n🔑 Configuring Gemini API...")
genai.configure(api_key='AIzaSyBI8sHX7fsjHx7Mhi7GagnsHpmj0zQHYhg')

# Load the model
print("🤖 Loading Gemini Pro Vision model...")
model = genai.GenerativeModel('gemini-1.5-flash')

# Directory containing the images
image_dir = 'dandadan/c001'
print(f"📁 Working directory: {image_dir}")

# Get total number of images for progress tracking
image_files = sorted([f for f in os.listdir(image_dir) if f.endswith(('.jpg', '.jpeg', '.png'))])
total_images = len(image_files)
print(f"📊 Found {total_images} images to process")

# Base prompt
prompt = """
describe what is happening in this comic, the dialogue said, the characters present 

present the data in a json format 
{
"character": {
"name":""
"description":""
"pose":""
"emotion":""
}
"ocr_text_describing": {
"dialogue": "",
"description_scene": ""
}
}
"""

# Output file
output_file = 'comic_analysis.json'

# Process each image in the directory
start_time = time.time()
for index, filename in enumerate(image_files, 1):
    current_time = datetime.now().strftime("%H:%M:%S")
    print(f"\n⏳ [{current_time}] Processing image {index}/{total_images}: {filename}")
    
    try:
        # Load and process image
        image_path = os.path.join(image_dir, filename)
        image = PIL.Image.open(image_path)
        
        print(f"📷 Image loaded: {image.size[0]}x{image.size[1]} pixels")
        
        # Generate initial response
        print("🔄 Generating scene description...")
        response = model.generate_content([prompt, image])
        print("✓ Scene description generated")
        
        # Parse the JSON from the response
        scene_description = extract_json_from_response(response.text)
        if scene_description is None:
            raise Exception("Failed to parse scene description JSON")
        
        # Generate narrator script
        print("🔄 Generating narrator script...")
        prompt_for_final_response = response.text + "Generate a precise and factual script for a narrator, reporting the events or details present in the submitted images. Focus on describing what is happening in a clear, objective manner without adding any transitions, music cues, or emotional language. The narration should solely report on the visual elements and actions captured in the images, providing a thorough and accurate description of the scene"
        final_response = model.generate_content(prompt_for_final_response)
        print("✓ Narrator script generated")
        
        # Prepare response data
        response_data = {
            filename: {
                "scene_description": scene_description,  # Now a proper JSON object
                "narrator_script": final_response.text,
                "processed_at": current_time
            }
        }
        
        # Stream update to JSON file
        append_to_json(output_file, response_data)
        
        # Calculate and display progress
        progress = (index / total_images) * 100
        elapsed_time = time.time() - start_time
        avg_time_per_image = elapsed_time / index
        remaining_images = total_images - index
        estimated_time_remaining = remaining_images * avg_time_per_image
        
        print(f"📊 Progress: {progress:.1f}%")
        print(f"⏱️ Time elapsed: {elapsed_time:.1f}s")
        print(f"⏳ Estimated time remaining: {estimated_time_remaining:.1f}s")
        
    except Exception as e:
        print(f"❌ Error processing {filename}: {str(e)}")
        error_data = {
            filename: {
                "error": str(e),
                "processed_at": current_time
            }
        }
        append_to_json(output_file, error_data)

# Final statistics
end_time = time.time()
total_time = end_time - start_time
print(f"\n✨ Processing completed!")
print(f"📊 Total images processed: {total_images}")
print(f"⏱️ Total time taken: {total_time:.1f} seconds")
print(f"⚡ Average time per image: {(total_time/total_images):.1f} seconds")
print(f"💾 Results saved to: {output_file}")