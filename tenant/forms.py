from django.forms import ModelForm, DateInput
from django import forms
from tenant.models import TblTenant, TblAgent
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.forms import PasswordResetForm


Doc_Choice = [(0, "Select"), (1, "Adhar Card"), (2, "Driving Licence"),
              (3, "Passport"), (4, "Election Card"), (5, "Pan Card"), ]
# Status = [(-1, "Select Status"), (1, "Visit"), (2, "Deal Accepted aggrement under process"),
#           (3, "Property handovered"), (4, "Ex-Tenant")]



class EmailValidationOnForgotPassword(PasswordResetForm):

    def clean_email(self):
        email = self.cleaned_data['email']
        if not TblAgent.objects.filter(email__iexact=email, is_active=True).exists():
            msg = "There is no user registered with the specified E-Mail address."
            self.add_error('email', msg)
        return email



class TenantRegistratonForm(ModelForm):
    class Meta:
        model = TblTenant
        exclude = ('tn_agent', 'tn_is_active','tn_joining_date','tn_status',)
        
    tn_name = forms.CharField(
        max_length=25, help_text="Enter Tenant's Name:", required=True)
    tn_contact = forms.CharField(
        max_length=10, help_text="Enter Tenant's Contact No:", required=True)
    tn_permanent_address = forms.CharField(widget=forms.Textarea(attrs={'width': "100%",'cols' : "80",'rows':"2"}), max_length=225, help_text="Tenant's Permenent address:")
    tn_profile = forms.ImageField(
        help_text='Upload Tenant\'s Picture here:', max_length=200, required=False)
    tn_document_description = forms.IntegerField(
        help_text='Document Type:', widget=forms.Select(choices=Doc_Choice))

    tn_document = forms.ImageField(help_text='Upload Document:', required=True)
    tn_reference_name = forms.CharField(
        help_text='Reference Name:', max_length=25, required=True)
    tn_reference_address = forms.CharField(widget=forms.Textarea(attrs={'width': "100%",'cols' : "80",'rows':"2"}),help_text='Reference Address:', max_length=255)
    # tn_status = forms.IntegerField(
    #     help_text='Tenant Status:', widget=forms.Select(choices=Status))
    tn_agent = forms.CharField(widget=forms.HiddenInput(),required=False)
    # tn_joining_date = forms.DateField(widget=forms.SelectDateWidget(),help_text="Select Joinning Date:",input_formats='%d/%m/%Y')        
    # tn_joining_date = forms.DateField(help_text='Date of Join:')
    tn_is_active = forms.HiddenInput()

    # def clean(self):
    #     cleaned_data=self.cleaned_data
    #     tn_document_description=cleaned_data.get('tn_document_description')
    #     list1=list(tn_document_description);
    #     tn_document_description=list1[0]
    #     cleaned_data['tn_document_description']=tn_document_description
    #     return cleaned_data


class AgentForm(ModelForm):
    class Meta:
        model = TblAgent
        exclude = ('groups','is_superuser','user_permissions','last_login','is_staff','is_active','date_joined')


    username=forms.CharField(max_length=15,help_text="Enter User Name:")
    password=forms.CharField(widget=forms.PasswordInput(attrs={'style': 'width: 728px; height: 30px; padding:4px 20px'}),help_text="Enter your Password:",required=True)
    password2=forms.CharField(widget=forms.PasswordInput(attrs={'style': 'width: 728px; height: 30px; padding:4px 20px'}),help_text="Enter your again Password:",required=True)
    first_name=forms.CharField(help_text="Enter your First Name:")
    last_name=forms.CharField(help_text="Enter your Last Name:")
    email=forms.EmailField(help_text="Enter Email id:")
    # date_joined=forms.DateField(help_text='Date of Join:')
    ag_contact=forms.CharField(help_text="Enter your Contact No:")
    ag_local_address=forms.CharField(widget=forms.Textarea(attrs={'width': "100%",'cols' : "80",'rows':"2"}), max_length=225,help_text="Enter Local Address:")
    ag_permanent_address=forms.CharField(widget=forms.Textarea(attrs={'width': "100%",'cols' : "80",'rows':"2"}), max_length=225,help_text="Enter Permenent Address:")
    ag_profile_image=forms.ImageField(help_text='Upload Profile Picture here:', max_length=200, required=False)


# class AgentCreationForm(UserCreationForm):

#     class Meta(UserCreationForm):
#         model = TblAgent
#         fields = ('username', 'email',)

# class AgentChangeForm(UserChangeForm):

#     class Meta:
#         model = TblAgent
#         fields = ('username', 'email')
