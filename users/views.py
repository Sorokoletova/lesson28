import json

from django.core.paginator import Paginator
from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from lesson28 import settings
from users.models import User, Location
from ads.models import Ads


class UserView(ListView):
    model = User
    queryset = User.objects.all()

    def get(self, request, *args, **kwargs):
        super().get(request, *args, **kwargs)
        self.object_list = self.object_list.annotate(total_ads=Count('ads'))
        paginator = Paginator(self.object_list, settings.TOTAL_ON_PAGE)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        users = []
        for user in page_obj:
            users.append({
                'id': user.id,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'user_name': user.user_name,
                'role': user.role,
                'age': user.age,
                'locations': list(map(str, user.locations.all())),
                'total_ads': len(self.object_list),

            })

        result = {"items": users,
                  "num_page": page_obj.paginator.num_pages,
                  "total": page_obj.paginator.count}

        return JsonResponse(result, safe=False)


class UserDetailView(DetailView):
    model = User

    def get(self, request, *args, **kwargs):
        user = self.get_object()

        return JsonResponse({
            'id': user.id,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'user_name': user.user_name,
            'role': user.role,
            'age': user.age,
            'locations': list(map(str, user.locations.all()))
        })


@method_decorator(csrf_exempt, name="dispatch")
class UserCreateView(CreateView):
    model = User
    fields = ["password", "first_name", "user_name", "last_name", "role", "age", "locations"]

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        user = User.objects.create(
            first_name=data["first_name"],
            last_name=data["last_name"],
            user_name=data["user_name"],
            password=data["password"],
            role=data["role"],
            age=data["age"],
        )
        for location_name in data["locations"]:
            location, _ = Location.objects.get_or_create(name=location_name)
            user.locations.add(location)

        return JsonResponse({
            'id': user.id,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'user_name': user.user_name,
            'role': user.role,
            'age': user.age,
            'locations': list(map(str, user.locations.all()))
        })


@method_decorator(csrf_exempt, name="dispatch")
class UserUpdateView(UpdateView):
    model = User
    fields = ["first_name", "last_name", "user_name", "role", "age", "locations"]

    def patch(self, request, *args, **kwargs):
        super().post(request, *args, **kwargs)

        data = json.loads(request.body)
        self.object.first_name = data['first_name']
        self.object.last_name = data['last_name']
        self.object.user_name = data['user_name']
        self.object.role = data['role']
        self.object.age = data['age']

        for location_name in data["locations"]:
            location, _ = Location.objects.get_or_create(name=location_name)
            self.object.locations.add(location)

        self.object.save()

        return JsonResponse({
            'id': self.object.id,
            'first_name': self.object.first_name,
            'last_name': self.object.last_name,
            'user_name': self.object.user_name,
            'role': self.object.role,
            'age': self.object.age,
            'locations': list(map(str, self.object.locations.all()))
        })


@method_decorator(csrf_exempt, name="dispatch")
class UserDeleteView(DeleteView):
    model = User
    success_url = "/"

    def delete(self, request, *args, **kwargs):
        super().delete(request, *args, **kwargs)

        return JsonResponse({"status": "ok"}, status=200)
