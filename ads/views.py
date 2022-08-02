import json


from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import DetailView, CreateView, ListView, UpdateView, DeleteView

import ads
from ads.models import Ads, Categorie
from lesson28 import settings
from users.models import User


class AdsView(ListView):
    model = Ads
    queryset = Ads.objects.all()

    # def __init__(self, **kwargs):
    #     super().__init__(kwargs)
    #     self.objects_list = None

    def get(self, request, *args, **kwargs):
        super().get(request, *args, **kwargs)
        self.objects_list = self.object_list.select_related('autor').order_by("-price")
        paginator = Paginator(self.object_list, settings.TOTAL_ON_PAGE)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        ads = []
        for a in page_obj:
            ads.append({
                'id': a.id,
                'name': a.name,
                'author_id': a.author_id,
                'author': a.author.first_name,
                'price': a.price,
                'description': a.description,
                'is_published': a.is_published,
                'category_id': a.category_id,
                'image': a.image.url if a.image else None,
            })

        result = {"items": ads,
                  "num_page": page_obj.paginator.num_pages,
                  "total": page_obj.paginator.count}

        return JsonResponse(result, safe=False)


class AdsDetailView(DetailView):
    model = Ads

    def get(self, request, *args, **kwargs):
        ads = self.get_object()
        return JsonResponse({
            'id': ads.id,
            'name': ads.name,
            'author_id': ads.author_id,
            'author': ads.author.first_name,
            'price': ads.price,
            'description': ads.description,
            'is_published': ads.is_published,
            'category_id': ads.category_id,
            'image': ads.image.url if ads.image else None,

        })


@method_decorator(csrf_exempt, name="dispatch")
class AdsCreateView(CreateView):
    model = Ads
    fields = ["name", "author", "price", "description", "category"]

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)

        author = get_object_or_404(User, id=data["author_id"])
        category = get_object_or_404(Categorie, id=data["category_id"])

        ads = Ads.objects.create(
            name=data['name'],
            author=author,
            price=data['price'],
            description=data['description'],
            is_published=data['is_published'],
#            category_id=data['category_id'], )
            category=category, )

        return JsonResponse({
            'id': ads.id,
            'name': ads.name,
            'author_id': ads.author_id,
            'author': ads.author.first_name,
            'price': ads.price,
            'description': ads.description,
            'is_published': ads.is_published,
            'category_id': ads.category_id,
            'image': ads.image.url if ads.image else None,

        })


@method_decorator(csrf_exempt, name="dispatch")
class AdsUpdateView(UpdateView):
    model = Ads
    fields = ["name", "author", "price", "description", "category"]

    def patch(self, request, *args, **kwargs):
        super().post(request, *args, **kwargs)

        data = json.loads(request.body)

        self.object.name = data['name']
        self.object.price = data['price']
        self.object.description = data['description']
        self.object.author = get_object_or_404(User, id=data["author_id"])
        self.object.category = get_object_or_404(Categorie, id=data["category_id"])

        self.object.save()
        return JsonResponse({
            'id': self.object.id,
            'name': self.object.name,
            'author_id': self.object.author_id,
            'author': self.object.author.first_name,
            'price': self.object.price,
            'description': self.object.description,
            'is_published': self.object.is_published,
            'category_id': self.object.category_id,
            'image': self.object.image.url if self.object.image else None,

        })


@method_decorator(csrf_exempt, name="dispatch")
class AdsDeleteView(DeleteView):
    model = Ads
    success_url = "/"

    def delete(self, request, *args, **kwargs):
        super().delete(request, *args, **kwargs)

        return JsonResponse({"status": "ok"}, status=200)


@method_decorator(csrf_exempt, name="dispatch")
class AdsUploadImageView(UpdateView):
    model = Ads
    fields = ['image']

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.image = request.FILES.get("image", None)
        self.object.save()

        return JsonResponse({
            'id': self.object.id,
            'name': self.object.name,
            'author_id': self.object.author_id,
            'author': self.object.author.first_name,
            'price': self.object.price,
            'description': self.object.description,
            'is_published': self.object.is_published,
            'category_id': self.object.category_id,
            'image': self.object.image.url if self.object.image else None
        })


class CategoryView(ListView):
    model = Categorie
    queryset = Categorie.objects.all()

    def get(self, request, *args, **kwargs):
        super().get(request, *args, **kwargs)
        self.objects_list = self.object_list.order_by("name")

        result = []
        for cat in self.objects_list:
            result.append({
                'id': cat.id,
                'name': cat.name,
            })

        return JsonResponse(result, safe=False)


class CategoryDetailView(DetailView):
    model = Categorie

    def get(self, request, *args, **kwargs):
        category = self.get_object()

        return JsonResponse({
            'id': category.id,
            'name': category.name,
        })


@method_decorator(csrf_exempt, name="dispatch")
class CategoryCreateView(CreateView):
    model = Categorie
    fields = ["name"]

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        category = Categorie.objects.create(
            name=data['name']
        )
        return JsonResponse({
            'id': category.id,
            'name': category.name,
        })


@method_decorator(csrf_exempt, name="dispatch")
class CategoryUpdateView(UpdateView):
    model = Categorie
    fields = ["name"]

    def patch(self, request, *args, **kwargs):
        super().post(request, *args, **kwargs)

        data = json.loads(request.body)
        self.object.name = data['name']

        self.object.save()

        return JsonResponse({
            'id': self.object.id,
            'name': self.object.name, })


@method_decorator(csrf_exempt, name="dispatch")
class CategoryDeleteView(DeleteView):
    model = Categorie
    success_url = "/"

    def delete(self, request, *args, **kwargs):
        super().delete(request, *args, **kwargs)

        return JsonResponse({"status": "ok"}, status=200)
