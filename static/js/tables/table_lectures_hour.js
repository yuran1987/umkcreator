var num_row_total_lec = 1;
var num_total_for_table_lec = "0/0/0";


function insertrow_lec(obj) {
    var num_p_p = parseInt($(obj).jexcel('getValue', 'A' + num_row_total_lec.toString()));
    var idCell = 'C' + (num_row_total_lec + 1).toString();
    var text_total = $(obj).jexcel('getValue', idCell);
    $(obj).jexcel('setValue', idCell, '');
    num_row_total_lec += 1;
    idCell = 'C' + (num_row_total_lec + 1).toString();
    $(obj).jexcel('setValue', idCell, text_total);
    //--------------------------------------------------
    num_p_p += 1;
    $(obj).jexcel('setValue', 'A' + num_row_total_lec.toString(), num_p_p);
}

function deleterow_lec(obj) {
    num_row_total_lec -= 1;
}

$('#tablelectureshour').jexcel({
    data: [
        ['1','','','','',''],
        ['','','Итого:','','',''],
    ],
    colHeaders: ['№ раздела',           '№ темы',                  'Наименование лекции',
                 'Трудоемкость (час.)', 'Формируемые компетенции', 'Методы преподавания'],
    colWidths: [ 100, 70, 200, 150, 250, 200],
    oninsertrow:insertrow_lec,
    ondeleterow:deleterow_lec,
    allowInsertColumn:false,
    wordWrap:true,
    columns: [
              { type: 'numeric' },
              { type: 'numeric' },
              { type: 'text',wordWrap:true },
              { type: 'text' },
              { type: 'text' },
              { type: 'autocomplete', source: methods_teacher_lec },
             ]
});


$('#tablelectureshour').jexcel('updateSettings', {
    cells: function (cell, col, row) {
        if(col==3) {
            if (row == num_row_total_lec) {
                    $(cell).addClass('readonly');
                    var tmp = arrText2Num(num_total_for_table_lec.split('/'));
                    $(cell).html('' + numeral(Math.round(tmp[0])).format('0') + '/' + numeral(Math.round(tmp[1])).format('0') + '/' + numeral(Math.round(tmp[2])).format('0'));
                } else {
                    $(cell).removeClass('readonly');
                    if (row == 0) {
                        num_total_for_table_lec = "0/0/0";
                    }


                    var tmp = arrText2Num($(cell).text().split('/'));
                    var curr = arrText2Num(num_total_for_table_lec.split('/'));

                    var index;
                    for (index = 0; index < tmp.length; ++index) {
                        curr[index] += tmp[index];
                    }

                    num_total_for_table_lec = numeral(curr[0]).format('0.0') + '/' + numeral(curr[1]).format('0.0') + '/' + numeral(curr[2]).format('0.0');
                }
        }
    }
});

$('#button_fill_hour_lec').on('click', function () {
      var hour_lec = arrText2Num(hours_for_calc[0].split('/'));
      hour_curr = [ hour_lec[0]/num_row_total_lec , hour_lec[1]/num_row_total_lec, hour_lec[2]/num_row_total_lec ];

      for(var i=1; i<=num_row_total_lec; i++)
      {
          $('#tablelectureshour').jexcel('setValue', 'D'+i, numeral(hour_curr[0]).format('0.0') + '/' + numeral(hour_curr[1]).format('0.0') + '/' + numeral(hour_curr[2]).format('0.0'));
          $('#tablelectureshour').jexcel('setValue', 'E'+i, competence);
      }

});