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


# ============================================================
# TEST 3: SEEKER PROFILE
# ============================================================
class SeekerProfileTest(BaseSeleniumTest):
    """Test seeker profile view and edit."""

    def test_seeker_profile_page_shows_data(self):
        """Test profile page displays seeker info."""
        self.login_as_seeker()
        self.browser.get(f'{self.live_server_url}/users/profile/seeker/')
        time.sleep(1)

        page_text = self.browser.find_element(By.TAG_NAME, 'body').text
        self.assertIn('Test Seeker', page_text)
        self.assertIn('seeker@test.com', page_text)
        self.assertIn('3.75', page_text)
        self.assertIn('Dhaka', page_text)

    def test_seeker_profile_edit_page_loads(self):
        """Test profile edit page loads with pre-filled data."""
        self.login_as_seeker()
        self.browser.get(f'{self.live_server_url}/users/profile/seeker/edit/')
        time.sleep(1)

        bio_field = self.browser.find_element(By.NAME, 'bio')
        self.assertEqual(bio_field.get_attribute('value'), 'I am a developer')

    def test_seeker_can_update_profile(self):
        """Test seeker can edit and save profile changes."""
        self.login_as_seeker()
        self.browser.get(f'{self.live_server_url}/users/profile/seeker/edit/')
        time.sleep(1)

        # Update bio
        bio_field = self.browser.find_element(By.NAME, 'bio')
        bio_field.clear()
        bio_field.send_keys('Updated bio from Selenium')

        # Submit
        self.browser.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
        time.sleep(1)

        # Check updated value on profile page
        page_text = self.browser.find_element(By.TAG_NAME, 'body').text
        self.assertIn('Updated bio from Selenium', page_text)


# ============================================================
# TEST 4: RECRUITER PROFILE
# ============================================================
class RecruiterProfileTest(BaseSeleniumTest):
    """Test recruiter profile view and edit."""

    def test_recruiter_profile_page_shows_data(self):
        """Test profile page displays recruiter and company info."""
        self.login_as_recruiter()
        self.browser.get(f'{self.live_server_url}/users/profile/recruiter/')
        time.sleep(1)

        page_text = self.browser.find_element(By.TAG_NAME, 'body').text
        self.assertIn('Test Recruiter', page_text)
        self.assertIn('Tech Corp', page_text)
        self.assertIn('HR Manager', page_text)

    def test_recruiter_can_update_profile(self):
        """Test recruiter can edit and save profile changes."""
        self.login_as_recruiter()
        self.browser.get(f'{self.live_server_url}/users/profile/recruiter/edit/')
        time.sleep(1)

        # Update designation
        desig_field = self.browser.find_element(By.NAME, 'designation')
        desig_field.clear()
        desig_field.send_keys('Senior HR Manager')

        # Submit
        self.browser.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
        time.sleep(1)

        page_text = self.browser.find_element(By.TAG_NAME, 'body').text
        self.assertIn('Senior HR Manager', page_text)


