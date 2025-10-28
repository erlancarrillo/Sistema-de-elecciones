from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Ciudadano

class RegistroForm(UserCreationForm):
    cedula = forms.CharField(max_length=20, required=True)
    nombre_completo = forms.CharField(max_length=200, required=True)
    fecha_nacimiento = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    direccion = forms.CharField(widget=forms.Textarea, required=True)
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            Ciudadano.objects.create(
                user=user,
                cedula=self.cleaned_data['cedula'],
                nombre_completo=self.cleaned_data['nombre_completo'],
                fecha_nacimiento=self.cleaned_data['fecha_nacimiento'],
                direccion=self.cleaned_data['direccion']
            )
        return user