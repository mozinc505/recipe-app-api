"""
Test for the user API
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

#URL od API-ja, ki ga bomo testirali
#Naredimo spremenljivko, kamor zapišemo endpoint za "User - create", da ne pišemo več čas isto
#V reverse metodi: user = app, create = endpoint
#Reverse omogoča, da dobimo URL od view-ja
CREATE_USER_URL = reverse('user:create') #Vrne celotno url pot do tega v našem projektu
TOKEN_URL = reverse('user:token') #to bo url endpoint za kreiranje token-ov v našen user API
ME_URL = reverse('user:me')

#Dodamo helper funkcijo, ki nam bo omogočila, da kreiramo uporabnika, ki ga bomo uporabili za testiranje
def create_user(**params):
    """Create and return a new user"""
    return get_user_model().objects.create_user(**params)


#TESTE RAZDELIMO NA PUBLIC in PRIVATE teste
#PUBLIC == pomeni == Unauthenticated requests (npr. registerind a new user)
#PRIVATE == pomeni == Authenticated requests

#Uporabimo ločene classe za te teste (public in private)

class PublicUserApiTests(TestCase):
    """Test the public features of the user API."""


    # Koda, ki se izvede pred izvedbo testov
    # Implementiramo določene modele, ki jih bomo uporabili pri izvedbi različnih testov
    # S setup metodo implementiramo določene modele za določene teste, ki jih dodamo v ta klas
    def setUp(self):
        self.client = APIClient()

    #TEST CASES

    #-------
    #TEST za testiranje userja
    #-------
    def test_create_user_success(self):
        """Test creating a user is successful."""

        #Naredimo dictionary, ki vsebuje podatke, ki jih bomo posredovali API-ju preko POST metode
        payload = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'name': 'Test Name',
        }
        #Naredimo HTTP POST REQUEST na ta URL in pošljemo zraven podatke zapisane v paylod dictionary-ju
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        #Preverimo ali je objekt res bil skreiran. Naredimo query - iščemo po emailu
        user = get_user_model().objects.get(email=payload['email'])

        #Preverimo, da password ustreza (da je bil user kreiran s pravim passwordom)
        self.assertTrue(user.check_password(payload['password']))

        #Preverimo, da slučajno ne vračamo passworda oz. HASH-a od passworda (ker ni potrebe za to)
        self.assertNotIn('password', res.data) #Preverimo, da v podatkih response-a ni "passworda"

    def test_user_with_email_exists_error(self):
        """Test error returned if user with email exists."""
        #Preverimo, da res dobimo napako v primeru, če želimo dodati uporabnika z istim emailom
        payload = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'name': 'Test Name',
        }

        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short_error(self):
        """Test an error is returned if password less than 5 chars."""
        payload = {
            'email': 'test@example.com',
            'password': 'pw',
            'name': 'Test Name',
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        #Preverimo, da ni naredil tega uporabnika (s prekratkim geslom)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists) #Potrdimo, da uporabnik res ne obstaja v bazi

    #-------
    #TEST za testiranje token-a
    #-------
    def test_create_token_for_user(self):
        """Tesst generates token for valied credentials."""

        #Naredimo userja
        user_details = {
            'name': 'Test Name',
            'email': 'test@example.com',
            'password': 'test-user-password-123',
        }
        create_user(**user_details)


        #To bo poslano token API-ju zato, da se logiramo
        payload = {
            'email': user_details['email'],
            'password': user_details['password'],
        }
        #Poslejmo TOKEN url-ju te podatke (payload), da generiramo token
        res = self.client.post(TOKEN_URL, payload)

        #Preverimo, da response vsebuje token in da je status odgovora OK
        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_bad_credentials(self):
        """Test returns error if credentials invalid."""
        create_user(email='test@example.com', password='goodpass')

        payload = {'email': 'test@example.com', 'password': 'badpass'}
        res = self.client.post(TOKEN_URL, payload)

        #PREVERIMO: Pričakujemo, da token ne bo generiran (ker smo dali slabe akreditacije)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_blank_password(self):
        """Test postina a blank password returns error."""
        create_user(email='test@example.com', password='goodpass')

        payload = {'email': 'test@example.com', 'password': ''}
        res = self.client.post(TOKEN_URL, payload)

        #PREVERIMO: Pričakujemo, da token ne bo generiran (ker smo dali prazno geslo)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    #-------
    #TEST za testiranje "me" endpointa
    #-------
    def test_retrieve_user_unauthorized(self):
        """Test authentication is required for users"""

        #Poskusimo pobrati podatke o userjih (me) brez predhodne avtentikacije --> mora vrniti napako

        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


#V tem klasu testiramo vse "requeste", ki zahtevajo, da je uporabnik predhodno avtenticiramo.
#Ločen klas uporabimo zato, da že na konstruktorju (SetUp metodi) avtenticiramo uporabnika in da to ne delamo pri vsakem testu posebej.
class PrivateUserAPITest(TestCase):
    """Test API request that require authentication"""

    def setUp(self):
        self.user = create_user(
            email='test@example.com',
            password='testpass123',
            name='Test Name',
        )
        self.client = APIClient()

        #Sometimes you may want to bypass authentication entirely and force all requests by the test client to be automatically treated as authenticated.
        #So any request we make with this client from hereon will be authenticated with the user that we specified.
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):
        """Test retrieving profile for logged in user"""

        #This will retrieve the details of the current authenticated user.
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'name': self.user.name,
            'email': self.user.email,
        })

    def test_post_me_not_allowed(self):
        """Test POST is not allowed for the me endpoint."""
        res = self.client.post(ME_URL, {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """Test updating the user profile for the authenticated user."""
        payload = {'name': 'Updated name', 'password': 'newpassword123'}

        res = self.client.patch(ME_URL, payload)

        self.user.refresh_from_db() #S tem osvezimo podatke iz baze (reread)

        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
