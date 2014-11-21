from mrjob.job import MRJob

import ast

# List of (lowercase) keywords to search for in the wishlist names.
keywords = map(lambda x:x.lower(), ["Nike", "Zumba", "fuel band", "iPhone"])

# Map Reduce job to search a list of wishlists for specific keywords and, if a keyword is found, output the
# wishlist owner's email together with the keyword and when the corresponding item was added to the wishlist.
# Run the script from the command line like this:
# python mr_wishlist_keywords.py wishlists.csv

class MRWishlistKeywords(MRJob):

    def mapper(self, _, line):

        # Each line that needs processing will (ideally) be in the following format:
        # <email address>\t<wishlist ID>\t<wishlist json>
        # The fields are separated by tab characters.  After splitting the line on tabs, if the email or wishlist
        # json do not exist, then skip the line.  Also, in some cases, the json will be "null" or "ERROR", in which
        #  case we skip the line as well.

        values = line.split("\t")

        if len(values) == 3 and values[0] and values[2]:
            email = values[0]

            # Protect against invalid data.  If the 3rd entry on the line is not a list, then skip it.  The wishlist
            # data may have "null" or "ERROR", for example.
            try:
                wishlist = ast.literal_eval(values[2]) # from a string representation to actual list.
            except ValueError:
                print "Skipping wishlist for " + email + "\t" + values[2] + " is not a literal."
            else:
                if wishlist:
                    for wishlist_item in wishlist:

                        # Take the wishlist name and split on the words.
                        words = map(lambda x:x.lower(), wishlist_item["name"].split())

                        # Find the common words in the wishlist name and the keywords we're looking for.
                        common_words = list(set(words).intersection(keywords))

                        if common_words:
                            for common_word in common_words:
                                # The key will be the email.  The value will be a tuple comprise of the keyword and the date
                                # the corresponding item was added.
                                yield email, (common_word, wishlist_item["date-added"])

    def reducer(self, key, values):
        # The key will be the email and the value will be the list of keywords and the dates the corresponding items
        # were added.
        yield key, list(values)


if __name__ == '__main__':
    MRWishlistKeywords.run()
