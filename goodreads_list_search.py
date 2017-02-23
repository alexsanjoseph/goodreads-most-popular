import os, urllib
import pandas as pd
from pathos.multiprocessing import ProcessingPool as Pool
import requests
from bs4 import BeautifulSoup
import re
from argparse import ArgumentParser
from itertools import compress

def convert_to_int(x):
    return int(x.replace(",", ""))

def request_and_find_type(search_string, tag):
    soup = request_link(search_string)
    return soup.findAll(tag)

def request_link(search_string):
    r = requests.get(search_string)
    return BeautifulSoup(r.content, "html.parser")

def search_for_text(all_items, regexp):
    book_links = [re.search(regexp, str(x)) for x in all_items]
    return list([x.groups(1)[0] for x in book_links if x])

def get_last_page_num(list_link):
    regexp = "page=(.*?)\""
    all_links = request_and_find_type(list_link, "a")
    all_pages = search_for_text(all_links, regexp)
    return max([int(x) for x in all_pages])

def get_description(all_items):
    description = None
    description_list = search_for_text(all_items, "freeText.*?>(.*)<")
    if len(description_list) > 0: description = max(description_list[:3], key = len)
    return description

def get_book_props(current_book_link):

    all_items = request_link(current_book_link)

    all_links = all_items.findAll("a")
    all_divs = all_items.findAll("div")
    all_spans = all_items.findAll("span")

    book_name = search_for_text(all_items.findAll("h1"), "bookTitle.*>[\n\s]*(.*?)[\s\n]<")[0]
    author = search_for_text(all_spans, "authorName.*itemprop=\"name\">(.*?)<")[0]
    rating = float(search_for_text(all_spans, "ratingValue.*?>([\d\\.]*)<")[0])
    votes = convert_to_int(search_for_text(all_spans, "ratingCount.*?>([\d,]*).*<")[0])
    description = get_description(all_spans)
    book_type = search_for_text(all_spans, "bookFormatType.*\">(.*?)<")[0]
    no_of_pages = convert_to_int(search_for_text(all_spans, "numberOfPages.*\">([\d\\.,]*).*<")[0])

    published_on = ""
    isbn = ""
    genre_1 = ""
    genre_2 = ""
    pages = ""
    return pd.DataFrame([(rating,votes,description)])

def get_book_props(current_book_link):
    all_items = request_link(current_book_link)
    output = get_props(all_items)

    # with open(book_ratings_file_name, 'a', encoding = 'utf-8') as f:
    #     output.to_csv(f, header = False, index=False)
    return output




if __name__ == "__main__":
    goodreads_link = "https://www.goodreads.com/list/show/"
    list_name = "1.Best_Books_Ever"
    list_link = goodreads_link + list_name
    total_pages = get_last_page_num(list_link); p = 2

    book_db_file = "goodreads_list_props.csv"
    #os.remove(book_ratings_file_name)
    if not os.path.exists(book_db_file):
        with open(book_db_file, 'w') as f: f.write("book_name,rating,votes,description\n")


    for p in range(total_pages):
        page = "?page=" + str(p)
        current_link = list_link + page
        all_links = request_and_find_type(current_link, "a")
        all_books = list(set(search_for_text(all_links, "\"(/book/show/.*?)\"")))
        all_book_links = ["https://www.goodreads.com/" + x for x in all_books]

        get_book_props(current_book_link)