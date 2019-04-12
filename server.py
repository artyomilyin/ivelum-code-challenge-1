from http.server import SimpleHTTPRequestHandler, HTTPServer
import re
from urllib.parse import urlparse, urlunparse

import requests
from bs4 import BeautifulSoup


class IvelumRequestHandler(SimpleHTTPRequestHandler):

    def do_GET(self):

        def replace_habr_link(parsed_link):
            url_list = list(parsed_link)
            url_list[0] = 'http'
            url_list[1] = f'127.0.0.1:{PORT}'
            return urlunparse(url_list)

        base_url = "https://habrahabr.ru/"
        url_to_open = f"{base_url}{self.path}"
        habr_response = requests.get(url_to_open)

        # precessing only text/html responses
        if 'text/html' in habr_response.headers['Content-Type']:
            soup = BeautifulSoup(habr_response.content, 'html5lib')

            # replace hostname and port for every link containing 'habr'
            for link in soup.find_all('a', href=True):
                link_href = link.get('href')
                parsed_link = urlparse(link_href)
                if 'habr' in parsed_link.netloc:
                    link['href'] = replace_habr_link(parsed_link)
            # repeat the same for <use xlink:href="..."> links (svg)
            for xlink in soup.find_all('use'):
                xlink_href = xlink.get('xlink:href')
                parsed_link = urlparse(xlink_href)
                if 'habr' in parsed_link.netloc:
                    xlink['xlink:href'] = replace_habr_link(parsed_link)
            # the search form should point to localhost as well
            for form in soup.find_all('form', action=True):
                form_action = form.get('action')
                parsed_link = urlparse(form_action)
                if 'habr' in parsed_link.netloc:
                    form['action'] = replace_habr_link(parsed_link)

            re_pattern = r'\b([^\W\d_]{6})\b'  # returns only 6-letter words, without digits and underscores

            # find every element which 'text' parameter matching the re_pattern and not being a script
            # then add ™ char to every 6-letter word
            exclude_tags = ['script', 'code', 'style']
            found_lines = [line for line in soup.find_all(text=re.compile(re_pattern))
                           if line.parent.name not in exclude_tags]
            for line in found_lines:
                new_line = re.sub(re_pattern, r'\1™', line)
                line.replaceWith(new_line)

            # replace response's content with modified one
            habr_response._content = soup.encode('utf-8')

        # add 'Content-Type' header with ResponseCode and return it
        self.send_response(200)
        self.send_header('Content-type', habr_response.headers.get('Content-Type'))
        self.end_headers()
        self.wfile.write(habr_response.content)


def run(port, server_class=HTTPServer, handler_class=IvelumRequestHandler):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting httpd on port {port}...')
    httpd.serve_forever()


if __name__ == "__main__":
    from sys import argv

    PORT = 8080
    # use port = 8080 if no arguments specified
    if len(argv) == 2:
        PORT = int(argv[1])
    run(port=PORT)
