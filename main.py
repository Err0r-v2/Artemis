# coding=utf-8


from functions import *


# Fonction principale
def main():
    global film_link
    global qualities

    clear()
    timeout = int(input('Veuillez entrer le timeout pratique pour les proxies : '))

    proxies = create_proxies(timeout)
    # Setting some variables
    film_list = []
    # The list that will contain all the qualities' link orf the choosen film
    qualities = []

    # Getting the film's name and entering the parameters in the url
    clear()
    search = input("Veuillez rentrer le nom du film : ")
    payload = {'search': search, 'p': 'films'}
    url = "https://www.zone-telechargement.onl/"

    # Executing url
    r = requests.get(url, params=payload)
    soup = BeautifulSoup(r.text, 'html.parser')

    # If not found then...
    if "Aucune fiches trouvées." in soup.prettify():
        print(Fore.RED + 'Pas de film trouvé' + Style.RESET_ALL)
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

    arg_film = int(input('Veuillez rentrer le nombre du film choisi : '))

    film_name1 = film_list[arg_film - 1]

    if arg_film > len(film_list) or arg_film < 1:
        print('Veuillez choisir un bon argument')
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
    for qualitie in qualities:
        attrs = get_attrs(qualitie)
        print(
            f'{a}. Qualité : {Fore.MAGENTA + attrs[0] + Style.RESET_ALL} \n| Langue : {Fore.LIGHTYELLOW_EX + attrs[1] + Style.RESET_ALL} \n| Taille du fichier : {Fore.GREEN + attrs[2] + Style.RESET_ALL} \n| Url : {Fore.CYAN + attrs[3] + Style.RESET_ALL}')
        a = a + 1

    arg_qualitie = int(input('Veuillez rentrer le nombre de la qualité choisie : '))

    if arg_qualitie > len(qualities) or arg_qualitie < 1:
        print('Veuillez choisir un bon argument')
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
        print('Résolution du captcha...', end=' ')
        fichier_url = bypass(get_attrs(qualities[arg_qualitie - 1])[3])
        print(Fore.GREEN+'Effectué.'+Style.RESET_ALL)

        # Check si le fichier est delete
        if BeautifulSoup(requests.get(fichier_url).text, 'html.parser').find(class_='bloc2'):
            print(Fore.RED + 'Fichier supprimé' + Style.RESET_ALL)
            sys.exit(0)

        print('Obtention du lien de téléchargement...', end=' ')
        # Request POST
        r_form = requests.post(fichier_url, headers=headers_form, data=data_form)
        soup_form = BeautifulSoup(r_form.text, 'html.parser')
        button = soup_form.find(class_="ok btn-general btn-orange")

        name = f"{film_name1} {get_attrs(qualities[arg_qualitie - 1])[0]}"

        try:
            # Trying to give the dl link (if no download in the last 2 hours)
            dl_url = button['href']
            print('Effectué.')
            dl(dl_url, name)

        # Print erreur si délai de dl
        except Exception as e:
            print(Fore.RED + ' \nBypass du lien requis.' + Style.RESET_ALL + '\nMise en route du bypasser...')
            try:
                dl(bypass_1fichier(fichier_url, proxies), name)
            except Exception as e:
                print(e)


if __name__ == "__main__":
    main()