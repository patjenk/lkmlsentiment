from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from json import dumps
import os
import requests
import urlparse


def make_link_absolute(unabsolute_url, base_url):
    """
    Taken from http://stackoverflow.com/questions/4468410/python-beautifulsoup-equivalent-to-lxml-make-links-absolute
    """
    return urlparse.urljoin(base_url, unabsolute_url)


def scrape():
    """
    roll through lmkl.org and start saving the archive locally.
    """
    archive_dir = "archive/"

    start_datetime = datetime(year=2010, month=1, day=1, hour=0, minute=0, second=0)
    base_url = "http://lkml.org/lkml/{year}/{month}/{day}"

    try:
        os.stat(archive_dir)
    except:
        os.mkdir(archive_dir)

    for day_count in range(0,10):
        current_datetime = start_datetime + timedelta(days=day_count)
        print "Archiving {}".format(current_datetime.strftime("%Y-%m-%d"))
        lkml_archive_day_url = base_url.format(year=current_datetime.year, month=current_datetime.month, day=current_datetime.day)
        lkml_day_message_set = set()
        day_http_request = requests.get(lkml_archive_day_url)
        soup = BeautifulSoup(day_http_request.text, "html.parser")
        for a_tag in soup.find_all("a"):
            tag_href = a_tag.get("href")
            if "{year}/{month}/{day}/".format(year=current_datetime.year, month=current_datetime.month, day=current_datetime.day) in str(tag_href) and tag_href not in lkml_day_message_set:
                lkml_day_message_set.add(tag_href)
                message_archive_url = make_link_absolute(tag_href, lkml_archive_day_url)
                message_http_request = requests.get(message_archive_url)
                message_soup = BeautifulSoup(message_http_request.text, "html.parser")
                try:
                    message_subject = message_soup.findAll("td", text="Subject")[0].findNext("td").text
                    message_date = message_soup.findAll("td", text="Date")[0].findNext("td").text
                    message_sender = message_soup.findAll("td", text="From")[0].findNext("td").text
                    message_body_element = message_soup.findAll("pre", attrs = {'itemprop': 'articleBody'})[0]
                    message_body = ""
                    for element in message_body_element.children:
                        line_content = str(element)
                        if "<br/>" == line_content:
                            message_body += "\n"
                        else:
                            message_body += line_content
                except:
                    continue
                data = {
                    'subject': message_subject,
                    'data': message_date,
                    'sender': message_sender,
                    'body': message_body
                        }
                filename = tag_href[1:].replace("/",".") + ".email.json"
                fh = open(archive_dir + filename, "w")
                fh.write(dumps(data))
                fh.close()


if __name__ == "__main__":
    scrape()
