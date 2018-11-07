var num_row_total_sec = 1;
var num_total_for_tablesectionshour = ['empty','0/0/0', '0/0/0', '0/0/0', '0/0/0', '0/0/0', '0/0/0', '0/0/0', '0'];
var num_total_for_tablesectionshour_right_total = ['0/0/0','0/0/0'];

function get_digits(n) {
    n = (typeof n == 'string') ? n : n.toString();
    if (n.indexOf('e') !== -1) return parseInt(n.split('e')[1]) * -1;
    var separator = (1.1).toString().split('1')[1];
    var parts = n.split(separator);
    return parts.length > 1 ? parts[parts.length - 1].length : 0;
}

function insertrow(obj) {
    var num_p_p = parseInt($(obj).jexcel('getValue', 'A'+num_row_total_sec.toString()));
    var idCell = 'B'+ (num_row_total_sec+1).toString();
    var text_total = $(obj).jexcel('getValue', idCell);
    $(obj).jexcel('setValue', idCell, ' ');
    num_row_total_sec += 1;
    idCell = 'B'+ (num_row_total_sec+1).toString();
    $(obj).jexcel('setValue', idCell, text_total);
    //--------------------------------------------------
    num_p_p +=1;
    $(obj).jexcel('setValue', 'A'+num_row_total_sec.toString(), num_p_p);
    //-----------------------------------------------------------
    num_total_for_tablesectionshour_right_total.push('0/0/0');
}

deleterow = function(obj) {
    num_total_for_tablesectionshour_right_total.pop();
    num_row_total_sec -= 1;
}
//Разделы (модули), темы дисциплин ви виды занятий
function arrText2Num(arr) {
    var result = new Array(arr.length);
    var index;
    for (index = 0; index < arr.length; ++index) {
          result[index] = parseFloat(arr[index].replace(/,/, '.'));
    }
    return result;
}

$('#tablesectionshour').jexcel({
    data: [
        ['1','','','','','','','',''],
        ['2','Итого:','','','','','','',''],
    ],
    colHeaders: ['№ п/п', 'Наименование разделов дисциплины', 'Лекции, час.',
                 'Практ. зан., час.', 'Лаб. зан., час.', 'Семинары, час.', 'СРС, час.',
                 'Всего, час.', 'Из них в интеракт. форме обуч., час.'],
    colWidths: [ 50, 300, 100, 100, 100, 120, 100, 100, 300 ],
    oninsertrow:insertrow,
    ondeleterow:deleterow,
    allowInsertColumn:false,
    wordWrap:true,
    columns: [
              { type: 'numeric' },
              { type: 'text' },
              { type: 'text' }, //mask:'##,##/##,##/##,##', options:{ reverse: true }
              { type: 'text' },
              { type: 'text' },
              { type: 'text' },
              { type: 'text' },
              { type: 'text', readOnly: true },
              { type: 'text' },
              ]
});

$('#tablesectionshour').jexcel('updateSettings', {
    cells: function (cell, col, row) {
       if (col > 1) {
            if (row == (num_row_total_sec - 1) && (col != 7)) {
                   $(cell).removeClass('readonly');
            }else {
              if (row == num_row_total_sec && (col != 7)) {
                    $(cell).addClass('readonly');
              }
            }
            if (row == num_row_total_sec) {
                var hour = arrText2Num(hours_for_calc[col-2].split('/'));
                if (col != 8){
                    var tmp = arrText2Num(num_total_for_tablesectionshour[col].split('/'));
                    if((hour[0]!=tmp[0] || hour[1]!=tmp[1] || hour[2]!=tmp[2]) && col!=5){
                        $(cell).css('color', '#ff0000');
                        $(cell).html(num_total_for_tablesectionshour[col]);
                    }else {
                        $(cell).css('color', '#000000');
                        $(cell).html('' + numeral(Math.round(tmp[0])).format('0') + '/' + numeral(Math.round(tmp[1])).format('0') + '/' + numeral(Math.round(tmp[2])).format('0'));
                    }
                }
                else{
                    var tmp = parseFloat(num_total_for_tablesectionshour[col]);
                    if(tmp != hour){
                        $(cell).css('color', '#ff0000');
                        $(cell).html(num_total_for_tablesectionshour[col]);
                    }else {
                        $(cell).css('color', '#000000');
                        $(cell).html('' + numeral(Math.round(tmp)).format('0'));
                    }
                }

            } else {
                $(cell).css('color', '#000000');
                if (col < 8) {
                    if (row == 0) {
                        num_total_for_tablesectionshour[col] = '0/0/0';
                    }

                    var tmp = arrText2Num($(cell).text().split('/'));
                    var curr = arrText2Num(num_total_for_tablesectionshour[col].split('/'));

                    var index;
                    for (index = 0; index < tmp.length; ++index) {
                        curr[index] += tmp[index];
                    }

                    num_total_for_tablesectionshour[col] = numeral(curr[0]).format('0.00') + '/' + numeral(curr[1]).format('0.00') + '/' + numeral(curr[2]).format('0.00');

                }else{

                    if(col==8){//столбец часы в интерактивной форме
                        if (row == 0) {
                            num_total_for_tablesectionshour[col] = '0';
                        }
                        num_total_for_tablesectionshour[col] = numeral(parseFloat(num_total_for_tablesectionshour[col]) + parseFloat($(cell).text())).format('0.00');
                    }
                }
            }
        }
        if(col == 7) {
            $(cell).css('color', '#000000');
            $(cell).html('' + num_total_for_tablesectionshour_right_total[row]);
        }else{
            if (col == 0) {
                  num_total_for_tablesectionshour_right_total[row] = '0/0/0';
            }
            var tmp = arrText2Num($(cell).text().split('/'));
            var curr = arrText2Num(num_total_for_tablesectionshour_right_total[row].split('/'));

            var index;
            for (index = 0; index < tmp.length; ++index) {
                curr[index] += tmp[index];
            }

            format_str = ["0.", "0.", "0."];

            for(var i=0; i<3; i++) {
                for (var j = 1; j <= get_digits(curr[i]); j++)
                    format_str[i] += "0"
            }

            num_total_for_tablesectionshour_right_total[row] = numeral(curr[0]).format(format_str[0]) + '/' + numeral(curr[1]).format(format_str[1]) + '/' + numeral(curr[2]).format(format_str[2]);
        }
    }


});

