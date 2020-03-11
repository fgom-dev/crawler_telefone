import re
import threading

import requests
from bs4 import BeautifulSoup

DOMINIO = 'https://django-anuncios.solyd.com.br'
URL_AUTOMOVEIS = 'https://django-anuncios.solyd.com.br/automoveis/'

LINKS = []
TELEFONES = []


def requisicao(url):
    try:
        resposta = requests.get(url)
        return resposta.text
    except Exception as error:
        print(error)


def parsing(resposta_html):
    try:
        soup = BeautifulSoup(resposta_html, 'html.parser')
        return soup
    except Exception as error:
        print('Erro ao fazer parsing HTML', error)


def encontrar_links(soup):
    links = []
    try:
        cards_pai = soup.find('div', class_='ui three doubling link cards')
        cards = cards_pai.find_all('a')
        for card in cards:
            link = card['href']
            links.append(link)
        return links
    except Exception as error:
        print(error)


def encontrar_telefone(soup):
    try:
        descricao = soup.find_all('div', class_="sixteen wide column")[2].p.get_text().strip()
        regex = re.findall(r"\(?0?([1-9]{2})[ \-\.\)]{0,2}(9?[ \-\.]?\d{4})[ \-\.]?(\d{4})", descricao)
        return regex
    except Exception as error:
        print(error)
        return None


def descobrir_telefones():
    while True:
        try:
            link_anuncio = LINKS.pop(0)
            resposta_anuncio = requisicao(DOMINIO + link_anuncio)
            soup_anuncio = parsing(resposta_anuncio)
            telefones = encontrar_telefone(soup_anuncio)
            for telefone in telefones:
                TELEFONES.append(telefone)
                salvar_telefone(telefone)
        except:
            break


def salvar_telefone(telefone):
    str_telefone = f'({telefone[0]}) {telefone[1]}-{telefone[2]}\n'
    try:
        with open('telefones.csv', 'a') as arquivo:
            arquivo.write(str_telefone)
    except Exception as error:
        print(error)


if __name__ == '__main__':
    try:
        resposta_busca = requisicao(URL_AUTOMOVEIS)
        soup_busca = parsing(resposta_busca)
        LINKS = encontrar_links(soup_busca)
        THREADS = []
        for i in range(12):
            t = threading.Thread(target=descobrir_telefones)
            THREADS.append(t)
        for t in THREADS:
            t.start()
        for t in THREADS:
            t.join()
        print(f'Encontramos {len(TELEFONES)} telefones!')
    except Exception as error:
        print(error)
