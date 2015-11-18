"""
Run through the files in archive and parse out the quoted text from previous emails in a thread.
"""
from json import dumps, load
import quotequail
import os
import talon
from talon import quotations
from talon.signature.bruteforce import extract_signature


def naive_quote_removal(email_body):
    """
    Do a really basic job of removing quoted text in emails and return the pure part.
    """
    result = ""
    for line in email_body.split("\n"):
        if not line.startswith(">"):
            result += line + "\n"
    return result


def parse_email_quotes():
    """
    Run through each file in archive and add 'clean_body' and 'signature' to 
    each email's information.
    """
    talon.init()
    archive_dir = "archive/"
    for filenum, filename in enumerate(os.listdir(archive_dir)):
        if filenum % 1000 == 0:
            print filenum
        if filename.endswith(".email.json"):
            full_filename = os.path.join(archive_dir, filename) 
            fh = open(full_filename, "r")
            email_data = load(fh)
            fh.close()
            if not "clean_body" in email_data or not 'signature' in email_data:
                reply_body = naive_quote_removal(email_data['body'])
                email_data['clean_body'], email_data['signature'] = extract_signature(reply_body)
                fh = open(full_filename, "w")
                fh.write(dumps(email_data))
                fh.close()


if __name__ == "__main__":
    parse_email_quotes()
