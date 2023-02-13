"""
Tests for the Djando admin modifications.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import Client


class AdminSiteTests(TestCase):
    """Test for Django admin."""

    # Koda, ki se izvede pred izvedbo testov
    # Implementiramo določene modele, ki jih bomo uporabili pri izvedbi različnih testov

    # S setup metodo implementiramo določene modele za določene teste, ki jih dodamo v ta klas

    # OPOMBA: UnitTest modul za Python uporablja drugačno sintakso (snakeCase)
    def setUp(self):
        """Create user and client."""
        self.client = Client() # To je Django test client

        self.admin_user = get_user_model().objects.create_superuser(
            email='admin@example.com',
            password='testpass123',
        )

        #Forsiramo avtentikacijo na tega userja
        #Vsaka zahteva, ki jo naredimo čez tega klienta (Client), bo avtenticirana s tem userjem, ki smo ga tukaj naredili.
        self.client.force_login(self.admin_user)
        self.user = get_user_model().objects.create_user(
            email='user@example.com',
            password='testpass123',
            name='Test user'
        )

    def test_users_list(self):
        """Test that users are listed on page."""

        # Dokumentacija za reverse: https://docs.djangoproject.com/en/3.1/ref/contrib/admin/#reversing-admin-urls
        url = reverse('admin:core_user_changelist') #To je pot do spletne strani s seznamom uporabnikov (znotraj django admin)
        res = self.client.get(url) # Request se bo avtenticirala z admin (forsiranim login-om, ki smo ga zgoraj nastavili)

        self.assertContains(res, self.user.name)
        self.assertContains(res, self.user.email)

    def test_edit_user_page(self):
        """Test the edit user page works."""
        url = reverse('admin:core_user_change', args=[self.user.id]) # Drugi parameter določa id uporabnika, ki ga želimo editirati
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200) #Status 200 pomeni, da je stran uspešno naložena = OK

    def test_create_user_page(self):
        """Test the create user page works."""
        url = reverse('admin:core_user_add')
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)