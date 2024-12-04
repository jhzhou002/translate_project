from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import RegistrationKey


# 自定义用户注册表单
class CustomUserCreationForm(UserCreationForm):
    username = forms.CharField(
        label='用户名',
        max_length=150,
        help_text="请输入您的用户名，不超过150个字符。",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入用户名'})
    )
    password1 = forms.CharField(
        label='密码',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '请输入密码'})
    )
    password2 = forms.CharField(
        label='确认密码',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '请再次输入密码'})
    )
    email = forms.EmailField(
        label='邮箱',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': '请输入邮箱'})
    )
    registration_key = forms.CharField(
        max_length=512,
        required=True,
        label="注册密钥",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入注册密钥'}),
        help_text="请输入管理员提供的有效注册密钥。"
    )

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2', 'email', 'registration_key')

    def clean_registration_key(self):
        registration_key = self.cleaned_data.get('registration_key')
        # 检查注册密钥是否有效并且未使用
        if not RegistrationKey.objects.filter(key=registration_key, is_used=False).exists():
            raise forms.ValidationError("无效或已被使用的注册密钥，请联系管理员获取新密钥。")
        return registration_key


# 自定义登录表单
class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        label='用户名',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入用户名'})
    )
    password = forms.CharField(
        label='密码',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '请输入密码'})
    )

    # 通用错误提示
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
