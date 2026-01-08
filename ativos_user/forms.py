from django import forms
from .models import AtivosUser

class AtivoUserForm(forms.ModelForm):
    class Meta:
        model = AtivosUser
        fields = ['limite_superior', 'limite_inferior', 'intervalo_verificacao', 'favorito', 'em_carteira'] # Adicionar campos
        widgets = {
            'limite_superior': forms.NumberInput(attrs={'class': 'form-control'}),
            'limite_inferior': forms.NumberInput(attrs={'class': 'form-control'}),
            'intervalo_verificacao': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'favorito': forms.CheckboxInput(attrs={'class': 'form-check-input'}), # Novo widget
            'em_carteira': forms.CheckboxInput(attrs={'class': 'form-check-input'}), # Novo widget
        }
        labels = {
            'limite_superior': 'Limite Superior (Venda)',
            'limite_inferior': 'Limite Inferior (Compra)',
            'intervalo_verificacao': 'Frequência de Checagem (minutos)',
            'favorito': 'Marcar como Favorito', # Novo label
            'em_carteira': 'Incluir na Carteira', # Novo label
        }