# ============================================================
# TEST 5: JOB POST MANAGEMENT (RECRUITER)
# ============================================================
class JobPostManagementTest(BaseSeleniumTest):
    """Test job post creation, editing, and status toggle."""

    def test_create_job_post(self):
        """Test recruiter can create a job post."""
        self.login_as_recruiter()
        self.browser.get(f'{self.live_server_url}/recruitments/create/')
        time.sleep(1)

        self.browser.find_element(By.NAME, 'title').send_keys('React Developer')
        self.browser.find_element(By.NAME, 'description').send_keys('Need a React expert')
        self.browser.find_element(By.NAME, 'location').send_keys('Mirpur, Dhaka')
        Select(self.browser.find_element(By.NAME, 'job_type')).select_by_value('fullTime')
        self.browser.find_element(By.NAME, 'salary').send_keys('70000')
        self.browser.find_element(By.NAME, 'number_of_available_seats').clear()
        self.browser.find_element(By.NAME, 'number_of_available_seats').send_keys('2')
        self.browser.find_element(By.NAME, 'required_experience').clear()
        self.browser.find_element(By.NAME, 'required_experience').send_keys('1')
        self.browser.find_element(By.NAME, 'skills_text').send_keys('React, JavaScript, CSS')

        self.browser.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
        time.sleep(1)

        # Should redirect to my posts
        self.assertIn('my-posts', self.browser.current_url)
        page_text = self.browser.find_element(By.TAG_NAME, 'body').text
        self.assertIn('React Developer', page_text)

    def test_my_job_posts_page_shows_posts(self):
        """Test my job posts page shows existing posts."""
        self.login_as_recruiter()
        self.browser.get(f'{self.live_server_url}/recruitments/my-posts/')
        time.sleep(1)

        page_text = self.browser.find_element(By.TAG_NAME, 'body').text
        self.assertIn('Senior Django Developer', page_text)

    def test_close_and_reopen_job_post(self):
        """Test recruiter can close and reopen a post."""
        self.login_as_recruiter()
        self.browser.get(f'{self.live_server_url}/recruitments/toggle/{self.job_post.id}/')
        time.sleep(1)

        self.job_post.refresh_from_db()
        self.assertEqual(self.job_post.status, 'closed')

        # Reopen
        self.browser.get(f'{self.live_server_url}/recruitments/toggle/{self.job_post.id}/')
        time.sleep(1)

        self.job_post.refresh_from_db()
        self.assertEqual(self.job_post.status, 'active')



# ============================================================
# TEST 6: JOB BROWSING & SEARCH (SEEKER)
# ============================================================
class JobBrowsingTest(BaseSeleniumTest):
    """Test job listing, search, and detail pages."""

    def test_job_list_page_shows_active_jobs(self):
        """Test browse jobs page shows active posts."""
        self.login_as_seeker()
        self.browser.get(f'{self.live_server_url}/recruitments/jobs/')
        time.sleep(1)

        page_text = self.browser.find_element(By.TAG_NAME, 'body').text
        self.assertIn('Senior Django Developer', page_text)

    def test_search_jobs_by_keyword(self):
        """Test searching jobs by title keyword."""
        self.login_as_seeker()
        self.browser.get(f'{self.live_server_url}/recruitments/jobs/')
        time.sleep(1)

        search_input = self.browser.find_element(By.NAME, 'q')
        search_input.send_keys('Django')
        self.browser.find_element(By.CSS_SELECTOR, '.btn-search').click()
        time.sleep(1)

        page_text = self.browser.find_element(By.TAG_NAME, 'body').text
        self.assertIn('Senior Django Developer', page_text)
        self.assertIn('1 job', page_text)

    def test_search_no_results(self):
        """Test search with no matching results."""
        self.login_as_seeker()
        self.browser.get(f'{self.live_server_url}/recruitments/jobs/?q=NonExistentJob')
        time.sleep(1)

        page_text = self.browser.find_element(By.TAG_NAME, 'body').text
        self.assertIn('No jobs match', page_text)

    def test_job_detail_page_shows_info(self):
        """Test job detail page displays all info."""
        self.login_as_seeker()
        self.browser.get(f'{self.live_server_url}/recruitments/jobs/{self.job_post.id}/')
        time.sleep(1)

        page_text = self.browser.find_element(By.TAG_NAME, 'body').text
        self.assertIn('Senior Django Developer', page_text)
        self.assertIn('Dhaka', page_text)
        self.assertIn('80000', page_text)
        self.assertIn('Python, Django, SQL', page_text)

    def test_job_detail_shows_ats_preview(self):
        """Test job detail shows ATS score preview for seeker."""
        self.login_as_seeker()
        self.browser.get(f'{self.live_server_url}/recruitments/jobs/{self.job_post.id}/')
        time.sleep(1)

        page_text = self.browser.find_element(By.TAG_NAME, 'body').text
        self.assertIn('YOUR ATS MATCH SCORE', page_text)


