import re
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from lxml import html
import tldextract
from utils.tokenize import tokenize_from_text

visited_hashes = set()
visited_urls = set()  # Add this new set to track visited URLs

def parse_url(url):
    # Remove URL fragment
    url = url.split('#')[0]
    parsed = urlparse(url)
    return parsed


def get_full_domain(url):
    extracted = tldextract.extract(url)
    # Reconstruct the domain with subdomain
    domain_parts = [part for part in [extracted.subdomain, extracted.domain, extracted.suffix] if part]
    full_domain = '.'.join(domain_parts)
    return full_domain

def is_domain_allowed(full_domain):
    allowed_domains = [
        'ics.uci.edu',
        'cs.uci.edu',
        'informatics.uci.edu',
        'stat.uci.edu',
    ]
    return any(full_domain.endswith(allowed_domain) for allowed_domain in allowed_domains)

def is_today_uci_url_allowed(parsed_url):
    allowed_today_prefix = '/department/information_computer_sciences/'
    return parsed_url.path.startswith(allowed_today_prefix)

def is_allowed_url(url):
    try:
        parsed_url = parse_url(url)
        full_domain = get_full_domain(url)

        # Check for HTTP or HTTPS scheme
        if parsed_url.scheme not in ('http', 'https'):
            return False

        # Check if domain is 'today.uci.edu'
        if full_domain == 'today.uci.edu':
            return is_today_uci_url_allowed(parsed_url)
        else:
            return is_domain_allowed(full_domain)
    except Exception as e:
        # Handle exceptions, e.g., malformed URLs
        print(f"Error processing URL {url}: {e}")
        return False
    
def get_number_of_words(resp, mode=""):
    # Check if response is valid and has content
    result = 0
    if resp.status != 200 or not resp.raw_response or not resp.raw_response.content:
        return result

    
    try:
        # Create BeautifulSoup object from the response content
        soup = BeautifulSoup(resp.raw_response.content, 'html.parser')
        #print("caaaaaaaaa")
        #print(soup.get_text().strip())
        #print("caaaaaaaaa")
        result = tokenize_from_text(soup.get_text().strip(), rtype='set')

    except Exception as e:
        print(f"Error count content from {resp.url}: {str(e)}")
        return result
    
    if mode == "w":
        import os
        import time
        
        stopword_file = 'stopword.txt' ## TO FIX, make it global
        stopwords = set()

        # Read the stopword.txt file into a set for quick lookup
        with open(stopword_file, 'r') as f:
            stopwords = set(line.strip() for line in f)

        for key in result:
            if key not in stopwords:

                # Define the path to the log file using the key
                file_path = os.path.join("Logs", f"{key}.k")

                # Create the file if it doesn't exist, or append to it if it does
                with open(file_path, 'a') as f:
                    timestamp = time.strftime('%Y%m%d%H%M%S')
                    f.write( f"{timestamp}\n")

                #print(f"Appended to file {file_path}")

    
    return len(result)


def is_resp_low_value(resp):
    # Check if response is valid and has content
    if resp.status != 200 or not resp.raw_response or not resp.raw_response.content:
        return True
    
    try:
        # Create BeautifulSoup object from the response content
        soup = BeautifulSoup(resp.raw_response.content, 'html.parser')
        
        # Get text content and remove extra whitespace
        text_content = ' '.join(soup.get_text().split())
        
        # If the page has very little text content, consider it low info
        if len(text_content) < 50:  # You can adjust this threshold
            return True
        
        # Duplicate Content Check using Python's built-in hash function
        content_hash = hash(text_content)
        if content_hash in visited_hashes:
            return True
        visited_hashes.add(content_hash)

        # High Link-to-Text Ratio Check
        links = soup.find_all('a')
        link_count = len(links)
        text_length = max(1, len(text_content))
        if link_count / text_length > 5:
            return True 
            
        # Large File Size Check
        if resp.raw_response.headers.get('Content-Length'):
            file_size = int(resp.raw_response.headers['Content-Length'])
            if file_size > 10 * 1024 * 1024:  # 10 MB threshold
                return True

        return False
        
    except Exception as e:
        print(f"Error parsing content from {resp.url}: {str(e)}")
        return True

def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]

def extract_next_links(url, resp):
    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content

    # ------------
    # Check if we've seen this URL before
    if resp.url in visited_urls:
        return list()
    visited_urls.add(resp.url)
    
    # check response
    if resp.status != 200:
        print(resp.error)
        return list() # empty list
    
    try: # 200 but no info
        tree = html.fromstring(resp.raw_response.content) # parse content
    except: 
        print(f'{resp.url} cannot be parsed')
        return list()
    
    if is_resp_low_value(resp):
        return list()
        
    hrefs = tree.xpath('//a[@href]/@href') # extract all <a> tags that have href; return href value

    # Modify this section to defragment URLs while creating absolute URLs
    links = [urljoin(resp.url, href).split('#')[0] for href in hrefs]  # remove fragments and convert relative to absolute

    n = get_number_of_words(resp, "w")   
    with open('found_urls.txt', 'a+') as f: # quick local save
        for link in links: 
            if link not in visited_urls:
                f.write(f"\n{url} - {n}")
    
    return links

def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.

    # conditions:
    # only the domains specified in assignment
    # avoid infinite loops
    #    (avoid by using the block list pattern)
    # avoid large files/files with low info value
    #   (Checked by Using the is_resp_low_value function above)

    # Other conditions to avoid:
    # Loggin/logout sessions, cart, checkout, etc.
    # These might lead to infinite loops.
    # Example:
    BLOCKLIST_PATTERNS = [
        r".*[\?&]page=.*",
        r".*[\?&]sort=.*",
        r".*[\?&](sessionid|sid|phpsessid)=.*",
        r".*\.(mp3|mp4|avi|wmv|flv|doc|docx|ppt|pptx|xls|xlsx)$",
        r".*\/(assets|static|public|dist)\/.*",
        r"^mailto:.*",
        r"^tel:.*",
        r".*[\?&](search|query|q|term)=.*",
        r".*[\?&](comment|replytocom)=.*",
        r".*\/(202\d|199\d|20\d{2})\/.*",  # Matches years from 1990 to 2029
        r".*[\?&](token|auth|key)=.*",
        r".*\.(rss|xml|atom)$",
        r".*[\?&]lang=.*",
        r".*\/(en|fr|de|es|jp)\/.*",
        r".*[\?&](affiliate|partner|ref)=.*",
        r".*[\?&](debug|test)=.*",
        r".*\/(api|v1|json|graphql)\/.*",
        r".*\/(status|heartbeat|healthcheck)\/.*",
    ]


    
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False

        # Check against blocklist patterns
        for pattern in BLOCKLIST_PATTERNS:
            if re.match(pattern, url, re.IGNORECASE):
                return False
            
        # Check if the URL is allowed within the allowed domains
        if not is_allowed_url(url):
            return False
            
        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())

    except TypeError:
        print ("TypeError for ", parsed)
        raise
