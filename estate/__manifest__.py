{
    "name": "Real Estate",
    "version": "1.2",
    "summary": "estate",
    "depends": ["base", "website", "mail"],
    "sequence": 10,
    "description": """
        Easy to use Real Estate App
    """,
    "category": "Real Estate",
    "application": True,
    "data": [
        # "security/security.xml",
        # "security/ir_rule.xml",
        "security/ir.model.access.csv",

        "views/estate_properties_controller_views.xml",

        "report/estate_property_reports.xml",
        "report/estate_property_templates.xml",

        # "data/demo_data.xml",

        "wizard/estate_property_offer_views.xml",
        "views/res_users_views.xml",
        "views/estate_property_offer_views.xml",
        "views/estate_property_tag_views.xml",
        "views/estate_property_type_views.xml",
        "views/estate_property_views.xml",
        "views/estate_menus.xml",
    ],
}
