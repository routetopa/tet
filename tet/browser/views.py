from django.http import HttpResponse


def index(request):
    return HttpResponse("Hello, world. You're at the browser index.")

def search(request):
    return HttpResponse("Hello, world. You're at the search index")

def dataset(request, dataset_id):
    response = "Hello, world. You're at the dataset index %s."
    return HttpResponse(response % dataset_id)