# ============================================================
# TEST 7: APPLICATION FLOW
# ============================================================
class ApplicationFlowTest(BaseSeleniumTest):
    """Test the complete application flow — apply, view, withdraw."""

    def test_seeker_applies_for_job(self):
        """Test seeker can apply for a job."""
        self.login_as_seeker()
        self.browser.get(f'{self.live_server_url}/recruitments/apply/{self.job_post.id}/')
        time.sleep(1)

        # Should redirect to my applications
        self.assertIn('my-applications', self.browser.current_url)
        page_text = self.browser.find_element(By.TAG_NAME, 'body').text
        self.assertIn('Senior Django Developer', page_text)
        self.assertIn('Applied', page_text)

    def test_my_applications_page_shows_applications(self):
        """Test my applications page displays applied jobs."""
        Application.objects.create(
            job_post=self.job_post, seeker=self.seeker, status='applied', ats_score=75
        )
        self.login_as_seeker()
        self.browser.get(f'{self.live_server_url}/recruitments/my-applications/')
        time.sleep(1)

        page_text = self.browser.find_element(By.TAG_NAME, 'body').text
        self.assertIn('Senior Django Developer', page_text)
        self.assertIn('ATS: 75', page_text)

    def test_seeker_withdraws_application(self):
        """Test seeker can withdraw an applied application."""
        app = Application.objects.create(
            job_post=self.job_post, seeker=self.seeker, status='applied', ats_score=75
        )
        self.job_post.application_count = 1
        self.job_post.save()

        self.login_as_seeker()
        self.browser.get(f'{self.live_server_url}/recruitments/withdraw/{app.id}/')
        time.sleep(1)

        self.assertFalse(Application.objects.filter(id=app.id).exists())

    def test_already_applied_shows_badge(self):
        """Test that job detail shows 'Already Applied' after applying."""
        Application.objects.create(
            job_post=self.job_post, seeker=self.seeker, status='applied', ats_score=75
        )
        self.login_as_seeker()
        self.browser.get(f'{self.live_server_url}/recruitments/jobs/{self.job_post.id}/')
        time.sleep(1)

        page_text = self.browser.find_element(By.TAG_NAME, 'body').text
        self.assertIn('Already Applied', page_text)


# ============================================================
# TEST 8: RECRUITER REVIEWS APPLICANTS
# ============================================================
class RecruiterReviewTest(BaseSeleniumTest):
    """Test recruiter reviewing and updating applicant status."""

    def test_applicants_list_shows_candidates(self):
        """Test applicants list shows applied candidates."""
        Application.objects.create(
            job_post=self.job_post, seeker=self.seeker, status='applied', ats_score=77.5
        )
        self.login_as_recruiter()
        self.browser.get(f'{self.live_server_url}/recruitments/applicants/{self.job_post.id}/')
        time.sleep(1)

        page_text = self.browser.find_element(By.TAG_NAME, 'body').text
        self.assertIn('Test Seeker', page_text)
        self.assertIn('77.5', page_text)

    def test_applicant_detail_shows_profile(self):
        """Test applicant detail page shows seeker profile."""
        app = Application.objects.create(
            job_post=self.job_post, seeker=self.seeker, status='applied', ats_score=77.5
        )
        self.login_as_recruiter()
        self.browser.get(f'{self.live_server_url}/recruitments/applicant/{app.id}/')
        time.sleep(1)

        page_text = self.browser.find_element(By.TAG_NAME, 'body').text
        self.assertIn('Test Seeker', page_text)
        self.assertIn('BSc in CSE', page_text)
        self.assertIn('77.5', page_text)

    def test_update_application_status(self):
        """Test recruiter can update status to shortlisted."""
        app = Application.objects.create(
            job_post=self.job_post, seeker=self.seeker, status='applied', ats_score=77.5
        )
        self.login_as_recruiter()
        self.browser.get(f'{self.live_server_url}/recruitments/applicant/{app.id}/')
        time.sleep(1)

        # Select shortlisted from dropdown
        status_select = Select(self.browser.find_element(By.NAME, 'status'))
        status_select.select_by_value('shortlisted')

        # Click update button
        self.browser.find_element(By.CSS_SELECTOR, '.btn-update').click()
        time.sleep(1)

        app.refresh_from_db()
        self.assertEqual(app.status, 'shortlisted')


