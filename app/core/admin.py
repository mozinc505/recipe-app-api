"""
Djando admin customization
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _ #S tem se integriraš v django translation system
#Če želiš spremeniti jezik django-a in to povsod, je najbolje, da to narediš v nastavitvah
#Kjerkoli boš uporabil _ se bo avtomatično preslikalo v text (gettext_lazy). To je standardni način pri djangu.

#OPOMBA: Naš user admin bomo imenovali UserAdmin, zato smo tega, ki ga uvozimo iz django (osnovnega) uvozili kot BaseUserAdmin

from core import models

class UserAdmin(BaseUserAdmin):
    """Define the admin pages for users."""
    ordering = ['id']
    list_display = ['email', 'name']
    #OPOMBA: Ker uporabljamo custom user klas (ki ima nekoliko drugačna polja) moramo poskrbeti,
    # da bo django admin naložil in prikazal ta in ne default
    fieldsets = (
        (None, {'fields': ('email', 'password')}), #Prvi parameter je naslov section-a
        (
            # Znak _ se pretvori v gettext_lazy (ker smo tako zgoraj določili)
            _('Permissions'),
            {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser',
               )
            }
        ),
        (_('Important dates'), {'fields': ('last_login',)}),
    )
    readonly_fields = ['last_login']
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email',
                'password1',
                'password2',
                'name',
                'is_active',
                'is_staff',
                'is_superuser',
            )
        }),
    )

    #OPOMBA: parameter "classes: ..." zgoraj, je način kako lahko uporabiš css v django-admin

#OPOMBA: Če ne specificiramo parametera UserAdmin pomeni, da bo za prikaz User django uporabil default nastavitve prikaza (za add, edit, ...)
admin.site.register(models.User, UserAdmin)
admin.site.register(models.Recipe) #Ne potrebujemo še drugega parametra, ker ne specificiramo nek custom class ampak uporabljamo default class za model
admin.site.register(models.Tag)
admin.site.register(models.Ingredient)