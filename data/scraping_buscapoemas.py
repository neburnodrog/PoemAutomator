import bs4
import requests
import os

"""Variable to hold the parsed lines"""
verses = []

""""""
url = "https://www.buscapoemas.net/poetas.html"

"""strings to exclude"""
roman_numerals = [
    "I",
    "II",
    "III",
    "IV",
    "V",
    "VI",
    "VII",
    "VIII",
    "IX",
    "X",
    "XI",
    "XII",
    "XIII",
    "XIV",
    "XV",
    "XVI",
    "XVII",
    "XVIII",
    "XIX",
    "XX",
    "XXI",
    "XXII",
    "XXIII",
    "XXIV",
    "XXV",
]

"""Path to poems"""
path = "/home/nebur/Desktop/poemautomator/data/buscapoemas"

"""List of poets to exclude"""
exclude_poets = [
    "https://www.buscapoemas.net/poeta/Alfonso-X-el-Sabio.htm",
    "https://www.buscapoemas.net/poeta/Francisco-de-Rojas-Zorrilla.htm",
    "https://www.buscapoemas.net/poeta/Fray-Luis-de-León.htm",
    "https://www.buscapoemas.net/poeta/Diego-de-Torres-y-Villarroel.htm",
    "https://www.buscapoemas.net/poeta/Cristóbal-de-Castillejo.htm",
    "https://www.buscapoemas.net/poeta/Bartolomé-de-Argensola.htm",
    "https://www.buscapoemas.net/poeta/Baltasar-del-Alcázar.htm",
    "https://www.buscapoemas.net/poeta/Gonzalo-de-Berceo.htm",
    "https://www.buscapoemas.net/poeta/Gutierre-de-Cetina.htm",
    "https://www.buscapoemas.net/poeta/Jorge-Manrique.htm",
    "https://www.buscapoemas.net/poeta/Juan-Boscán.htm",
    "https://www.buscapoemas.net/poeta/Juan-Ruiz-Arcipreste-de-Hita.htm",
    "https://www.buscapoemas.net/poeta/Juan-de-Tassis-y-Peralta.htm",
    "https://www.buscapoemas.net/poeta/Marqués-de-Santillana.htm",
    "https://www.buscapoemas.net/poeta/San-Juan-de-la-Cruz.htm",
    "https://www.buscapoemas.net/poeta/Tirso-de-Molina.htm",
    "https://www.buscapoemas.net/poeta/José-Antonio-Ramos-Sucre.htm",
]


def getting_the_verses(poem_url, poet_path):
    """filtering the lines and the tags"""

    poem_name = poem_url[34:]
    poem_name = poem_name[:poem_name.find("/")]

    try:
        with open(f"{path}/{poet_path}/{poem_name}.txt") as f:
            print("\t[+] Retrieving {} from txt-file".format(poem_url))
            verses_poem = f.read().split("\n")

    except FileNotFoundError:
        print("\t[+] Scraping {}".format(poem_url))

        resp = requests.get(poem_url)
        soup = bs4.BeautifulSoup(resp.text, "lxml")

        poem = soup.select("#poema_contenedor_poema")[0]

        verses_poem = []
        for elem in poem:
            if isinstance(elem, bs4.element.NavigableString):
                if str(elem) not in roman_numerals and str(elem).upper() != str(elem):
                    verso = str(elem).replace("\xa0", " ").strip()
                    verses_poem.append(verso)

        with open(f"{path}/{poet_path}/{poem_name}.txt", "w") as f:
            print("\n".join(verses_poem), file=f)

    return verses_poem


def getting_poets(buscapoemas_url=url):
    """parsing the POET-URLS"""

    if not os.path.exists(path):
        os.mkdir(path)

    print("[+] Getting the poet-urls from buscapoemas.net")

    resp = requests.get(buscapoemas_url)
    soup = bs4.BeautifulSoup(resp.text, "lxml")
    anchors = soup.select("li a")
    hrefs = [anchor["href"] for anchor in anchors]
    links = [href for href in hrefs if "/poeta/" in href]
    poet_urls = set(links)

    return sorted(list(poet_urls))


def getting_poems(poet_url, poet_path):
    """parsing the POEM-URLS"""

    try:
        os.mkdir(f"{path}/{poet_path}")
    except FileExistsError:
        pass

    resp = requests.get(poet_url)
    soup = bs4.BeautifulSoup(resp.text, "lxml")
    poem_anchors = soup.select(".slot_poema_autor")
    poem_urls = [tag.a["href"] for tag in poem_anchors]

    return poem_urls


def main():
    urls_poets = getting_poets(url)

    verses = []

    counter = 0
    for poet_url in urls_poets:
        if poet_url in exclude_poets:
            continue

        poet_path = poet_url[34:-4]
        counter += 1
        urls_poems = getting_poems(poet_url, poet_path)

        print(f"\n[+] [{counter}/{len(urls_poets) - len(exclude_poets)}] "
              f"Extracting the verses from {poet_url}\n")

        for poem_url in urls_poems:
            verses.extend(getting_the_verses(poem_url, poet_path))


if __name__ == "__main__":
    main()
