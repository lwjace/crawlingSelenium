from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import json

# Chrome 웹드라이버 설정 (수동 다운로드 경로 사용)
chrome_driver_path = "D:\\study\\python\\work\\chromedriver.exe"  # ChromeDriver 경로

# Service 객체 생성
service = Service(executable_path=chrome_driver_path)
driver = webdriver.Chrome(service=service)

try:
    # 웹 페이지 로드
    driver.get('https://www.lguplus.com/benefit-event/ongoing/387')

    # jQuery 동적 로드
    driver.execute_script("""
    if (typeof jQuery == 'undefined') {
        var script = document.createElement('script');
        script.src = 'https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js';
        script.type = 'text/javascript';
        document.getElementsByTagName('head')[0].appendChild(script);
    }
    """)

    # 잠시 대기하여 jQuery가 로드될 시간을 줌
    time.sleep(2)

    # JavaScript 코드 삽입: 모든 프레임워크의 이벤트 리스너를 추적
    driver.execute_script("""
    // 순환 참조 제거를 위한 JSON 직렬화 함수
    function safeStringify(obj, replacer, spaces) {
        var cache = [];
        const retVal = JSON.stringify(obj, (key, value) =>
            typeof value === 'object' && value !== null
                ? cache.includes(value)
                    ? undefined // Duplicate reference found, discard key
                    : cache.push(value) && value // Store value in our collection
                : value,
            spaces
        );
        cache = null; // Enable garbage collection
        return retVal;
    }

    // Vue.js 이벤트 핸들러 추적
    (function() {
        var elementsWithListeners = [];
        var allElements = document.querySelectorAll('*');
        
        allElements.forEach(function(element) {
            if (element.__vue__) {
                var vueInstance = element.__vue__;
                var eventNames = Object.keys(vueInstance._events);
                elementsWithListeners.push({tag: element.tagName, id: element.id, classes: element.className, events: eventNames});
            }
        });
        
        window.getVueElementsWithListeners = function() {
            return safeStringify(elementsWithListeners);
        };
    })();
    
    // React 이벤트 핸들러 추적
    (function() {
        var elementsWithListeners = [];
        var allElements = document.querySelectorAll('*');
        
        allElements.forEach(function(element) {
            for (var key in element) {
                if (key.startsWith('__reactEventHandlers$')) {
                    elementsWithListeners.push({tag: element.tagName, id: element.id, classes: element.className, handlers: element[key]});
                    break;
                }
            }
        });
        
        window.getReactElementsWithListeners = function() {
            return safeStringify(elementsWithListeners);
        };
    })();
    
    // jQuery AJAX 이벤트 핸들러 추적
    (function($) {
        var originalAjax = $.ajax;
        var ajaxHandlers = [];
    
        $.ajax = function(settings) {
            ajaxHandlers.push(settings);
            return originalAjax.apply(this, arguments);
        };
    
        window.getAjaxHandlers = function() {
            return safeStringify(ajaxHandlers);
        };
    })(jQuery);
    """)

    with open("event_listeners.txt", "w") as file:
        # Vue.js 이벤트 핸들러가 있는 요소를 찾기
        vue_elements_with_listeners = json.loads(driver.execute_script("return getVueElementsWithListeners();"))
        file.write("Vue.js 이벤트 핸들러가 있는 요소들:\n")
        file.write(json.dumps(vue_elements_with_listeners, indent=2) + "\n\n")

        # Vue.js 이벤트 핸들러가 있는 요소와 상호작용
        for item in vue_elements_with_listeners:
            tag = item['tag']
            element_id = item['id']
            classes = item['classes']
            events = item['events']
            
            if element_id:
                element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, element_id)))
            elif classes:
                element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, classes.split()[0])))
            else:
                element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, tag)))

            # 요소가 화면에 표시될 때까지 대기
            WebDriverWait(driver, 10).until(EC.visibility_of(element))

            for event_type in events:
                if event_type == 'click':
                    # 요소가 화면에 표시되도록 스크롤
                    driver.execute_script("arguments[0].scrollIntoView();", element)
                    # 요소가 클릭 가능해질 때까지 대기
                    WebDriverWait(driver, 10).until(EC.element_to_be_clickable(element))
                    element.click()
                elif event_type == 'mouseover':
                    ActionChains(driver).move_to_element(element).perform()
                elif event_type == 'keyup':
                    element.send_keys(Keys.RETURN)
                # 필요한 경우 다른 이벤트 타입에 대한 처리 추가
                time.sleep(1)  # 각 상호작용 사이에 약간의 대기 시간 추가

        # React 이벤트 핸들러가 있는 요소를 찾기
        react_elements_with_listeners = json.loads(driver.execute_script("return getReactElementsWithListeners();"))
        file.write("React 이벤트 핸들러가 있는 요소들:\n")
        file.write(json.dumps(react_elements_with_listeners, indent=2) + "\n\n")

        # React 이벤트 핸들러가 있는 요소와 상호작용
        for item in react_elements_with_listeners:
            tag = item['tag']
            element_id = item['id']
            classes = item['classes']
            handlers = item['handlers']
            
            if element_id:
                element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, element_id)))
            elif classes:
                element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, classes.split()[0])))
            else:
                element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, tag)))

            # 요소가 화면에 표시될 때까지 대기
            WebDriverWait(driver, 10).until(EC.visibility_of(element))

            for event_type in handlers:
                if event_type == 'onClick':
                    # 요소가 화면에 표시되도록 스크롤
                    driver.execute_script("arguments[0].scrollIntoView();", element)
                    # 요소가 클릭 가능해질 때까지 대기
                    WebDriverWait(driver, 10).until(EC.element_to_be_clickable(element))
                    element.click()
                elif event_type == 'onMouseOver':
                    ActionChains(driver).move_to_element(element).perform()
                elif event_type == 'onKeyUp':
                    element.send_keys(Keys.RETURN)
                # 필요한 경우 다른 이벤트 타입에 대한 처리 추가
                time.sleep(1)  # 각 상호작용 사이에 약간의 대기 시간 추가

        # jQuery AJAX 이벤트 핸들러 확인
        ajax_handlers = json.loads(driver.execute_script("return getAjaxHandlers();"))
        file.write("jQuery AJAX 이벤트 핸들러:\n")
        file.write(json.dumps(ajax_handlers, indent=2) + "\n\n")

finally:
    # 웹드라이버 종료
    driver.quit()
