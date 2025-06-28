import random
from src.utils.logger import log
import pickle
import os
import time
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium import webdriver
from src.scrapers.ScraperFactory import Scraper
from src.data.models import Article
from typing import List, Dict, Any


class seleniumRssScrapper(Scraper):
    def __init__(self, rate_limite, agents, search_word="inflation"):
        self.url = 'https://www.npr.org/'
        self.agent = agents[0]
        self.proxy = agents[1]
        self.cookies_file = 'session_cookies.pkl'
        self.search_word = search_word

    def web_driver(self):
        options = Options()
        options.add_argument(f"--user-agent={self.agent}")
        profile = FirefoxProfile()
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-web-security")
        options.add_argument("--disable-features=VizDisplayCompositor")
        options.add_argument("--start-maximized")
        profile.set_preference("permissions.default.image", 2)
        profile.set_preference("dom.webdriver.enabled", False)
        profile.set_preference("useAutomationExtension", False)
        options.profile = profile

        driver = webdriver.Firefox(options=options)

        log.info(f"Using Proxy: {self.proxy} | User-Agent: {self.agent}")
        return driver

    def save_cookies(self, driver):
        try:
            cookies = driver.get_cookies()
            with open(self.cookies_file, 'wb') as f:
                pickle.dump(cookies, f)
            log.info(f"Cookies saved to {self.cookies_file}")
        except Exception as e:
            log.error(f"Failed to save cookies: {e}")

    def load_cookies(self, driver):
        try:
            if os.path.exists(self.cookies_file):
                with open(self.cookies_file, 'rb') as f:
                    cookies = pickle.load(f)
                for cookie in cookies:
                    driver.add_cookie(cookie)
                log.info(f"Cookies loaded from {self.cookies_file}")
                return True
            else:
                log.info("No saved cookies found")
                return False
        except Exception as e:
            log.error(f"Failed to load cookies: {e}")
            return False

    def clear_session(self, driver):
        try:
            driver.delete_all_cookies()
            if os.path.exists(self.cookies_file):
                os.remove(self.cookies_file)
            log.info("Session cleared and cookies deleted")
        except Exception as e:
            log.error(f"Failed to clear session: {e}")

    def maintain_session(self, driver):
        try:
            driver.refresh()
            time.sleep(random.uniform(2, 4))
            self.save_cookies(driver)
            log.info("Session maintained and cookies updated")
        except Exception as e:
            log.error(f"Failed to maintain session: {e}")

    def scrape(self, url):
        """Scrape RSS feed data using Selenium"""
        # For RSS tasks, we don't need the URL parameter since we use hardcoded NPR URL
        # But we should validate that we have a search word
        if not self.search_word:
            raise ValueError("Search word is required for RSS scraping")
            
        driver = self.web_driver()
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        time.sleep(random.uniform(1.5, 3.5))

        try:
            driver.get(self.url)
            # Accept cookie banner if present
            try:
                consent_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Accept')]"))
                )
                consent_button.click()
            except:
                pass  # no cookie prompt
            # load existing cookies
            self.load_cookies(driver)
            driver.refresh()  # Refresh to apply cookies
            time.sleep(random.uniform(1.5, 3.5))
            word = self.search_word

            search_link = driver.find_element(By.CSS_SELECTOR, "a#navigation_dropdown-search")
            driver.execute_script("arguments[0].click();", search_link)
            time.sleep(random.uniform(1.5, 3.5))
            # Save cookies after successful navigation
            self.save_cookies(driver)
            # search word
            self.search(driver, word)

            self.checkbox(driver)
            time.sleep(random.uniform(1.5, 3.5))
            select_elem = Select(driver.find_element(By.CSS_SELECTOR, "div.filterDate select.searchdd"))
            options = [option.get_attribute('value') for option in select_elem.options]
            print(options)
            time.sleep(random.uniform(1.5, 3.5))
            self.filter_by_date(driver, random.choice(options))
            select_elem = Select(driver.find_element(By.CSS_SELECTOR, "div.filterProg select.searchdd"))
            options =  [option.get_attribute('value') for option in select_elem.options]
            print(options)
            self.filter_by_program(driver, random.choice(options))
            time.sleep(random.uniform(1.5, 3.5))

            while True:
                if not self.load_more(driver):
                    break
            raw_data = self.extract_data(driver)
            self.save_cookies(driver)
            driver.quit()
            
            # Preprocess the data and convert to Article objects
            articles = self.preprocess_data(raw_data)
            
            # Add source type metadata
            for article in articles:
                article.source_type = 'rss'
                if not article.scraped_at:
                    article.scraped_at = datetime.now()
                article.metadata['search_word'] = self.search_word
            
            log.info(f"Successfully scraped {len(articles)} RSS articles")
            return articles
            
        except Exception as e:
            log.error(e)
            driver.quit()
            return []

    def search(self, driver, word):
        search_input = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="search"]'))
        )
        driver.execute_script("""
            const input = arguments[0];
            const val = arguments[1];

            const nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value").set;
            nativeInputValueSetter.call(input, val);

            input.dispatchEvent(new Event('input', { bubbles: true }));
            input.dispatchEvent(new Event('change', { bubbles: true }));
        """, search_input, word)

    def checkbox(self, driver):
        checkbox = driver.find_element(By.CSS_SELECTOR, "input[type='checkbox'][name='tabId'][value='hoa']")
        checkbox.click()  # toggles checkbox

    def filter_by_date(self, driver, option):
        date_filter = Select(driver.find_element(By.CSS_SELECTOR, "div.filterDate select.searchdd"))
        date_filter.select_by_value(option)

    def filter_by_program(self, driver, option):
        prog_filter = Select(driver.find_element(By.CSS_SELECTOR, "div.filterProg select.searchdd"))
        prog_filter.select_by_value(option)

    def load_more(self, driver):
        try:
            # Wait for and click the Load More button
            load_more = WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.ais-InfiniteHits-loadMore"))
            )
            
            # Automatically click Load More (no interactive input)
            print("Loading more results automatically...")
            load_more.click()
            time.sleep(1)
            return True
            
        except:
            print("No more Load More button.")
            return False

    def extract_data(self, driver):
        articles = driver.find_elements(By.CSS_SELECTOR, "ul.ais-InfiniteHits-list > li")
        data = []
        for article in articles:
            try:
                # Extract article title and link
                title_element = article.find_element(By.CSS_SELECTOR, "h2.title a")
                title = title_element.text.strip()
                href = title_element.get_attribute("href")
                author_spans = article.find_elements(By.CSS_SELECTOR,
                                                     "p.byline .ais-Highlight span span.ais-Highlight-nonHighlighted")
                authors = [span.text.strip() for span in author_spans if span.text.strip()]
                author = ", ".join(authors) if authors else "Unknown"
                snippet_element = article.find_element(By.CSS_SELECTOR, ".ais-Snippet")
                snippet_text = snippet_element.text.strip()
                article = Article(
                    source_type= "rss",
                    source = "NPR",
                    title = title,
                    url = href,
                    summary= snippet_text,
                    tags = [self.search_word] if self.search_word else [],
                    scraped_at= datetime.now(),
                    metadata={
                        'scraper': 'Selenium_scraper',
                        'framework': 'selenium'
                    }
                )
                # info = {
                #     'title': title,
                #     'author': author,
                #     'url': href,
                #     'href': href,
                #     'summary': snippet_text,
                #     'content': snippet_text,
                #     'source': 'NPR',
                #     'tags': [self.search_word] if self.search_word else []
                # }
                data.append(article)
            except Exception as e:
                log.error(f"{e}")
                data.append(Article())
        return data
