odoo.define('backend_debranding_v11.dashboard', function (require) {
"use strict";

    var dashboard = require('web_settings_dashboard');
    dashboard.Dashboard.include({
        start: function(){
            this.all_dashboards  = _.without(this.all_dashboards, 'planner', 'apps');
            this.$('.o_web_settings_dashboard_apps').parent().remove();
            this.$('.o_web_settings_dashboard_planner').parent().remove();
            return this._super();
        },
    });
});
