from django.http import request
from django.http import response
from django.shortcuts import render
from django.http.response import JsonResponse, HttpResponseRedirect, Http404
from django.shortcuts import render, HttpResponse, redirect
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q, fields
import json
from datetime import datetime, timedelta
from django.utils import timezone
from django.urls import reverse
from .models import Category, CodeLibrary, Language, Source



def queries():
    """
    Returns a dictionary of data containing list of favorite codes,
    and list of code categories and avilable programming languages.
    Data is retrieved from two tables: Category and CodeLibrary.

    This dictionary of data will be used in other view functions.
    """

    qs1 = Category.objects.all()
    categories_items = [x.serialize() for x in qs1]
    categories = [c['category'] for c in categories_items]

    qs2 = Language.objects.all()
    language_items = [x.serialize() for x in qs2]
    languages = [l['language'] for l in language_items]

    all_codes = CodeLibrary.objects.all()
    total_no= len(all_codes)

    title_items = [x.serialize() for x in all_codes]
    titles = [t['title'] for t in title_items]

    favorites = CodeLibrary.objects.filter(is_favorite=True)
    favorites_no = len(favorites)

    data = {
        'titles': titles,
        'categories': categories,
        'languages': languages,
        'favorites_no': favorites_no,
        'total_no': total_no,
    }

    return data



def home_view(request):
    """ 
        Home Page view function - URL: "/"
        shows a list of favorites codes
    """

    # titles in favorite
    titles = CodeLibrary.objects.filter(is_favorite=True)
    favorites_no =  queries().get('favorites_no')

    languages = queries().get('languages')

    categories = queries().get('categories')
    total_no = queries().get('total_no')


    return render(request, 'home.html', context={
        "categories": categories,
        'titles': titles,
        'languages': languages,
        'favorites_no': favorites_no,
        'total_no': total_no,
        'alltitles' : '- Listing Favorite Codes'
    })



def all_view(request):
    """ 
        url: "/all"
        Shows in home page a list of all codes.
    """
    data = queries()
    data["alltitles"] = '- Listing All Codes'
    return render(request, 'home.html', context=data)




@csrf_exempt
def title_source_view(request):
    """
        url : "/title-source"
        handles the request for selected code item

        JSON response is populated in codes title list and 
        code information text area by get_content_of_code_item.js 
    """

    if request.method =='POST':
        
        post_data = json.loads(request.body.decode("utf-8"))
        title = post_data.get('select_title')

        qs = CodeLibrary.objects.filter(title=title)
        
        if not qs.exists():
            return JsonResponse({"error":"object not exists"}, 
                                    status=404)
        
        obj = qs.first()
        title_obj = getattr(obj, 'title')
        created_at_obj =  getattr(obj, 'created_at')
        language_obj = getattr(obj, 'language')

        category_objs = getattr(obj, 'category').all().values()
        a_list = []
        for item in category_objs:
            a_list.append(item.get("category"))
        category_obj = ", ".join(a_list)

        is_favorite_obj = getattr(obj, 'is_favorite')
        source_obj = getattr(obj, 'source')
        
        # source_obj is an object not a value, this object is from 
        # class field named as source in class CodeLibrary

        # Retrive value of source object
        source = getattr(source_obj, 'source')
        
        code_info = """{l}, "{c}", "{cta}", {isf}""".format(
                        l=language_obj, 
                        cta=created_at_obj, 
                        isf=is_favorite_obj,
                        c=category_obj)
        data = { 
            "code_info": code_info,
            'source': source,
        }
    
        return JsonResponse(data, status=200)

    data = { 'warning: ' :'no title display'}
    return JsonResponse(data, status=200)




def add_new_code_view(request):
    """
        url: "/new-code"

        Opens a new page with a form for adding new code.
        Renders 'add_new_code.html' and saves form data in database.
    """

    if request.method == 'POST' and request.POST['title']:
        t = request.POST['title']
        l = request.POST['language']
        c = request.POST.getlist('category')
        s = request.POST['source']
        f = request.POST.get('is_favorite', False)

        cl = CodeLibrary()

        #### title
        cl.title = t
        #### language - One To Many
        cl.language = Language.objects.get(language=l)
        #### source - One To One
        source_obj = Source.objects.create(source=s)
        source_obj.save()
        source_id = source_obj.id
        cl.source = Source.objects.get(id=source_id)
        #### favorite - Boolean
        if f == 'on':
            cl.is_favorite = True
        else:
            cl.is_favorite = False

        #### Save a row in CodeLibrary table        
        cl.save()

        #### After saving object, define manay to many relationship
        for elem in c:
            category_obj = Category.objects.filter(category=elem).first()
            obj_id = category_obj.id
            cl.category.add(obj_id)

    qs1 = Category.objects.all()
    categories_items = [x.serialize() for x in qs1]
    categories = [c['category'] for c in categories_items]

    qs2 = Language.objects.all()
    language_items = [x.serialize() for x in qs2]
    languages = [l['language'] for l in language_items]

    return render(request, 'add_new_code.html', context={
                    "categories": categories,
                    "languages": languages
                })