$('#button_fill_hour_sections').on('click', function () {
      console.log('button_fill_hour_lec');
      var hour_lec = arrText2Num(hours_for_calc[0].split('/'));
      var hour_prakt = arrText2Num(hours_for_calc[1].split('/'));
      var hour_labs = arrText2Num(hours_for_calc[2].split('/'));
      var hour_samost = arrText2Num(hours_for_calc[4].split('/'));
      var hour_interakiv = parseInt(hours_for_calc[6]);

      var format_str_lec = ['0.', '0.', '0.']
      var format_str_prakt = ['0.', '0.', '0.']
      var format_str_labs = ['0.', '0.', '0.']
      var format_str_samost = ['0.', '0.', '0.']
      var format_str_interaktiv = '0.';


      for(var i=0; i<3; i++)
      {
          for(var j=1; j<=get_digits(hour_lec[i]/num_row_total_sec) && j<=3; j++)
            format_str_lec[i] += "0"

          for(var j=1; j<=get_digits(hour_prakt[i]/num_row_total_sec) && j<=3; j++)
            format_str_prakt[i] += "0"

          for(var j=1; j<=get_digits(hour_labs[i]/num_row_total_sec) && j<=3; j++)
            format_str_labs[i] += "0"

          for(var j=1; j<=get_digits(hour_samost[i]/num_row_total_sec) && j<=3; j++)
            format_str_samost[i] += "0"
      }

      for(var j=1; j<=get_digits(hour_interakiv/num_row_total_sec) && j<=3; j++)
            format_str_interaktiv += "0"

      for(var i=1; i<=num_row_total_sec; i++)
      {
          $('#tablesectionshour').jexcel('setValue', 'C'+i, numeral(hour_lec[0]/num_row_total_sec).format(format_str_lec[0]) + '/' +
                                                            numeral(hour_lec[1]/num_row_total_sec).format(format_str_lec[1]) + '/' +
                                                            numeral(hour_lec[2]/num_row_total_sec).format(format_str_lec[2])); //заполнение лекции
          $('#tablesectionshour').jexcel('setValue', 'D'+i, numeral(hour_prakt[0]/num_row_total_sec).format(format_str_prakt[0]) + '/' +
                                                            numeral(hour_prakt[1]/num_row_total_sec).format(format_str_prakt[1]) + '/' +
                                                            numeral(hour_prakt[2]/num_row_total_sec).format(format_str_prakt[2])); //заполнение практ
          $('#tablesectionshour').jexcel('setValue', 'E'+i, numeral(hour_labs[0]/num_row_total_sec).format(format_str_labs[0]) + '/' +
                                                            numeral(hour_labs[1]/num_row_total_sec).format(format_str_labs[1]) + '/' +
                                                            numeral(hour_labs[2]/num_row_total_sec).format(format_str_labs[2])); //заполнение лаборат
          $('#tablesectionshour').jexcel('setValue', 'F'+i, '0/0/0'); //заполнение семинар
          $('#tablesectionshour').jexcel('setValue', 'G'+i, numeral(hour_samost[0]/num_row_total_sec).format(format_str_samost[0]) + '/' +
                                                            numeral(hour_samost[1]/num_row_total_sec).format(format_str_samost[1]) + '/' +
                                                            numeral(hour_samost[2]/num_row_total_sec).format(format_str_samost[2])); //заполнение самост

          $('#tablesectionshour').jexcel('setValue', 'I'+i, numeral(hour_interakiv/num_row_total_sec).format(format_str_interaktiv));
      }

});