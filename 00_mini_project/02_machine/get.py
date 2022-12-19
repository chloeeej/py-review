from bs4 import BeautifulSoup, NavigableString
import requests
import re


def data(code):
    url = 'https://movie.naver.com/movie/bi/mi/basic.naver?code=' + code

    response = requests.get(url)
    html = response.content
    soup = BeautifulSoup(html, 'html.parser')

    div = soup.find('div', 'mv_info')

    # 영화제목
    title = div.find('a').get_text()

    # 평점
    em = div.find_all('em')
    temp_list = []

    for e in em:
        temp = e.get_text()
        if (re.match(r'(?<!\S)\d(?!\S)', temp)) or (temp == '.'):
            temp_list.append(temp)

    final_rating = []

    if len(temp_list) == 9:
        del temp_list[0]
        final_rating.append(0)

    count = 0

    while count < len(temp_list):
        final_rating.append(str(temp_list[count]) + str(temp_list[count+1]) +
                     str(temp_list[count+2]) + str(temp_list[count+3]))
        count += 4

    ratings = list(map(float, final_rating))

    # 개요, 감독, 등급
    info = []

    info_spec = div.find('p', 'info_spec')
    info_spec2 = div.find('div', 'info_spec2')

    specs = info_spec.find_all('a')
    specs2 = info_spec2.find_all('a')
    span = info_spec.find_all('span')
    
    runtime = ''
    for i in span:
        if '분' in i.get_text():
            runtime = i.get_text().replace('분', '').replace(' ', '')

    temp1 = []

    for i in specs:
        if not isinstance(i, NavigableString):
            temp1.append(i.get_text().replace('\n', '').replace('\t', ''))

    genres = ['애니메이션', '모험', '코미디', '드라마', '공포', '범죄', '스릴러', '가족', '액션', 'SF', '사극', '역사', '전쟁', '뮤지컬', '멜로', '로맨스']

    genre = ''
    year = ''
    age = ''
    director = ''
    
    age_list = ['전체 관람가', '12세 관람가', '15세 관람가', '청소년 관람불가', '제한상영가', '등급보류 ']

    for i in temp1:
        if i in genres:
            genre += i + '/'
        elif re.match(r'[0-9]', i) or re.match(r'[.]', i):
            year += i
        else:
            if i in age_list:
                age = i

    genre = genre.strip('/')
    director = specs2[0].get_text()
    regex = re.compile(r'([12]\d{3}.(0[1-9]|1[0-2]).(0[1-9]|[12]\d|3[01]))')

    splitted_year = regex.search(year).group(1)
    splitted_age = re.sub(r'([12]\d{3}.(0[1-9]|1[0-2]).(0[1-9]|[12]\d|3[01]))', '', year)

    info.append(genre)
    info.append(splitted_year)

    if splitted_age != '':
        info.append(splitted_age)
    else:
        info.append(age)

    info.append(director)
    info.append(runtime)

    dict1 = {'title': title, 'ratings': ratings, 'info': info}
    return dict1


def ratings(code):
    url = 'https://movie.naver.com/movie/bi/mi/point.naver?code=' + code
    response = requests.get(url)

    html = response.content
    soup = BeautifulSoup(html, 'html.parser')
    rating = soup.find_all('div', 'grp_sty4')

    if len(rating) == 1:
        return None

    point = rating[1].find('ul', 'grp_point')

    stack = []

    for p in point:
        if not isinstance(p, NavigableString):
            temp = p.get_text().replace('\n', '')
            temp = re.sub(r'[ㄱ-ㅎ|ㅏ-ㅣ|가-힣a-zA-z]', '', temp)

            stack.append(temp)

    names = ['연출', '연기', '스토리', '영상미', 'OST']

    result = {}

    for i, j in zip(names, stack):
        result.update({i: j})

    # TODO: 이 함수를 불러올 함수에셔 dict2를 임의로 만들어서 Key 값으로 영화제목을 넣어줄 것.
    return result


def actor(code):
    url = 'https://movie.naver.com/movie/bi/mi/detail.naver?code=' + code
    response = requests.get(url)
    html = response.content
    soup = BeautifulSoup(html, 'html.parser')

    div = soup.find('div', 'made_people')
    p_info = div.find_all('div', 'p_info')

    result = []

    for i in p_info:
        if '주연' in str(i):
            result.append(i.find('a').get_text())
    if result:
        return result
    else:
        return None


def main():
    codes = ['191634', '69105', '52420', '101062', '90834', '89294']
    datas = []

    for i in codes:
        temp_data = data(i)

        temp_ratings = ratings(i)
        temp_ratings = {'평점': temp_ratings}

        temp_actor = actor(i)
        temp_actor = {'주연': temp_actor}

        temp_data.update(temp_ratings)
        temp_data.update(temp_actor)
        datas.append(temp_data)

    print(datas)



if __name__ == '__main__':
    main()