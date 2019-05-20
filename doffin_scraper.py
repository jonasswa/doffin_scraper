'''
Super naive script returning RSS feed (xml) of doffin-projects
'''

from typing import Tuple, List
from bs4 import BeautifulSoup as bs
from urllib.request import Request, urlopen
from urllib.parse import urlencode


def _get_html(address: str, query: dict = {})\
        -> str:
     
    if address[-1] != '?':
        address+= '?'


    req = Request(address + urlencode(query), headers={'User-Agent': 'Mozilla/66.0.1'})
    page = urlopen(req).read()
    
    return page


def _formatpubdate(date: str)\
        -> str:
    # convert a yyyymmddhhmmss (UTC) string to RSS pubDate format
    from calendar import weekday, month_abbr, day_abbr
    year, month, day = date[:4], date[4:6], date[6:8]
    hour, minute, second = date[8:10], date[10:12], date[12:14]
    if not hour:
        hour = "12"
    if not minute:
        minute = "00"
    if not second:
        second = "00"
    wday = weekday(int(year), int(month), int(day))
    return "%s, %s %s %s 00:00:00 GMT" % (
        day_abbr[wday], day, month_abbr[int(month)], year)


def get_rss_doffin(search_string: str)\
        -> str:
    
    url = 'https://doffin.no/Notice?'
    search_string = search_string.replace(' ', '+')
    print(search_string)
    query = {
        'Query': search_string,
        'OrderingType': 1,
        'OrderingDirection': 1,
        'IncludeExpired': False,
        'NoticeType': 2
    
    }

    html_content = _get_html(url, query)

    elements_div = 'notice-search-item'                      
    title_div = 'notice-search-item-header'
    
    soup = bs(html_content, 'html.parser')
    elements = soup.findAll('div', class_=elements_div)
    titles = []
    urls = []
    descriptions = []
    dates = []
    
    for element in elements:
        title = element.find('div', class_=title_div)
        title = title.find('a', class_='', href=True)
        url = title['href'] 
        title = title.text
        url = 'https://www.doffin.no' + url
        date = element.find('div', class_='right-col')
        date = date.text[-11:]
        date = date.replace('-','')
        date = _formatpubdate(date)
        dates.append(date)
        desc_page = _get_html(url)
        desc_soup = bs(desc_page, 'html.parser')
        print(title)
        desc = desc_soup.find("h3", text="Kort beskrivelse")
        if desc!=None:
            desc = desc.parent.parent.parent
            desc = desc.find_all('div', class_='eps-sub-section-body')[3]
            description = desc.text
        else:
            description = title
        titles.append(title)
        urls.append(url)
        descriptions.append(description)
    
    rss = '<?xml version="1.0", encoding "UTF-8" ?>\n<rss version="2.0">\n\n'
    rss += '<channel>\n'
    
    for i in range(len(titles)):
        rss+='\n<item>\n'
        rss+='<title>{}</title>\n'.format(titles[i])
        rss+='<link>{}</link>\n'.format([urls[i]])
        rss+='<description>{}</description>\n'.format(descriptions[i])
        rss+='<pubDate>{}</pubDate>\n'.format(dates[i])
        rss+='</item>\n'

    rss+='\n</channel>\n</rss>'


if __name__ == '__main__':
    get_rss_doffin('test')

