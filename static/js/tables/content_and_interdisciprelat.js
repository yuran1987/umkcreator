$('#tablecontentOfSections').jexcel({
    colHeaders: ['№ п/п', 'Наименование раздела дисциплины', 'Содержание раздела дисциплины'],
    colWidths: [ 50, 300, 500 ],
    allowInsertColumn:false,
    wordWrap:true,
    columns: [
        { type: 'numeric' },
        { type: 'text'},
        { type: 'text'},
    ]
});

$('#tableinterdiscipRelations').jexcel({
    colHeaders: ['№ п/п', 'Наименование обеспечиваемых (последующих) дисциплин', '№ разделов и тем данной дисциплины, необходимых для изучения обеспечиваемых (последующих) дисциплин'],
    colWidths: [ 50, 300, 500 ],
    allowInsertColumn:false,
    wordWrap:true,
    columns: [
        { type: 'numeric' },
        { type: 'autocomplete', source: next_discip },
        { type: 'text'},
    ]
});