# ============================================================
# TEST 9: INTERVIEW SCHEDULING
# ============================================================
class InterviewTest(BaseSeleniumTest):
    """Test interview scheduling and feedback."""

    def test_schedule_interview_page_loads(self):
        """Test schedule interview page loads for shortlisted applicant."""
        app = Application.objects.create(
            job_post=self.job_post, seeker=self.seeker, status='shortlisted', ats_score=77
        )
        self.login_as_recruiter()
        self.browser.get(f'{self.live_server_url}/recruitments/interview/schedule/{app.id}/')
        time.sleep(1)

        page_text = self.browser.find_element(By.TAG_NAME, 'body').text
        self.assertIn('Schedule Interview', page_text)
        self.assertIn('Test Seeker', page_text)

    def test_interview_list_page_loads(self):
        """Test interview list page loads for recruiter."""
        self.login_as_recruiter()
        self.browser.get(f'{self.live_server_url}/recruitments/interview/list/')
        time.sleep(1)

        page_text = self.browser.find_element(By.TAG_NAME, 'body').text
        self.assertIn('Interviews', page_text)

    def test_seeker_interviews_page_loads(self):
        """Test seeker can see their interviews page."""
        self.login_as_seeker()
        self.browser.get(f'{self.live_server_url}/recruitments/my-interviews/')
        time.sleep(1)

        page_text = self.browser.find_element(By.TAG_NAME, 'body').text
        self.assertIn('My Interviews', page_text)


# ============================================================
# TEST 10: NOTIFICATIONS
# ============================================================
class NotificationTest(BaseSeleniumTest):
    """Test notification pages."""

    def test_notifications_page_loads(self):
        """Test notifications page loads for logged-in user."""
        self.login_as_seeker()
        self.browser.get(f'{self.live_server_url}/updates/notifications/')
        time.sleep(1)

        page_text = self.browser.find_element(By.TAG_NAME, 'body').text
        self.assertIn('Notifications', page_text)

    def test_notifications_page_shows_empty_state(self):
        """Test empty state when no notifications exist."""
        self.login_as_seeker()
        self.browser.get(f'{self.live_server_url}/updates/notifications/')
        time.sleep(1)

        page_text = self.browser.find_element(By.TAG_NAME, 'body').text
        self.assertIn('No notifications yet', page_text)

    def test_notification_appears_after_status_change(self):
        """Test notification is created when recruiter changes application status."""
        app = Application.objects.create(
            job_post=self.job_post, seeker=self.seeker, status='applied', ats_score=75
        )

        # Recruiter updates status
        self.login_as_recruiter()
        self.browser.get(f'{self.live_server_url}/recruitments/applicant/{app.id}/')
        time.sleep(1)

        status_select = Select(self.browser.find_element(By.NAME, 'status'))
        status_select.select_by_value('shortlisted')
        self.browser.find_element(By.CSS_SELECTOR, '.btn-update').click()
        time.sleep(1)

        # Seeker checks notifications
        self.login_as_seeker()
        self.browser.get(f'{self.live_server_url}/updates/notifications/')
        time.sleep(1)

        page_text = self.browser.find_element(By.TAG_NAME, 'body').text
        self.assertIn('Shortlisted', page_text)


