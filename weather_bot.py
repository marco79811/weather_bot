### 套件載入

datetime、爬蟲等依照系統>內建>第三方順序載入
"""

# 系統模組
import os

# 內建模組
from datetime import datetime, time, date   #新增date
from os import listdir
import json
from dataclasses import dataclass

# 第三方模組
import pytz
import requests
from bs4 import BeautifulSoup
import pandas as pd

#爬蟲的共同變數:header設定隱藏爬蟲
header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'}

"""### 爬蟲

爬取空氣品質預報資料
"""

# 爬取空氣品質預報資料
air_url = 'https://data.moenv.gov.tw/api/v2/aqf_p_01?api_key=e8dd42e6-9b8b-43f8-991e-b3dee723a52d&limit=1000&sort=publishtime%20desc&format=JSON'
air_r = requests.get(air_url, headers=header)
air_r.encoding = 'UTF-8' # 指定編碼方式，utf-8、UTF-8、UTF8、utf8 都一樣
air_soup = BeautifulSoup(air_r.text, 'html.parser')

# json解析
# 只要看起來是字典格式，就表示這是 json 格式，所以用 json 模組轉換成字典：
air_data = json.loads(air_r.text)
#air_data
#air_data['records'][1]

#先取得當日預報日期縮減資料範圍
current_date = str(date.today())   #轉為字串

#預報日期為當日的所有空氣品質資料air_today
#抓取資料欄位:'forecastdate','area','aqi','majorpollutant','publishtime'(預報日期,空品區,AQI,主要汙染物,預報發布時間)
air_today = []
for a in air_data['records']:
    if a['forecastdate'] == current_date:  #先抓預報時間為當日的資料縮小資料範圍
        air_row = [a['forecastdate'] ,a['area'], int(a['aqi']),a['majorpollutant'],a['publishtime']]
        air_today.append(air_row)

#air_today

"""爬取天氣資料"""

# 爬取天氣資料
weather_url = 'https://opendata.cwa.gov.tw/fileapi/v1/opendataapi/F-C0032-001?Authorization=rdec-key-123-45678-011121314&format=JSON'
weather_r = requests.get(weather_url, headers=header)
weather_r.encoding = 'UTF-8' # 指定編碼方式，utf-8、UTF-8、UTF8、utf8 都一樣
weather_soup = BeautifulSoup(weather_r.text, 'html.parser')

# json解析
# 只要看起來是字典格式，就表示這是 json 格式，所以用 json 模組轉換成字典：
weather_data = json.loads(weather_r.text)

"""### 字典建立

建立台灣七大地區字典:twregion_d
"""

twregion_lst = ['北北基宜','桃竹苗','中彰投','雲嘉南','高屏澎','花東','外島']
twregion_d = {}
for i in range(1,len(twregion_lst)+1):
    twregion_d[i]=twregion_lst[i-1]
print(twregion_d)

"""建立台灣地區對應縣市字典:twregion_county_d"""



"""建立所在地區代碼對應縣市描述字典regioncode_county_d

