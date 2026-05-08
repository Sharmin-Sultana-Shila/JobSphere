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

# ============================================================
# TEST 1: REGISTRATION
# ============================================================
class RegistrationTest(BaseSeleniumTest):
    """Test user registration flow in the browser."""

    def test_register_page_loads(self):
        """Test that the register page opens successfully."""
        self.browser.get(f'{self.live_server_url}/users/register/')
        heading = self.browser.find_element(By.TAG_NAME, 'h2')
        self.assertEqual(heading.text, 'Create Account')

    def test_register_seeker_successfully(self):
        """Test complete seeker registration flow."""
        self.browser.get(f'{self.live_server_url}/users/register/')

        # Select seeker role
        seeker_radio = self.browser.find_element(By.ID, 'role-seeker')
        seeker_radio.click()

        # Fill form
        self.browser.find_element(By.NAME, 'name').send_keys('New Seeker')
        self.browser.find_element(By.NAME, 'email').send_keys('newseeker@test.com')
        self.browser.find_element(By.NAME, 'password').send_keys('newpass123')
        self.browser.find_element(By.NAME, 'confirm_password').send_keys('newpass123')

        # Submit
        self.browser.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
        time.sleep(1)

        # Should redirect to seeker onboarding
        self.assertIn('onboarding/seeker', self.browser.current_url)

    def test_register_recruiter_successfully(self):
        """Test complete recruiter registration flow."""
        self.browser.get(f'{self.live_server_url}/users/register/')

        # Select recruiter role
        recruiter_radio = self.browser.find_element(By.ID, 'role-recruiter')
        recruiter_radio.click()

        # Fill form
        self.browser.find_element(By.NAME, 'name').send_keys('New Recruiter')
        self.browser.find_element(By.NAME, 'email').send_keys('newrecruiter@test.com')
        self.browser.find_element(By.NAME, 'password').send_keys('newpass123')
        self.browser.find_element(By.NAME, 'confirm_password').send_keys('newpass123')

        # Submit
        self.browser.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
        time.sleep(1)

        # Should redirect to recruiter onboarding
        self.assertIn('onboarding/recruiter', self.browser.current_url)

    def test_register_password_mismatch_shows_error(self):
        """Test that mismatched passwords show error on register page."""
        self.browser.get(f'{self.live_server_url}/users/register/')

        self.browser.find_element(By.NAME, 'name').send_keys('Bad User')
        self.browser.find_element(By.NAME, 'email').send_keys('bad@test.com')
        self.browser.find_element(By.NAME, 'password').send_keys('pass123')
        self.browser.find_element(By.NAME, 'confirm_password').send_keys('different456')

        self.browser.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
        time.sleep(1)

        # Should stay on register page with error
        self.assertIn('register', self.browser.current_url)
        error_msg = self.browser.find_element(By.CSS_SELECTOR, '.messages .error')
        self.assertIn('Passwords do not match', error_msg.text)

    def test_register_duplicate_email_shows_error(self):
        """Test that registering with existing email shows error."""
        self.browser.get(f'{self.live_server_url}/users/register/')

        self.browser.find_element(By.NAME, 'name').send_keys('Duplicate')
        self.browser.find_element(By.NAME, 'email').send_keys('seeker@test.com')
        self.browser.find_element(By.NAME, 'password').send_keys('testpass123')
        self.browser.find_element(By.NAME, 'confirm_password').send_keys('testpass123')

        self.browser.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
        time.sleep(1)

        # Should stay on register page
        self.assertIn('register', self.browser.current_url)


# ============================================================
# TEST 2: LOGIN & LOGOUT
# ============================================================
class LoginLogoutTest(BaseSeleniumTest):
    """Test login and logout flow."""

    def test_login_page_loads(self):
        """Test that login page opens successfully."""
        self.browser.get(f'{self.live_server_url}/users/login/')
        heading = self.browser.find_element(By.TAG_NAME, 'h2')
        self.assertEqual(heading.text, 'Welcome Back')

    def test_seeker_login_redirects_to_feed(self):
        """Test seeker login goes to feed page."""
        self.login_as_seeker()
        self.assertIn('feed', self.browser.current_url)

    def test_recruiter_login_redirects_to_feed(self):
        """Test recruiter login goes to feed page."""
        self.login_as_recruiter()
        self.assertIn('feed', self.browser.current_url)

    def test_invalid_login_shows_error(self):
        """Test wrong password shows error."""
        self.browser.get(f'{self.live_server_url}/users/login/')
        self.browser.find_element(By.NAME, 'email').send_keys('seeker@test.com')
        self.browser.find_element(By.NAME, 'password').send_keys('wrongpassword')
        self.browser.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
        time.sleep(1)

        # Should stay on login page
        self.assertIn('login', self.browser.current_url)

    def test_logout_redirects_to_login(self):
        """Test logout sends user back to login page."""
        self.login_as_seeker()
        self.browser.find_element(By.CSS_SELECTOR, '.btn-logout').click()
        time.sleep(1)
        self.assertIn('login', self.browser.current_url)
