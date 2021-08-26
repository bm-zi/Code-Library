from django.urls import path

from .views import (
    home_view,
    all_view,
    title_source_view, 
    add_new_code_view,
    delete_code_view,
    modify_form_view,
    modify_code_view,
    
    save_source_view,
    search_codes_view,
    
    change_favorite_view,
    help_view,
)


urlpatterns = [
    path('', home_view, name='home_view'),
    path('all/', all_view, name='all_view'),
    path('title-source/', title_source_view),
    path('new-code/', add_new_code_view, name='add_new_code_view'),
    path('delete-code/', delete_code_view, name='delete_code_view'),
    path('modify-form/<select_title>/', modify_form_view, name='modify_form_view'),
    path('modify-code', modify_code_view, name='modify_code_view'),
    path('save/', save_source_view, name='save_source_view'),
    path('search-codes/', search_codes_view, name='search_codes_view'),
    path('change-fav/', change_favorite_view, name='change_favorite_view'),
    path('help/', help_view, name='help_view'),
]