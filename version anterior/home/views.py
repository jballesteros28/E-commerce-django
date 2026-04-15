from django.shortcuts import render, redirect

# Create your views here.
def index(request, template_name:str='home/index.html'):
  return render(request, template_name)



def cambiar_tema(request):
    tema_actual = request.session.get('tema', 'light')
    request.session['tema'] = 'dark' if tema_actual == 'light' else 'light'
    return redirect(request.META.get('HTTP_REFERER', '/'))