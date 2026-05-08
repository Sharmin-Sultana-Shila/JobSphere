import time
from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from users.models import User, JobSeeker, Recruiter, Company
from recruitments.models import JobPost, Application
from updates.models import ChatRoom, ChatRoomMember


class BaseSeleniumTest(LiveServerTestCase):
    """
    Base class for all Selenium tests.
    Sets up Chrome browser and creates test data.
    """

    @classmethod
    def setUpClass(cls):
        """Start Chrome browser before all tests."""
        super().setUpClass()
        options = webdriver.ChromeOptions()
        # Remove the line below if you want to SEE the browser during tests
        # options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--window-size=1920,1080')
        cls.browser = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )
        cls.browser.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        """Close browser after all tests."""
        cls.browser.quit()
        super().tearDownClass()

    def setUp(self):
        """Create test users and data before each test."""
        # Create seeker user
        self.seeker_user = User.objects.create_user(
            email='seeker@test.com',
            name='Test Seeker',
            user_type='seeker',
            password='testpass123'
        )
        self.seeker = JobSeeker.objects.create(
            user=self.seeker_user,
            bio='I am a developer',
            cgpa=3.75,
            experience_years=2,
            education='BSc in CSE',
            skills_text='Python, Django, JavaScript',
            location='Dhaka',
            career_goals='Become a senior developer'
        )

        # Create recruiter user
        self.recruiter_user = User.objects.create_user(
            email='recruiter@test.com',
            name='Test Recruiter',
            user_type='recruiter',
            password='testpass123'
        )
        self.company = Company.objects.create(
            name='Tech Corp',
            location='Dhaka, Bangladesh'
        )
        self.recruiter = Recruiter.objects.create(
            user=self.recruiter_user,
            company=self.company,
            designation='HR Manager',
            dept='Human Resources'
        )

        # Create a job post
        self.job_post = JobPost.objects.create(
            poster=self.recruiter_user,
            poster_type='recruiter',
            title='Senior Django Developer',
            description='We need an experienced Django developer for our team.',
            location='Dhaka',
            job_type='fullTime',
            salary=80000,
            number_of_available_seats=3,
            required_experience=2,
            skills_text='Python, Django, SQL',
            status='active'
        )

        # Create industry chat rooms
        ChatRoom.objects.get_or_create(
            name='Software Engineering',
            defaults={'description': 'Tech discussion', 'room_type': 'software', 'member_count': 0}
        )

    def login_as_seeker(self):
        """Helper: Log in as the test seeker."""
        self.browser.get(f'{self.live_server_url}/users/login/')
        email_input = self.browser.find_element(By.NAME, 'email')
        password_input = self.browser.find_element(By.NAME, 'password')
        email_input.clear()
        email_input.send_keys('seeker@test.com')
        password_input.clear()
        password_input.send_keys('testpass123')
        self.browser.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
        time.sleep(1)

    def login_as_recruiter(self):
        """Helper: Log in as the test recruiter."""
        self.browser.get(f'{self.live_server_url}/users/login/')
        email_input = self.browser.find_element(By.NAME, 'email')
        password_input = self.browser.find_element(By.NAME, 'password')
        email_input.clear()
        email_input.send_keys('recruiter@test.com')
        password_input.clear()
        password_input.send_keys('testpass123')
        self.browser.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
        time.sleep(1)

