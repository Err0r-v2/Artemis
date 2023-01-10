# coding=utf-8

from functions import *
from rich.console import Console
from rich.table import Table
from rich import box


# Fonction principale
def main(timeout=2):
    clear()
    print("""
        ░█████╗░██████╗░████████╗███████╗███╗░░░███╗██╗░██████╗
        ██╔══██╗██╔══██╗╚══██╔══╝██╔════╝████╗░████║██║██╔════╝
        ███████║██████╔╝░░░██║░░░█████╗░░██╔████╔██║██║╚█████╗░
        ██╔══██║██╔══██╗░░░██║░░░██╔══╝░░██║╚██╔╝██║██║░╚═══██╗
        ██║░░██║██║░░██║░░░██║░░░███████╗██║░╚═╝░██║██║██████╔╝
        ╚═╝░░╚═╝╚═╝░░╚═╝░░░╚═╝░░░╚══════╝╚═╝░░░░░╚═╝╚═╝╚═════╝░
        """)

    animate(red("Made by "), 0.05)

    time.sleep(0.15)
    sys.stdout.write(':')
    sys.stdout.flush()

    animate(cyan(" Err0r#0002"), 0.05)

    print('\nReading cache', end='')

    animate("...", 0.3)
    with open('.cache.txt', 'r') as cache_file:
        cache = cache_file.read().splitlines()
        cache_file.close()

    try:

        if time.time() - float(cache[0]) <= 300:
            print(green(' Found!'))
            proxies = cache[1:]
            time.sleep(1)
        else:
            print(red(' Expired!'))
            proxies = create_proxies(timeout, '.cache.txt')
            time.sleep(1)

    except (IndexError, ValueError):
        print(red(' Not Found!'))
        proxies = create_proxies(timeout, '.cache.txt')

    # Setting some variables
    film_list = []
    # The list that will contain all the qualities' link orf the choosen film
    qualities = []

    clear()
    # Getting the film's name and entering the parameters in the url
    search = input("Please enter the movie name : ")
    payload = {'search': search, 'p': 'films'}
    url = "https://www.zone-telechargement.onl/"

    # Executing url
    r = requests.get(url, params=payload)
    soup = BeautifulSoup(r.text, 'html.parser')

    # If not found then...
    if "Aucune fiches trouvées." in soup.prettify():
        print(red('No movie found'))
        sys.exit()

    # Else print the film's list
    else:
        for u_soup in soup.find_all(class_="cover_infos_title"):
            film_name = u_soup.find('a').get_text()
            if film_name not in film_list:
                film_list.append(u_soup.find('a').get_text())

    a = 1
    for film in film_list:
        print(f'{a}. {film}')
        a += 1

    arg_film = int(input('Please enter the number of the movie : '))

    film_name1 = film_list[arg_film - 1]

    film_link = str
    if arg_film > len(film_list) or arg_film < 1:
        print(red('Please choose a valid argument'))
        sys.exit()
    else:
        # Going to the film webpage
        for u_soup in soup.find_all(class_="cover_infos_title"):
            film_name = u_soup.find('a').get_text()
            if film_name == film_list[arg_film - 1]:
                film_link = f"{url}{u_soup.find('a').get('href')}"
                break

    r_film = requests.get(film_link)
    s_film = BeautifulSoup(r_film.text, 'html.parser')

    qualities.append(film_link)

    # Getting all the qualities and printing them
    if s_film.find(class_='otherversions'):
        for link in s_film.find(class_='otherversions').find_all('a'):
            qualities.append(f"{url}{link.get('href')}")

    clear()
    a = 1

    table = Table(box=box.SQUARE)

    table.add_column("Number", justify="center", style="cyan", no_wrap=True)
    table.add_column("Quality", style="magenta", justify="left")
    table.add_column("Language", justify="left", style="green")
    table.add_column("File size", justify="center", style="green")

    for qualitie in qualities:
        attrs = get_attrs(qualitie)
        table.add_row(str(a), attrs[0], attrs[1], attrs[2])
        a += 1

    console = Console()
    console.print(table)

    arg_qualitie = int(input('Enter the selected qualitie : '))

    if arg_qualitie > len(qualities) or arg_qualitie < 1:
        print(red('Please choose a valid argument'))
        sys.exit()

    else:
        clear()
        # Données du formulaire pour la request POST
        headers_form = {
            'cookie': 'AF=22123'
        }
        data_form = {
            'dl_no_ssl': 'off',
            'dlinline': 'off'
        }

        # Tries to bypass the url (BETA)
        print('Captcha resolving...', end=' ')
        fichier_url = bypass(get_attrs(qualities[arg_qualitie - 1])[3])
        print(green('Done.'))

        # Check si le fichier est delete
        if BeautifulSoup(requests.get(fichier_url).text, 'html.parser').find(class_='bloc2'):
            print(red('File deleted'))
            sys.exit(0)

        print('Getting the download link...', end=' ')
        # Request POST
        r_form = requests.post(fichier_url, headers=headers_form, data=data_form)
        soup_form = BeautifulSoup(r_form.text, 'html.parser')
        button = soup_form.find(class_="ok btn-general btn-orange")

        name = f"{film_name1} {get_attrs(qualities[arg_qualitie - 1])[0]}"

        try:
            # Trying to give the dl link (if no download in the last 2 hours)
            dl_url = button['href']
            print(green('Done.'))
            dl(dl_url, name)

        # Print erreur si délai de dl
        except KeyError:
            print(red(' Bypass necessary.'))
            print('Starting bypasser...', end=' ')
            try:
                dl(bypass_1fichier(fichier_url, proxies), name)
            except Exception as e:
                print(e)


if __name__ == "__main__":
    main()
