from django.contrib.auth.views import (
                        PasswordResetDoneView,PasswordResetConfirmView,
                        PasswordResetView,
                        PasswordResetCompleteView,)
from django.urls import path, re_path, include
from django.conf import settings

urlpatterns = [
    re_path('^reset_password_form/$',PasswordResetView.as_view(template_name='registration/password_reset_form.html'),name='password_reset'),
    re_path('^confirm/{?P<uidb64>[0-9A-Za-z]+}-{?P<token>,+}/$',PasswordResetConfirmView.as_view(),name='password_reset_confirm'),
    re_path('^complete/$',PasswordResetCompleteView.as_view()),
    re_path('^done/$',PasswordResetDoneView.as_view(),name='password_reset_done'),
]