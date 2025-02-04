import re

def normalize_url(url):
    """
    Normalize the URL by removing fragment identifiers (anything after #).
    """
    return re.sub(r'#.*$', '', url)

def count_same_urls(file_path):
    try:
        # Read the file content
        with open(file_path, 'r') as file:
            file_content = file.read().splitlines()  # Read all lines as separate URLs

        # Normalize URLs by removing fragments and store in a set to count unique ones
        normalized_urls = [normalize_url(url) for url in file_content]

        # Count occurrences of each normalized URL
        url_count = {}
        for url in normalized_urls:
            if url in url_count:
                url_count[url] += 1
            else:
                url_count[url] = 1

        return url_count

    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        return {}

def count_subdomains_from_file(file_path):
    # Regular expression to match subdomains of ics.uci.edu
    subdomain_pattern = r'https?://([a-zA-Z0-9-]+)\.ics\.uci\.edu' 
    try:
        # Read the file content
        with open(file_path, 'r') as file:
            file_content = file.read()

        # Find all matching subdomains in the content
        subdomains = re.findall(subdomain_pattern, file_content)
        
        # Return the count of unique subdomains
        return len(set(subdomains))  # Using set to get unique subdomains

    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        return 0

if __name__ == "__main__":
    file_path = "found_urls.txt"  # Path to your file with URLs
    
    # 4. Count the subdomains from the file
    subdomain_count = count_subdomains_from_file(file_path)
    
    print(f"Number of subdomains for '*.ics.uci.edu' in {file_path}: {subdomain_count}")

    # 1. How many unique pages did you find? 
    # Get the count of URLs
    url_count = count_same_urls(file_path)
    urls_n = len(url_count)
    # Print the results
    print(f"Number of unique url  in {file_path}: {urls_n}")
    #for url, count in url_count.items():
    #    print(f"URL: {url} - Count: {count}")
