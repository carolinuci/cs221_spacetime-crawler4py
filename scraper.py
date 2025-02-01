import re
from urllib.parse import urlparse, urljoin
from lxml import html

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
        print(resp.error)
        return list() # empty list
    
    try: # 200 but no info
        tree = html.fromstring(resp.raw_response.content) # parse content
    except: 
        print(f'{resp.url} cannot be parsed')
        return list()
        
    hrefs = tree.xpath('//a[@href]/@href') # extract all <a> tags that have href; return href value
    # print(resp.url)
    # print(hrefs)    

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
    # avoid large files/files with low info value
    
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
        print ("TypeError for ", parsed)
        raise
