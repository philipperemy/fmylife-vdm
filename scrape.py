import json
import os

import requests
from bs4 import BeautifulSoup


def fetch_all_articles_for_page(page_id=1):
    # url = 'https://www.fmylife.com/?page={}'.format(page_id)
    url = 'https://www.viedemerde.fr/?page={}'.format(page_id)
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
        author = article.find('div', {'class': 'article-topbar'}).contents[0].strip().split('\n')[-1]
        date_and_loc = article.find('div', {'class': 'article-topbar'}).contents[-1].strip().replace('\n', '')[1:]
        date = date_and_loc.split('-')[0].strip()
        loc = ' '.join(date_and_loc.split('-')[1:]).strip().replace('   ', ' ').replace('  ', ' ')
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
    output_dir = 'output'
    print('Dumping everything in {}'.format(output_dir))
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    for page_id in range(1, 100000):
        output_filename = os.path.join(output_dir, 'data_{}.json').format(page_id)
        if os.path.isfile(output_filename):
            print('{} already exists. Skipping.'.format(output_filename))
            continue
        results = fetch_all_articles_for_page(page_id=page_id)
        if len(results) == 0:
            print('Finished.')
            exit(1)
        else:
            with open(output_filename, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)


if __name__ == '__main__':
    main()
