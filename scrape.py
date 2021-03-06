import json
import os
from argparse import ArgumentParser

import requests
from bs4 import BeautifulSoup


def get_script_arguments():
    args = ArgumentParser()
    args.add_argument('--website', required=True, choices=['vdm', 'fmylife'])
    return args.parse_args()


def fetch_all_articles_for_page(website, page_id=1):
    if website == 'vdm':
        url = 'https://www.viedemerde.fr/?page={}'.format(page_id)
    elif website == 'fmylife':
        url = 'https://www.fmylife.com/?page={}'.format(page_id)
    else:
        raise Exception('Unknown website.')
    print('Fetching {} ... '.format(url), end='')
    resp = requests.get(url)
    assert resp.status_code == 200
    a = BeautifulSoup(resp.content, 'lxml')
    articles = a.find_all('article', {'class': 'col-xs-12 article-panel'})
    json_outputs = []
    for article in articles:
        is_valid_article = article.find('div', {'class': 'vote vote-group vote-up-group'}) is not None
        if not is_valid_article:
            continue
        article_link = article.find('a', {'class': 'article-link'}).attrs['href']
        article_title_div = article.find('h2', {'class': 'classic-title'})
        if article_title_div is not None:
            article_title = str(article_title_div.contents[0])
        else:
            article_title = ''
        article_content = article.find('div', {'class': 'article-contents'}).find('a').contents[-1].strip()
        vote_up = article.find('div', {'class': 'vote vote-group vote-up-group'}).find('div', {
            'class': 'vote-brick vote-count'}).contents[0].strip()
        vote_down = article.find('div', {'class': 'vote vote-group vote-down-group'}).find('div', {
            'class': 'vote-brick vote-count'}).contents[0].strip()
        smiley_scores = []
        for smiley in article.find_all('div', {'class': 'sharre_count count'}):
            smiley_scores.append(smiley.contents[0].strip())
        smiley_names = []
        for smiley in article.find_all('img', {'class': 'icon_smiley_art'}):
            smiley_names.append(smiley.attrs['alt'])
        num_comments = article.find('div', {'class': 'action-item action-link'}).find('a').contents[0].strip()

        top_bar = article.find('div', {'class': 'article-topbar'}).text.strip().split('-')
        div = [a.replace('\n', ' ').strip() for a in top_bar]
        author = div[0]
        if author == 'Par' or author == 'By':
            author = ''
        if author.startswith('Par '):
            author = author.replace('Par ', '')
        if author.startswith('By '):
            author = author.replace('By ', '')
        date = div[1]
        loc = ' '.join(div[2:]).replace('  ', ' ')
        gender = 'male' if article.find('i', {'class': 'fa fa-male'}) is not None else 'female'
        json_article = {
            'article_link': article_link,
            'article_title': article_title,
            'article_content': article_content,
            'vote_up': vote_up,
            'vote_down': vote_down,
            'smileys': dict(zip(smiley_names, smiley_scores)),
            'num_comments': num_comments,
            'author': author,
            'date': date,
            'location': loc,
            'gender': gender,
        }
        # print(json_article)
        json_outputs.append(json_article)
    print('Found {} results.'.format(len(json_outputs)))
    return json_outputs


def main():
    args = get_script_arguments()
    output_dir = args.website
    print('Dumping everything in {}.'.format(output_dir))
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    for page_id in range(1, 100000):
        output_filename = os.path.join(output_dir, 'data_{}.json').format(page_id)
        if os.path.isfile(output_filename):
            print('{} already exists. Skipping.'.format(output_filename))
            continue
        results = fetch_all_articles_for_page(args.website, page_id)
        if len(results) == 0:
            print('Finished.')
            exit(1)
        else:
            with open(output_filename, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)


if __name__ == '__main__':
    main()
