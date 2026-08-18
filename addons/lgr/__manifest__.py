{
    "name": "LGR",
    "summary": "Custom document layout for Accounting and Sales reports",
    "version": "1.2.2",
    "category": "Technical",
    "author": "Luke Gareth Ribchester",
    "license": "LGPL-3",
    "depends": ["web", "account", "sale"],
    "data": [
        "report/external_layout_templates.xml",
        "data/report_layout_data.xml",
    ],
    "assets": {
        "web.report_assets_common": [
            "lgr/static/src/scss/lgr.scss",
        ],
    },
    "installable": True,
    "application": False,
}
