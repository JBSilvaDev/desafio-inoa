from django import forms
from .models import AtivosUser

class AtivoUserForm(forms.ModelForm):
    class Meta:
        model = AtivosUser
        fields = ['limite_superior', 'limite_inferior', 'intervalo_verificacao']
        widgets = {
            'limite_superior': forms.NumberInput(attrs={'class': 'form-control'}),
            'limite_inferior': forms.NumberInput(attrs={'class': 'form-control'}),
            'intervalo_verificacao': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
        }
        labels = {
            'limite_superior': 'Limite Superior (Venda)',
            'limite_inferior': 'Limite Inferior (Compra)',
            'intervalo_verificacao': 'Frequência de Checagem (minutos)',
        }
