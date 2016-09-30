from django.shortcuts import render

# Create your views here.
def webapp_console(request):
    return render(request,'index.html')