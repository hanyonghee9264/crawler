import os
from urllib import parse

import requests
from bs4 import BeautifulSoup


class Episode:
    def __init__(self, webtoon_id, no, url_thumbnail, title, rating, created_date):
        self.webtoon_id = webtoon_id
        self.no = no
        self.url_thumbnail = url_thumbnail
        self.title = title
        self.rating = rating
        self.created_date = created_date

    @property
    def url(self):
        """
        self.webtoon_id, self.no 요소를 사용하여
        실제 에피소드 페이지 URL을 리턴
        :return:
        """
        url = 'http://comic.naver.com/webtoon/list.nhn?'
        params = {
            'titleId': self.webtoon_id,
            'no': self.no,
        }
        episode_url = url + parse.urlencode(params)
        return episode_url

    def get_image_url_list(self):
        print('get_image_url_list start')
        file_path = 'data/episode_detail-{webtoon_id}-{episode_no}.html'.format(
            webtoon_id=self.webtoon_id,
            episode_no=self.no,
        )
        print('file_path:', file_path)
        if os.path.exists(file_path):
            print('os.path.exists:True')
            html = open(file_path, 'rt').read()
        else:
            print('os.path.exists: Flase')
            print('http get request, url:', self.url)
            response = requests.get(self.url)
            html = response.text
            open(file_path, 'wt').write(html)

        soup = BeautifulSoup(html, 'lxml')
        img_list = soup.select('div.wt_viewer > img')
        return [img.get('src') for img in img_list]

    def download_all_images(self):
        for url in self.get_image_url_list():
            self.download(url)

    def download(self, url_img):
        """
        :param url_img: 실제 이미지의 URL
        :return:
        """
        # 서버에서 거부하지 않도록 HTTP헤더 중 'Referer'항목을 채워서 요청
        url_referer = f'http://comic.naver.com/webtoon/detail.nhn?titleId={self.webtoon_id}'
        headers = {
            'Referer': url_referer,
        }
        response = requests.get(url_img, headers=headers)

        # 이미지 URL에서 이미지명을 가져옴
        file_name = url_img.rsplit('/', 1)[-1]

        dir_path = f'data/{self.webtoon_id}/{self.no}'
        os.makedirs(dir_path, exist_ok=True)

        file_path = f'{dir_path}/{file_name}'
        open(file_path, 'wb').write(response.content)


class Webtoon:
    def __init__(self, webtoon_id):
        self.webtoon_id = webtoon_id
        self._title = None
        self._author = None
        self._description = None
        self._episode_list = None
        self._html = ''

    def _get_info(self, attr_name):
        if not getattr(self, attr_name):
            self.set_info()
        return getattr(self, attr_name)

    @property
    def title(self):
        return self._get_info('_title')

    @property
    def author(self):
        return self._get_info('_author')

    @property
    def description(self):
        return self._get_info('_description')

    @property
    def html(self):
        if not self._html:
            file_path = 'data/episode_list-{webtoon_id}.html'.format(
                webtoon_id=self.webtoon_id
            )
            url_episode_list = 'http://comic.naver.com/webtoon/list.nhn'
            params = {
                'titleId': self.webtoon_id,
            }
            if os.path.exists(file_path):
                html = open(file_path, 'rt').read()
            else:
                response = requests.get(url_episode_list, params)
                print(response.url)
                html = response.text
                open(file_path, 'wt').write(html)
            self._html = html
        return self._html

    def set_info(self):
        """
        자신의 html속성을 파싱한 결과를 사용해
        자신의 title, author, description 속성값을 할당
        :return: None
        """
        soup = BeautifulSoup(self.html, 'lxml')
        h2_title = soup.select_one('div.detail > h2')
        title = h2_title.contents[0].strip()
        author = h2_title.contents[1].get_text(strip=True)
        description = soup.select_one('div.detail > p').get_text(strip=True)
        self._title = title
        self._author = author
        self._description = description

    def crawl_episode_list(self):
        soup = BeautifulSoup(self.html, 'lxml')
        table = soup.select_one('table.viewList')
        tr_list = table.select('tr')
        episode_list = list()
        for index, tr in enumerate(tr_list[1:]):
            if tr.get('class'):
                continue
            url_thumbnail = tr.select_one('td:nth-of-type(1) img').get('src')
            url_detail = tr.select_one('td:nth-of-type(1) > a').get('href')
            query_string = parse.urlsplit(url_detail).query
            query_dict = parse.parse_qs(query_string)
            no = query_dict['no'][0]
            title = tr.select_one('td:nth-of-type(2) > a').get_text(strip=True)
            rating = tr.select_one('td:nth-of-type(3) strong').get_text(strip=True)
            created_date = tr.select_one('td:nth-of-type(4)').get_text(strip=True)
            new_episode = Episode(
                webtoon_id=self.webtoon_id,
                no=no,
                url_thumbnail=url_thumbnail,
                title=title,
                rating=rating,
                created_date=created_date,
            )
            episode_list.append(new_episode)
        self._episode_list = episode_list

    @property
    def episode_list(self):
        if not self._episode_list:
            self.crawl_episode_list()
        return self._episode_list


if __name__ == '__main__':
    webtoon1 = Webtoon(651673)
    print(webtoon1.title)
    print(webtoon1.author)
    print(webtoon1.description)
    e1 = webtoon1.episode_list[0]
    e1.download_all_images()
