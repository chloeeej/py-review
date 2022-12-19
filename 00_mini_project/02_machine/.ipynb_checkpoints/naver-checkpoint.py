import ast
import urllib.request


client_id = "zNy0lMSY0raZjZipmO_1"
client_secret = "ZlPl2DL9sf"

encText = urllib.parse.quote("미니언즈")
yearfrom = '2015'
yearto = '2015'

url = "https://openapi.naver.com/v1/search/movie.json?query=" + encText + '&yearfrom=' + yearfrom +  '&yearto=' + yearto # JSON 결과
# url = "https://openapi.naver.com/v1/search/blog.xml?query=" + encText # XML 결과
request = urllib.request.Request(url)

request.add_header("X-Naver-Client-Id", client_id)
request.add_header("X-Naver-Client-Secret", client_secret)

response = urllib.request.urlopen(request)

rescode = response.getcode()
if(rescode==200):
    response_body = response.read()
    data = ast.literal_eval(response_body.decode('utf-8'))
    print(data['items'][0]['link'].replace('\\', '').split('=')[1])
    
else:
    print("Error Code:" + rescode)