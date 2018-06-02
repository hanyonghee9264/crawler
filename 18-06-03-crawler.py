import os
# 입력 받은 경로에 대해 True/False로 나타낼 수 있는 모듈
from urllib import parse
# Url 파싱을 위한 python 표준 모듈
import requests
# 웹에서 정보를 가져오기 위해 쓰이는 모듈
from bs4 import BeautifulSoup
# 웹에서 가져온 정보 중 데이터를 뽑아내기 위해 쓰이는 모듈

class Episode:
    # 클래스 에피소드
    def __init__(self, webtoon_id, no, url_thumbnail, title, rating, created_date):
        self.webtoon_id = webtoon_id
        self.no = no
        self.url_thumbnail = url_thumbnail
        self.title = title
        self.rating = rating
        self.created_date = created_date
    # 초기화 함수로 웹툰에 대한 id값, no, 썸네일, 제목, 별점, 수정날짜를 보여준다.
    @property
    # 속성
    def url(self):
        """
        self.webtoon_id, self.no 요소를 사용하여
        실제 에피소드 페이지 URL을 리턴
        :return:
        """
        url = 'http://comic.naver.com/webtoon/list.nhn?'
        # url이라는 변수에 웹툰에 대한 url을 할당
        params = {
            'titleId': self.webtoon_id,
            'no': self.no,
        }
        # 매개변수로 타이틀의 id값과 no를 할당하며 self가 붙어 있는걸 보니
        # property 속성을 주어 Episode 클래스에 인스턴스를 속성형태로 호출 함
        episode_url = url + parse.urlencode(params)
        # url 내용과 매개변수로 할당한 내용(파싱)을 합치는것 (string)
        return episode_url
        # 웹툰의 id값과 no를 episode_url에 리턴한다.
    def get_image_url_list(self):
        # url 리스트 중 이미지를 얻기 위한 매서드
        print('get_image_url_list start')
        # 호출이 잘 되는지 확인하는 과정이다.
        file_path = 'data/episode_detail-{webtoon_id}-{episode_no}.html'.format(
            webtoon_id=self.webtoon_id,
            episode_no=self.no,
        )
        # 파일경로로 data/episode.... html의 형태로 저장, 제목에는 id값과 no가 들어간다.
        # 위와 같이 하는 것은 내가 있었던 위치를 서버에 알려줌과 동시에 referer하는 과정
        print('file_path:', file_path)
        # 프린트로 잘 되는지 확인
        if os.path.exists(file_path):
            # 그치만 만약 html형태로 저장되었다면
            print('os.path.exists:True')
            # 존재한다고 확인하는 과정
            html = open(file_path, 'rt').read()
            # 이러한 내용을 읽으며 html 변수에 할당
        else:
            # 만약에 존재하지 않는다면..
            print('os.path.exists: Flase')
            # 존재하지 않는다고 일단 확인 한 뒤
            print('http get request, url:', self.url)
            # 다시 서버에 요청, 프린트물로 확인
            response = requests.get(self.url)
            # response라는 변수에 다시한번 url에 요청하며 할당
            html = response.text
            # 그 내용은 텍스트 형식으로 html이라는 변수에 할당
            open(file_path, 'wt').write(html)
            # 그리고 html을 다시 덮어써야 함

        soup = BeautifulSoup(html, 'lxml')
        # 데이터(html변수에 할당한 내용)를 뽑아내기 위한 과정
        img_list = soup.select('div.wt_viewer > img')
        # div에 클래스는 wt_viewer에 자손인 img를 img_list라는 변수에 할당
        return [img.get('src') for img in img_list]
        # img에서 src라는 내용만 추출하여 이러한 내용들을
        # img_list안에 img들을 나열하여 뽑아낸다.

    def download_all_images(self):
        # 이미지 다운로드를 하기 위한 매서드
        for url in self.get_image_url_list():
            # url이란 객체에 위에서 만든 이미지리스트 매서드를 for문을 통해 나열
            self.download(url)
            # 이러한 url을 다운
    def download(self, url_img):
        """
        :param url_img: 실제 이미지의 URL
        :return:
        """
        # 서버에서 거부하지 않도록 HTTP헤더 중 'Referer'항목을 채워서 요청
        url_referer = f'http://comic.naver.com/webtoon/detail.nhn?titleId={self.webtoon_id}'
        # url referer하는 과정. 위에서 설명 한번 나왔음
        headers = {
            'Referer': url_referer,
        }
        # headers에 Referer한 정보들을.. (이 부분 설명이 부족함)
        response = requests.get(url_img, headers=headers)
        # 이렇게 얻은 정보들을 response라는 변수에 할당
        # (이러한 과정을 통해 네이버 웹툰이 막는 것을 피할 수 있음)
        file_name = url_img.rsplit('/', 1)[-1]
        # 이미지 다운로드를 하기 위해 split을 썼는데 우리가 원하는 이미지는
        # 뒤에 위치하기 때문에 rsplit을 썼으며 /을 기준으로 1번째만 나눈다.
        # 뒤에 [-1]은 맨뒤에 첫번째를 가르킨다.
        dir_path = f'data/{self.webtoon_id}/{self.no}'
        os.makedirs(dir_path, exist_ok=True)
        # 위 두 과정은 디렉토리를 만들어야 이미지들을 저장시키는데
        # 강의 내용만으로는 이해가 부족함
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
    # 초기화 함수를 통해 초기화 시켜주며 언더바(_) 1개로 private은 아니지만 왠만하면 건들지 말라는 의미
    # title ~ episode_list 들은 아래의 property 속성을 통해 None을 넣었음
    # html은 url을 넣기위해 '' 라고 문자열이 들어갈 것이라는 의미

    def _get_info(self, attr_name):
        if not getattr(self, attr_name):
            self.set_info()
        return getattr(self, attr_name)
    # 위에 title ~ episode_list 들을 호출 시킬 매서드
    # getattr은 내장함수로 param으로 전달 된 객체의 이름에 해당하는 속성 값을 리턴시켜 줌

    @property
    def title(self):
        return self._get_info('_title')
    # 위에서 설명함

    @property
    def author(self):
        return self._get_info('_author')
    # 위에서 설명함

    @property
    def description(self):
        return self._get_info('_description')
    # 위에서 설명함

    @property
    def html(self):
        # html 매서드
        if not self._html:
            # 만약 _html이 없다면
            file_path = 'data/episode_list-{webtoon_id}.html'.format(
                webtoon_id=self.webtoon_id
            )
            # 파일 경로를 설정해주고 id값을 넣어줘서 저장
            url_episode_list = 'http://comic.naver.com/webtoon/list.nhn'
            # 위와 같음
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
        # 데이터를 뽑아내기위해 사용 (html)
        h2_title = soup.select_one('div.detail > h2')
        # html에 데이터에서 detail이라는 클래스를 가진 div에서
        # 상속받는 h2의 내용을 h2_title이라는 변수에 할당
        title = h2_title.contents[0].strip()
        # 위의 변수에서 할당한 내용에 contets중 첫번째의 내용을 공백제거하여 title이라는 변수에 할당
        author = h2_title.contents[1].get_text(strip=True)
        # 위의 변수에서 두번째의 내용을 텍스트 형식으로 공백제거하여 author라는 변수에 할당
        description = soup.select_one('div.detail > p').get_text(strip=True)
        # select_one을 통해 한가지만 찾아낼껀데 detail이라는 클래스를 가진 div를 텍스트 형식으로
        # 공백제거 하여 description 이란 변수에 할당
        self._title = title
        self._author = author
        self._description = description
        # 위에서 뽑은 데이터 들을 self를 통하여 클래스 인스턴스로 만듬

    def crawl_episode_list(self):
        # 웹툰의 에피소드 목록들 (1화~10화 이런형태)
        soup = BeautifulSoup(self.html, 'lxml')
        # BeautifulSoup를 통해 html의 데이터를 뽑아낼것임
        table = soup.select_one('table.viewList')
        # 그 중 viewList라는 클래스를 가진 테이블을 찾아 table이라는 변수에 할당
        tr_list = table.select('tr')
        # table의 tr들을 뽑아내 tr_list라는 변수에 할당
        episode_list = list()
        # 이러한 것들을 리스트 형식으로 할 것임
        for index, tr in enumerate(tr_list[1:]):
            # index와 tr이라는 변수에 enumerate를 통해 나눌 것이며
            # tr_list중 첫번째부터 끝까지 돌릴 것임
            if tr.get('class'):
                # 만약 tr에서 class를 얻는다면
                continue
                # 계속 해라라
            url_thumbnail = tr.select_one('td:nth-of-type(1) img').get('src')
            # tr 안에 td에서 그 중 src의 내용 중 첫번째 이미지를 url_thumbnail에 할당
            url_detail = tr.select_one('td:nth-of-type(1) > a').get('href')
            # 위와 같은 내용과 비슷함
            query_string = parse.urlsplit(url_detail).query
            query_dict = parse.parse_qs(query_string)
            # 이거에 대한 내용들은 좀 더 공부가 필요함
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
            # 이러한 것들을 new_episde에 할당
            episode_list.append(new_episode)
            # 기존 episode_list를 new_episode에 추가
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