# veFuzz Documentation

## Description

`veFuzz` is a Python script designed for web content discovery by fuzzing a target URL with a wordlist. It supports various customization options such as custom headers, HTTP methods, response code filtering, and more.

## Usage

```bash
python vefuzz.py -w path_to_wordlist -u target_url -o output_file [options]
```

## Options

-w, --wordlist: Path to the keyword list file.
-u, --url: URL of the target website with 'FUZZ' as a placeholder.
-o, --output: Output file to save results.
-fc, --filter_code: HTTP response codes to ignore.
-fl, --filter_length: Filter by HTTP response length.
-fs, --filter_size: Filter by HTTP response size.
-H, --headers: Custom headers for the HTTP request with 'FUZZ' as a placeholder.
--no-ssl: Disable SSL certificate verification.
-t, --timeout: Timeout for HTTP requests in seconds.
-e, --extensions: Manipulate extensions.
-m, --method: HTTP method to be used (default: GET).

## Example

```bash
python vefuzz.py -w common.txt -u https://example.com/FUZZ -o output.txt -fc 404 -t 10
```
This example fuzzes the URL https://example.com/FUZZ with the words from the common.txt wordlist, saving the results to output.txt, and ignoring HTTP response code 404 with a timeout of 10 seconds.

## Additional Notes

- The script supports both HTTP and HTTPS URLs.
- The word 'FUZZ' in the URL is replaced with each word from the wordlist.
- Custom headers can be specified using the -H option.
- SSL certificate verification can be disabled with --no-ssl.

## Credits

Version: 1.0
Author: Wiktor Nowakowski
Inspired by FFUF (https://github.com/ffuf/ffuf)

## Disclaimer

This script is designed for ethical and legal use only. Ensure you have proper authorization before using it on any target. The author and contributors are not responsible for any misuse or damage caused by this script.
