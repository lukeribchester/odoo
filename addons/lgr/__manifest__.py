{
    "name": "LGR",
    "summary": "Custom document layout for Accounting and Sales reports",
    "version": "1.3.8",
    "category": "Technical",
    "author": "Luke Gareth Ribchester",
    "license": "LGPL-3",
    "depends": ["web", "account", "sale"],
    "data": [
        "report/external_layout_templates.xml",
        "report/account_document_details.xml",
        "report/sale_document_details.xml",
        "report/preview_document_details_templates.xml",
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
