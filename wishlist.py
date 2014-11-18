
# This script reads a list of email addresses from a file, then for each email address it
# 1) loads an Amazon web page
# 2) submits the email address through a form
# 3) searches the resulting page for wish list IDs
# 4) calls a url with the wish list ID and retrieves the corresponding wish list
# 5) appends the email address, wish list ID, and wish list to a file
#
# The script assumes that you have deployed the php files from https://github.com/doitlikejustin/amazon-wish-lister
# onto a server to be used to retrieve the wish list using a wish list ID.

import mechanize
import cookielib
import re

# URL of an Amazon page containing a form that can be used to retrieve wish lists based on email addresses.
AMAZON_WISHLIST_EMAIL_URL = 'http://www.amazon.com/gp/registry/search.html?ie=UTF8&type=wishlist'

# URL used to retrieve Amazon wish lists from wish list IDs (see https://github.com/doitlikejustin/amazon-wish-lister)
AMAZON_WISHLIST_ID_URL = 'http://localhost:8888/wishlist.php/?id='

def main():

    # Configure mechanize.  It's used for web page scraping and site crawling.
    br = mechanize.Browser()
    cj = cookielib.LWPCookieJar()
    br.set_cookiejar(cj)

    br.set_handle_equiv(True)
    br.set_handle_gzip(True)
    br.set_handle_redirect(True)
    br.set_handle_referer(True)
    br.set_handle_robots(False)

    # Read list of emails.  Assume one email per line.
    infile = open("bb_only_emails.txt", 'r')
    emails = infile.readlines()

    LINE_BUFFERED = 1

    f = open('wishlist.txt', 'w+', LINE_BUFFERED)

    i = 0

    for email in emails:

        i += 1

        # Remove the newline character from the end of the email.
        email = email.replace('\n', '')

        # Get the wish list ID from the email address if it exists.
        # If the wish list ID exists, then retrieve the corresponding wish list as well.
        wishlist_id = retrieve_wishlist_id(email, br)

        if wishlist_id == "":
            wishlist = ""
        else:
            wishlist = retrieve_wishlist(wishlist_id, br)

        wishlist_entry = email + " (" + wishlist_id + "): " + wishlist

        print(str(i) + ": " + wishlist_entry)

        f.write(wishlist_entry)
        f.write('\n')

    f.close()

def retrieve_wishlist_id(email, br):
    br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)

    r= br.open(AMAZON_WISHLIST_EMAIL_URL)

    # Select the second (index one) form
    form = br.select_form(nr=1)

    br.form['field-name'] = email
    response1 = br.submit()

    response1_data = response1.get_data()

    match = re.search(r'action="/gp/registry/wishlist/([a-zA-Z0-9]+)', response1_data)

    if match:
        # Use a back reference to get the wish list.
        wishlistID = match.group(1)
        print 'found', wishlistID
        return wishlistID
    else:
        print 'did not find'
        return ""


def retrieve_wishlist(wishlist_id, br):

    br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)

    r= br.open(AMAZON_WISHLIST_ID_URL + wishlist_id)

    html = r.read()

    return html

main()