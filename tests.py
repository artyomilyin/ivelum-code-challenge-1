import re
import unittest
from urllib.parse import urlparse
import random

import requests
from bs4 import BeautifulSoup


PORT = 8080


class IvelumHttpProxyServerTests(unittest.TestCase):

    @staticmethod
    def no_six_letter_words(soup_obj):

        """
        Returns `AssertionError` if there is any 6-letter word that is not followed by a '™' sign.
        """

        re_pattern = r'\b([^\W\d_]{6})\b[^™]'  # for some reason you need to put '™' sign after \b char
        regex_matching_lines = soup_obj.find_all(text=re.compile(re_pattern))
        found_lines = [line for line in regex_matching_lines if line.parent.name != 'script']
        assert not found_lines

    @staticmethod
    def no_habr_links(href_list):

        """
        Returns `AssertionError` if there is a 'habr' substring in any of links from `href_list`.
        """

        for link in href_list:
            assert "habr" not in urlparse(link).netloc

    def test_words_and_links(self):

        """
        Gets a response from `127.0.0.1:{port}`, then checks if there is any
        link to habr website in href parameter of <a> tag.
        Then checks if there is any 6-letter word that is not followed by a '™' sign.
        Then the function repeats the same steps for five random links from the page, which lead to localhost.
        """

        initial_request = requests.get(f"http://127.0.0.1:{PORT}")
        soup = BeautifulSoup(initial_request.content, 'html.parser')
        link_hrefs = [link.get('href') for link in soup.find_all('a', href=True)]
        self.no_habr_links(link_hrefs)
        self.no_six_letter_words(soup)

        for i in range(5):
            localhost_links = [link for link in link_hrefs if urlparse(link).netloc == f'127.0.0.1:{PORT}']
            random_link = random.choice(localhost_links)
            print(f"random_link is {random_link}")
            test_request = requests.get(random_link)
            test_soup = BeautifulSoup(test_request.content, 'html.parser')
            test_links = [link.get('href') for link in test_soup.find_all('a', href=True)]
            self.no_habr_links(test_links)
            self.no_six_letter_words(test_soup)


if __name__ == '__main__':
    from sys import argv

    if len(argv) == 2:
        PORT = int(argv[1])

    unittest.main()