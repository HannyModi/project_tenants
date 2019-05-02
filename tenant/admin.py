from django.contrib import admin
from tenant.models import (TblAgent,
                           TblAgentAllocation,
                           TblMasterProperty,
                           TblMasterPropertyClone,
                           TblProperty,
                           TblPropertyAllocation,
                           TblRentCollection,
                           TblTenant,
                           TblVisit,)
from django.contrib.auth.admin import UserAdmin, UserCreationForm
# Register your models here.


class UserCreateForm(UserCreationForm):

    class Meta:
        model = TblAgent
        fields = ('username',
                  'first_name',
                  'last_name',
                  'ag_contact')


class UserAdmin1(UserAdmin):
    add_form = UserCreateForm

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('first_name',
                       'last_name',
                       'username',
                       'password1',
                       'password2',
                       'ag_contact',),
        }),
    )


admin.site.register(TblAgent, UserAdmin1)
admin.site.register(TblAgentAllocation)
admin.site.register(TblMasterProperty)
admin.site.register(TblProperty)
admin.site.register(TblPropertyAllocation)
admin.site.register(TblRentCollection)
admin.site.register(TblTenant)
admin.site.register(TblVisit)
