import wget
import urllib.error
import glob
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import random
import time
import requests
from bs4 import BeautifulSoup
import sys
import os, platform
import threading
import math
from colorama import Fore, Style


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
    nbDecimals = len(str(number).split('.')[1])
    if nbDecimals <= digits:
        return number
    stepper = 10.0 ** digits
    return math.trunc(stepper * number) / stepper


# Utilise Selenium pour résoudre le captcha de dl-protect.info (possible que ça ne fonctionne pas), bypass primaire
# si la sécurité est pas ouf
def bypass(url):
    os.environ['WDM_LOG_LEVEL'] = '0'
    user_agent = f'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (HTML, like Gecko) Chrome/{random.randint(50, 99)}.0.3112.50 Safari/537.36'

    options = Options()
    options.add_argument(f'user-agent={user_agent}')
    options.add_argument("disable-notifications")
    options.add_experimental_option("useAutomationExtension", False)  # Adding Argument to Not Use Automation Extension
    options.headless = True

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    driver.get(url)

    time.sleep(random.randint(1, 2))
    try:
        captcha_button = driver.find_element(by=By.CLASS_NAME, value='g-recaptcha')
        driver.execute_script("arguments[0].click();", captcha_button)
    except Exception as e:
        print("Link not working", e)
        sys.exit(0)

    time.sleep(1)

    try:
        return driver.find_element(by=By.PARTIAL_LINK_TEXT, value='https://1fichier.com').text

    except Exception as e:
        return input("Enter the url manually : ")


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
    print(green('Effectué.'))
    print('Testing proxies with ipify.org and 1fichier.com...', end=' ')

    def test_proxy(proxy, url, timeout, valid_proxies_list: list):
        proxies = {
            'https': f'socks5h://{proxy}'
        }

        try:
            requests.get('https://api.ipify.org', proxies=proxies, timeout=timeout)
            try:
                r = requests.get(url, proxies=proxies, timeout=timeout)

                if r.status_code == 200:
                    valid_proxies_list.append(proxy)
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

    print(f'Effectué en {truncate(time.time() - start, 3)} secondes. Nous avons {len(valid_proxies)} proxies prometteurs.')
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
