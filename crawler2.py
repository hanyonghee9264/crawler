import os             # 환경 변수나 디렉터리, 파일등의 os자원을 제어
from io import BytesIO
from urllib import parse # ????

import requests # 웹페이지를 불러오는? 모듈
from bs4 import BeautifulSoup # html 및 xml 파일에서 데이터를 가져오는 라이브러리


class Episode:
    def __init__(self, webtoon_id, no, url_thumbnail,      # 초기화 함수 호출
                 title, rating, created_date):
        self.webtoon_id = webtoon_id
        self.no = no
        self.url_thumbnail = url_thumbnail
        self.title = title
        self.rating = rating
        self.created_date = created_date

    @property              # 속성을 나타내며 self로 특별한 인자를 가질 수 없다. (강의내용) 그리고 양?을 줄 일 수있다.
    def url(self):         # url인걸 보니 주소 매서드 생성
        """                # doctype으로 맨 위에 남기며 주석과 비슷한 역할을 한다. (매서드에 대한 설명)
        self.webtoon_id, self.no 요소를 사용하여
        실제 에피소드 페이지 URL을 리턴
        :return:
        """
        url = 'http://comic.naver.com/webtoon/detail.nhn?'
        params = {
            'titleId': self.webtoon_id,
            'no': self.no,
        }
        episode_url = url + parse.urlencode(params)
        return episode_url

    def get_image_url_list(self):  # 매서드로 매서드명을 보니 url_list에서 이미지를 불러들이는 것으로 생각 셀프가 하나인 이유는 클래스 Episode에 매서드로 들어갔기 때문에 특별한 인자가 필요 없으며 self 자신으로 표현
        print('get_image_url_list start')

        file_path = 'data/episode_detail-{webtoon_id}-{episode_no}.html'.format(
            webtoon_id=self.webtoon_id,
            episode_no=self.no,
        )                                               # file_path는 파일의길 처럼 data에 html이란 파일을 저장했다.
        print('file_path:', file_path)

        if os.path.exists(file_path):                   # if문 내용을보면 os모듈이 존재하는지 여부 확인
            print('os.path.exists: True')
            html = open(file_path, 'rt').read()
        else:
            print('os.path.exists: False')              # 없으면 우선 os모듈이 존재안한다고 보며 False라고 프린트
            print(' http get request, url:', self.url)  # 다시 request url을 가져오는 것으로 보임
            response = requests.get(self.url)           # response라는 변수에 다시한번 요청
            html = response.text                        # 그 가져온 데이터 내용을 text형식으로 저장하며 변수 html로 저장
            open(file_path, 'wt').write(html)           # 열어보며 wt는 텍스트를 덮어쓴다는 뜻이며 html에 쓰고 여는 동작


        soup = BeautifulSoup(html, 'lxml')              # BeautifulSoup를 html로 호

        img_list = soup.select('div.wt_viewer > img')   # img_list라는 변수에 div.wt_viewer에서 이미지를 찾는 동작

        return [img.get('src') for img in img_list]

    def download_all_images(self):                      # 모든 이미지를 다운하는 매서드
        for url in self.get_image_url_list():           # 위의 매서드인 이미지리스트에서 url을 반목문인 for이 들어가 순차적으로 나열
            self.download(url)                          # 다운로드

    def download(self, url_img):                        # 다운로드라는 매서드를 생성 그리고 url_img라는 매개변수가 왜 들어갔는지는 모르겠음
        """
        :param url_img: 실제 이미지의 URL
        :return:
        """
        url_referer = f'http://comic.naver.com/webtoon/list.nhn?titleId={self.webtoon_id}'
        headers = {
            'Referer': url_referer,
        }
        response = requests.get(url_img, headers=headers)

        file_name = url_img.rsplit('/', 1)[-1]

        dir_path = f'data/{self.webtoon_id}/{self.no}'
        os.makedirs(dir_path, exist_ok=True)

        file_path = f'{dir_path}/{file_name}'
        open(file_path, 'wb').write(response.content)


