import argparse
import os
import requests as r
from urllib3.exceptions import InsecureRequestWarning
import warnings

def main():
    # Command-line argument parser setup
    parser = argparse.ArgumentParser(description='veFuzz')
    parser.add_argument("-w", "--wordlist", metavar="path_to_list", type=str, help="Path to the keyword list file")
    parser.add_argument("-u", "--url", metavar="target_url", type=str, help="URL of the target website with 'FUZZ' as a placeholder")
    parser.add_argument("-o", "--output", metavar="output", type=str, help="Output file")
    parser.add_argument("-fc", metavar="filter_code", type=int, nargs='+', help="HTTP response codes to ignore")
    parser.add_argument("-fl", metavar="filter_length", type=int, help="Filter by HTTP response length")
    parser.add_argument("-fs", metavar="filter_size", type=int, help="Filter by HTTP response size")
    parser.add_argument("-H", "--headers", metavar="key:value", type=str, nargs='+', help="Custom headers for the HTTP request with 'FUZZ' as a placeholder")
    parser.add_argument("--no-ssl", action="store_true", help="Disable SSL certificate verification")
    parser.add_argument("-t", "--timeout", type=float, help="Timeout for HTTP requests in seconds")
    parser.add_argument("-e", "--extensions", metavar="extensions", type=str, nargs="+", help="Manipulate extensions.")
    parser.add_argument("-m", "--method", metavar="http_method", type=str, default="GET", help="HTTP method to be used (default: GET)")
    args = parser.parse_args()

    wordlist = args.wordlist
    url = args.url
    output = args.output
    filter_c = args.fc
    filter_l = args.fl
    filter_s = args.fs
    headers = parse_headers(args.headers) if args.headers else None
    verify_ssl = not args.no_ssl
    timeout = args.timeout
    extensions = args.extensions
    http_method = args.method

    ssl_error_displayed = False

    # Validate arguments and proceed if valid
    if validate_args(url, output, wordlist):
        send_request(url, wordlist, output, filter_c, filter_l, filter_s, headers, verify_ssl, ssl_error_displayed, timeout, extensions, http_method)
    else:
        print('Invalid arguments')

def parse_headers(headers):
    # Parse headers into a dictionary
    parsed_headers = {}
    if headers:
        for header_group in headers:
            for header in header_group.split(','):
                key, value = header.split(':', 1)
                parsed_headers[key.strip()] = value.strip().replace('FUZZ', '{}')
    return parsed_headers

def validate_args(url, output, wordlist):
    try:
        # Validate command-line arguments
        if (url.startswith('https://') or url.startswith('http://')) and 'FUZZ' in url and os.path.exists(wordlist) and (output is None or output.endswith('.txt')):
            return True
        else:
            return False
    
    except Exception as e:
        # Handle validation exceptions
        print(f'Error validating arguments: {e}')

def send_request(url, wordlist_path, output_path, filter_code, filter_length, filter_size, headers, verify_ssl, ssl_error_displayed, timeout, extensions, http_method):
    # Counter for processed words
    word_counter = 0

    if not verify_ssl and not ssl_error_displayed:
        # Display a warning if SSL certificate verification is disabled
        print("Warning: SSL certificate verification is disabled. InsecureRequestWarning will be suppressed.")
        warnings.simplefilter('ignore', InsecureRequestWarning)
        ssl_error_displayed = True

    with open(wordlist_path, 'r', encoding='utf-8') as wl:
        # Display information about the fuzzing session
        info_statement(http_method, url, extensions, timeout, filter_code)
        for w in wl:
            try:
                # Increment word counter for each word processed
                word_counter += 1

                # Check if 'FUZZ' is in the URL
                if 'FUZZ' in url:
                    # Replace 'FUZZ' with the current word from the wordlist
                    prep_url = url.replace('FUZZ', w.strip())
                    if extensions is not None:
                        # Join the list of extensions into a single string and add it to the URL
                        prep_url += "".join(extensions)
                else:
                    # If 'FUZZ' is not in the URL, append the word from the wordlist
                    prep_url = url + w.strip()

                # Use the specified HTTP method
                response = r.request(http_method, prep_url, headers=headers, verify=verify_ssl, timeout=timeout)

                response_code = response.status_code    
                response_size = len(response.content)
                response_length = len(response.text.split('\n'))

                # Check and print the results based on filters
                if filter_code is None and filter_size is None and filter_length is None:
                    print_result(w, response_code, response_size, response_length, output_path)
                if filter_code is not None and response_code not in filter_code:
                    print_result(w, response_code, response_size, response_length, output_path)
                    continue
                if filter_length is not None and response_length != filter_length:
                    print_result(w, response_code, response_size, response_length, output_path)
                    continue
                if filter_size is not None and response_size != filter_size:
                    print_result(w, response_code, response_size, response_length, output_path)
                
                # Print the word counter for each iteration
                print(f'\rProcessed {word_counter} words from the wordlist', end='', flush=True)

            except r.exceptions.SSLError as e:
                # Handle SSL errors during the request
                print(f'\nSSL error occurred while sending request: {e}')
                ssl_error_displayed = True
                return 0
            except Exception as e:
                # Handle other errors during the request
                print(f'\nError occurred while sending request: {e}')
                return 0
    
    # Print the final word counter
    print(f'\nProcessed {word_counter} words from the wordlist.')

def print_result(word, http_code, weight, length, output_path):
    # Print the result to the console and write it to the output file if specified
    out = f'{word.strip()}      [Status: {http_code} Size: {weight} Lines: {length}]\n'
    
    if output_path is not None:
        with open(output_path, 'a', encoding='utf-8') as o:
            print(out)
            o.write(out)
    else:
        print(out)

def info_statement(method, url, extension, timeout, filter_code):
    # Display information about the fuzzing session
    print(r"""                     ______                             
                    /      \                            
 __     __  ______ |  $$$$$$\__    __ ________ ________ 
|  \   /  \/      \| $$_  \$|  \  |  |        |        \
 \$$\ /  $|  $$$$$$| $$ \   | $$  | $$\$$$$$$$$\$$$$$$$$
  \$$\  $$| $$    $| $$$$   | $$  | $$ /    $$  /    $$ 
   \$$ $$ | $$$$$$$| $$     | $$__/ $$/  $$$$_ /  $$$$_ 
    \$$$   \$$     | $$      \$$    $|  $$    |  $$    \
     \$     \$$$$$$$\$$       \$$$$$$ \$$$$$$$$\$$$$$$$$                                                     
                                                        
  Version: 1.0
  Made by: Wiktor Nowakowski
  Inspired by: FFUF (https://github.com/ffuf/ffuf)                                                      
""")
    print("***************************************************************")
    print("")
    print(f":: Method: {method}")
    print(f":: URL: {url}")
    print(f":: Timeout: {timeout}")
    print(f":: Extension: {extension}")
    print(f":: Blacklist codes: {filter_code}")
    print("")
    print("***************************************************************\n")

if __name__ == "__main__":
    main()
