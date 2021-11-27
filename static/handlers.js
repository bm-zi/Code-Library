
function getElements() {
    /* returns a list of home page elements */
    var select_title_elem = document.getElementById('select-title');
    if (!select_title_elem.options[select_title_elem.selectedIndex]){
        select_title_elem = ''
    }
    else { 
        var select_title = select_title_elem.options[select_title_elem.selectedIndex].text;
    }

    var select_operation_elem = document.getElementById('select-operation');
    var select_operation = select_operation_elem.options[select_operation_elem.selectedIndex].text;

    var textarea_source = document.getElementById('textarea-source');
    var textarea_codeinfo = document.getElementById('textarea-codeinfo');

    return [ select_title, 
        select_operation,
        textarea_source,
        textarea_codeinfo
    ]
}


function getSelectValues(select) {
    /* 
        Function is called in another function categoryHandler().
        It takes html select element as argument and returns a list 
        of selected options, for select element with ability of 
        having multiple selections. 
    */
    var result = [];
    var options = select && select.options;
    var opt;

    for (var i=0, iLen=options.length; i<iLen; i++) {
        opt = options[i];

        if (opt.selected) {
        result.push(opt.value || opt.text);
        }
    }
    return result;
}



function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function setHeader(xhr){
    var csrftoken = getCookie('csrftoken')
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.setRequestHeader("HTTP_X_REQUESTED_WITH", "XMLHttpRequest");
    xhr.setRequestHeader("X-Requested-With", "XMLHttpRequest");
    xhr.setRequestHeader("X-CSRFToken", csrftoken);
}