所在地區代碼：(1.北北基宜、2.桃竹苗、3.中彰投、4.雲嘉南、5.高屏澎、6.花東、7.外島)對應縣市描述
"""

regioncode_county_d = {
    1:'1.臺北市、2.新北市、3.基隆市、4.宜蘭縣',
    2:'5.桃園市、6.新竹市、7.新竹縣、8.苗栗縣',
    3:'9.臺中市、10.彰化縣、11.南投縣',
    4:'12.雲林縣、13.嘉義市、14.嘉義縣、15.臺南市',
    5:'16.高雄市、17.屏東縣、18.澎湖縣',
    6:'19.花蓮縣、10.臺東縣(含綠島、蘭嶼)',
    7:'21.金門縣、22.馬祖(連江縣)'
}
#給予輸入縣市提示使用
#regioncode_county_d[region_code]

"""空氣品質預報使用的字典"""

#縣市代碼對應縣市名、空品區字典countycode_airarea_d
#縣市代碼:縣市名稱、空品區字典
countycode_airarea_d ={
    1:['臺北市','北部']
   ,2:['新北市','北部']
   ,3:['基隆市','北部']
   ,4:['宜蘭縣','宜蘭']
   ,5:['桃園市','北部']
   ,6:['新竹市','竹苗']
   ,7:['新竹縣','竹苗']
   ,8:['苗栗縣','竹苗']
   ,9:['臺中市','中部']
   ,10:['彰化縣','中部']
   ,11:['南投縣','中部']
   ,12:['雲林縣','雲嘉南']
   ,13:['嘉義市','雲嘉南']
   ,14:['嘉義縣','雲嘉南']
   ,15:['臺南市','雲嘉南']
   ,16:['高雄市','高屏']
   ,17:['屏東縣','高屏']
   ,18:['澎湖縣','澎湖']
   ,19:['花蓮縣','花東']
   ,20:['臺東縣','花東']
   ,21:['金門縣','金門']
   ,22:['連江縣','馬祖']
}
#countycode_airarea_d[1][0]


#空氣品質對應人體健康影響、活動建議代碼字典aquality_health_d
#空氣品質:健康影響描述、活動建議代碼
aquality_health_d ={
    '良好':['污染程度低或無污染',0]
   ,'普通':['對非常少數之極敏感族群產生輕微影響',1]
   ,'對敏感族群不健康':['可能會對敏感族群的健康造成影響，但是對一般大眾的影響不明顯',2]
   ,'對所有族群不健康':['對所有人的健康開始產生影響，對於敏感族群可能產生較嚴重的健康影響',3]
   ,'非常不健康':['健康警報：所有人都可能產生較嚴重的健康影響',4]
   ,'危害':['健康威脅達到緊急，所有人都可能受到影響',5]
}


#使用者族群與對應不同空氣品質下的活動建議字典group_suggest_d
#使用者族群:空氣品質[良好,普通,對敏感族群不健康,對所有族群不健康,非常不健康,危害]下的活動建議
group_suggest_d = {
    '一般民眾':['正常戶外活動'
              ,'正常戶外活動'
              ,'如果有不適，如眼痛，咳嗽或喉嚨痛等，應該考慮減少戶外活動'
              ,'如果有不適，如眼痛，咳嗽或喉嚨痛等，應減少體力消耗，特別是減少戶外活動'
              ,'應減少戶外活動'
              ,'應避免戶外活動，室內應緊閉門窗，必要外出應配戴口罩等防護用具']
    ,'學生':['正常戶外活動'
           ,'正常戶外活動'
           ,'仍可進行戶外活動，但建議減少長時間劇烈運動'
           ,'應避免長時間劇烈運動，進行其他戶外活動時應增加休息時間'
           ,'應立即停止戶外活動，並將課程調整於室內進行'
           ,'應立即停止戶外活動，並將課程調整於室內進行']
    ,'孩童':['正常戶外活動'
           ,'建議注意可能產生的咳嗽或呼吸急促症狀，但仍可正常戶外活動'
           ,'建議減少體力消耗活動及戶外活動，必要外出應配戴口罩;具有氣喘的人應增加使用吸入劑的頻率'
           ,'建議留在室內並減少體力消耗活動，必要外出應配戴口罩;具有氣喘的人應增加使用吸入劑的頻率'
           ,'應留在室內並減少體力消耗活動，必要外出應配戴口罩;具有氣喘的人應增加使用吸入劑的頻率'
           ,'應留在室內並避免體力消耗活動，必要外出應配戴口罩;具有氣喘的人應增加使用吸入劑的頻率']
    ,'老人':['正常戶外活動'
           ,'建議注意可能產生的咳嗽或呼吸急促症狀，但仍可正常戶外活動'
           ,'建議減少體力消耗活動及戶外活動，必要外出應配戴口罩;具有氣喘的人應增加使用吸入劑的頻率'
           ,'建議留在室內並減少體力消耗活動，必要外出應配戴口罩;具有氣喘的人應增加使用吸入劑的頻率'
           ,'應留在室內並減少體力消耗活動，必要外出應配戴口罩;具有氣喘的人應增加使用吸入劑的頻率'
           ,'應留在室內並避免體力消耗活動，必要外出應配戴口罩;具有氣喘的人應增加使用吸入劑的頻率']
    ,'敏感族群':['正常戶外活動'
               ,'建議注意可能產生的咳嗽或呼吸急促症狀，但仍可正常戶外活動'
               ,'建議減少體力消耗活動及戶外活動，必要外出應配戴口罩;具有氣喘的人應增加使用吸入劑的頻率'
               ,'建議留在室內並減少體力消耗活動，必要外出應配戴口罩;具有氣喘的人應增加使用吸入劑的頻率'
               ,'應留在室內並減少體力消耗活動，必要外出應配戴口罩;具有氣喘的人應增加使用吸入劑的頻率'
               ,'應留在室內並避免體力消耗活動，必要外出應配戴口罩;具有氣喘的人應增加使用吸入劑的頻率']
}

"""### 函式

