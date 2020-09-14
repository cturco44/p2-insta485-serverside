"""
Check live deployed web app.

EECS 485 Project 2

Andrew DeOrio <awdeorio@umich.edu>
"""
import re
from urllib.parse import urlparse
import bs4


def test_deploy():
    """Verify curl log from AWS deployed site."""
    # Verify log
    with open("deployed_insta485.log") as infile:
        log = infile.read()
    assert "localhost" not in log
    assert "amazonaws.com" in log
    assert "200 OK" in log
    assert "nginx" in log
    assert "Connection refused" not in log
    assert "GET /accounts/login/" in log

    # Parse HTML, which should be the login page
    with open("deployed_insta485.html") as infile:
        html = infile.read()
    soup = bs4.BeautifulSoup(html, "html.parser")
    text = soup.get_text()
    text = re.sub(r"\s+", " ", text)
    links = [x.get("href") for x in soup.find_all("a")]
    links = [urlparse(x).path for x in links]  # just the path part of URL
    form_inputs = [submit.get("name") for button in soup.find_all('form')
                   for submit in button.find_all("input") if submit]

    # Verify content of login page
    assert "/accounts/create/" in links
    assert "username" in form_inputs
    assert "password" in form_inputs
