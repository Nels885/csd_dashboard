from django.core.management import call_command

from .base import UnitTest, User, Group, Permission
from dashboard.models import Post, UserProfile, ShowCollapse, WebLink

from io import StringIO


class DashboardCommandTestCase(UnitTest):

    def setUp(self):
        super(type(self), self).setUp()
        Group.objects.create(name='Test')
        author = UserProfile.objects.first()
        Post.objects.create(title='Test', overview='test', author=author)
        WebLink.objects.create(title='Test', url='https://test.com', type='PSA', description='test')
        self.out = StringIO()

    def test_clear_auth_Group_table(self):
        groups_old = Group.objects.count()
        call_command('clearauth', '--group', stdout=self.out)
        groups_new = Group.objects.count()
        self.assertEqual(groups_old, groups_new + 1)
        self.assertIn(
            "Suppression des données de la table Group terminée!",
            self.out.getvalue()
        )

    def test_clear_auth_Permission_table(self):
        permissions_old = Permission.objects.count()
        call_command('clearauth', '--permission', stdout=self.out)
        permissions_new = Permission.objects.count()
        self.assertNotEqual(permissions_old, 0)
        self.assertEqual(permissions_new, 0)
        self.assertIn(
            "Suppression des données de la table Permission terminée!",
            self.out.getvalue()
        )

    def test_clear_auth_all_table(self):
        users_old = User.objects.count()
        call_command('clearauth', '--all', stdout=self.out)
        user_news = User.objects.count()
        self.assertEqual(users_old, user_news + 2)
        self.assertIn(
            "Suppression des données des tables de Auth terminée!",
            self.out.getvalue()
        )

    def test_clear_dashboard_post_table(self):
        posts_old = Post.objects.count()
        call_command('cleardashboard', '--post', stdout=self.out)
        posts_new = Post.objects.count()
        self.assertEqual(posts_old, posts_new + 1)
        self.assertIn(
            "Suppression des données de la table Post terminée!",
            self.out.getvalue()
        )

    def test_clear_dashboard_showcollapse_table(self):
        collapses_old = ShowCollapse.objects.count()
        call_command('cleardashboard', '--showcollapse', stdout=self.out)
        collapses_new = ShowCollapse.objects.count()
        self.assertEqual(collapses_old, collapses_new + 2)
        self.assertIn(
            "Suppression des données de la table ShowCollapse terminée!",
            self.out.getvalue()
        )

    def test_clear_dashboard_userprofile_table(self):
        profiles_old = UserProfile.objects.count()
        call_command('cleardashboard', '--userprofile', stdout=self.out)
        profiles_new = UserProfile.objects.count()
        self.assertEqual(profiles_old, profiles_new + 2)
        self.assertIn(
            "Suppression des données de la table UserProfile terminée!",
            self.out.getvalue()
        )

    def test_clear_dashboard_weblink_table(self):
        weblinks_old = WebLink.objects.count()
        call_command('cleardashboard', '--weblink', stdout=self.out)
        weblinks_new = WebLink.objects.count()
        self.assertEqual(weblinks_old, weblinks_new + 1)
        self.assertIn(
            "Suppression des données de la table WebLink terminée!",
            self.out.getvalue()
        )

    def test_clear_dashboard_all_table(self):
        call_command('cleardashboard', '--all', stdout=self.out)
        for obj_nb in [Post.objects.count(), ShowCollapse.objects.count(), UserProfile.objects.count(),
                       WebLink.objects.count()]:
            self.assertEqual(obj_nb, 0)
        self.assertIn(
            "Suppression des données des tables de Dashboard terminée!",
            self.out.getvalue()
        )

    def test_send_email(self):
        call_command("sendemail", "--late_products", "--vin_error", "--vin_corvet",  stdout=self.out)
        self.assertIn("Envoi de l'email des produits en retard terminée!", self.out.getvalue())
        self.assertIn("Pas d'erreurs de VIN a envoyer !", self.out.getvalue())
        self.assertIn("Pas de VIN sans données CORVET à envoyer !", self.out.getvalue())
