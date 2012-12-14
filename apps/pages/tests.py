from django.test import LiveServerTestCase
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

class MySeleniumTests(LiveServerTestCase):
    #fixtures = ['user-data.json']

    @classmethod
    def setUpClass(cls):
        #cls.selenium = WebDriver()
        cls.selenium = webdriver.Chrome(executable_path="/Users/blaze/Downloads/chromedriver2")
        cls.selenium.implicitly_wait(3)
        super(MySeleniumTests, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super(MySeleniumTests, cls).tearDownClass()

    def test_login(self):
        from django.contrib.auth.models import User

        from selenium.webdriver.support.wait import WebDriverWait
        timeout = 5

        users = []
        max_user = User.objects.count() + 1
        # create users
        for x in xrange(max_user,max_user+11):
            try:
                max_user = x
                username = 'admin%s' % max_user
                email = 'admin@admin%s.com' % max_user
                user = User.objects.create_user(username, email, 'admin')
                user.first_name = 'admin%s' % max_user
                user.save()
                user = user.userprofile
                users.append(user)
                # adding to love page
                #from pages.models import Pages, Membership
                #page = Pages.objects.get(id=23)
                print "%S" % user
                #import datetime
                #from_date = datetime.date(2008, 6, 24)
                #Membership.objects.create(user=user,page=page,type='IN',from_date=from_date)
                #page.users_loved.add(user)
                #page.loves += 1
                #page.save()
            except:
                continue
        # create page
        from pages.models import Pages
        admin = user
        Pages.objects.create(name='test', username='test', user = admin, type='BS', loves_limit=5)

        for user in users[:0]:
            self.selenium.get('%s%s' % (self.live_server_url, '/account/login/'))
            username_input = self.selenium.find_element_by_id("id_login-email")
            username_input.send_keys(user.username)
            password_input = self.selenium.find_element_by_id("id_login-password")
            password_input.send_keys('admin')
            password_input.send_keys(Keys.RETURN)

            self.selenium.get('%s%s' % (self.live_server_url, '/pages/business/test/'))
            loves = self.selenium.find_element_by_class_name("love_button")
            loves.click()

            WebDriverWait(self.selenium, timeout).until(
            lambda driver: driver.find_element_by_class_name('loved'))

            self.selenium.get('%s%s' % (self.live_server_url, '/account/logout/'))

        self.selenium.get('%s%s' % (self.live_server_url, '/account/login/'))
        username_input = self.selenium.find_element_by_id("id_login-email")
        username_input.send_keys(admin.username)
        password_input = self.selenium.find_element_by_id("id_login-password")
        password_input.send_keys('admin')
        password_input.send_keys(Keys.RETURN)

        WebDriverWait(self.selenium, timeout).until(
        lambda driver: driver.find_element_by_class_name('profile_micro_header'))
        self.selenium.get('%s%s' % (self.live_server_url, '/pages/page/test/settings/'))

        self.selenium.find_element_by_id("loves_settings").click()

        card = self.selenium.find_element_by_class_name("card-number")
        card.send_keys('378282246310005')
        card = self.selenium.find_element_by_class_name("card-cvc")
        card.send_keys('123')
        card = self.selenium.find_element_by_class_name("card-expiry-month")
        card.send_keys('11')
        card = self.selenium.find_element_by_class_name("card-expiry-year")
        card.send_keys('2015')

        self.selenium.execute_script("$('#loves-value').val('$0')")
        self.selenium.find_element_by_id("submit-card").click()

        WebDriverWait(self.selenium, timeout).until(
        lambda driver: driver.find_element_by_name('stripeToken'))

        #self.selenium.find_element_by_id("loves_settings").click()

        self.selenium.find_element_by_id("submit-card").click()




