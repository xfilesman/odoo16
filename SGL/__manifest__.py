{
    'name': 'SGL',
    'version': '16.0.1.1.1',
    'summary': 'File Cover Management',
    'author': 'Your Company',
    'category': 'Operations',
    'depends': ['base', 'web'],
    'data': [
        'data/sgl_file_cover_sequences.xml',
        'views/sgl_file_cover_view.xml',
        'views/sgl_file_cover_activity_column_wizard.xml',
        'security/ir.model.access.csv',
        'data/sgl_file_cover_sequence.xml',
    ],
    'qweb': [
    ],
    'images': ['static/description/logo.png'],
    'assets': {
        'web.assets_backend': [
            'SGL/static/src/js/activity_list_view.js',
            'SGL/static/src/css/rtl_fix.css',
            'SGL/static/src/css/file_cover_design.css',
            'SGL/static/src/js/one_line_text.js',
            'SGL/static/src/js/list_footer_egp.js',
        ],
        'web.assets_qweb': [
            'SGL/static/src/xml/activity_list_buttons.xml',
        ],
    },
    'installable': True,
    'application': True,
}