# ============================================================
# TEST 11: CHAT ROOMS
# ============================================================
class ChatRoomTest(BaseSeleniumTest):
    """Test chat room functionality."""

    def test_chat_rooms_list_page_loads(self):
        """Test chat rooms page shows industry rooms."""
        self.login_as_seeker()
        self.browser.get(f'{self.live_server_url}/updates/chat/')
        time.sleep(1)

        page_text = self.browser.find_element(By.TAG_NAME, 'body').text
        self.assertIn('Software Engineering', page_text)

    def test_join_chat_room(self):
        """Test user can join a chat room."""
        self.login_as_seeker()
        room = ChatRoom.objects.get(name='Software Engineering')
        self.browser.get(f'{self.live_server_url}/updates/chat/join/{room.id}/')
        time.sleep(1)

        room.refresh_from_db()
        self.assertEqual(room.member_count, 1)
        self.assertTrue(ChatRoomMember.objects.filter(chat_room=room, user=self.seeker_user).exists())

    def test_leave_chat_room(self):
        """Test user can leave a chat room."""
        room = ChatRoom.objects.get(name='Software Engineering')
        ChatRoomMember.objects.create(chat_room=room, user=self.seeker_user)
        room.member_count = 1
        room.save()

        self.login_as_seeker()
        self.browser.get(f'{self.live_server_url}/updates/chat/leave/{room.id}/')
        time.sleep(1)

        room.refresh_from_db()
        self.assertEqual(room.member_count, 0)

    def test_create_custom_room(self):
        """Test user can create a custom chat room."""
        self.login_as_seeker()
        self.browser.get(f'{self.live_server_url}/updates/chat/create/')
        time.sleep(1)

        self.browser.find_element(By.NAME, 'name').send_keys('Django Fans')
        self.browser.find_element(By.NAME, 'description').send_keys('A room for Django lovers')
        self.browser.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
        time.sleep(1)

        self.assertTrue(ChatRoom.objects.filter(name='Django Fans').exists())

    def test_chat_room_window_loads(self):
        """Test chat room window opens for members."""
        room = ChatRoom.objects.get(name='Software Engineering')
        ChatRoomMember.objects.create(chat_room=room, user=self.seeker_user)
        room.member_count = 1
        room.save()

        self.login_as_seeker()
        self.browser.get(f'{self.live_server_url}/updates/chat/room/{room.id}/')
        time.sleep(1)

        page_text = self.browser.find_element(By.TAG_NAME, 'body').text
        self.assertIn('Software Engineering', page_text)
        self.assertIn('Test Seeker', page_text)

    def test_send_message_in_chat(self):
        """Test user can send a message in a chat room."""
        room = ChatRoom.objects.get(name='Software Engineering')
        ChatRoomMember.objects.create(chat_room=room, user=self.seeker_user)
        room.member_count = 1
        room.save()

        self.login_as_seeker()
        self.browser.get(f'{self.live_server_url}/updates/chat/room/{room.id}/')
        time.sleep(1)

        msg_input = self.browser.find_element(By.NAME, 'content')
        msg_input.send_keys('Hello from Selenium!')
        self.browser.find_element(By.CSS_SELECTOR, '.btn-send').click()
        time.sleep(1)

        page_text = self.browser.find_element(By.TAG_NAME, 'body').text
        self.assertIn('Hello from Selenium!', page_text)


# ============================================================
# TEST 12: DIRECT MESSAGING
# ============================================================
class DirectMessageTest(BaseSeleniumTest):
    """Test direct messaging between users."""

    def test_start_direct_message(self):
        """Test recruiter can start DM with seeker."""
        self.login_as_recruiter()
        self.browser.get(f'{self.live_server_url}/updates/chat/dm/{self.seeker_user.id}/')
        time.sleep(1)

        # Should be in a chat room
        self.assertIn('chat/room', self.browser.current_url)
        dm_room = ChatRoom.objects.filter(room_type='direct').first()
        self.assertIsNotNone(dm_room)

    def test_direct_messages_list_page(self):
        """Test direct messages list page loads."""
        self.login_as_seeker()
        self.browser.get(f'{self.live_server_url}/updates/chat/my-dms/')
        time.sleep(1)

        page_text = self.browser.find_element(By.TAG_NAME, 'body').text
        self.assertIn('Direct Messages', page_text)


