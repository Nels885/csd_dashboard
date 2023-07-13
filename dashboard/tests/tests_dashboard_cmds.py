from django.core.management import call_command
from django.contrib.auth.models import ContentType
from django.utils import timezone

from .base import UnitTest, User, Group, Permission
from dashboard.models import Post, UserProfile, ShowCollapse, WebLink, Contract
from squalaetp.models import Indicator, Xelon

from io import StringIO


class DashboardCommandTestCase(UnitTest):

    def setUp(self):
        super(type(self), self).setUp()
        Group.objects.create(name='Test')
        Post.objects.create(title='Test', overview='test', author=self.user)
        WebLink.objects.create(title='Test', url='https://test.com', type='PSA', description='test')
        Contract.objects.create(id=1, code='test')
        xelon = Xelon.objects.create(numero_de_dossier='A123456789', date_retour=timezone.now())
        indicator = Indicator.objects.create(
            date=timezone.now(), products_to_repair=1, late_products=1, express_products=1, output_products=1)
        indicator.xelons.add(xelon)
        self.out = StringIO()

    def test_clear_auth_Group_table(self):
        groups_old = Group.objects.count()
        call_command('clearauth', '--group', stdout=self.out)
        groups_new = Group.objects.count()
        self.assertEqual(groups_old, groups_new + 1)
        self.assertIn("Suppression des données de la table Group terminée!", self.out.getvalue())

    def test_clear_auth_Permission_table(self):
        permissions_old = Permission.objects.count()
        call_command('clearauth', '--permission', stdout=self.out)
        permissions_new = Permission.objects.count()
        self.assertNotEqual(permissions_old, 0)
        self.assertEqual(permissions_new, 0)
        self.assertIn("Suppression des données de la table Permission terminée!", self.out.getvalue())

    def test_clear_auth_all_table(self):
        users_old = User.objects.count()
        call_command('clearauth', '--all', stdout=self.out)
        user_news = User.objects.count()
        self.assertEqual(users_old, user_news + 2)
        self.assertIn("Suppression des données des tables de Auth terminée!", self.out.getvalue())

    def test_clear_dashboard_post_table(self):
        posts_old = Post.objects.count()
        call_command('cleardashboard', '--post', stdout=self.out)
        posts_new = Post.objects.count()
        self.assertEqual(posts_old, posts_new + 1)
        self.assertIn("Suppression des données de la table Post terminée!", self.out.getvalue())

    def test_clear_dashboard_showcollapse_table(self):
        collapses_old = ShowCollapse.objects.count()
        call_command('cleardashboard', '--showcollapse', stdout=self.out)
        collapses_new = ShowCollapse.objects.count()
        self.assertEqual(collapses_old, collapses_new + 2)
        self.assertIn("Suppression des données de la table ShowCollapse terminée!", self.out.getvalue())

    def test_clear_dashboard_userprofile_table(self):
        profiles_old = UserProfile.objects.count()
        call_command('cleardashboard', '--userprofile', stdout=self.out)
        profiles_new = UserProfile.objects.count()
        self.assertEqual(profiles_old, profiles_new + 2)
        self.assertIn("Suppression des données de la table UserProfile terminée!", self.out.getvalue())

    def test_clear_dashboard_weblink_table(self):
        weblinks_old = WebLink.objects.count()
        call_command('cleardashboard', '--weblink', stdout=self.out)
        weblinks_new = WebLink.objects.count()
        self.assertEqual(weblinks_old, weblinks_new + 1)
        self.assertIn("Suppression des données de la table WebLink terminée!", self.out.getvalue())

    def test_clear_dashboard_contract_table(self):
        contracts_old = Contract.objects.count()
        call_command('cleardashboard', '--contract', stdout=self.out)
        contracts_new = Contract.objects.count()
        self.assertEqual(contracts_old, contracts_new + 1)
        self.assertIn("Suppression des données de la table Contract terminée!", self.out.getvalue())

    def test_clear_dashboard_all_table(self):
        call_command('cleardashboard', '--all', stdout=self.out)
        for obj_nb in [Post.objects.count(), ShowCollapse.objects.count(), UserProfile.objects.count(),
                       WebLink.objects.count()]:
            self.assertEqual(obj_nb, 0)
        self.assertIn("Suppression des données des tables de Dashboard terminée!", self.out.getvalue())

    def test_clear_django_all_table(self):
        call_command('cleardjango', '--all', stdout=self.out)
        obj_nb = ContentType.objects.count()
        self.assertEqual(obj_nb, 0)
        self.assertIn("Suppression des données des tables de Django terminée!", self.out.getvalue())

    def test_send_email(self):
        # Sending emails without data in the database
        call_command(
            "sendemail", "--late_products", "--pending_products", "--vin_error", "--contract", "--vin_corvet",
            stdout=self.out)
        self.assertIn("Envoi de l'email des produits en retard terminée!", self.out.getvalue())
        self.assertIn("Envoi de l'email des produits en cours terminée!", self.out.getvalue())
        self.assertIn("Pas d'erreurs de VIN a envoyer !", self.out.getvalue())
        self.assertIn("Pas de contracts a envoyer !", self.out.getvalue())
        self.assertIn("Pas de VIN sans données CORVET à envoyer !", self.out.getvalue())

        # Sending emails with data in the database
        Contract.objects.update(is_active=True, renew_date=timezone.now())
        Xelon.objects.filter(numero_de_dossier='A123456789').update(vin_error=True)
        Xelon.objects.create(numero_de_dossier='A987654321', vin=self.vin, date_retour=timezone.now())
        call_command("sendemail", "--vin_error", "--contract", "--vin_corvet", stdout=self.out)
        self.assertIn("Envoi de l'email des erreurs de VIN terminée !", self.out.getvalue())
        self.assertIn("Envoi de l'email des contrats terminée !", self.out.getvalue())
        self.assertIn("Envoi de l'email des VINs sans données CORVET terminée !", self.out.getvalue())

    def test_update_auth(self):
        users = User.objects.all()
        call_command("updateauth", "-E", "test", stdout=self.out)
        self.assertIn(f"[AUTH] Email domain update completed: USER = {users.count()}", self.out.getvalue())

    def test_load_contract(self):
        call_command("loadcontract", stdout=self.out)
        self.assertIn("[CONTRACT] Path to excel file missing !", self.out.getvalue())

        call_command("loadcontract", "-f" "test.xlsx", stdout=self.out)
        self.assertIn("[CONTRACT] No excel file found", self.out.getvalue())
