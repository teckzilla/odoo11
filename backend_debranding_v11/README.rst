=======================
Odoo debranding Kit
=======================

In this Module Extra_Modules Folder We Put Two Modules.

- POS Debranding
- Website Debranding

Below Remove in Odoo:

1. Deletes Odoo label in footer
2. Replaces "Odoo" in page title
3. Replaces "Odoo" in help message for empty list
4. Deletes Documentation, Support, About links
5. Replaces default logo by empty image
6. Replaces "Odoo" in Dialog Box
7. Replaces "Odoo" in strings marked for translation.
8. Replaces default favicon to a custom one
9. **Hides Apps menu** (by default, only admin (superuser) can see Apps menu. You could change it via tick "Show Modules Menu" in user's access rights tab)
10. Disables server requests to odoo.com (publisher_warranty_url)
11. Deletes "My odoo.com account" button
12. Deletes Apps and other blocks from Settings/Dashboard
13. Replaces "Odoo" in planner
14. Replaces footer in planner to a custom one.
15. Deletes "Odoo" in a request message for permission desktop notifications

By default the module replaces "Odoo" to "Your Company/Tag". To configure
module open Settings\\System Parameters and modify

 - backend_debranding.new_title (put space in value if you don't need Brand in Title)
 - backend_debranding.new_name (your Brand)
 - backend_debranding.favicon_url
 - backend_debranding.planner_footer

