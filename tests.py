import re
import unittest
from urllib.parse import urlparse, urlunparse
import random

import requests
from bs4 import BeautifulSoup, Comment

from server import EXCLUDE_TAGS

PORT = 8080


class IvelumHttpProxyServerTests(unittest.TestCase):

    @staticmethod
    def compare_bare_strings(link):

        """
        Returns `AssertionError` if there is difference in text between
        the same pages on habrahabr.ru and on localhost.
        """

        def prepare_strings_to_compare(url):
            # get html from url
            req = requests.get(url)
            soup = BeautifulSoup(req.content.decode('utf-8'), 'html5lib')
            # clear html from unnecessary elements
            # we don't need comments
            for child in soup.body.children:
                if isinstance(child, Comment):
                    child.extract()
            # promo html may differ from time to time
            promo_class = 'column-wrapper column-wrapper_bottom column-wrapper_bordered'
            for element in soup.find_all("section", {'class': promo_class}):
                element.extract()
            # megapost teasers may differ
            for element in soup.find_all("ul", {'class': 'megapost-teasers'}):
                element.extract()
            # similar posts and vacancies may differ
            for element in soup.find_all("div", {'class': 'default-block_content'}):
                element.extract()
            # exclude tags like script, style, code from html
            for unwanted_tag in soup(EXCLUDE_TAGS):
                unwanted_tag.extract()
            # return strings that are not empty
            return [s.strip() for s in soup.stripped_strings if s.strip() != '']

        # get the link for habr with the same path
        url_list = list(urlparse(link))
        url_list[0] = 'https'
        url_list[1] = 'habrahabr.ru'
        habr_link = urlunparse(url_list)

        # get cleared string lists
        strings_local = prepare_strings_to_compare(link)
        strings_habr = prepare_strings_to_compare(habr_link)

        # number of strings should match
        assert len(strings_habr) == len(strings_local)

        for x in range(len(strings_habr)):
            # compare strings
            if strings_habr[x] != strings_local[x]:
                # if strings are not equal, then compare word by word
                pattern = r'[^\w™]+'
                words_habr = [word.strip() for word in re.split(pattern, strings_habr[x])]
                words_local = [word.strip() for word in re.split(pattern, strings_local[x])]

                # number of words should match
                assert len(words_habr) == len(words_local)

                for word_index in range(len(words_local)):
                    if words_local[word_index] != words_habr[word_index]:
                        # if words don't match then it should be a '™' sign
                        difference = words_local[word_index].replace(words_habr[word_index], "")
                        assert difference == '™'

    @staticmethod
    def no_six_letter_words(soup_obj):

        """
        Returns `AssertionError` if there is any 6-letter word that is not followed by a '™' sign.
        """

        re_pattern = r'\b([^\W\d_]{6})\b[^™]'  # for some reason you need to put '™' sign after \b char
        regex_matching_lines = soup_obj.find_all(text=re.compile(re_pattern))
        found_lines = [line for line in regex_matching_lines
                       if line.parent.name not in EXCLUDE_TAGS and not isinstance(line, Comment)]
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
        Then checks if string content matches on both habr website and localhost server.
        Then the function repeats the same steps for five random links from the page, which lead to localhost.
        """

        initial_link = f"http://127.0.0.1:{PORT}"
        initial_request = requests.get(initial_link)
        soup = BeautifulSoup(initial_request.content.decode('utf-8'), 'html5lib')
        link_hrefs = [link.get('href') for link in soup.find_all('a', href=True)]
        xlink_hrefs = [xlink.get('xlink:href') for xlink in soup.find_all('use')]
        form_actions = [form.get('action') for form in soup.find_all('form')]
        self.no_habr_links(link_hrefs + xlink_hrefs + form_actions)
        self.no_six_letter_words(soup)
        self.compare_bare_strings(initial_link)

        for i in range(5):
            localhost_links = [link for link in link_hrefs if urlparse(link).netloc == f'127.0.0.1:{PORT}']
            random_link = random.choice(localhost_links)
            print(f"random_link is {random_link}")
            test_request = requests.get(random_link)
            test_soup = BeautifulSoup(test_request.content.decode('utf-8'), 'html5lib')
            test_links = [link.get('href') for link in test_soup.find_all('a', href=True)]
            test_xlinks = [xlink.get('xlink:href') for xlink in test_soup.find_all('use')]
            self.no_habr_links(test_links + test_xlinks)
            self.no_six_letter_words(test_soup)
            self.compare_bare_strings(random_link)


if __name__ == '__main__':
    from sys import argv

    if len(argv) == 2:
        PORT = int(argv[1])

    unittest.main()
