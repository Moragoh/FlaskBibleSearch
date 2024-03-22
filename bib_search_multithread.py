import json
import os
import time
from concurrent.futures import ThreadPoolExecutor


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

def search_in_files(folder_path, file_names, keywords):
    results = []
    for file_name in file_names:
        book_name = os.path.splitext(file_name)[0]
        book_path = os.path.join(folder_path, file_name)

        # Search each chapter of the book as it is streamed in
        for chapter in stream_book(book_path):
            for verse in chapter['verses']:
                if keywords.lower() in verse['content'].lower():
                    results.append({
                        'book': book_name,
                        'chapter': chapter['chapter'],
                        'verse': verse['verse'],
                        'content': verse['content']
                    })
    return results

def search_across_folder(folder_path, keywords):
    results = []

    # Get the list of files in the folder of books
    file_names = [file_name for file_name in os.listdir(folder_path) if file_name.endswith('.json')]

    # Divide the file names into two halves
    mid = len(file_names) // 2
    first_half_files = file_names[:mid]
    second_half_files = file_names[mid:]

    # Use ThreadPoolExecutor to run the searches in parallel
    with ThreadPoolExecutor(max_workers=2) as executor:
        # Submit the two search tasks
        future1 = executor.submit(search_in_files, folder_path, first_half_files, keywords)
        future2 = executor.submit(search_in_files, folder_path, second_half_files, keywords[::-1])  # Reverse keywords for end to start search

        # Combine the results from both searches
        results.extend(future1.result())
        results.extend(future2.result())

    return results

# Example usage
NT_FILE_PATH = './EN/NT'

sentence = "grace of God"

# Record the start time
start_time = time.time()

results = search_across_folder(NT_FILE_PATH, sentence)

elapsed_time = time.time() - start_time
print(f"ELAPSED TIME: {elapsed_time} seconds")

print(results)
