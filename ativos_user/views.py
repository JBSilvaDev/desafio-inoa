from django.shortcuts import render

# Create your views here.
def favoritos(request):
  return render(request, 'favoritos.html')