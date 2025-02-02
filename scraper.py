import re
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from lxml import html
import hashlib

visited_hashes = set()

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
        
        # Duplicate Content Check
        content_hash = hashlib.sha256(text_content.encode('utf-8')).hexdigest()
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
        
    except Exception:
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
    # check response
    if resp.status != 200:
        return list() # empty list
    
    try: # 200 but no info
        tree = html.fromstring(resp.raw_response.content) # parse content
    except: 
        return list()
    
    if is_resp_low_value(resp):
        return list()
        
    hrefs = tree.xpath('//a[@href]/@href') # extract all <a> tags that have href; return href value

    links = [urljoin(resp.url, href) for href in hrefs]  # some urls are relative - convert these to absolute

    with open('found_urls.txt', 'a+') as f: # quick local save
        for link in links: f.write(f'\n{link}')
    
    return links

def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.

    # conditions:
    # only the domains specified in assignment
    # clean url (i.e. remove fragments)
    # avoid infinite loops
    #    (avoid by using the block list pattern)
    # avoid large files/files with low info value
    #   (Checked by Using the is_resp_low_value function above)

    # Other conditions to avoid:
    # Loggin/logout sessions, cart, checkout, etc.
    # Example:
    # BLOCKLIST_PATTERNS = [
    #     r".*[\?&]page=.*",
    #     r".*[\?&]sort=.*",
    #     r".*[\?&](sessionid|sid|phpsessid)=.*",
    #     r".*\.(mp3|mp4|avi|wmv|flv|doc|docx|ppt|pptx|xls|xlsx)$",
    #     r".*\/(assets|static|public|dist)\/.*",
    #     r"^mailto:.*",
    #     r"^tel:.*",
    #     r".*[\?&](search|query|q|term)=.*",
    #     r".*[\?&](comment|replytocom)=.*",
    #     r".*\/(202\d|199\d|20\d{2})\/.*",  # Matches years from 1990 to 2029
    #     r".*[\?&](token|auth|key)=.*",
    #     r".*\.(rss|xml|atom)$",
    #     r".*[\?&]lang=.*",
    #     r".*\/(en|fr|de|es|jp)\/.*",
    #     r".*[\?&](affiliate|partner|ref)=.*",
    #     r".*[\?&](debug|test)=.*",
    #     r".*\/(api|v1|json|graphql)\/.*",
    #     r".*\/(status|heartbeat|healthcheck)\/.*",
    # ]


    
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
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
        raise
