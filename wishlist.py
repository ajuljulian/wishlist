import mechanize
import cookielib
import re

def main():

    br = mechanize.Browser()
    cj = cookielib.LWPCookieJar()
    br.set_cookiejar(cj)

    br.set_handle_equiv(True)
    br.set_handle_gzip(True)
    br.set_handle_redirect(True)
    br.set_handle_referer(True)
    br.set_handle_robots(False)

    br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)

    r= br.open('http://www.amazon.com/gp/registry/search.html?ie=UTF8&type=wishlist')

    # Select the second (index one) form
    form = br.select_form(nr=1)

    br.form['field-name'] = 'ajuljulian@yahoo.com'
    response1 = br.submit()

    response1_data = response1.get_data()

    match = re.search(r'action="/gp/registry/wishlist/([a-zA-Z0-9]+)', response1_data)

    if match:
        print 'found', match.group(1)
    else:
        print 'did not find'

main()