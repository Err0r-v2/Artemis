import glob
import math
import os
import platform
import sys
import threading
import time
import urllib.error
import requests
import wget

from bs4 import BeautifulSoup
from colorama import Fore, Style
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException


def animate(words, sleep):
    for char in words:
        time.sleep(sleep)
        sys.stdout.write(char)
        sys.stdout.flush()

    time.sleep(sleep)


def red(string: str):
    return Fore.RED + string + Style.RESET_ALL


def green(string: str):
    return Fore.GREEN + string + Style.RESET_ALL


def cyan(string: str):
    return Fore.CYAN + string + Style.RESET_ALL


def magenta(string: str):
    return Fore.MAGENTA + string + Style.RESET_ALL


def blue(string: str):
    return Fore.BLUE + string + Style.RESET_ALL


def clear():
    if platform.system() == 'Windows':
        os.system('cls')
    else:
        os.system('clear')


def truncate(number, digits) -> float:
    # Improve accuracy with floating point operations, to avoid truncate(16.4, 2) = 16.39 or truncate(-1.13, 2) = -1.12
    nbdecimals = len(str(number).split('.')[1])
    if nbdecimals <= digits:
        return number
    stepper = 10.0 ** digits
    return math.trunc(stepper * number) / stepper


# Utilise Selenium pour résoudre le captcha de dl-protect.info (possible que ça ne fonctionne pas), bypass primaire
# si la sécurité est pas ouf
def bypass(url):
    a = uc.Chrome()

    a.get(url)
    time.sleep(2)
    try:
        for i in range(2):
            a.find_elements(By.XPATH, "//a[@rel='external nofollow']")[0].click()
            time.sleep(2)

    except NoSuchElementException:
        print('Unable to locate')
        time.sleep(0.5)
    except IndexError:
        print('IndexError')

    for window in a.window_handles:
        a.switch_to.window(window)
        if a.current_url.startswith('https://dl-protect.net/'):
            break

    time.sleep(2)
    a.execute_script("arguments[0].click();", a.find_element(By.TAG_NAME, 'button'))
    return a.find_element(By.XPATH, "//a[@rel='external nofollow']").text


def create_proxies(timeout, cache_path: str):
    print('Getting new proxies...', end=' ')
    start = time.time()
    params = {'request': 'displayproxies',
              'protocol': 'socks5',
              'timeout': 2000,
              'country': 'all',
              'ssl': 'yes',
              'anonymity': 'elite,anonymous'}

    r = requests.get('https://api.proxyscrape.com/v2', params=params)

    proxy_list = r.text.splitlines()
    valid_proxies = []
    print(green('Done.'))
    print('Testing proxies with ipify.org and 1fichier.com...', end=' ')

    def test_proxy(prox, url, timeout, valid_proxies_list: list):
        proxies = {
            'https': f'socks5h://{prox}'
        }

        try:
            requests.get('https://api.ipify.org', proxies=proxies, timeout=timeout)
            try:
                r = requests.get(url, proxies=proxies, timeout=timeout)

                if r.status_code == 200:
                    valid_proxies_list.append(prox)
            except:
                pass

        except:
            pass

    threads = []
    for proxy in proxy_list:
        thread = threading.Thread(target=test_proxy, args=(proxy, 'https://1fichier.com/', timeout, valid_proxies,))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    print(
        f'Done in {truncate(time.time() - start, 3)} seconds. {len(valid_proxies)} proxies found.')

    with open(cache_path, 'w') as cache:
        cache.write(f'{time.time()}\n')
        for proxy in valid_proxies:
            cache.write(f'{str(proxy)}\n')

    time.sleep(3)
    return valid_proxies


# This function returns the attributes of a film by its zone telechargement url
# return attr = [quality, language, size, 1fichier link]
def get_attrs(film_url):
    attrs = []
    r_film = requests.get(film_url)
    s_film = BeautifulSoup(r_film.text, 'html.parser')

    for u_soup in s_film.find_all('strong'):
        if u_soup.get_text() == 'Qualité :':
            attrs.append(u_soup.next_sibling)
        elif u_soup.get_text() == 'Langue :':
            attrs.append(u_soup.next_sibling)
        elif u_soup.get_text() == 'Taille du fichier :':
            attrs.append(u_soup.next_sibling)

    attrs.append(s_film.find(attrs={'rel': 'external nofollow'}).get('href'))

    return attrs


def bar_progress(current, total, width=80):
    progress_message = "Downloading : %d%% [%s / %s]" % (
        current / total * 100, convert_size(current), convert_size(total))
    # Don't use print() as it will print in new line every time.
    sys.stdout.write("\r" + progress_message)
    sys.stdout.flush()


# Convertis des bytes en une valeur + adaptée
def convert_size(size_bytes):
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return "%s %s" % (s, size_name[i])


def dl(url, name):
    try:
        wget.download(url, bar=bar_progress, out='Films/')
        list_of_files = glob.glob('Films/*')
        latest_file = max(list_of_files, key=os.path.getctime)
        os.rename(latest_file, f'Films/{name}.{latest_file[-3:]}')

    except urllib.error.HTTPError as e:
        print(f"Lien expiré veuillez réessayer plus tard\n Erreur : {e}\nLien :{url}")

    except ConnectionAbortedError:
        print("Téléchargement avorté... Veuillez relancer le téléchargement")

    except KeyboardInterrupt:
        print('\nStopping download...')
        print('Goodbye!')


def bypass_1fichier(url, proxies):
    headers_form = {
        'cookie': 'AF=22123'
    }
    data_form = {
        'dl_no_ssl': 'yes',
        'dlinline': 'off'
    }
    for proxy in proxies:
        p = {
            'https': f'socks5h://{proxy}',
            'http': f'socks5h://{proxy}'
        }
        try:
            r_form = requests.post(url, proxies=p, headers=headers_form, data=data_form)
            soup_form = BeautifulSoup(r_form.text, 'html.parser')
            print(Fore.GREEN + 'Bypass done !' + Style.RESET_ALL)
            return soup_form.find(class_="ok btn-general btn-orange")['href']

        except Exception as e:
            pass

    print(red("The bypass did not worked..."))