class Webtoon:
    def __init__(self, webtoon_id):
        self.webtoon_id = webtoon_id
        self._title = None                   # 모든 get_info를 통해 호출 가능하며 언더바(_)1개를 쓰는게 좋다고 강의영상에도 나와있음
        self._author = None                  # 1개를 주로 쓰며 언더바(__)개는 private 속성으로 다른 개발자나 협업 할 경우 건들 수 없음
        self._description = None             # 즉 확신이 있을때만 2개를 쓰지만 강사님께서 대체적으로 한개만 쓰라고 나와있음
        self._episode_list = list()
        self._html = ''

    def _get_info(self, attr_name):
        if not getattr(self, attr_name):
            self.set_info()
        return getattr(self, attr_name)

    @property                                # 타이틀과 저자, 디스크립션을 속성값으로 주어 원래는 if문으로 길게 나와있던것을
    def title(self):                         # 가독성을 위해 반복되는 것을 줄이기 위해 property라는 속성을 주었다.
        return self._get_info('_title')

    @property
    def author(self):
        return self._get_info('_author')

    @property
    def description(self):
        return self._get_info('_description')

    @property
    def html(self):
        if not self._html:                   # 만약 html이 아니라면 파일 경로 및 url, params 재설정
            file_path = 'data/episode_list-{webtoon_id}.html'.format(webtoon_id=self.webtoon_id)
            url_episode_list = 'http://comic.naver.com/webtoon/list.nhn'
            params = {
                'titleId': self.webtoon_id,
            }
            if os.path.exists(file_path):    # 만약에 파일 경로가 존재한다면
                html = open(file_path, 'rt').read()         # html이란 변수를 보여줄껀데 이것은 읽기만 가능하도록 설정
            else:
                response = requests.get(url_episode_list, params)    # 만약에 없다면 url을 재 요청해야한다.
                print(response.url)
                html = response.text                                 # 요청을해서 html이라는 변수에 response를 텍스트 형식으로 저장
                open(file_path, 'wt').write(html)                    # 그리고 열어주며 파일이 이미있을경우는 덮어쓴다.
            self._html = html
        return self._html

    def set_info(self):                                          # 아까 위에 title과 author, description을 줄여주기 위해 쓴 것
        """
        자신의 html속성을 파싱한 결과를 사용해
        자신의 title, author, description속성값을 할당
        :return: None
        """
        soup = BeautifulSoup(self.html, 'lxml')                  # BeautifulSoup을 통해 html을 호출 그리고 soup라는 변수에 저장

        h2_title = soup.select_one('div.detail > h2')            # div.detail에서 h2가 들어간 내용을 찾아 h2_title 변수에 저장
        title = h2_title.contents[0].strip()                     # ????
        author = h2_title.contents[1].get_text(strip=True)
        description = soup.select_one('div.detail > p').get_text(strip=True)

        self._title = title
        self._author = author
        self._description = description

    def crawl_episode_list(self):
        """
        자기자신의 webtoon_id에 해당하는 HTML문서에서 Episode목록을 생성
        :return:
        """
        soup = BeautifulSoup(self.html, 'lxml')               # BeautifulSoup를 soup 변수에 넣어주고 html형식이지만 self가 왜 붙어있는지는 모르겠음

        table = soup.select_one('table.viewList')             # 테이블이란 변수에 table.viewList의 내용중에 한가지만 포함한
        tr_list = table.select('tr')
        episode_list = list()
        for index, tr in enumerate(tr_list[1:]):
            if tr.get('class'):
                continue
            url_thumbnail = tr.select_one('td:nth-of-type(1) img').get('src') # nth-of-tpye은 css로 순서를 가리킨다. 즉 괄호안에 1번째에 img태그를 선택하며 이것은 src의 주소를 호출한다.
            from urllib import parse
            url_detail = tr.select_one('td:nth-of-type(1) > a').get('href')
            query_string = parse.urlsplit(url_detail).query
            query_dict = parse.parse_qs(query_string)
            no = query_dict['no'][0]

            title = tr.select_one('td:nth-of-type(2) > a').get_text(strip=True)     # nth-of-tpye은 css로 순서를 가리킨다. 즉 괄호안에 2번째중에 a태그를 선택한다는 것이다.
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