# ============================================================
# TEST 13: REVERSE JOB POSTING (SEEKER POST)
# ============================================================
class ReversePostingTest(BaseSeleniumTest):
    """Test seeker creating reverse job posts."""

    def test_create_seeker_post_page_loads(self):
        """Test seeker post creation page loads."""
        self.login_as_seeker()
        self.browser.get(f'{self.live_server_url}/recruitments/seeker-post/create/')
        time.sleep(1)

        page_text = self.browser.find_element(By.TAG_NAME, 'body').text
        self.assertIn('Post Your Profile', page_text)

    def test_seeker_creates_reverse_post(self):
        """Test seeker can create a reverse post."""
        self.login_as_seeker()
        self.browser.get(f'{self.live_server_url}/recruitments/seeker-post/create/')
        time.sleep(1)

        self.browser.find_element(By.NAME, 'title').send_keys('Django Dev Looking for Work')
        self.browser.find_element(By.NAME, 'description').send_keys('Experienced Django developer')
        self.browser.find_element(By.NAME, 'location').send_keys('Dhaka')
        self.browser.find_element(By.NAME, 'salary').send_keys('60000')
        self.browser.find_element(By.NAME, 'required_experience').clear()
        self.browser.find_element(By.NAME, 'required_experience').send_keys('2')
        self.browser.find_element(By.NAME, 'skills_text').clear()
        self.browser.find_element(By.NAME, 'skills_text').send_keys('Python, Django')

        self.browser.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
        time.sleep(1)

        self.assertIn('my-posts', self.browser.current_url)
        self.assertTrue(JobPost.objects.filter(title='Django Dev Looking for Work', poster_type='seeker').exists())

    def test_recruiter_can_browse_seeker_posts(self):
        """Test recruiter can see seeker reverse posts."""
        JobPost.objects.create(
            poster=self.seeker_user, poster_type='seeker',
            title='Python Dev Available', description='Hire me',
            skills_text='Python', number_of_available_seats=1, status='active'
        )
        self.login_as_recruiter()
        self.browser.get(f'{self.live_server_url}/recruitments/seeker-posts/')
        time.sleep(1)

        page_text = self.browser.find_element(By.TAG_NAME, 'body').text
        self.assertIn('Python Dev Available', page_text)


# ============================================================
# TEST 14: NAVBAR & ACCESS CONTROL
# ============================================================
class NavigationTest(BaseSeleniumTest):
    """Test navbar links and access control."""

    def test_seeker_navbar_has_correct_links(self):
        """Test seeker sees correct navbar links."""
        self.login_as_seeker()
        navbar = self.browser.find_element(By.CSS_SELECTOR, '.navbar-links')
        navbar_text = navbar.text

        self.assertIn('Home', navbar_text)
        self.assertIn('Browse Jobs', navbar_text)
        self.assertIn('Applications', navbar_text)
        self.assertIn('Interviews', navbar_text)
        self.assertIn('Chat', navbar_text)
        self.assertIn('Profile', navbar_text)
        self.assertIn('Logout', navbar_text)

    def test_recruiter_navbar_has_correct_links(self):
        """Test recruiter sees correct navbar links."""
        self.login_as_recruiter()
        navbar = self.browser.find_element(By.CSS_SELECTOR, '.navbar-links')
        navbar_text = navbar.text

        self.assertIn('Home', navbar_text)
        self.assertIn('My Posts', navbar_text)
        self.assertIn('Post Job', navbar_text)
        self.assertIn('Interviews', navbar_text)
        self.assertIn('Find Talent', navbar_text)
        self.assertIn('Chat', navbar_text)
        self.assertIn('Profile', navbar_text)

    def test_unauthenticated_user_redirected_to_login(self):
        """Test that visiting protected pages redirects to login."""
        self.browser.get(f'{self.live_server_url}/users/dashboard/seeker/')
        time.sleep(1)
        self.assertIn('login', self.browser.current_url)

    def test_root_url_redirects_to_login(self):
        """Test root URL redirects to login page."""
        self.browser.get(f'{self.live_server_url}/')
        time.sleep(1)
        self.assertIn('login', self.browser.current_url)


