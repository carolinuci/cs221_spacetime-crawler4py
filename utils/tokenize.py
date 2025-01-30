import re
from collections import Counter
import argparse

# Part A: Word Frequencies from assignment 01

# Method 1: tokenize
# Reads a text file and returns a list or a set of tokens (words)

def tokenize(text_file_path, rtype=""):
    tokens = []
    try:
        with open(text_file_path, 'r', encoding="utf8") as file:
            text = file.read().lower()  # Convert the text to lowercase to ignore capitalization
            # Use regex to extract words (alphanumeric characters)
            tokens = re.findall(r'\b\w+\b', text)
    except FileNotFoundError:
        print(f"The file at {text_file_path} was not found.")

    if rtype == "set":
        return set(tokens)

    return tokens


# Method 2: computeWordFrequencies
# Takes a list of tokens and returns a dictionary with the frequency of each token.
def computeWordFrequencies(tokens):
    return dict(Counter(tokens))

# Method 3: printnew
# Prints the word frequencies ordered by decreasing frequency.


def printnew(frequencies):
    sorted_frequencies = sorted(
        frequencies.items(), key=lambda x: x[1], reverse=True)

    print("Word Frequencies (ordered by frequency):")
    for word, count in sorted_frequencies:
        print(f"{word}: {count}")

# Main function to demonstrate the solution


def main():
    # Specify the path to the text file (adjust the file path as needed)
    parser = argparse.ArgumentParser(
        description="Compute word frequencies from a text file. if there is no argv for file, it uses sample.txt")
    parser.add_argument("file_path", help="Path to the text file",
                        nargs="?", default="sample.txt")
    args = parser.parse_args()

    text_file_path = args.file_path  # Get the file path from command-line argument

    # Tokenize the file content
    tokens = tokenize(text_file_path)

    if tokens:  # Only proceed if the list of tokens is not empty
        # Compute word frequencies
        frequencies = computeWordFrequencies(tokens)

        # Print the word frequencies
        printnew(frequencies)
        #print(len(frequencies))

# Execute the main function
if __name__ == "__main__":
    main()
