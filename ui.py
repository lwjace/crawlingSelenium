import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementNotInteractableException, StaleElementReferenceException, TimeoutException, NoSuchElementException, NoSuchWindowException
import time

# 로깅 설정
logging.basicConfig(level=logging.ERROR,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[logging.FileHandler('element_interaction_errors.txt', 'w', 'utf-8'),
                              logging.StreamHandler()])

logger = logging.getLogger(__name__)

# Interaction log 설정
interaction_logger = logging.getLogger('interaction_logger')
interaction_logger.setLevel(logging.INFO)
interaction_handler = logging.FileHandler('element_interactions.txt', 'w', 'utf-8')
interaction_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
interaction_logger.addHandler(interaction_handler)

# 웹 드라이버 설정 (Chrome 사용 예시)
driver_path = "D:\\study\\python\\work\\chromedriver.exe"
service = Service(driver_path)
driver = webdriver.Chrome(service=service)

# URL 열기
initial_url = 'https://www.lguplus.com/benefit-event/ongoing/387'
driver.get(initial_url)

# ActionChains 객체 생성
actions = ActionChains(driver)
wait = WebDriverWait(driver, 10)

# 상호작용한 요소들을 저장할 집합
interacted_elements = set()

def get_element_identifier(element):
    try:
        outer_html = element.get_attribute('outerHTML')
        return outer_html
    except StaleElementReferenceException:
        return None

def get_visible_elements():
    elements = driver.find_elements(By.CSS_SELECTOR, 'a, button, input, select, textarea, [onclick]')
    visible_elements = [element for element in elements if EC.visibility_of(element)(driver)]
    return visible_elements

def interact_with_element(element, original_url):
    try:
        current_url = driver.current_url

        element_id = get_element_identifier(element)

        if element_id in interacted_elements or element_id is None:
            return

        # 요소 정보 로깅
        interaction_logger.info(f"Interacting with element: {element_id}")

        # 클릭 가능한 요소 클릭
        if element.tag_name in ['a', 'button']:
            actions.move_to_element(element).click().perform()

        # 입력 가능한 요소에 키 입력
        elif element.tag_name in ['input', 'textarea']:
            actions.move_to_element(element).send_keys('Test input').perform()

        # 드롭다운 메뉴 선택
        elif element.tag_name == 'select':
            for option in element.find_elements(By.TAG_NAME, 'option'):
                actions.move_to_element(option).click().perform()

        # 포커스 및 키보드 입력
        actions.move_to_element(element).send_keys(Keys.TAB).perform()

        # 마우스 호버
        actions.move_to_element(element).perform()

        # 상호작용한 요소를 집합에 추가
        interacted_elements.add(element_id)

        # 상호작용 후 URL이 변경되었는지 확인
        if driver.current_url != current_url:
            logger.error(f"URL changed after interacting with element {element.tag_name}. Reverting to {original_url}")
            driver.get(original_url)
            WebDriverWait(driver, 10).until(EC.url_to_be(original_url))

    except TimeoutException as e:
        logger.error(f"Timeout while waiting for element to be clickable: {e}")
    except StaleElementReferenceException as e:
        logger.error(f"Stale element reference before accessing tag name: {e}")
        try:
            tag_name = element.tag_name
        except StaleElementReferenceException as inner_e:
            logger.error(f"Stale element reference after accessing tag name: {inner_e}")
    except ElementNotInteractableException as e:
        logger.error(f"Element not interactable: {e}")
    except NoSuchWindowException:
        logger.error("Window closed unexpectedly.")
        return
    except Exception as e:
        logger.error(f"Unexpected error: {e}")

def interact_with_visible_elements():
    while True:
        try:
            visible_elements = get_visible_elements()
            for element in visible_elements:
                interact_with_element(element, initial_url)
            time.sleep(1)  # 잠시 대기 후 다시 시도
        except NoSuchWindowException:
            logger.error("Window closed unexpectedly.")
            break

# 각 요소에 대해 가능한 상호작용 시도
interact_with_visible_elements()

# 드라이버 종료
driver.quit()
