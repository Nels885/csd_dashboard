from selenium.webdriver.support.ui import Select

from dashboard.tests.base import FunctionalTest, By
from squalaetp.models import Xelon
from tools.models import CsdSoftware, TagXelon


class ToolsSeleniumTestCase(FunctionalTest):

    def setUp(self):
        super(ToolsSeleniumTestCase, self).setUp()
        self.add_perms_user(CsdSoftware, 'add_csdsoftware')

    def test_soft_add_is_valid(self):
        driver = self.driver
        old_soft = CsdSoftware.objects.count()

        # Creating session cookie for to access Software add form
        self.login()
        cookie = self.client.cookies['sessionid']
        driver.get(self.live_server_url + '/tools/soft/add/')
        driver.add_cookie({'name': 'sessionid', 'value': cookie.value, 'secure': False, 'path': '/'})
        driver.refresh()
        driver.get(self.live_server_url + '/tools/soft/add/')

        # Inserting values into the form
        jig = driver.find_element(By.NAME, 'jig')
        version = driver.find_element(By.NAME, 'new_version')
        link = driver.find_element(By.NAME, 'link_download')
        status = driver.find_element(By.NAME, 'status')
        submit = driver.find_element(By.NAME, 'btn_soft_add')
        jig.send_keys('1234567890')
        version.send_keys('RT4')
        link.send_keys('FF')
        Select(status).select_by_visible_text('En test')
        submit.click()

        new_soft = CsdSoftware.objects.count()
        self.assertEqual(new_soft, old_soft + 1)
        self.assertEqual(driver.current_url, self.live_server_url + '/tools/soft/')

    def test_soft_list_page(self):
        driver = self.driver

        # Creating session cookie for to access Software add form
        self.login()
        cookie = self.client.cookies['sessionid']
        driver.get(self.live_server_url + '/tools/soft/')
        driver.add_cookie({'name': 'sessionid', 'value': cookie.value, 'secure': False, 'path': '/'})
        driver.refresh()
        driver.get(self.live_server_url + '/tools/soft/')

        self.assertEqual(driver.current_url, self.live_server_url + '/tools/soft/')

    # def test_tag_xelon_add_is_valid(self):
    #     driver = self.driver
    #     old_tags = TagXelon.objects.count()
    #     obj = Xelon.objects.create(
    #         numero_de_dossier='A123456789', vin=self.vin, modele_produit='produit', modele_vehicule='peugeot')
    #
    #     self.add_perms_user(TagXelon, 'add_tagxelon')
    #     self.login()
    #     cookie = self.client.cookies['sessionid']
    #     driver.get(self.live_server_url + '/tools/tag-xelon/add/')
    #     driver.add_cookie({'name': 'sessionid', 'value': cookie.value, 'secure': False, 'path': '/'})
    #     driver.refresh()
    #     driver.get(self.live_server_url + '/tools/tag-xelon/add/')
    #
    #     # Inserting values into the form
    #     xelon = driver.find_element(By.ID, 'id_xelon')
    #     calibre = Select(driver.find_element(By.ID, 'id_calibre'))
    #     telecode = Select(driver.find_element(By.ID, 'id_telecode'))
    #     submit = driver.find_elements(By.CSS_SELECTOR, 'button.btn.btn-primary')
    #     xelon.send_keys(obj.numero_de_dossier)
    #     calibre.select_by_visible_text('Logiciel CAL')
    #     telecode.select_by_visible_text('Non')
    #     submit[0].click()
    #
    #     new_tags = TagXelon.objects.count()
    #     self.assertEqual(new_tags, old_tags + 1)
