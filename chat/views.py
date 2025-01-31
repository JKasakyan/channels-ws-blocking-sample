from django.shortcuts import render

def chat_async(request):
    return render(request, "chat/index_async.html")

def chat_sync(request):
    return render(request, "chat/index_sync.html")