空氣品質函式: def air_quality(age, disease, county_code)
"""

def air_quality(age, disease, county_code):

    #空氣品質預報資料處理
    #找出縣市對應空品區
    loc_name = countycode_airarea_d[county_code][0]
    loc_airarea = countycode_airarea_d[county_code][1]

    #找出空品區最新發布的空氣品質預報:每日 10:30、16:30、22:00
    max_publishdate = max([x[4] for x in air_today if x[1]==loc_airarea])

    #當日的所有空氣品質資料air_today
    #資料欄位:'forecastdate','area','aqi','majorpollutant','publishtime'(預報日期,空品區,AQI,主要汙染物,預報發布時間)
    for loc_air in air_today:
        #找出該縣市最新空氣品質預報
        if loc_air[1] == loc_airarea and loc_air[4] == max_publishdate:
            #空氣品質數值loc_aqi
            loc_aqi = loc_air[2]
            #主要污染物名稱loc_majorpollutant，若為空值則為'無主要污染物'
            if loc_air[3] == '':
                loc_majorpollutant = '無主要污染物'
            else:
                loc_majorpollutant = loc_air[3]

    # AQI值判斷空氣品質，用字典對應人體健康影響與其活動對應代碼
    if loc_aqi in range(0,51):
        loc_aquality = '良好'
    elif loc_aqi in range(51,101):
        loc_aquality = '普通'
    elif loc_aqi in range(101,151):
        loc_aquality= '對敏感族群不健康'
    elif loc_aqi in range(151,201):
        loc_aquality= '對所有族群不健康'
    elif loc_aqi in range(201,301):
        loc_aquality = '非常不健康'
    else:
        loc_aquality = '危害'
    '''
    match loc_aqi:
        case _ if loc_aqi <= 50:
            loc_aquality = '良好'
        case _ if loc_aqi <= 100:
            loc_aquality = '普通'
        case _ if loc_aqi <= 150:
            loc_aquality = '對敏感族群不健康'
        case _ if loc_aqi <= 200:
            loc_aquality = '對所有族群不健康'
        case _ if loc_aqi <= 300:
            loc_aquality = '非常不健康'
        case _:
            loc_aquality = '危害'
    這邊感覺可以改這樣，就不用一直if elif一直判斷了

    '''
    #找出該空氣品質下的健康影響描述 health_effect、活動建議代碼 activity_level
    health_effect, activity_level = aquality_health_d[loc_aquality][0], aquality_health_d[loc_aquality][1]

    #找出使用者族群與適合的活動建議
    #使用者族群類別group_category判斷
    group_category = []

    #敏感族群優先
    if disease == 1:
        group_category.append('敏感族群')
    #次要依年齡判斷族群
    if age in range(16,21):   #學生:16~20
        group_category.append('學生')
    elif age in range(0,16):  #孩童:0~15
        group_category.append('孩童')
    elif age >= 65:       #老人:>=65
        group_category.append('老人')
    #若不具備以上的類別則為一般民眾
    if group_category == []:
        group_category.append('一般民眾')

    #使用者族群類別group_category給予活動建議activity_suggestion主要判斷依據:第一個分類為主main_group
    main_group = group_category[0]  #使用者所屬族群主要判斷依據main_group
    activity_suggestion = group_suggest_d[main_group][activity_level]  #該空氣品質下的活動建議activity_suggestion
    group_name = '、'.join(group_category)  #使用者符合的族群類別group_name

    #回傳給使用者的訊息
    air_result = f'{loc_name}今日({current_date})於{loc_airarea}的空氣品質預報：\n1.空氣品質: {loc_aquality}（AQI = {loc_aqi})。\n2.主要污染物: {loc_majorpollutant}。\n3.對健康影響: {health_effect}。\n4.給予{group_name}的活動建議: {activity_suggestion}。\n5.預報最新取得時間: {max_publishdate}。'
    return air_result, loc_aqi, group_name #新增回傳loc_aqi, group_name

"""天氣結果函式: def weather(county_code)"""

# 天氣資料類別建立
@dataclass
class WeatherClass:
    city: str  # 縣市名稱
    wx: str  # 天氣現象
    maxt: int  # 最高溫
    mint: int  # 最低溫
    pop: int  # 降雨機率
    updatedate: str  # 預報最新取得日期

# 天氣函式
def weather(county_code):
    update = weather_data["cwaopendata"]["sent"]
    updatetime = update.split("T")[1][0:5]
    global w
    loc_name = countycode_airarea_d[county_code][0]
    for i in weather_data["cwaopendata"]["dataset"]["location"]:
        if i["locationName"] == loc_name:
            w = WeatherClass(
                city=i["locationName"],
                wx=i["weatherElement"][0]["time"][0]["parameter"]["parameterName"],
                maxt=int(i["weatherElement"][1]["time"][0]["parameter"]["parameterName"]),
                mint=int(i["weatherElement"][2]["time"][0]["parameter"]["parameterName"]),
                pop=int(i["weatherElement"][4]["time"][0]["parameter"]["parameterName"]),
                updatedate=update.split("T")[0],
            )
    weather_result = (
              f"{w.city}今日({w.updatedate})的天氣預報: \n"
              f"1.天氣概述: {w.wx}。 \n"
              f"2.最高溫度: {w.maxt}度。 \n"
              f"3.最低溫度: {w.mint}度。 \n"
              f"4.降雨機率: {w.pop}%。 \n"
              f"5.預報最新取得時間: {w.updatedate} {updatetime}。"
              )
    return weather_result

"""依溫度決定服裝:"""

def temperature(clothes, pants, accessories, mint):
  clothes_d = {
      1: {"發熱衣","高領厚毛衣","防風羽絨外套"}, #10度以下
      2: {"厚帽T","毛衣","長大衣"},#11-15度
      3: {"長袖上衣","毛背心","厚棉外套"},#16-20度
      4: {"針織衫","薄帽T","襯衫","薄外套"},#21-25度
      5: {"短袖T恤","抗UV遮陽外套"},#26-30度
      6: {"透氣排汗T恤","抗UV遮陽外套"},#31度以上
  }
  pants_d = {
      1: {"發熱褲","毛長褲"}, #10度以下
      2: {"毛長褲"},#11-15度
      3: {"長褲","長裙"},#16-20度
      4: {"長褲","長裙"},#21-25度
      5: {"七分褲","薄長褲"},#26-30度
      6: {"短褲","短裙"},#31度以上
  }
  accessories_d = {
      1: {"毛帽","口罩","圍巾","毛襪","雪靴","厚手套"}, #10度以下
      2: {"毛帽","口罩","圍巾","厚襪子","手套"},#11-15度
      3: {"口罩","圍巾","襪子","手套"},#16-20度
      4: {"口罩","襪子"},#21-25度
      5: {"鴨舌帽","傘"},#26-30度
      6: {"遮陽帽","涼鞋","傘"},#31度以上
  }
  if mint<=10:
    clothes.update(clothes_d[1])
    pants.update(pants_d[1])
    accessories.update(accessories_d[1])
  elif mint<=15:
    clothes.update(clothes_d[2])
    pants.update(pants_d[2])
    accessories.update(accessories_d[2])
  elif mint<=20:
    clothes.update(clothes_d[3])
    pants.update(pants_d[3])
    accessories.update(accessories_d[3])
  elif mint<=25:
    clothes.update(clothes_d[4])
    pants.update(pants_d[4])
    accessories.update(accessories_d[4])
  elif mint<=30:
    clothes.update(clothes_d[5])
    pants.update(pants_d[5])
    accessories.update(accessories_d[5])
  elif 31<=mint:
    clothes.update(clothes_d[6])
    pants.update(pants_d[6])
    accessories.update(accessories_d[6])
  return clothes, pants, accessories

"""依空氣品質決定是否戴口罩:"""

def mask(accessories, loc_aqi, group_name):
  loc_aqi = int(loc_aqi)
  if group_name == "敏感族群" or "孩童" or "老人":
    if loc_aqi >= 101:
      accessories.add("口罩")
  else:
    if loc_aqi >= 151:
      accessories.add("口罩")
  return accessories

"""依下雨機率決定是否帶雨傘:"""

def umbrella(accessories, pop):
  if pop >= 60:
    accessories.add("傘")
  return accessories

"""### 變數輸入

