from django.contrib import admin
from django.urls import path
from core import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.home, name="home"),
    path("businesses/", views.businesses, name="businesses"),
    path("businesses/<slug:slug>/", views.business_detail, name="business_detail"),
    path("about/", views.about, name="about"),
    path("technology/", views.technology, name="technology"),
    path("paint/", views.paint, name="paint"),
    path("projects/", views.projects, name="projects"),
    path("insights/", views.insights, name="insights"),
    path("careers/", views.careers, name="careers"),
    path("partnerships/", views.partnerships, name="partnerships"),
    path("contact/", views.contact, name="contact"),
    path("contact/sent/", views.contact_sent, name="contact_sent"),
    path("privacy/", views.legal, {"kind": "privacy"}, name="privacy"),
    path("terms/", views.legal, {"kind": "terms"}, name="terms"),
]
