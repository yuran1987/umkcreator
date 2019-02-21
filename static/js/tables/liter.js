var num_row_total = 1;
var num_total_for_table = "0/0/0";
var literature_list = []; //Писок литературы который найден


function insertrow_lit(obj) {
    num_row_total += 1;
}

function deleterow_lit(obj) {
    num_row_total -= 1;
}


//-------------------------------ЗАГРУЗКА----------------------------------------------------------
$.when( $.ready ).then(function() {
    $("#button_add_to_table").prop("disabled", true);
    data = $('#id_data_field').val();
    if(data.length>0) {
        if(JSON.parse(data).length>1) {
            num_row_total = JSON.parse(data).length - 1;
            $('#tablejexcel').jexcel('setData', data); // Перечень тем занятий
        }
    }
});
//-------------------------------СОХРАНЕНИЕ----------------------------------------------------------
$('#btn_save').on('click', function () {
    data = $('#tablejexcel').jexcel('getData');//------ Перечень тем  занятий
    if(data.length>0) $('#id_data_field').val(JSON.stringify(data));
    literature_list.length = 0;
});


$('#tablejexcel').jexcel({
    data: [
        ['Основная','','','','','','','','',''],
        ['Дополнительная','','','','','','','','',''],
    ],
    colHeaders: ['№', 'Название учебной и учебно методической литературы, автор, изд-во', 'Год издания', 'Вид издания', 'Вид занятий', 'Кол-во экземпляров в БИК, шт.', 'Контингент', 'Обеспеченность, %', 'Место хранения', 'Наличие эл. варианта в ЭБС ТИУ'],
    colWidths: [ 100, 300, 100, 100, 100, 220, 100, 150, 120, 200],
    colAlignments: [ 'center', 'center', 'center','center', 'center', 'center','center', 'center', 'center', 'center' ],
    tableOverflow:true,
    tableHeight:'300px',
    oninsertrow:insertrow_lit,
    ondeleterow:deleterow_lit,
    allowInsertColumn:false,
    columns: [
              { type: 'text' },
              { type: 'text', wordWrap:true },
              { type: 'numeric' },
              { type: 'text' },
              { type: 'autocomplete', source:[ 'Лек','Практ','Лаб','Самост','КР','Лек.,Практ.','Лек.,Лаб.', 'Практ.,Лаб.', 'Лек.,Практ.,Лаб.' ] },
              { type: 'text' },
              { type: 'text' },
              { type: 'text' },
              { type: 'text' },
              { type: 'text' },
             ]
});

$('#start_bsearch').on('click', function () {
    var type_search = $("#id_type_search_system").val() //тип поисковой системы urait или lanbook

    $.getJSON("get/" + type_search +'/' + $('#id_liter_search').val().split(" ").join("+") + "/", function(data) {//отправка запроса сайту Юрайт
        var items = [];
        $("#id_liters_list").find('option').remove();//$("#id_liters_list").find('option').not(':first').remove();
        literature_list.length = data.length;

        for(var i=0; i<data.length; i++)
        {
          var str = data[i]['name'] +" " + data[i]['author'] +  " // " + data[i]['place'] + " " + data[i]['year'] + " " + data[i]['pages'] + "c.";
          var html_code = '<option value="val:' + i + '">' + str + '</option>';
          $("#id_liters_list").append(html_code);
          literature_list[i] = data[i];
        }
       console.log("success");
       $("#button_add_to_table").prop("disabled", false);
    })
    .fail(function() {
      alert('По вашему запросу ничего не найдено!');
      $("#button_add_to_table").prop("disabled", true);
    });
});

$('#button_add_to_table').on('click', function () {
    var n = parseInt($("#id_liters_list").val().split(':')[1]);

    $('#tablejexcel').jexcel('setValue', 'B'+num_row_total, literature_list[n]['author'] + " " + literature_list[n]['name'] + " // " + literature_list[n]['place'] + " " + literature_list[n]['pages'] + "с." + " ISBN:" + literature_list[n]['isbn']);
    $('#tablejexcel').jexcel('setValue', 'C'+num_row_total, literature_list[n]['year']);
    $('#tablejexcel').jexcel('setValue', 'D'+num_row_total, literature_list[n]['type']);
    $('#tablejexcel').jexcel('setValue', 'I'+num_row_total, literature_list[n]['place']);
    $('#tablejexcel').jexcel('setValue', 'F'+num_row_total, 'неограниченный доступ');
    $('#tablejexcel').jexcel('setValue', 'J'+num_row_total, literature_list[n]['URL']);
    $('#tablejexcel').jexcel('setValue', 'H'+num_row_total, 100);

    $('#tablejexcel').jexcel('insertRow', 1);
});