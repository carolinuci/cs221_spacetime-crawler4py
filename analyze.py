import re

def normalize_url(url):
    """
    Normalize the URL by removing fragment identifiers (anything after #).
    """
    url_without_fragment = re.sub(r'#.*$', '', url)
    normalized_url = re.sub(r',.*$', '', url_without_fragment)  # Remove anything after a comma
    return normalized_url

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
    

def extract_max_column_value(file_path):
    """
    Extract the number after the comma in each URL and return the maximum value.
    """
    max_value = 0
    result = ""
    
    try:
        # Read the file content
        with open(file_path, 'r') as file:
            file_content = file.read().splitlines()  # Read all lines as separate URLs

        # Extract the second column (after the comma) and find the maximum value
        for url in file_content:
            # Match the number after the comma in the URL (e.g., '21' or '370')
            match = re.search(r' - (\d+)', url)
            if match:
                value = int(match.group(1))
                if value > max_value:
                    max_value = value
                    result = url
        
        return result

    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        return None
    

def list_and_sort_directories_by_file_count(parent_dir):
    import subprocess
    # Linux command to list and sort directories by the number of files
    #command = f"find {parent_dir} -mindepth 1 -maxdepth 1 -type d -exec sh -c 'echo -n \"{{}} \"; find \"{{}}\" -type f | wc -l' \; | sort -k2 -n -r"
    # limit 50
    command = 'find '+ parent_dir + ' -type f -name "*.k" -exec wc -l {} + | sort -n -r | head -n 50'

    #command = f"find {parent_dir} -mindepth 1 -maxdepth 1 -type d -exec sh -c 'echo -n \"{{}} \"; find \"{{}}\" -type f | wc -l' \; | sort -k2 -n -r | head -n 50"
    try:
        # Run the command and get the output
        result = subprocess.check_output(command, shell=True, text=True)
        
        # Print the sorted directories with file counts
        print("Most frequency words and counts:")
        print(result)

    except subprocess.CalledProcessError as e:
        print(f"Error occurred: {e}")




if __name__ == "__main__":
    file_path = "found_urls.txt"  # Path to your file with URLs
    
   

    # Question 1. How many unique pages did you find? 
    # Get the count of URLs
    url_count = count_same_urls(file_path)
    urls_n = len(url_count)
    # Print the results
    print(f"Number of unique url  in {file_path}: {urls_n}")
    #for url, count in url_count.items():
    #    print(f"URL: {url} - Count: {count}")

    # Question 2
    max_url= extract_max_column_value(file_path)
    # Print the results
    print(f"Number of max word url, words : {max_url}")



    # Question 3
    # use linux cmd line
    parent_directory = "./Logs/"
    list_and_sort_directories_by_file_count(parent_directory)



     # Question 4. Count the subdomains from the file
    subdomain_count = count_subdomains_from_file(file_path)
    print(f"Number of subdomains for '*.ics.uci.edu' in {file_path}: {subdomain_count}")

