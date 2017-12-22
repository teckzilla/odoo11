odoo.define('backend_debranding.title', function(require) {
"use strict";
    var core = require('web.core');
    var QWeb = core.qweb;
    var _t = core._t;
    var WebClient = require('web.WebClient');
    var rpc = require('web.rpc');
//    var Model = require('web.DataModel');
//    var model = new Model("ir.config_parameter");
    var title_part
//        var r = model.query(['value'])
//                 .filter([['key', '=', 'backend_debranding.new_title']])
//             .limit(1)
//             .all().then(function (data) {
//                 if (!data.length)
//                     return;
//                 title_part = data[0].value;
//                 title_part = title_part.trim();
//                 });
      var r =  rpc.query({
            model: 'ir.config_parameter',
            method: 'search_read',
            args: [[['key', '=', 'backend_debranding.new_title']],['value']],
            limit: 1,
        }).then(function (data) {
             if (!data.length)
                 return;
             title_part = data[0].value;
             title_part = title_part.trim();
             });
    WebClient.include({
    init: function(parent, client_options) {
        this._super(parent, client_options);

         this.set('title_part', {"zopenerp": title_part});
//        this.get_title_part();
    },
    get_title_part: function(){
        if (!openerp.session.db)
            return;
        var self = this;
//        var model = new Model("ir.config_parameter");

//        var r = model.query(['value'])
//                 .filter([['key', '=', 'backend_debranding.new_title']])
//             .limit(1)
//             .all().then(function (data) {
//                 if (!data.length)
//                     return;
        var r = rpc.query({
            model: 'ir.config_parameter',
            method: 'search_read',
            args: [[['key', '=', 'backend_debranding.new_title']],['value']],
            limit: 1,
        }).then(function (data) {
                 if (!data.length)
                     return;
                 title_part = data[0].value;
                 title_part = title_part.trim();
                 self.set('title_part', {"zopenerp": title_part});
                 });
    },
 });
});
