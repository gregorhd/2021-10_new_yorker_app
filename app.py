

import csv
from connection_pool import get_connection
import database
from models.article import Article
from tqdm import tqdm

DATABASE_PROMPT = "Enter the DATABASE_URI value or leave empty to load from .env file: "
MENU_PROMPT = """-- Menu --

1) Add a single article you've read
2) Add a CSV of article URLs (no header)
3) List all articles you've read
4) Exit

Enter your choice: """


def prompt_create_article():
    url = input("Enter article URL: ").strip()

    article = Article(url)
    article.save()

def prompt_add_CSV():
    csv_path = input("Please provide the absolute path to the CSV containing the URLs (no header): ")
    with open(csv_path, 'r') as f:
        total_iters = sum(1 for row in f)
        f.seek(0) # reset file object to position 0
        reader = csv.reader(f)
        for elem in tqdm(reader, total=total_iters):
            article = Article(elem[0])
            article.save()


def list_all_articles():
    # to avoid creating new Article objects and scraping the website again
    # not using article.title, article.author, article.date
    for article in Article.all():
        print(f"'{article[0]}' by {article[1]} ({article[2]}))")


MENU_OPTIONS = {
    "1": prompt_create_article,
    "2": prompt_add_CSV,
    "3": list_all_articles
}


def menu():

    with get_connection() as connection:
        database.create_tables(connection)

    while (selection := input(MENU_PROMPT)) != "4":
        try:
            MENU_OPTIONS[selection]()
        except KeyError:
            print("Invalid input selected. Please try again.")


menu()
