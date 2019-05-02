yepnope({ // or Modernizr.load
    test: Modernizr.inputtypes.date,
    nope: [
        'https://cdnjs.cloudflare.com/ajax/libs/jqueryui/1.11.2/jquery-ui.min.js',

        'https://cdnjs.cloudflare.com/ajax/libs/jqueryui/1.11.2/jquery-ui.min.css',
        'https://cdnjs.cloudflare.com/ajax/libs/jqueryui/1.11.2/jquery-ui.structure.min.css',
        'https://cdnjs.cloudflare.com/ajax/libs/jqueryui/1.11.2/jquery-ui.theme.min.css',

    ],

    callback:function (url) {

        if(url === 'https://cdnjs.cloudflare.com/ajax/libs/jqueryui/1.11.2/jquery-ui.min.js') {

            var idx=0;

            $('input[type="date"]').each( function() {
                var _this=$(this),
                    prefix='alt'+ String(idx++) + '_',
                    _val=_this.val();

                _this
                .attr('placeholder', 'gg/mm/aaaa')
                .attr('autocomplete', 'off')
                .prop('readonly', true)
                .after('<input type="text" class="altfield" id="' + prefix + _this.attr('id')  + '" name="' + _this.attr('name') + '" value="' + _val + '">')
                .removeAttr('name')
                .val('')
                .datepicker({
                    altField: '#'+ prefix + _this.attr('id'),
                    dateFormat: 'dd/mm/yy',
                    altFormat: 'yy-mm-dd'
                });

                if(_val) {
                    _this.datepicker('setDate', $.datepicker.parseDate('yy-mm-dd', _val) );
                };
            });


            // min attribute
            $('input[type="date"][min]').each(function() {
                var _this=$(this);
                _this.datepicker( "option", "minDate", $.datepicker.parseDate('yy-mm-dd', _this.attr('min')));
            });

            // max attribute
            $('input[type="date"][max]').each(function() {
                var _this=$(this);
                _this.datepicker( "option", "maxDate", $.datepicker.parseDate('yy-mm-dd', _this.attr('max')));
            });
        }
    }
});