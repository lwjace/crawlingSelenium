from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time

def get_input_elements_with_parents(driver, parent_levels):
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    input_elements = soup.find_all(['input', 'select', 'textarea'])

    blind_parents = soup.find_all(class_='blind')
    for blind_parent in blind_parents:
        input_elements.extend(blind_parent.find_all(['input', 'select', 'textarea']))

    valid_inputs = [el for el in input_elements if el.name != 'input' or el.get('type') != 'hidden']
    
    input_with_parents = []
    for el in valid_inputs:
        current_el = el
        for _ in range(parent_levels):
            parent = current_el.find_parent()
            if parent:
                current_el = parent
            else:
                break
        input_with_parents.append((el, current_el))
    
    return input_with_parents

def click_element_via_js(driver, element):
    driver.execute_script("arguments[0].click();", element)

def close_modal(driver):
    try:
        close_buttons = driver.find_elements(By.CSS_SELECTOR, '[data-dismiss="modal"], .modal-footer button, .close')
        for button in close_buttons:
            click_element_via_js(driver, button)
            time.sleep(0.5)
    except Exception as e:
        print(f"Error closing modal: {e}")

def analyze_html(file_path, parent_levels):
    input_urls = []
    error_urls = []

    try:
        with open(file_path, 'r') as file:
            urls = [line.strip() for line in file.readlines()]
    except Exception as e:
        print(f"Error reading file: {e}")
        return

    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    for url in urls:
        try:
            driver.get(url)
            WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.TAG_NAME, 'body')))
            original_url = driver.current_url

            checkboxes = driver.find_elements(By.CSS_SELECTOR, 'input[type="checkbox"]')
            for checkbox in checkboxes:
                try:
                    label = checkbox.find_element(By.XPATH, './following-sibling::label')
                    if '(필수)' in label.text or '필수' in label.text:
                        click_element_via_js(driver, checkbox)
                        time.sleep(0.5)
                except Exception as e:
                    print(f"Error processing checkbox: {e}")

            driver.execute_script("""
                var modals = document.querySelectorAll('[data-toggle="modal"], [data-bs-toggle="modal"]');
                modals.forEach(function(modal) {
                    modal.click();
                });
            """)
            time.sleep(2)

            initial_inputs_with_parents = get_input_elements_with_parents(driver, parent_levels)
            initial_input_set = set((el.get('id'), el.get('type')) for el, _ in initial_inputs_with_parents)
            initial_container_dict = {}
            for el, parent in initial_inputs_with_parents:
                part_html = str(parent)
                if part_html not in initial_container_dict:
                    initial_container_dict[part_html] = []
                input_id = el.get('id', 'N/A')
                input_type = el.get('type', 'N/A')
                initial_container_dict[part_html].append((input_id, input_type))

            buttons = driver.find_elements(By.TAG_NAME, 'button')
            new_inputs_with_parents = []
            processed_buttons = []

            for button in buttons:
                try:
                    button.click()
                    time.sleep(1)
                    WebDriverWait(driver, 5).until(EC.url_changes(original_url))

                    if driver.current_url != original_url:
                        print(f"URL changed to {driver.current_url} after clicking button. Processing the new page and returning to original.")
                        driver.back()
                        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.TAG_NAME, 'body')))
                        time.sleep(2)
                        continue

                    processed_buttons.append(button)

                    current_inputs_with_parents = get_input_elements_with_parents(driver, parent_levels)
                    current_input_set = set((el.get('id'), el.get('type')) for el, _ in current_inputs_with_parents)
                    new_input_elements_with_parents = [(el, parent) for el, parent in current_inputs_with_parents if (el.get('id'), el.get('type')) not in initial_input_set]
                    new_inputs_with_parents.extend(new_input_elements_with_parents)
                    initial_input_set.update(current_input_set)
                except TimeoutException:
                    print(f"Timeout while waiting for URL change after clicking button. Continuing with the same page.")
                except Exception as e:
                    print(f"Error clicking button: {e}")

            time.sleep(2)

            # 모달창 닫기
            close_modal(driver)

            if initial_inputs_with_parents or new_inputs_with_parents:
                input_urls.append(url)
                container_dict = initial_container_dict.copy()
                for el, parent in new_inputs_with_parents:
                    part_html = str(parent)
                    if part_html not in container_dict:
                        container_dict[part_html] = []
                    input_id = el.get('id', 'N/A')
                    input_type = el.get('type', 'N/A')
                    container_dict[part_html].append((input_id, input_type))

                input_html_parts = []
                for part_html, inputs in container_dict.items():
                    inputs_info = "\n".join([f"<p><strong>ID:</strong> {input_id} | <strong>Type:</strong> {input_type}</p>" for input_id, input_type in inputs])
                    condition = 'This input appears within a modal dialog.' if 'modal' in part_html.lower() else 'This input does not have specific conditional visibility.'
                    part_html = (f"<!-- Inputs Info: {inputs_info} -->\n"
                                 f"<div class='input-container'>\n"
                                 f"<p><strong>Condition:</strong> {condition}</p>\n"
                                 f"{inputs_info}\n"
                                 f"{part_html}\n"
                                 f"</div>")
                    input_html_parts.append(part_html)
                
                input_html = '\n'.join(input_html_parts)
                
                html_content = f"""
                <html>
                <head>
                    <style>
                        .input-container {{
                            border: 1px solid #000;
                            padding: 10px;
                            margin: 10px 0;
                        }}
                    </style>
                </head>
                <body>
                    {input_html}
                </body>
                </html>
                """
                
                filename = url.replace('http://', '').replace('https://', '').replace('/', '_') + '.html'
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(html_content)
        except Exception as e:
            error_urls.append((url, str(e)))

    driver.quit()

    with open('input_urls.txt', 'w') as f:
        for url in input_urls:
            f.write(f"{url}\n")

    with open('error_urls.txt', 'w') as f:
        for url, error in error_urls:
            f.write(f"{url} - {error}\n")

file_path = 'collected_urls.txt'
parent_levels = 2

analyze_html(file_path, parent_levels)
