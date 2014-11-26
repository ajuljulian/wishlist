from mrjob.job import MRJob

import ast

# Map Reduce job to search a list of wishlists for specific terms and, if a term is found, output the
# wishlist owner's email together with the wishlist item name and date it was added.
# Run the script from the command line like this ("terms.txt" is the file containing a newline-delimited set of terms):
# python mr_wishlist_keywords.py wishlists.csv --file terms.txt

class MRWishlistKeywords(MRJob):

    def mapper_init(self):

        # Read in a list of terms to search against in the wishlist names.  Convert to lowercase.
        global terms
        terms = map(lambda x:x.lower(), [line.strip() for line in open('terms.txt')])

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
                # Bad data - skip the line
                pass
            else:
                if wishlist:
                    for wishlist_item in wishlist:

                        # Take the wishlist name and split on the words.
                        words = map(lambda x:x.lower(), wishlist_item["name"].split())

                        # Find the common strings in the wishlist name and the terms we're looking for.
                        common_terms = [x for x in terms if x in wishlist_item["name"].lower()]

                        if common_terms:
                            for common_word in common_terms:
                                # The key will be the email.  The value will be a tuple comprise of the keyword and the date
                                # the corresponding item was added.
                                yield email, (wishlist_item["name"], wishlist_item["date-added"])

    def reducer(self, key, values):
        # The key will be the email and the value will be the list of wishlist names and the dates the corresponding items
        # were added.
        yield key, list(values)


if __name__ == '__main__':
    MRWishlistKeywords.run()
