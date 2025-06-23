from django.shortcuts import render



def index(request):     
    return render(request, 'index.html')
def about(request):
    return render(request, 'about.html')
def contact(request):
    return render(request, 'contact.html')
def gallery(request):
    return render(request, 'gallery.html')
def blog(request):
    return render(request, 'blog.html')
def faq(request):
    return render(request, 'faq.html')
def testimonials(request):
    return render(request, 'testimonials.html')
def events(request):
    return render(request, 'events.html')
def news(request):
    return render(request, 'news.html')
def login(request):
    return render(request, 'login.html')
def signup(request):
    return render(request, 'signup.html')