@csrf_exempt
def delete_code_view(request):
    """
        url: "/delete-code"

        Deletes selected code from database and is handled by script 
        'delete_selected_code.js'.
    """

    if request.method =='POST':
        try:
            data_from_post = json.load(request)['select_title']
            qs = CodeLibrary.objects.filter(title=data_from_post)
        
            if qs.exists():
                obj = qs.first()
                title = getattr(obj, 'title')
                obj.delete()
                
                message = '"' + title + '" has been deleted.'
                status = 200
        
        except:
            message = "No code has been deleted.\nTry to select a code item properly first!"
            status = 404
    
        return JsonResponse({ 'message': message }, status=status)




@csrf_exempt
def modify_form_view(request, select_title):
    """
        url: "/modify-form/<select_title>"

        It just renders modify_form.html with prefilled data 
        fetched from home page handled by "modify_selected_code.js"
    """
    check_cl = CodeLibrary.objects.filter(title=select_title).exists()

    if check_cl:
        cl = CodeLibrary.objects.filter(title=select_title).first()
        source = cl.serialize().get('source')
        categories = queries().get('categories')
        languages = queries().get('languages')

        return render(request, 'modify_form.html/', context={
                        "select_title": select_title,
                        "categories": categories,
                        "languages": languages,
                        "source": source
                    })
    else:
        return redirect('/')



def modify_code_view(request):
    """
    Form data in template 'modify_form.html' comes to server 
    as a post request and modified code information will be saved in 
    database.
    """

    if request.method == 'POST':
        # gets from form:
        originalTitle = request.POST.get('original-title')
        ttl = request.POST.get('title') 
        lang = request.POST.get('language') 
        categ = request.POST.getlist('category')
        src = request.POST.get('source') 
        fvt = request.POST.get('is_favorite')

       
        CodeLibrary.objects.filter(title=originalTitle).update(
                                                           title=ttl)

        newcode = CodeLibrary.objects.filter(title=ttl)

        lang_id = Language.objects.get(language=lang).id
        newcode.update(language=lang_id)

        src_id = newcode.first().source.id
        Source.objects.filter(id=src_id).update(source=src)

        if fvt == 'on':
            CodeLibrary.objects.filter(title=ttl).update(
                                                    is_favorite=True)
        else:
            CodeLibrary.objects.filter(title=ttl).update(
                                                   is_favorite=False)
        
        CodeLibrary.objects.filter(title=ttl).first().category.clear()

        for elem in categ:
            cat_id = Category.objects.filter(
                                        category=elem).first().id

            newcode.first().category.add(cat_id)

    data = queries()
    return render(request, 'home.html', context=data)




@csrf_exempt
def save_source_view(request):
    """
    post request with source code fetched from textarea will be
    send to server with 'save_source.js' and after updating the 
    source code in database, response will be populated in text
    area in home page template.

    """
    if request.method == 'POST':
        data = request.body
        data = json.loads(data)
        select_title = data.get('select_title')
        textarea_source = data.get('textarea_source')
        obj = CodeLibrary.objects.filter(title=select_title)
        if obj.exists():
            src_id = obj.first().source.id
            Source.objects.filter(id=src_id).update(
                                            source=textarea_source)
        data = {
            'select_title': select_title
        }
        return JsonResponse(data)

    data = {'Warning:':'Save was not successful'}
    return JsonResponse(data, status=404) 
        



