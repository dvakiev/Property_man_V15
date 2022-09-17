/* eslint-env es6 */
/* eslint-disable no-unused-vars */
/* eslint-disable prefer-const */
/* eslint-disable no-shadow */
/* eslint-disable capitalized-comments */
odoo.define('kw_dms.document', function (require) {
    "use strict";

    let core = require('web.core');
    let Sidebar = require('web.Sidebar');
    let field_utils = require('web.field_utils');

    let _t = core._t;

    Sidebar.include({
        init: function (parent, options) {
            this._super.apply(this, arguments);
            this.sections.splice(
                1, 0, {'name': 'docs', 'label': _t('Documents')});
            this.items.docs = [];
        },
        start: function () {
            let _super = this._super.bind(this);
            let def = this._updateDocuments();
            return def.then(_super);
        },
        destroy: function () {
            this._super.apply(this, arguments);
        },
        updateEnv: function (env) {
            this.env = env;
            let _super = _.bind(this._super, this, env);
            let def = this._updateDocuments();
            def.then(_super);
        },
        _redraw: function () {
            this._super.apply(this, arguments);
        },
        _updateDocuments: function () {
            if (this.items.docs === undefined) {
                return $.when();
            }
            let activeId = this.env.activeIds[0];
            if (!activeId) {
                this.items.docs = [];
                return $.when();
            }
            let domain = [
                ['model', '=', this.env.model],
                ['res_id', '=', activeId],
            ];
            let fields = ['name', 'create_uid', 'create_date',
                'write_uid', 'write_date'];
            return this._rpc({
                model: 'kw.document',
                method: 'search_read',
                context: this.env.context,
                domain: domain,
                fields: fields,
            }).then(this._processDocuments.bind(this));

        },
        _processDocuments: function (documents) {
            let self = this;
            _.chain(documents)
                .groupBy(function (documents) {
                    return documents.name;
                })
                .each(function (document) {
                    if (document.length > 1) {
                        _.map(document, function (document, i) {
                            document.name = _.str.sprintf(
                                _t("%s (%s)"), document.name, i + 1);
                        });
                    }
                });
            _.each(documents, function (a) {
                a.label = a.name;
                // if (a.state === 'ready') {
                //     a.label = '<span class="text-success">' +
                //         a.name + '</span>';
                // }

                a.callback = function () {
                    self.do_action({
                        type: 'ir.actions.act_window',
                        name: a.name,
                        res_model: 'kw.document',
                        res_id: a.id,
                        views: [[false, 'form']],
                        target: 'current',
                    });
                };
                a.create_date = field_utils.parse.datetime(
                    a.create_date, 'create_date', {isUTC: true});
                a.create_date_string = field_utils.format.datetime(
                    a.create_date, 'create_date', self.env.context.params);
                a.write_date = field_utils.parse.datetime(
                    a.write_date, 'write_date', {isUTC: true});
                a.write_date_string = field_utils.format.datetime(
                    a.write_date, 'write_date', self.env.context.params);
            });
            documents.push({
                label: _t('New document...'),
                callback: function () {
                    self.do_action({
                        type: 'ir.actions.act_window',
                        name: _('Create doc'),
                        res_model: 'kw.document',
                        res_id: false,
                        views: [[false, 'form']],
                        target: 'new',
                        context: {
                            default_model: self.env.model,
                            default_res_id: self.env.activeIds[0],
                        },
                    });
                },
            });
            if (this.env.model !== 'kw.document') {
                this.items.docs = documents;
            }
        },
    });

});
