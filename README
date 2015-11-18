An attempt to analyze the Linux Kernel Mailing List (LKML) for sentiment and how nice people are to each other.

# Scraping and Building a Local Archive
Populates 'archive/' with LKML data.

`python scrape.py`

## Archive Structure
Each email is saved into an file. Each file is named lkml."%Y.%m.%d".{daily-email-number}.email.json.

The format of the file is pure json. The json object has the following properties:
* body: What was sent in the email. This is the unparsed original contents.
* sender: The name of the sender (usually this does not contain their email address).
* date: The time and date the email was sent.
* subject: The subject of the sent email.

# Munging the Archive
Mirroring the archive leaves the quoted text and other extraneous information in the body of each email. The `scripts/parse_email_quotes.py` script adds a 'clean_body' and 'signature' field to each email. The clean body is intended to be "pure" new text.

To munge the data, run `python scripts/parse_email_qoutes.py`.

** clean_body: This is the new text added by the sender with a best effort to remove any email signature.
** signature: This is the extracted email signature that the sender included.

# Measuring the email content.
The script sentinment_emails.py runs over the files in archive and adds 

* 'naive-word-sentiment': The score computed by our home grown word ranker.
* 'tp.com-sentiment': The score computed by text-processing.com of the email body.

to each entry.

# Other Stuff

## Dictionaries
1. Download the word dataset from http://www2.imm.dtu.dk/pubdb/views/publication_details.php?id=6010 and place AFIN-111.txt into the "dictionaries" directory in this project.

# Future work
1. Improve scraper
    a. Use the scrapy framework.
    b. Find a better source than LKML.org. Some emails weren't available.
2. Improve the munger
    a. Build a tool to measure how well we munge the data. This will help us move forward faster.
    b. Create a method for extracting source code.
    c. Improve signature extraction
3. Improve Analysis
    a. Create a naive bayes filter.
    b. Improve the speed of the word-sentiment analyzer.
4. Improve presentation
    a. Create a framework for extracting the data we generate.
    b. Use a static site generator to display information about each email.