def search_codes_view(request):
    """
    url: "/search-codes"

    Search query in titles and code sources.
    AJAX jquey in "search_codes.js" sends data as a get request and 
    populates the title list when the server response is successful.
    """
    
    data = queries()
    
    if request.method == 'GET':
        
        # Check if the form 'form-search-code' is sending values 
        # from fields to this view function

        if request.GET['q'] :  code_pattern = request.GET['q']  
        if request.GET['days']: 
            day_str = request.GET['days']
            how_many_days = int(day_str.strip())
        if request.GET['select-language'] : 
            language_selected = request.GET['select-language']
        if request.GET.getlist('select-category'): 
            categories_list = request.GET.getlist('select-category')


        # Can have 11 search combinations - 11 if conditional

        # 1
        if ( request.GET['q'] and   
                not request.GET['days'] and 
                not request.GET['select-language'] and 
                not request.GET.getlist('select-category')
                ) :
            qst = CodeLibrary.objects.filter(
                Q(title__icontains=code_pattern)|Q(source__source__icontains=code_pattern)
            )
        
        # 2
        if ( not request.GET['q'] and   
                    request.GET['days'] and 
                    not request.GET['select-language'] and 
                    not request.GET.getlist('select-category')
                    ) :
            qst = CodeLibrary.objects.filter(
                created_at__gte=timezone.now()-timedelta(
                                                days=how_many_days))
        # 3
        if ( not request.GET['q'] and   
                    not request.GET['days'] and 
                    request.GET['select-language'] and 
                    not request.GET.getlist('select-category')
                    ) :
            qst = CodeLibrary.objects.filter(
                language__language=language_selected).all().distinct()

        # 4
        if ( not request.GET['q'] and   
                    not request.GET['days'] and 
                    not request.GET['select-language'] and 
                    request.GET.getlist('select-category')
                    ) :
            qst = CodeLibrary.objects.filter(
                category__category__in=categories_list).all().distinct()

        # 5
        if ( request.GET['q'] and   
                    request.GET['days'] and
                    not request.GET['select-language'] and
                    not request.GET.getlist('select-category')
                    ) :    
            qst = CodeLibrary.objects.filter(
                Q(title__icontains=code_pattern)|Q(source__source__icontains=code_pattern)
            ).filter(
                created_at__gte=timezone.now()-timedelta(
                                                days=how_many_days))


        # 6
        if ( request.GET['q'] and   
                    not request.GET['days'] and 
                    request.GET['select-language'] and 
                    not request.GET.getlist('select-category')
                    ) :   
            qst = CodeLibrary.objects.filter(
                Q(title__icontains=code_pattern)|Q(source__source__icontains=code_pattern)
            ).filter(
                language__language=language_selected).all().distinct()
            

        # 7
        if ( request.GET['q'] and   
                    not request.GET['days'] and 
                    not request.GET['select-language'] and 
                    request.GET.getlist('select-category')
                    ) :    
            qst = CodeLibrary.objects.filter(
                Q(title__icontains=code_pattern)|Q(source__source__icontains=code_pattern)
                ).filter(
                        category__category__in=categories_list).all().distinct()

        # 8
        if ( not request.GET['q'] and   
                    request.GET['days'] and 
                    request.GET['select-language'] and 
                    not request.GET.getlist('select-category')
                    ) :    
            qst = CodeLibrary.objects.filter(
                created_at__gte=timezone.now()-timedelta(
                                                days=how_many_days)).filter(
                language__language=language_selected).all().distinct()
  

        # 9
        if ( not request.GET['q'] and
                    request.GET['days'] and 
                    not request.GET['select-language'] and 
                    request.GET.getlist('select-category')
                    ) : 
            qst = CodeLibrary.objects.filter(
                created_at__gte=timezone.now()-timedelta(days=how_many_days)).filter(
                        category__category__in=categories_list).all().distinct().filter(
                            category__category__in=categories_list).all().distinct()


        # 10
        if ( not request.GET['q'] and
                not request.GET['days'] and 
                not request.GET['select-language'] and 
                not request.GET.getlist('select-category')
                ):
            qst = CodeLibrary.objects.all()

        # 11
        if ( request.GET['q'] and
                request.GET['days'] and 
                request.GET['select-language'] and 
                request.GET.getlist('select-category')
                ):
            qst = CodeLibrary.objects.filter(
                Q(title__icontains=code_pattern)|Q(source__source__icontains=code_pattern)).filter(
                created_at__gte=timezone.now()-timedelta(
                                                days=how_many_days)).filter(
                language__language=language_selected).all().distinct().filter(
                category__category__in=categories_list).all().distinct()

        # 12
        if ( not request.GET['q'] and
                not request.GET['days'] and 
                request.GET['select-language'] and 
                request.GET.getlist('select-category')
                ):
            qst = CodeLibrary.objects.filter(
                language__language=language_selected).all().distinct().filter(
                category__category__in=categories_list).all().distinct()


        result = []
        if qst.exists():
            for elem in qst:
                result.append(elem.title)
            countopts = len(result)

        else:
            error_msg = 'No result found'
            result = [error_msg,]
            countopts = 0

        data['titles'] = result
        data['countopts'] = 'search result: ' + str(countopts)
        return render(request, 'home.html', context=data)

    result = ['Search field is empty!',]
    data['titles'] = result

    return render(request, 'home.html', context=data)


def change_favorite_view(request):
    """
        url: "/change-fav"

        Toggles the value of is_favorite field in database.
        AJAX jQuery post request in "change_favorite.js" handles the 
        job.
    """
    if request.method == 'POST':
        
        post_data = json.loads(request.body.decode("utf-8"))
        title = post_data.get('select_title')

        selected_code = CodeLibrary.objects.filter(title=title)
        if selected_code.exists():
            fav_val = CodeLibrary.objects.filter(
                                title=title).first().is_favorite
            
            if fav_val:
                CodeLibrary.objects.filter(
                        title=title).update(is_favorite=False)
            else:
                CodeLibrary.objects.filter(
                            title=title).update(is_favorite=True)


        qst = CodeLibrary.objects.filter(title=title)
        
        result = []
        for elem in qst:
            print(elem)
            result.append(elem.title)

        data = {'result': result}
        return JsonResponse(data)

    # else: 
    #     data = {'error': 'query not successful!'}     
    #     return JsonResponse(data)


def help_view(request):
    favorites_no =  queries().get('favorites_no')
    total_no = queries().get('total_no')
    
    return render(request, 'help.html', context={
        'favorites_no': favorites_no,
        'total_no': total_no,
    })