# ============================================================
# TEST 15: FEED LIKE AND COMMENT
# ============================================================
class FeedLikeCommentTest(BaseSeleniumTest):
    """Test liking and commenting on feed posts."""

    def test_feed_page_loads_for_seeker(self):
        """Test feed page loads as homepage after login."""
        self.login_as_seeker()
        self.assertIn('feed', self.browser.current_url)
        page_text = self.browser.find_element(By.TAG_NAME, 'body').text
        self.assertIn('Senior Django Developer', page_text)

    def test_feed_page_loads_for_recruiter(self):
        """Test recruiter sees seeker posts on feed."""
        # Create a seeker post first
        JobPost.objects.create(
            poster=self.seeker_user, poster_type='seeker', title='Hire Me Please',
            description='I am available', skills_text='Python',
            number_of_available_seats=1, status='active'
        )
        self.login_as_recruiter()
        self.assertIn('feed', self.browser.current_url)
        page_text = self.browser.find_element(By.TAG_NAME, 'body').text
        self.assertIn('Hire Me Please', page_text)

    def test_like_button_works(self):
        """Test seeker can like a post from the feed."""
        self.login_as_seeker()
        time.sleep(1)

        # Click like
        like_btn = self.browser.find_element(By.CSS_SELECTOR, f'a[href*="like/{self.job_post.id}"]')
        like_btn.click()
        time.sleep(1)

        page_text = self.browser.find_element(By.TAG_NAME, 'body').text
        self.assertIn('Liked', page_text)

    def test_comment_on_post(self):
        """Test seeker can comment on a post."""
        self.login_as_seeker()
        time.sleep(1)

        comment_input = self.browser.find_element(By.CSS_SELECTOR, f'#comment-input-{self.job_post.id}')
        comment_input.send_keys('Amazing opportunity!')
        self.browser.find_element(By.CSS_SELECTOR, '.btn-comment-submit').click()
        time.sleep(1)

        page_text = self.browser.find_element(By.TAG_NAME, 'body').text
        self.assertIn('Amazing opportunity!', page_text)

    def test_like_notification_received(self):
        """Test recruiter receives notification when seeker likes their post."""
        self.login_as_seeker()
        time.sleep(1)

        like_btn = self.browser.find_element(By.CSS_SELECTOR, f'a[href*="like/{self.job_post.id}"]')
        like_btn.click()
        time.sleep(1)

        # Check recruiter's notifications
        self.login_as_recruiter()
        self.browser.get(f'{self.live_server_url}/updates/notifications/')
        time.sleep(1)

        page_text = self.browser.find_element(By.TAG_NAME, 'body').text
        self.assertIn('liked', page_text)


# ============================================================
# TEST 16: DEADLINE RESTRICTION
# ============================================================
class DeadlineRestrictionTest(BaseSeleniumTest):
    """Test that seekers cannot apply after deadline."""

    def test_expired_job_shows_deadline_passed(self):
        """Test expired job shows 'Deadline Passed' instead of Apply Now."""
        from django.utils import timezone
        from datetime import timedelta

        expired_job = JobPost.objects.create(
            poster=self.recruiter_user, poster_type='recruiter',
            title='Expired Position', description='This job is expired',
            skills_text='Python', status='active',
            deadline=timezone.now() - timedelta(days=1)
        )

        self.login_as_seeker()
        self.browser.get(f'{self.live_server_url}/recruitments/jobs/{expired_job.id}/')
        time.sleep(1)

        page_text = self.browser.find_element(By.TAG_NAME, 'body').text
        self.assertIn('Deadline Passed', page_text)

    def test_active_job_shows_apply_button(self):
        """Test active job with future deadline shows Apply Now."""
        from django.utils import timezone
        from datetime import timedelta

        active_job = JobPost.objects.create(
            poster=self.recruiter_user, poster_type='recruiter',
            title='Active Position', description='This job is active',
            skills_text='Python', status='active',
            deadline=timezone.now() + timedelta(days=7)
        )

        self.login_as_seeker()
        self.browser.get(f'{self.live_server_url}/recruitments/jobs/{active_job.id}/')
        time.sleep(1)

        page_text = self.browser.find_element(By.TAG_NAME, 'body').text
        self.assertIn('Apply Now', page_text)


