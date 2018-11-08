var num_row_total_samost = 1;
var num_total_for_table_samost = "0/0/0";

function insertrow_samost(obj) {
    var num_p_p = parseInt($(obj).jexcel('getValue', 'A' + num_row_total_samost.toString()));
    var idCell = 'C' + (num_row_total_samost + 1).toString();
    var text_total = $(obj).jexcel('getValue', idCell);
    $(obj).jexcel('setValue', idCell, '');
    num_row_total_samost += 1;
    idCell = 'C' + (num_row_total_samost + 1).toString();
    $(obj).jexcel('setValue', idCell, text_total);
    //--------------------------------------------------
    num_p_p += 1;
    $(obj).jexcel('setValue', 'A' + num_row_total_samost.toString(), num_p_p);
}

function deleterow_samost(obj) {
    num_row_total_samost -= 1;
}

$('#tablesamosthour').jexcel({
    data: [
        ['1','','','','',''],
        ['','','Итого:','','',''],
    ],
    colHeaders: ['№ п/п', '№ раздела (модуля) и темы', 'Наименование темы',
                 'Трудоемкость (час.)', 'Виды контроля', 'Формируемые компетенции'],
    colWidths: [ 100, 200, 200, 150, 250, 200],
    oninsertrow: insertrow_samost,
    ondeleterow: deleterow_samost,
    allowInsertColumn:false,
    columns: [
              { type: 'numeric' },
              { type: 'text' },
              { type: 'autocomplete', source: type_samost_work },
              { type: 'text' },
              { type: 'autocomplete', source: forms_control },
              { type: 'text' },
             ]
});

$('#tablesamosthour').jexcel('updateSettings', {
    cells: function (cell, col, row) {
        $(cell).css('color', '#000000');
        if(col==3) {
            if (row == num_row_total_samost) {
                    $(cell).addClass('readonly');
                    var tmp = arrText2Num(num_total_for_table_samost.split('/'));
                    var hour  = arrText2Num(hours_for_calc[4].split('/'));
                    if(tmp[0] != hour[0] || tmp[1] != hour[1] || tmp[2] != hour[2]){
                        $(cell).css('color', '#ff0000');
                        $(cell).html(num_total_for_table_samost);
                    }else{
                        $(cell).css('color', '#000000');
                        $(cell).html('' + numeral(Math.round(tmp[0])).format('0') + '/' + numeral(Math.round(tmp[1])).format('0') + '/' + numeral(Math.round(tmp[2])).format('0'));
                    }
                } else {
                    $(cell).removeClass('readonly');
                    if (row == 0) {
                        num_total_for_table_samost = "0/0/0";
                    }
                    //num_total_for_table_samost += parseFloat($(cell).text().replace(/,/, '.'));
                    var tmp = arrText2Num($(cell).text().split('/'));
                    var curr = arrText2Num(num_total_for_table_samost.split('/'));

                    for (var index = 0; index < tmp.length; ++index) {
                        curr[index] += tmp[index];
                    }
                    num_total_for_table_samost = numeral(curr[0]).format('0.0') + '/' + numeral(curr[1]).format('0.0') + '/' + numeral(curr[2]).format('0.0');
                }
        }
    }
});

$('#button_fill_hour_samost').on('click', function () {
      var hour_samost = arrText2Num(hours_for_calc[4].split('/'));
      hour_curr = [hour_samost[0]/num_row_total_samost , hour_samost[1]/num_row_total_samost, hour_samost[2]/num_row_total_samost ];

      for(var i=1; i<=num_row_total_samost; i++)
      {
          $('#tablesamosthour').jexcel('setValue', 'D'+i, numeral(hour_curr[0]).format('0.0') + '/' + numeral(hour_curr[1]).format('0.0') + '/' + numeral(hour_curr[2]).format('0.0'));
          $('#tablesamosthour').jexcel('setValue', 'F'+i, competence);
      }

});