function codeDisplayHandler() {  
    /* Gets content of selected code title from server and poplulates 
    the textarea. It also populates a div with information about the
    code. This function is called when changing between selected item 
    in codes title list whith id "select-title".
    */
    const select_title = getElements()[0]

    var url = '/title-source/';
    var method = "POST";

    var data = JSON.stringify({ select_title : select_title, });
    var xhr = new XMLHttpRequest();
    xhr.open(method, url)
    setHeader(xhr)
    xhr.onload = function() {
        var div_code_content = document.getElementById("code-content")
        div_code_content.hidden = false;
        var xhrResponseText = xhr.responseText;
        var jsonResponse = JSON.parse(xhrResponseText);
        textarea_source = getElements()[2];
        textarea_source.hidden = false;
        div_codeinfo = getElements()[3];
        div_codeinfo.hidden = false;
        textarea_source.innerHTML = jsonResponse.source;
        
        var str = jsonResponse.code_info
        // convert a string containg double quoted elements into an arry 
        var arr = str.match(/(".*?"|[^",\s]+)(?=\s*,|\s*$)/g);        
        var infoTable = document.getElementById('info-table');
        infoTable.rows[0].cells[0].innerHTML = arr[0];
        infoTable.rows[0].cells[1].innerHTML = arr[2].replace(/['"]+/g, '');
        infoTable.rows[1].cells[0].innerHTML = arr[1].replace(/['"]+/g, '');
        
        if (arr[3] === 'True' ){
            infoTable.rows[1].cells[1].innerHTML = 'is favorite'
        }
        else {
            infoTable.rows[1].cells[1].innerHTML = 'not favorite'
        }
        // Alternative solution, instead of populating html table:
        // div_codeinfo.innerHTML = arr;
        
    }
    xhr.send(data)
    return
}



function saveSourceHandler() {
    
    select_title = getElements()[0]
    textarea_source = getElements()[2].value;
    var url = '/save/';
    var data = JSON.stringify({ select_title: select_title, textarea_source: textarea_source});
    var method = "POST";
    var xhr = new XMLHttpRequest();
    xhr.open(method, url);
    setHeader(xhr)
    xhr.onload = function () {
        window.location.href =  "";
    };
    xhr.send(data)
    return
}



function modifyHandler() {
    select_title = getElements()[0]
    

        var url = '/modify-form/' + select_title + '/';
        var data =  JSON.stringify({ select_title: select_title });
        var method = "POST";
        var xhr = new XMLHttpRequest();
        xhr.open(method, url);
        setHeader(xhr)
        xhr.onload = function () {
            var response_url = xhr.responseURL;
            window.location.href =  response_url;
        };
        xhr.send(data)
        return
}



function favoriteHandler() {
    select_title = getElements()[0]
    console.log(select_title)
    var url = '/change-fav/';
    var data =  JSON.stringify({ select_title: select_title });
    var method = "POST";
    var xhr = new XMLHttpRequest();
    xhr.open(method, url);
    setHeader(xhr)
    xhr.onload = function () {
        window.location = window.location;
        window.location.href = "/";
    };
    xhr.send(data)
    return
};



function deleteHandler() {
    select_title = getElements()[0]

    var url = '/delete-code/';
    var data =  JSON.stringify({ select_title: select_title });
    var method = "POST";
    var xhr = new XMLHttpRequest();
    xhr.open(method, url);
    setHeader(xhr)
    xhr.onload = function () {
        var data = xhr.responseText;
        var jsonResponse = JSON.parse(data);
        alert(jsonResponse.message);
        window.location = window.location; // F5
    };
    xhr.send(data)
    return
}

function searchHandler() {
    
}



function categoryHandler() {
    var el = document.getElementsByName('select-category')[0];
    var select_categories = getSelectValues(el);
    

    var url = '/search-by-categories/';
    var data = JSON.stringify({ select_categories: select_categories, });
    var method = "POST";
    var xhr = new XMLHttpRequest();
    
    xhr.open(method, url);
    setHeader(xhr)
    xhr.onload = function () {

        var data = xhr.responseText;
        var jsonResponse = JSON.parse(data);
        
        options = jsonResponse.codes_filtered_by_categories
        
        if (options == "No code found for selected categories."){
            $("#options-number").text("items found: 0");
        }
        else {
            var countStr = "items found: " + options.length;
            $("#options-number").text(countStr);
        }

        var code_items_elem = document.getElementById('select-title');

        var length = code_items_elem.options.length;
        for (i = length-1; i >= 0; i--) {
            code_items_elem.options[i] = null;
        }

        for(var i = 0; i < options.length; i++) {
            var opt = options[i];
            
            var el = document.createElement("option")
            el.text = opt;
            el.value = opt;
        
            code_items_elem.appendChild(el);
        }
    }
    xhr.send(data)
    return
}



function selectMinHandler(){
    var el = document.getElementById('select-title');
    var opts = $('#select-title option').length;
    el.setAttribute("size", opts );
}

function oneRowHandler(){
    el = document.getElementById('select-title');
    el.setAttribute("size", 1 );
}


function textareaMaxHandler(){
        var page_up = document.getElementById("page-up");
        var page_down = document.getElementById("page-down")
        page_up.hidden = false;    
        page_down.hidden = false;

        var el = document.getElementById("textarea-source");
        var count = el.value.split("\n").length;
        $('#textarea-source').attr('rows', count);
}


function textareaMinHandler(){
    var page_down = document.getElementById("page-down")
    var page_up = document.getElementById("page-up");
    page_down.hidden = true;
    page_up.hidden = true; 
    var el = document.getElementById("textarea-source");
    var count = el.value.split("\n").length;
    $('#textarea-source').attr('rows', 6);
}


function textareaFullScreen(){
    document.querySelector('#textarea-source').style.width= "100vw";
    document.querySelector('#textarea-source').style.height="100vh";
}


function downloadCodeHandler(){
    var textareaVal = document.getElementById('textarea-source').value;
    var filename = "output.txt";
    download(textareaVal, filename);

    function download(textareaVal, filename){
        var element = document.createElement('a');
        element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(textareaVal));
        element.setAttribute('download', filename);
        element.style.display = 'none';
        document.body.appendChild(element);
        element.click();
        document.body.removeChild(element);
    }
    window.location = window.location;
}



function languageHandler() {
    var el = document.getElementById('select-language');
    var selected_language = el.options[el.selectedIndex].text;
    var url = '/filter-by-language/';
    var data = JSON.stringify({selected_language:selected_language,});
    var method = "POST";
    var xhr = new XMLHttpRequest();
    xhr.open(method, url);
    setHeader(xhr)
    xhr.onload = function () {
        var data_in = xhr.responseText;
        var jsonResponse = JSON.parse(data_in);
        options = jsonResponse.codes_filtered_by_language;
        var countStr = "items found: " + options.length
        $("#options-number").text(countStr);
        var code_items_elem = document.getElementById('select-title');
        var length = code_items_elem.options.length;

        for (i = length-1; i >= 0; i--) {
            code_items_elem.options[i] = null;
        }

        for(var i = 0; i < options.length; i++) {
            var opt = options[i];
            
            var el = document.createElement("option")
            el.text = opt;
            el.value = opt;
        
            code_items_elem.appendChild(el);
        }
    };
    xhr.send(data)
    return
}

function countOptions(){
    var number=$("#select-title").children('option').length;
    $("#options-number").text(number)
}



/*
    if (elem != 'NaN' && elem != null && elem != '') {
        elem.addEventListener('onchange', handlerFunction)
    }
*/