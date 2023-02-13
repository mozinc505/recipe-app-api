"""
Serializers for the user API View.
"""
from django.contrib.auth import (
    get_user_model,
    authenticate,
)
from django.utils.translation import gettext as _ #To je standardni način pri django (standardna konvencija pri prevodih)

#Uvozimo serializers modul iz rest_frameworka
#Serializers omogočajo pretvorbo objektov iz in v python objekte
#Sprejme JSON, validira podatke in spremeni v python objekt ali objekt iz našega modela (definiranega v bazi)
from rest_framework import serializers

#ModelSerializer-ji nam omogočajo, da pretvorimo podatke v model, ki ga navedemo v sereializer-ju
class UserSerializer(serializers.ModelSerializer):
    """Serializer for the user object."""

    #S tem klasom povemo django.rest_frameworku, kateri model, katera polja in katere dodatne argumente želimo posredovati serilizatorju.
    #Serializer mora vedeti kateri model predstavlja.
    class Meta:
        model = get_user_model() #Povemo serializer-ju kateri model predstavlja

        #These are the fields we want to enable for serializer (katera polja so mu na voljo)
        #Katera polja morajo biti navedena v "requestu", da bodo preslikana v model.
        #Navedemo samo tista polja, ki jih uporabnik lahko nastavlja preko API-ja (ne polj, kot so is_staff, is_active)
        fields = ['email', 'password', 'name']
        #Kwargs = je dictionary, ki nam omogoča, da določimo dodatne metapodatke k poljem
        extra_kwargs = {'password': {'write_only': True, 'min_length': 5}}

    #Method allows us to override the behaviour that the serializer does when it creates a new objets (out of serializer)
    #OPOMBA: Ta metoda se kliče samo, po validaciji in samo takrat, ko je validacija uspešna - SICER PA NE
    def create(self, validated_data):
        """Create and return a user with encrypted password"""

        #Default obnašanje bi bilo, da serializer shrani podatke tako kot jih dobi.
        #Mi pa hočemo, da je password kriptiran --> zato uporabimo našo metodo za kreiranje userja, ki jih posredujemo že validirane podatke od serializer-ja.
        return get_user_model().objects.create_user(**validated_data)

    #Update method is called whenever we're performing update actions on the model that the serializer represents.
    #PARAM:
    # - instance: instance that is updated (that is the model instance that is going to be updated)
    # - validated_data: is the data that is already passed through serializer validation
    def update(self, instance, validated_data):
        """Update and return user."""
        #We are overriding the Update method on our User Serializer.

        #Retrieve the data from validated_data dictionary (with pop method)
        #OPOMBA: pop methoda odstrani podatek iz dictionary-ja (get methoda ga samo vrne)
        #Password je opcijski. Uporabnik lahko update-a tudi samo email, naziv,... --> zato v primeru, da ga ni nastavimo Default na None.
        password = validated_data.pop('password', None)

        #Update-amo vse razen passworda (smo ga zgoraj s pop metodo odstranili iz podatkov)
        #Zakaj: ker ne smemo gesla shraniti kot text ampak, ga želimo shraniti v hash obliki čez metodo za nastavljanje gesel
        user = super().update(instance, validated_data) #S tem update-tamo model (preko osnovnega klasa iz katerega smo dedovali)

        #Preverimo ali je bil password tudi update-an (ta bo true, če je bil med podatki za update)
        if password:
            user.set_password(password) #Nastavimo password, ki je bil podan
            user.save() #Shranimo ta nov password

        return user


class AuthTokenSerializer(serializers.Serializer):
    """Serializer for the user auth token."""

    email = serializers.EmailField()
    password = serializers.CharField(
        style={'input_type': 'password'},

        #Django po defaultu naredi TRIM pri vnosnih poljih
        trim_whitespace=False,
    )

    #Dodamo še validator.
    #Validate method is called on a serializer on the validation stage, when it goes to validate the input to the serializer.
    #POSTOPEK:
    #The validate method is going to be called at the validation stage by our view.
    #So, when the data is posted to the view, it's going to pass it to the serializer and then it's going to call validate
    #to validate that the data is correct.
    def validate(self, attrs):
        """Validate and authenticate the user."""

        #Poberemo podatke, ki jih je uporabnik vnesel (that the user provided on input)
        email = attrs.get('email')
        password = attrs.get('password')

        #Poklicemo metodo za avtentikacijo, ki je vgrajena v django
        user = authenticate(
            request=self.context.get('request'),
            username=email,
            password=password,
        )

        #Preverimo ali je "user" nastavljen (če je avtentikacija uspela, ga nastavi, sicer ne)
        if not user:
            msg = _('Unable to authenticate with provided credentials.')

            #Dvignemo error in "view" bo to prevedel v HTTP_400_BAD_REQUEST
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user #Vrnemo objekt userja, ki ga potem lahko uporabimo v view-ju
        return attrs