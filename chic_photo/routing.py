from django.urls import path, include
import chic_photo.views as v
hx_urlpatterns = [
   path('order_form/', v.order_form, name='order-form'),
   path('profile_form/', v.profile_form, name='profile-form'),

]


urlpatterns = [
    path('', v.index, name='index'),
    path('', include(hx_urlpatterns)),
    path('login/', v.LoginView.as_view(), name='login'),
    path('logout/', v.LogoutView.as_view(), name='logout'),
    path('register/', v.RegistrationView.as_view(), name='register'),
    path('profile/', v.profile, name='profile'),
    path('studiospaces', v.StudioSpaceList.as_view(), name='studio-spaces'),
    path('photographers', v.Photographers.as_view(), name='photographers'),
    path('orders/', v.orders, name='orders'),
    path('orders/getorderform/', v.get_order_form, name='order-form'),
    path('profile/edit_profile/', v.user_form_view, name='edit_profile'),
    path('profile/edit_photographer/', v.photographer_form_view, name='edit'),
    path('generate_invoice/<int:order_id>/', v.generate_invoice, name='generate_invoice'),
    path('cancel_order/<int:order_id>/', v.cancel_order, name='cancel_order'),
]