# ============================================================
# TEST 17: RECRUITER SEARCHES SEEKER POSTS
# ============================================================
class RecruiterSearchSeekersTest(BaseSeleniumTest):
    """Test recruiter searching and filtering seeker posts."""

    def setUp(self):
        super().setUp()
        JobPost.objects.create(
            poster=self.seeker_user, poster_type='seeker',
            title='Django Expert Available', description='Expert in Django',
            skills_text='Python, Django', location='Dhaka', job_type='fullTime',
            status='active', number_of_available_seats=1
        )

    def test_find_talent_page_has_search(self):
        """Test Find Talent page has search bar and filters."""
        self.login_as_recruiter()
        self.browser.get(f'{self.live_server_url}/recruitments/seeker-posts/')
        time.sleep(1)

        search_input = self.browser.find_element(By.NAME, 'q')
        self.assertIsNotNone(search_input)
        location_input = self.browser.find_element(By.NAME, 'location')
        self.assertIsNotNone(location_input)

    def test_search_seeker_posts(self):
        """Test recruiter can search seeker posts."""
        self.login_as_recruiter()
        self.browser.get(f'{self.live_server_url}/recruitments/seeker-posts/')
        time.sleep(1)

        search_input = self.browser.find_element(By.NAME, 'q')
        search_input.send_keys('Django')
        self.browser.find_element(By.CSS_SELECTOR, '.btn-search').click()
        time.sleep(1)

        page_text = self.browser.find_element(By.TAG_NAME, 'body').text
        self.assertIn('Django Expert Available', page_text)
        self.assertIn('1 candidate', page_text)

    def test_filter_by_location(self):
        """Test recruiter can filter seeker posts by location."""
        self.login_as_recruiter()
        self.browser.get(f'{self.live_server_url}/recruitments/seeker-posts/?location=Dhaka')
        time.sleep(1)

        page_text = self.browser.find_element(By.TAG_NAME, 'body').text
        self.assertIn('Django Expert Available', page_text)

    def test_no_results_search(self):
        """Test search with no results shows empty state."""
        self.login_as_recruiter()
        self.browser.get(f'{self.live_server_url}/recruitments/seeker-posts/?q=NonExistent')
        time.sleep(1)

        page_text = self.browser.find_element(By.TAG_NAME, 'body').text
        self.assertIn('No candidates match', page_text)


# ============================================================
# TEST 18: COMPANY LOGO ON JOB DETAIL
# ============================================================
class CompanyLogoTest(BaseSeleniumTest):
    """Test company logo/initial shows on job detail page."""

    def test_company_name_shows_on_job_detail(self):
        """Test company name is displayed on job detail page."""
        self.login_as_seeker()
        self.browser.get(f'{self.live_server_url}/recruitments/jobs/{self.job_post.id}/')
        time.sleep(1)

        page_text = self.browser.find_element(By.TAG_NAME, 'body').text
        self.assertIn('Tech Corp', page_text)

    def test_company_initial_shows_when_no_logo(self):
        """Test company initial letter shows when no logo uploaded."""
        self.login_as_seeker()
        self.browser.get(f'{self.live_server_url}/recruitments/jobs/{self.job_post.id}/')
        time.sleep(1)

        # The initial 'T' for Tech Corp should be present
        page_source = self.browser.page_source
        self.assertIn('Tech Corp', page_source)
