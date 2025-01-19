import json

def clean_text(text):
    """Clean the text by removing unnecessary characters and formatting"""
    # Remove \n characters
    text = text.replace('\n', ' ')
    # Remove multiple spaces
    text = ' '.join(text.split())
    return text

def extract_narrator_scripts():
    """Extract narrator scripts from comic_analysis.json and save to txt file"""
    try:
        # Step 1: Read the JSON file
        print("📖 Reading comic_analysis.json...")
        with open('comic_analysis.json', 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)
        
        # Step 2: Create a list to store formatted scripts
        formatted_scripts = []
        
        # Step 3: Process each entry in order
        print("🔄 Processing narrator scripts...")
        for filename in sorted(data.keys()):
            try:
                # Get the narrator script
                script = data[filename].get('narrator_script', '')
                if script:
                    # Clean the text
                    clean_script = clean_text(script)
                    # Add filename and cleaned script to list
                    formatted_scripts.append(f"{clean_script}\n")
                    print(f"✓ Processed {filename}")
            except Exception as e:
                print(f"❌ Error processing {filename}: {str(e)}")
        
        # Step 4: Write to output file
        output_file = 'narrator_scripts.txt'
        print(f"\n📝 Writing to {output_file}...")
        with open(output_file, 'w', encoding='utf-8') as txt_file:
            # Join all scripts with double newlines for separation
            txt_file.write('\n'.join(formatted_scripts))
        
        print(f"✨ Successfully extracted {len(formatted_scripts)} narrator scripts to {output_file}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    extract_narrator_scripts()