import json
import os
import time

NT_FILE_PATH = './EN/NT'

def stream_book(file_path):
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

def search_across_folder(folder_path, keywords):
    results = []
    # Iterate over all files in the folder
    for file_name in os.listdir(folder_path):
        # Check if the file is a JSON file
        if file_name.endswith('.json'):
            # Extract the book name from the file name
            book_name = os.path.splitext(file_name)[0]

            # Get the full path of the file
            book_path = os.path.join(folder_path, file_name)

            # Stream each book and search for the keyword
            for chapter in stream_book(book_path):
                """REGULAR SEARCH"""
                for verse in chapter['verses']:
                    if keywords.lower() in verse['content'].lower():
                        results.append({
                            'book': book_name, # For the name of the book, use the variable obtained from the file name
                            'chapter': chapter['chapter'],
                            'verse': verse['verse'],
                            'content': verse['content']
                        })
    return results

# Example usage
sentence = "grace of God"

# Record the start time
start_time = time.time()

results = search_across_folder(NT_FILE_PATH, sentence)

elapsed_time = time.time() - start_time
print(f"ELAPSED TIME: {elapsed_time} seconds")

print(results)