使用者輸入所在地區代碼：1.北北基宜、2.桃竹苗、3.中彰投、4.雲嘉南、5.高屏澎、6.花東、7.外島(例如:1)
"""

region_code = int(input("輸入所在地區代碼，1.北北基宜、2.桃竹苗、3.中彰投、4.雲嘉南、5.高屏澎、6.花東、7.外島(例如:1):"))

"""依據地區決定使用者接下來要輸入的縣市範圍：
北北基宜：1.臺北市、2.新北市、3.基隆市、4.宜蘭縣、23.重新選擇地區
桃竹苗：5.桃園市、6.新竹市、7.新竹縣、8.苗栗縣、23.重新選擇地區
中彰投：9.臺中市、10.彰化縣、11.南投縣、23.重新選擇地區
雲嘉南：12.雲林縣、13.嘉義市、14.嘉義縣、15.臺南市、23.重新選擇地區
高屏澎：16.高雄市、17.屏東縣、18.澎湖縣、23.重新選擇地區
花東：19.花蓮縣、10.臺東縣(含綠島、蘭嶼)、23.重新選擇地區
外島：21.金門縣、22.馬祖(連江縣)、23.重新選擇地區

輸入所在地區代碼：1.臺北市、2.新北市、3.基隆市、4.宜蘭縣、23.重新選擇地區(例如:2)
"""

county_code = int(input(f'輸入所在縣市代碼，{regioncode_county_d[region_code]}(例如:2):'))
print(county_code)

"""使用者輸入年齡(例如：18)：


"""

age = int(input("輸入年齡(例如：18):"))

"""使用者輸入回答是否為有心臟、呼吸道、氣喘及心血管疾病患者或孕婦(例如:是/否)
心臟、呼吸道、氣喘、心血管疾病患者或為孕婦(是輸入:1，否輸入:0)
"""

disease = int(input("心臟、呼吸道、氣喘、心血管疾病患者或為孕婦(是則輸入:1，否則輸入:0):"))

"""### 呼叫函式"""

#呼叫天氣函式
print(weather(county_code))

#呼叫空氣品質函式
print()
air_result, loc_aqi, group_name = air_quality(age, disease, county_code)    #新增回傳loc_aqi, group_name
print(air_result)

#呼叫服裝函式
clothes = set()
pants = set()
accessories = set()
clothes, pants, accessories = temperature(clothes, pants, accessories, w.mint)
accessories = mask(accessories, loc_aqi, group_name)
accessories = umbrella(accessories, w.pop)
print()
print(f"{w.city}今日({w.updatedate})的穿搭建議:\n"
      f"1.上身: {', '.join(clothes)}。\n"
      f"2.下身: {', '.join(pants)}。\n"
      f"3.配件: {', '.join(accessories)}。")
