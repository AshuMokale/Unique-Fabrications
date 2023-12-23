from django.urls import path
from . import views
# from .views import GeneratePdf
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # path('',views.index, name='index'),
    path('', views.index, name="index"),
    path('about', views.about, name="about"),
    path('login', views.login_user, name="login"),
    path('logout', views.logout_user, name="logout"),
    path('signup', views.sign_up, name="signup"),
    path('show_users', views.show_users, name="show_users"),
    path('delete_user/<int:id>', views.delete_user, name="delete_user"),
    path('edit_user/<int:id>', views.edit_user, name="edit_user"),
    path('update_user', views.update_user, name="update_user"),
    path('services', views.services, name="services"),
    path('service/<int:id>', views.service, name="service"),
    # path('quotation', GeneratePdf.as_view(), name="quotation"),
    path('add_service', views.add_service, name="add_service"),
    path('edit_service/<int:id>', views.edit_service, name="edit_service"),
    path('update_service', views.update_service, name="update_service"),
    path('delete_service/<int:id>', views.delete_service, name="delete_service"),
    path('quotation/<int:id>', views.quotation, name="quotation"),
    path('order', views.order, name="order"),
    path('orders', views.orders, name="orders"),
    path('edit_order/<int:id>', views.edit_order, name="edit_order"),
    path('update_order', views.update_order, name="update_order"),
    path('delete_order/<int:id>', views.delete_order, name="delete_order"),
    path('payment/<int:id>', views.payment, name="payment"),
    path('feedback',views.feedback,name='feedback'),
    path('insert_feedback', views.insert_feedback, name="insert_feedback"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)