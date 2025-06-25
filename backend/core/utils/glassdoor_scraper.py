from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from typing import List, Dict, Optional
import time
import logging
from bs4 import BeautifulSoup
import re
import urllib.parse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GlassdoorScraper:
    def __init__(self):
        """Initialize the scraper with Chrome options."""
        self.options = webdriver.ChromeOptions()
        self.options.add_argument('--headless')
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-dev-shm-usage')
        self.options.add_argument('--disable-gpu')
        self.options.add_argument('--window-size=1920,1080')
        self.options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')

    def _clean_text(self, text: str) -> str:
        """Clean the text by removing extra whitespace and special characters."""
        if not text:
            return ""
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[^\w\s.,!?-]', '', text)
        return text.strip()

    def _extract_question_data(self, question_element) -> Dict:
        """Extract data from a question element."""
        try:
            # Get the question text
            question_text = question_element.find_element(By.CSS_SELECTOR, '[data-test="interview-question"]').text
            question_text = self._clean_text(question_text)

            # Get the answer if available
            try:
                answer_element = question_element.find_element(By.CSS_SELECTOR, '[data-test="interview-answer"]')
                answer_text = self._clean_text(answer_element.text)
            except NoSuchElementException:
                answer_text = ""

            # Get metadata
            metadata = {}
            
            # Get date
            try:
                date_element = question_element.find_element(By.CSS_SELECTOR, '[data-test="interview-date"]')
                metadata['date'] = self._clean_text(date_element.text)
            except NoSuchElementException:
                metadata['date'] = ""

            # Get difficulty
            try:
                difficulty_element = question_element.find_element(By.CSS_SELECTOR, '[data-test="interview-difficulty"]')
                metadata['difficulty'] = self._clean_text(difficulty_element.text)
            except NoSuchElementException:
                metadata['difficulty'] = ""

            # Get role
            try:
                role_element = question_element.find_element(By.CSS_SELECTOR, '[data-test="interview-role"]')
                metadata['role'] = self._clean_text(role_element.text)
            except NoSuchElementException:
                metadata['role'] = ""

            # Get application process
            try:
                process_element = question_element.find_element(By.CSS_SELECTOR, '[data-test="interview-process"]')
                metadata['process'] = self._clean_text(process_element.text)
            except NoSuchElementException:
                metadata['process'] = ""

            # Get offer status
            try:
                offer_element = question_element.find_element(By.CSS_SELECTOR, '[data-test="interview-offer"]')
                metadata['offer_status'] = self._clean_text(offer_element.text)
            except NoSuchElementException:
                metadata['offer_status'] = ""

            return {
                'question': question_text,
                'answer': answer_text,
                'metadata': metadata
            }
        except Exception as e:
            logger.error(f"Error extracting question data: {str(e)}")
            return None

    def _build_url(self, company_name: str, role: Optional[str] = None) -> str:
        """Build the Glassdoor URL for the company and role."""
        # Format company name for URL
        company_url = company_name.lower().replace(' ', '-')
        
        # Base URL for company interviews
        base_url = f"https://www.glassdoor.com/Interview/{company_url}-interview-questions-SRCH_IL.0,{len(company_name)}_{company_url}.htm"
        
        if role:
            # Format role for URL
            role_url = role.lower().replace(' ', '-')
            # Add role to the URL path
            base_url = f"https://www.glassdoor.com/Interview/{company_url}-{role_url}-interview-questions-SRCH_IL.0,{len(company_name)}_{company_url}.htm"
        
        return base_url

    def _handle_cookie_consent(self, driver):
        """Handle cookie consent popup if it appears."""
        try:
            cookie_button = driver.find_element(By.ID, "onetrust-accept-btn-handler")
            cookie_button.click()
            time.sleep(1)  # Wait for the popup to disappear
        except NoSuchElementException:
            pass  # No cookie consent popup found

    def _handle_sign_in_prompt(self, driver):
        """Handle sign-in prompt if it appears."""
        try:
            close_button = driver.find_element(By.CSS_SELECTOR, '[data-test="modal-close"]')
            close_button.click()
            time.sleep(1)  # Wait for the popup to disappear
        except NoSuchElementException:
            pass  # No sign-in prompt found

    def get_interview_questions(self, company_name: str, role: Optional[str] = None, max_pages: int = 3) -> List[Dict]:
        """
        Scrape interview questions for a given company and role from Glassdoor.
        
        Args:
            company_name (str): Name of the company to search for
            role (str, optional): Specific role to filter questions for
            max_pages (int): Maximum number of pages to scrape (default: 3)
            
        Returns:
            List[Dict]: List of interview questions with their answers and metadata
        """
        driver = None
        questions = []
        
        try:
            driver = webdriver.Chrome(options=self.options)
            wait = WebDriverWait(driver, 10)
            
            base_url = self._build_url(company_name, role)
            logger.info(f"Scraping interview questions for {company_name}" + (f" - Role: {role}" if role else ""))
            
            for page in range(1, max_pages + 1):
                url = f"{base_url}?p={page}" if page > 1 else base_url
                driver.get(url)
                
                # Handle popups
                self._handle_cookie_consent(driver)
                self._handle_sign_in_prompt(driver)
                
                # Wait for questions to load
                try:
                    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '[data-test="interview-question"]')))
                except TimeoutException:
                    logger.warning(f"No questions found on page {page}")
                    break
                
                # Get all question elements
                question_elements = driver.find_elements(By.CSS_SELECTOR, '[data-test="interview-question"]')
                
                for element in question_elements:
                    question_data = self._extract_question_data(element)
                    if question_data:
                        # If role is specified, only include questions that match the role
                        if role and question_data['metadata'].get('role'):
                            if role.lower() not in question_data['metadata']['role'].lower():
                                continue
                        questions.append(question_data)
                
                # Add a small delay between pages
                time.sleep(2)
                
            logger.info(f"Successfully scraped {len(questions)} questions for {company_name}" + (f" - Role: {role}" if role else ""))
            return questions
            
        except Exception as e:
            logger.error(f"Error scraping Glassdoor: {str(e)}")
            return []
            
        finally:
            if driver:
                driver.quit()

def get_company_interview_questions(company_name: str, role: Optional[str] = None, max_pages: int = 3) -> List[Dict]:
    """
    Convenience function to get interview questions for a company and role.
    
    Args:
        company_name (str): Name of the company to search for
        role (str, optional): Specific role to filter questions for
        max_pages (int): Maximum number of pages to scrape (default: 3)
        
    Returns:
        List[Dict]: List of interview questions with their answers and metadata
    """
    scraper = GlassdoorScraper()
    return scraper.get_interview_questions(company_name, role, max_pages)

# Example usage
if __name__ == "__main__":
    company = "Google"
    role = "Software Engineer"
    role_questions = get_company_interview_questions(company, role)
    print(f"\nFound {len(role_questions)} questions for {company} - {role}")
    
    # Print first 3 questions from role-specific results
    for q in role_questions[:3]:
        print("\nQuestion:", q['question'])
        print("Answer:", q['answer'])
        print("Metadata:", q['metadata']) 