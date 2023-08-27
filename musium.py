import json
import time
from time import sleep

import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# --크롬창을 숨기고 실행-- driver에 options를 추가해주면된다
# options = webdriver.ChromeOptions()
# options.add_argument('headless')

url = 'https://map.naver.com/v5/search'
driver = webdriver.Chrome('./chromedriver')  # 드라이버 경로
# driver = webdriver.Chrome('./chromedriver',chrome_options=options) # 크롬창 숨기기
driver.get(url)
key_word = '화성 미술관'  # 검색어

# css 찾을때 까지 10초대기
def time_wait(num, code):
    try:
        wait = WebDriverWait(driver, num).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, code)))
    except:
        print(code, '태그를 찾지 못하였습니다.')
        driver.quit()
    return wait

# frame 변경 메소드
def switch_frame(frame):
    driver.switch_to.default_content()  # frame 초기화
    driver.switch_to.frame(frame)  # frame 변경

# 페이지 다운
def page_down(num):
    body = driver.find_element(By.CSS_SELECTOR, 'body')
    body.click()
    for i in range(num):
        body.send_keys(Keys.PAGE_DOWN)

# css를 찾을때 까지 10초 대기
time_wait(10, 'div.input_box > input.input_search')

# (1) 검색창 찾기
search = driver.find_element(By.CSS_SELECTOR, 'div.input_box > input.input_search')
search.send_keys(key_word)  # 검색어 입력
search.send_keys(Keys.ENTER)  # 엔터버튼 누르기
print('검색완료')

sleep(5)

# (2) frame 변경
switch_frame('searchIframe')
page_down(40)
sleep(3)
print('프레임변경완료')

# 주차장 리스트
customer_list = driver.find_elements(By.CSS_SELECTOR, 'li.VLTHu')
# 페이지 리스트
next_btn_code = '.zRM9F > a'
next_btn = driver.find_elements(By.CSS_SELECTOR, next_btn_code)
for btns in next_btn:
    print(btns.text)
print('next_btn_lenght = ' , len(next_btn))

# dictionary 생성
customer_dict = {'업체정보': []}
# 시작시간
start = time.time()
print('[크롤링 시작...]')

# 크롤링 (페이지 리스트 만큼)
for btn in range(len(next_btn))[1:]:  # next_btn[0] = 이전 페이지 버튼 무시 -> [1]부터 시작
    print('btn : ',btn)
    customer_list = driver.find_elements(By.CSS_SELECTOR, 'li.Ki6eC.YPAJV')
    print(len(customer_list))
    names = driver.find_elements(By.CSS_SELECTOR, '.YFsgn')  # (3) 장소명
    detail_buttons = driver.find_elements(By.CSS_SELECTOR, 'a.u92d5')

    for data in range(len(customer_list)):  # 주차장 리스트 만큼
        print(data)

        switch_frame('searchIframe')

        sleep(1)
        try:
            # 지번, 도로명 초기화
            name = ''
            num_address = ''
            road_address = ''
            phone = ''
            shopUrl = ''


            # (5) 주소 버튼 누르기
            
            element = detail_buttons.__getitem__(data)
            print('이름 클릭')
            element.click()

            # 로딩 기다리기
            sleep(1)

            switch_frame('entryIframe')
            print('프레임변경완료')
            sleep(1)
            
            address_buttons = driver.find_elements(By.CSS_SELECTOR, '.PkgBl')
            address_buttons.__getitem__(0).click()
            sleep(1)

            try:
                name_box = driver.find_elements(By.CSS_SELECTOR, '.Fc1rA')
                name = name_box[0].text
            except:
                name = '-'

            try:
                phone_box = driver.find_elements(By.CSS_SELECTOR, '.xlx7Q')
                phone = phone_box[0].text
            except:
                phone = '-'

            try:
                shopUrl_box = driver.find_elements(By.CSS_SELECTOR, 'div.jO09N > a:first-child')
                shopUrl = shopUrl_box[0].text
            except:
                shopUrl = '-'

            print(name)
            print(phone)
            print(shopUrl)

            try:
                addr_elements = driver.find_elements(By.CSS_SELECTOR, '.Y31Sf > div')

                addr_texts = [element.text for element in addr_elements]
                
                # 도로명 주소와 우편번호 주소 처리
                for addr_text in addr_texts:
                    if '도로명' in addr_text:
                        start_index = addr_text.index('도로명') + len('도로명')
                        end_index = addr_text.index('복사', start_index)
                        road_address = addr_text[start_index:end_index]
                        print(f"도로명 주소: {road_address}")
                    elif '우편번호' in addr_text:
                        start_index = addr_text.index('우편번호\n') + len('우편번호\n')
                        num_address = addr_text[start_index:start_index + 5]
                        print(f"우편번호: {num_address}")
            except:
                road_address='-'
                num_address='-'

            # dict에 데이터 집어넣기
            dict_temp = {
                'name': name,
                'num_address': num_address,
                'road_address': road_address,
                'phone': phone,
                'shopUrl': shopUrl
            }

            customer_dict['업체정보'].append(dict_temp)
            print(f'{name} ...완료')

            sleep(1)

        except Exception as e:
            print(e)
            print('ERROR!' * 3)

            # dict에 데이터 집어넣기
            dict_temp = {
                'name': name,
                'num_address': num_address,
                'road_address': road_address,
                'phone': phone,
                'shopUrl': shopUrl
            }

            customer_dict['업체정보'].append(dict_temp)
            print('------------------------------------------')

            sleep(2)

    switch_frame('searchIframe')
    sleep(1)

    # if not next_btn[-1].is_enabled():
    #     break

    # if names[-1]:  # 마지막 주차장일 경우 다음버튼 클릭
    #     next_btn[-1].click()
    #     sleep(2)
    #     page_down(40)

    #     sleep(1)

    # if btn == len(next_btn)-2:
    #     print('마지막 페이지')
    #     break

    # next_btn[-1].click()
    # sleep(3)
    # page_down(40)

    # sleep(2)
    break

# json 파일로 저장
with open(f'{key_word}.json', 'w', encoding='utf-8') as f:
    json.dump(customer_dict, f, indent=5, ensure_ascii=False)

# DataFrame 생성
df = pd.DataFrame(customer_dict['업체정보'])

# DataFrame을 Excel 파일로 저장
excel_path = f'data/{key_word}.xlsx'
df.to_excel(excel_path, index=False)

print('[데이터 수집 완료]\n소요 시간 :', time.time() - start)
driver.quit()  # 작업이 끝나면 창을 닫는다.