openerp.x_fiscal_printer = function (openerp)
{   
    editorExtensionId = "obmjkpjjkpmdaimiknpbpemcjknnofpl";

    openerp.web.client_actions.add( 'fp_query', 'openerp.x_fiscal_printer.Query');
    openerp.x_fiscal_printer.Query = openerp.web.Widget.extend({
        template: 'FiscalPrinterQuery',
        events: {
            'click button.oe_list_publish': 'publishPrinters',
            'click button.oe_list_update': 'updateList',
        },
        init: function (field_manager, node) {
            console.log('loading...');
            this._super(field_manager, node);

            this.printers=null;

            this.is_app_running = $.Deferred();

            this.editorExtensionId = "obmjkpjjkpmdaimiknpbpemcjknnofpl";

            var self = this;
            chrome.runtime.sendMessage(this.editorExtensionId, {operation: "is_app_running"},
                function(response) {
                    self.is_app_running.resolve();
                });
        },
        start: function () {
            this._super(this, arguments);
            var self = this;
            this.is_app_running.done(function() { self.updateList(); });
        },
        updateList: function() {
            var self = this;
            var sndMsg = chrome.runtime.sendMessage;
            sndMsg(this.editorExtensionId, {operation: "list_printers"},
                function(response) {
                    self.printers = response.splice(0);
                    self.updateWidget();
                    return true;
                });
        },
        updateWidget: function() {
            var self = this;
            $('.oe_view_manager_body').show();
            if (this.printers) {
                $('.oe_fiscal_printer_message_no_app').addClass('oe_form_invisible');
                if (this.printers.length == 0) {
                    $('.oe_view_manager_messages').show();
                    $('.oe_view_manager_view_list').hide();
                    $('.oe_fiscal_printer_message_no_app').hide();
                    $('.oe_fiscal_printer_message_no_printers').show();
                    return;
                } else {
                    $('.oe_view_manager_messages').hide();
                    $('.oe_view_manager_view_list').show();
                    var tbody = $('.oe_field_fiscal_printer_table table tbody');
                    // Clean list
                    tbody.empty()
                    // Complete list
                    this.printers.forEach(function(p){
                        var row = "<tr class='oe_fiscal_printer'>" +
                                  "<td><input type='checkbox' class='oe_list_record_selector'/></td>" +
                                  "<td data-id='protocol'>" + p.protocol + "</td>" +
                                  "<td data-id='model'>" + p.model + "</td>" +
                                  "<td data-id='serialNumber'>" + p.serialNumber + "</td>" +
                                  "<td data-id='pos'>" + p.pos + "</td>" +
                                  "</tr>";
                        tbody.append(row);
                    });
                    return;
                };
            } else {
                $('.oe_view_manager_messages').show();
                $('.oe_view_manager_view_list').hide();
                $('.oe_fiscal_printer_message_no_app').show();
                $('.oe_fiscal_printer_message_no_printers').hide();
            };
        },
        publishPrinters: function() {
            $('tr.oe_fiscal_printer').has('input:checked').each(function(i, p){
                var data = {};
                $(p).children().each(function(i, d){
                    var a = d.attributes['data-id'];
                    if (a) { data[a.value] = d.textContent; };
                })
                data.name = data.serialNumber;
                new openerp.web.Model('fiscal_printer.fiscal_printer').call('create', [data]);
            });
        }
    });

    openerp.web.client_actions.add( 'fp_test', 'openerp.x_fiscal_printer.Test');
    openerp.x_fiscal_printer.Test = function(manager, action) {
        var self = this;
        var dataset = new openerp.web.DataSet(this, 'fiscal_printer.fiscal_printer');
        dataset.read_ids(action.context.active_ids).done(function(records){
            _(records).each(function(record) {
                chrome.runtime.sendMessage(editorExtensionId, {
                    operation: "test_printer",
                    protocol: record.protocol,
                    serialNumber: record.serialNumber,
                    model: record.model },
                    function(response) { });
            });
        });
    };

    openerp.web.form.widgets.add('fp_update', 'openerp.x_fiscal_printer.FieldFiscalPrinterUpdate');
    openerp.x_fiscal_printer.FieldFiscalPrinterUpdate = openerp.web.form.AbstractField.extend({
        events: {
            'click div.oe_fp_update button': 'updatePrinter',
            'click div.oe_fp_check_printer button': 'checkPrinter',
        },
        template : "FieldFiscalPrinterUpdate",
        init: function (view, node) {
            this._super(view, node);
            console.log('loading...');

            this.is_app_running = $.Deferred();

            var self = this;
            chrome.runtime.sendMessage(editorExtensionId, {operation: "is_app_running"},
                function(response) { self.is_app_running.resolve(); });
            return;
        },
        start: function () {
            var self = this;
            
            this.$el.find('.oe_fp_update').hide();
            this.$el.find('.oe_fp_check_printer').hide();
            this.$el.find('.oe_fp_check_app').show();

            this.is_app_running.done(function(){
                self.checkPrinter();
            });

            this._super.apply(this, arguments);
        },
        checkPrinter: function() {
            var self = this;
            var fields = self.field_manager.fields;
            self.$el.find('.oe_fp_check_app').hide();
            chrome.runtime.sendMessage(editorExtensionId, {
                operation: "exists_printer",
                protocol: fields.protocol.get_value(),
                serialNumber: fields.serialNumber.get_value(),
                model: fields.model.get_value() },
                function(response) {
                    if (response) {
                        self.$el.find('.oe_fp_update').show();
                        self.$el.find('.oe_fp_check_printer').hide();
                    } else {
                        self.$el.find('.oe_fp_update').hide();
                        self.$el.find('.oe_fp_check_printer').show();
                    }
                });
        },
        updatePrinter: function() {
            var self = this;
            var fields = self.field_manager.fields;
            var fiscal_printer_id = self.field_manager.datarecord.id;
            chrome.runtime.sendMessage(editorExtensionId, {
                    operation: "get_printer_data",
                    protocol: fields.protocol.get_value(),
                    serialNumber: fields.serialNumber.get_value(),
                    model: fields.model.get_value() },
                    function(response) {
                        if (response) {
                            fields.clock.set_value(response.fields.clock);
                            fields.printerStatus.set_value(response.fields.printerStatus);
                            var attribute_ids = [];
                            for (var k in response.attributes) {
                                if (response.attributes.hasOwnProperty(k)) {
                                    attribute_ids.push({
                                        'name': k,
                                        'value': response.attributes[k],
                                        'readOnly': response.readonly.indexOf(k) >= 0,
                                        'lastUpdate': new Date().toString('yyyy-MM-dd HH:mm:ss'),
                                        'fiscal_printer_id': fiscal_printer_id,
                                    });
                                }
                            };
                            fields.attribute_ids.set_value(attribute_ids);
                        } else {
                            self.checkPrinter();
                        }
                    });
        },
    });

    // Load, update and store attribute.
    openerp.web.form.widgets.add('fp_attribute', 'openerp.x_fiscal_printer.FieldFiscalPrinterAttribute');
    openerp.x_fiscal_printer.FieldFiscalPrinterAttribute = openerp.web.form.FieldChar.extend({
        events: {
            'click img#fp_connect': 'Connect',
            'click img#fp_read':    'Read',
            'click img#fp_write':   'Write',
        },
        template : "FieldFiscalPrinterAttribute",
        init: function (view, node) {
            this._super(view, node);
            console.log('loading...');

            this.is_app_running = $.Deferred();

            var self = this;
            chrome.runtime.sendMessage(editorExtensionId, {operation: "is_app_running"},
                function(response) { self.is_app_running.resolve(); });
            return;
        },
        start: function () {
            var self = this;
            self.$("#fp_read").hide();
            self.$("#fp_write").hide();
            self.$("#fp_connect").hide();

            this.is_app_running.done(function(){ self.Connect(); });

            this._super.apply(this, arguments);
        },
        render_value: function() {
            this.Connect();
            this._super.apply(this, arguments);
        },
        Connect: function () {
            var self = this;
            var fields = self.field_manager.fields;
            var dataset = new openerp.web.DataSetStatic(this,
                fields.fiscal_printer_id.field.relation,
                self.build_context());
            var readOnly = fields.readOnly.get_value();
            dataset.read_ids(fields.fiscal_printer_id.get_value()).then(function(record) {
                chrome.runtime.sendMessage(editorExtensionId, {
                    operation: "exists_printer",
                    protocol: record.protocol,
                    serialNumber: record.serialNumber,
                    model: record.model },
                    function(response) {
                        if (response) {
                            self.$("#fp_read").show();
                            if (self.field_manager.fields.readOnly.get_value()) {
                                self.$("#fp_write").hide();
                            } else {
                                self.$("#fp_write").show();
                            }
                            self.$("#fp_connect").hide();
                        } else {
                            self.$("#fp_read").hide();
                            self.$("#fp_write").hide();
                            self.$("#fp_connect").show();
                        };
                    });
            });
        },
        Read: function () {
            var self = this;
            var fields = this.field_manager.fields;
            var dataset = new openerp.web.DataSetStatic(this,
                fields.fiscal_printer_id.field.relation,
                self.build_context());
            var name = fields.name.get_value();

            var set_value_ = function(value_) {
                self.$("input").val(value_);
            };

            dataset.read_ids(fields.fiscal_printer_id.get_value()).then(function(record) {
                chrome.runtime.sendMessage(editorExtensionId, {
                    operation: "read_field",
                    field: name,
                    protocol: record.protocol,
                    serialNumber: record.serialNumber,
                    model: record.model },
                    set_value_);
                });
        },
        Write: function () {
            var self = this;
            var fields = this.field_manager.fields;
            var dataset = new openerp.web.DataSetStatic(this,
                fields.fiscal_printer_id.field.relation,
                self.build_context());
            var name = fields.name.get_value();
            var value = self.$("input").val();

            var finish = function(response) {
                if (response == null) {
                    self.do_warn("Can't store value in printer",
                            "Field can't be writen.");
                } else 
                if (response.result) {
                    self.do_warn("Can't store value in printer", response.strResult);
                } else {
                    console.log("Stored in printer", response);
                    //fields.lastCommit.set_value(new Date().toString('yyyy-MM-dd HH:mm:ss'));
                };
            };

            dataset.read_ids(fields.fiscal_printer_id.get_value()).then(function(record) {
                chrome.runtime.sendMessage(editorExtensionId, {
                    operation: "write_field",
                    field: name,
                    value: value,
                    protocol: record.protocol,
                    serialNumber: record.serialNumber,
                    model: record.model },
                    finish);
                });
        },
    });
    
    // Remite.
    openerp.web.form.widgets.add('fp_control', 'openerp.x_fiscal_printer.FieldFiscalPrinterControl');
    openerp.x_fiscal_printer.FieldFiscalPrinterControl = openerp.web.form.FieldMany2One.extend({
        events: { },
        template : "FieldFiscalPrinterControl",
        init: function (view, node) {
            this._super(view, node);
            console.log('loading...');
            var source = new EventSource("fp/fp_print");
            source.onmessage = function(event) {
                debugger;
            };
            return;
        },
        start: function () {
            var self = this;
            this._super.apply(this, arguments);
        },
    });
};
// vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
