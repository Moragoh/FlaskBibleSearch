from flask import Flask, request, jsonify
import json

app = Flask(__name__)

# Generator function to stream JSON file one entry at a time
def stream_json_file(file_path):
    with open(file_path) as f:
        decoder = json.JSONDecoder() # Initialize decoder, which will parse the JSON
        buffer = '' # Storage for the partial JSON content read from file
        for line in f:
            buffer += line.strip() # Removes all leading and trailing whitespace and keeps adding it to buffer
            # With each updated version of the buffer, we try and decode it to see if we have a complete JSON object 
            # after reading in line by line
            while buffer: 
                try:
                    # Attempts to decode a JSON object in the current buffer
                    # obj is the decoded JSON object, and idx the index in the bugger where the decoding ended
                    obj, idx = decoder.raw_decode(buffer) 

                    # In the current buffer, cut off the last complete JSON object we read, leaving only the next partial 
                    # JSON object so that the next JSON object can be read in line by line and parsed
                    # .lstrip() gets rid of leading whitespace from the left side of the string to remove traling whitespace
                    # from the sliced string
                    buffer = buffer[idx:].lstrip() 
                    
                    # Yields most recent complete JSON object that was parsed
                    # Unlike return, yield pauses the function, saves its state, and returns the value to its caller
                    # and starts from where it left off the next time it is called
                    for chapter in obj['chapters']:
                        yield chapter
                except ValueError: 
                    # If parsing fails, means we do not have a complete JSON object so continue to read more lines
                    break

# Load the JSON file for 1 Corinthians
BIBLE_FILE_PATH = '1_corinthians.json'

@app.route('/search', methods=['GET'])
def handle_search():
    keyword = request.args.get('keyword')
    if not keyword:
        return jsonify({'error': 'No keyword provided'}), 400

    results = []
    # Each entry is the last complete JSON entry parsed from file
    for entry in stream_json_file(BIBLE_FILE_PATH):
        print(entry)
        for chapter in entry['chapters']:
            for verse in chapter['verses']:
                if keyword.lower() in verse['content'].lower():
                    results.append({
                        'book': entry['bookName'],
                        'chapter': chapter['chapter'],
                        'verse': verse['verse'],
                        'content': verse['content']
                    })
    return jsonify({'results': results})

if __name__ == '__main__':
    app.run(debug=True)
