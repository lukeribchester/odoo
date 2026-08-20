# LGR

An importable custom document layout and invoice-template foundation for Odoo Online. The module adds **LGR** to Odoo's
document-layout selector without modifying any of Odoo's built-in layouts. It also routes Odoo's standard invoice-report
branch through an independent LGR primary template based on the resolved default invoice document. Installation does not
automatically select the LGR document layout for a company or change an existing partner or journal report preference.

## Layout behavior

The first page of each document starts with a context-aware masthead inside the report article. It contains:

- An optional context-aware document title. Odoo's translated document-type wording is preserved while a trailing
  document identifier and separator are removed. Receipts use the title `Receipt`; no empty title space is reserved when
  no title remains.
- An optional single-column details table 6 mm beneath the title. Accounting, Sales, and the generic layout preview
  provide built-in detail fragments. If a fragment exists without a title, it starts at the top left without an empty
  title row.
- Structured company details in the left information column: the legal entity name, postal address, an immediately
  following unprefixed email address, a half-line gap, and `VAT <number>`. If email is missing, the gap remains between
  the address and VAT. Missing optional values are omitted.
- Recipient details in the adjacent information column: its mapped heading, legal entity name, postal address, a
  half-line gap, and `VAT <number>` when available.
- The company logo at the top right. The information area expands when no logo is configured.

The visible masthead appears only on the first page. Its order is title, details, then the address columns, with 6 mm
between the title and details and between the details and addresses. The logo remains at the top right. A non-collapsing
24 mm gap separates the completed masthead from the first report-owned content, including any shipping or secondary
address block. Because the masthead participates in normal article flow, later pages do not reserve its height.

Normal HTML output and the layout preview give the masthead an 11 mm top inset. For Accounting and Sales PDF batches in
which every document uses LGR, the module requests an 11 mm top margin and zero header spacing through Odoo's supported
report-rendering values. LGR retains a zero-height technical header so Odoo can keep headers, articles, and footers
indexed per document, but that header has no visible content. Mixed LGR/built-in batches and batches containing only
built-in layouts preserve their incoming paper-format margins and header spacing. As wkhtmltopdf applies these settings
to the complete batch, an LGR page in a mixed batch may consequently have more top whitespace. A custom paper format is
not required.

The repeating footer displays `company.report_footer` on the left. Generated PDFs show `Page X of Y` on the right; the
document-layout preview shows `Page 1 of 1`. Normal HTML reports omit the counter because Odoo cannot provide a reliable
total page count there.

The layout preserves Odoo's report article metadata, document slot, complete hidden PDF title, address and information
blocks, configured font and colors, and all six built-in table styles. Structural layout tables and every shared
key/value table are excluded from document-table styling. The original complete title remains in Odoo's invisible
article heading for PDF invoice splitting even though the cleaned visible title is rendered in the first-page masthead.

## Custom invoice template and canonical routing

`lgr.report_invoice_document` is a primary inheritance of `account.report_invoice_document`. It provides an independent
invoice-design surface while retaining Odoo's resolved default invoice architecture, including compatible extension
views. Version 1.5.0 established this routing and stable customization point; version 1.5.2 includes the focused body
behavior provided by the optional Studio-controlled quantity and unit-price setting described below. Version 1.6.0 adds
the structured payment and bank details described below, and version 1.6.1 aligns those details with the document-detail
grid. Version 1.6.2 shortens the bank-transfer QR instruction while preserving its two-line presentation. Version 1.6.3
uses separate column ratios for the payment and bank tables. Version 1.6.4 moves Terms and Conditions above the payment
details in the float-aware left column. Version 1.6.5 refines its spacing and the structured payment labels. Version
1.6.6 aligns regular LGR report-body text with the existing compact document-detail typography. Version 1.6.7 adds a
label above invoice Terms and Conditions. Version 1.6.8 restores the normal report text color for that section and moves
the company contact gap to immediately before VAT. Version 1.6.9 consolidates account, reference, and payment-term rows
beneath a single **Payment Details** heading while preserving their existing field and document-type boundaries. Version
1.6.10 gives invoice section rows a consistent `#f0f0f0` background across all six document-table styles, and version
1.6.11 standardizes their font weight at `600` (semi-bold). Version 1.6.12 registers Odoo's bundled Open Sans SemiBold
face so that this weight is visibly distinct when Open Sans is selected as the company report font. Version 1.6.13
aligns the compact line height and visible content gaps of the **Note** and **Payment Details** headings. Version 1.6.14
changes the bank-transfer QR instruction to three lines: `Scan the payment`, `details with your`, and
`banking application`; the payment-link QR wording remains unchanged. Version 1.7.0 separates safely matched invoice
product names from their additional descriptions so the description can use a smaller type size. Version 1.7.1 removes
the white-circle Odoo overlay from the bank-transfer QR while leaving the generated QR image and payment payload intact.
Version 1.7.2 removes the secondary product/default-UoM conversion beneath ordinary and grouped invoice-line quantities
while retaining each line's primary quantity and selected unit.

`lgr.report_invoice_use_lgr_document` extends `account.report_invoice` at priority 99 and changes only the existing
standard branch whose report name is `account.report_invoice_document`. That branch calls
`lgr.report_invoice_document`; its condition, language handling, iteration, report container, and other dispatcher
branches remain unchanged. In particular, a country module that makes `_get_name_invoice_report()` return another
primary invoice-template key continues through its own branch rather than being forced through LGR.

The module deliberately does not register another `ir.actions.report`. Odoo's existing **Invoice PDF** action and its
Accounting report model remain canonical, preserving payment-line behavior, QR preparation, invoice validation, EDI
post-processing, attachment generation, portal and pro-forma fallback paths, and multi-invoice splitting. There is no
second **LGR Invoice PDF** choice to configure. Existing partner and journal preferences remain stored and continue to
select their configured report actions; selecting Odoo's canonical invoice action uses the LGR standard branch, while a
different report action is outside this routing change.

For records that resolve to Odoo's standard invoice-document branch, real rendering through Print, Send & Print, PDF
generation, and the portal's canonical report path uses the LGR invoice document. Odoo's generic **Configure Document
Layout** preview and its dedicated
`account.report_invoice_document_preview` template are intentionally not replaced by this invoice-template route. The
existing LGR preview adapters continue to preview the document layout and context-aware masthead, while invoice-body
design changes must be validated with a real invoice preview or rendered report. Existing generated invoice PDF
attachments are not rewritten by the module update; use a new invoice or another normal Odoo regeneration path when
validating the new route.

### Studio-controlled quantity and unit-price visibility

The optional Studio-owned Boolean `account.move.x_studio_hide_quantity` controls the Quantity and Unit Price columns for
any document rendered through `lgr.report_invoice_document`. When the field exists and is checked, LGR omits both
headers and all normal, grouped, and collapsed-line cells for those columns from HTML and generated PDF output. When the
field is false or absent, both standard columns remain visible. The report applies no customer/vendor or document-type
filter; Studio continues to own the checkbox's placement and visibility. Its existing Studio label remains **Hide
quantities**, even though the checked state now hides both Quantity and Unit Price.

This is a visual report setting only. It does not change stored quantities or unit prices, calculations, exports, or
EDI/UBL data. The Discount, Taxes, and Amount columns and all totals remain visible. LGR does not define the custom
field and adds no Studio dependency, model field, or access rule. Odoo's generic **Configure Document Layout** preview
uses a separate invoice-preview template and is therefore not authoritative for this invoice-body option; validate it
with a real invoice HTML preview or newly rendered PDF. Previously generated PDF attachments remain unchanged until Odoo
regenerates or replaces them through its normal workflow.

Hiding these columns may make a full VAT invoice unsuitable for its applicable invoicing requirements. Dutch and EU
guidance generally requires the quantity or extent of supplied goods or services and the applicable unit price where
relevant. Review each intended use against the
official [Belastingdienst invoice requirements](https://www.belastingdienst.nl/wps/wcm/connect/bldcontentnl/belastingdienst/zakelijk/btw/administratie_bijhouden/facturen_maken/factuureisen/)
and [European Commission VAT invoicing guidance](https://taxation-customs.ec.europa.eu/taxation/vat/vat-businesses/invoicing_en),
and obtain professional advice when necessary.

### Invoice secondary quantity display

Ordinary and grouped or collapsed-price invoice product rows display only their primary quantity and selected unit. LGR
removes Odoo's muted secondary conversion to the product/default UoM, such as `17.00 Units` beneath `17.00 Hours`,
including the conversion's line break and wrapper. Collapsed-composition summaries retain their sole intended quantity;
they are not secondary conversions.

This is a presentation-only change for invoice-family reports routed through `lgr.report_invoice_document`. It does not
modify stored quantities, UoM conversions, calculations, exports, or EDI/UBL data. Sales quotations and orders, the
generic document-layout preview, and statutory invoice templates that bypass the LGR route remain unchanged. Existing
generated PDF attachments retain their prior rendering until regenerated through Odoo's normal workflow.

### Invoice product-name and description styling

For an ordinary or grouped invoice product line, LGR separates the product name from its additional description only
when the complete displayed line text either exactly equals the translated product display name or begins with that
exact name followed by a newline. A safely matched product name retains the invoice body's inherited `.875rem`
(approximately 14 px) size, weight, and color. Any content after the matching first line is rendered beneath it as a
separate block at `.75rem` (12 px), normal `400` weight, normal report color, `1.25` line height, and no added margin.
All remaining description lines and line breaks are preserved.

If the translated product name is unavailable or the complete text does not match this exact prefix contract, LGR
renders Odoo's original complete line value unchanged. This safe fallback protects manually rewritten labels,
productless lines, imported values, and localization variations without dropping or rewriting content. Ordinary product
rows and grouped or collapsed-price product rows use the split in desktop and mobile output. Sections, subsections, note
rows, and collapsed-composition summaries retain Odoo's existing rendering.

This behavior changes presentation only. It does not modify invoice-line names, products, calculations, stored values,
exports, or EDI/UBL data. Alternate statutory invoice templates that bypass `lgr.report_invoice_document` remain
unchanged, and the generic document-layout preview is not authoritative for this invoice-body feature.

### Invoice section-row styling

Invoice line-table rows carrying Odoo's `.o_line_section` class use a consistent `#f0f0f0` background when rendered
through `lgr.report_invoice_document`. The LGR-scoped rule applies to ordinary and grouped or collapsed section rows in
desktop and mobile output and takes precedence over each of Odoo's six selectable document-table styles. Section text
retains the normal configured report text color for readability and uses `font-weight: 600` (semi-bold) in ordinary and
grouped or collapsed rows. The weight applies to every section-row cell, including any amount or total cell. Subsection
rows, product rows, notes, headers, totals outside section rows, and invoice tables rendered through alternate statutory
templates remain unchanged. LGR registers Odoo's existing
`/web/static/fonts/google/Open_Sans/Open_Sans-SemiBold.ttf` file as the normal `600` face for the internal `Open_Sans`
font family; it adds no font binary. Select **Open Sans** in **Configure Document Layout** to obtain the exact SemiBold
face. Other configured font families remain unchanged, and a family without a registered `600` face may map that
requested weight to another available face.

### Consolidated payment details

The invoice's existing Terms and Conditions (`account.move.narration`) are the first left-side block beneath the invoice
line table, before fiscal and tax notes and before the payment details. A bold `Note` label appears without a colon
immediately above the rich-text content. The label uses `.875rem` text, `1.2` line height, and a `2mm` bottom margin.
The label and narration inherit the normal configured report text color; deliberate colors embedded in rich-text content
remain effective. The narration content and inheritance anchor remain unchanged. An automatic-width, hidden-overflow
wrapper keeps the complete block within the space beside the right-floating totals; if that space is insufficient, the
complete block flows beneath the totals. Non-collapsing spacing places the label exactly 12 mm below the invoice table
and the narration block 24 mm before the following notes or payment section.

The LGR invoice body keeps payment information in Odoo's existing left-aligned `#payment_term` area alongside the
right-floating totals. An automatic-width, hidden-overflow wrapper provides one available width without introducing
another float. When a visible payment reference or payment term exists, a bold **Payment Details** heading appears in
the normal configured report text color. The heading uses `.875rem` text and `1.2` line height, with a `1.5mm` bottom
margin before the single structured table. Together with the first row's existing `.5mm` top cell padding, this gives
approximately `2mm` from the heading to the first visible row text. Available rows render in this order:

1. **Name** `account.move.company_id.name`
2. **IBAN** `account.move.partner_bank_id.account_number`
3. **BIC/SWIFT** `account.move.partner_bank_id.bank_bic`, when available
4. **Reference** `account.move.payment_reference`
5. **Terms** the translated `account.payment.term.name`

The first three account rows retain Odoo's existing scope: they are shown only for an outgoing invoice or incoming
refund that has both a payment reference and a selected partner bank. **Reference** uses the same outgoing-invoice or
incoming-refund condition but remains visible without a selected bank. **Terms** appears whenever
`invoice_payment_term_id` exists, including on customer credit notes, sales receipts, vendor bills, vendor credit notes,
purchase receipts, pro-formas, and self-billing variants. Consequently, both reference-only and terms-only documents
render the heading and table, while a document with neither value emits no heading, table, or associated empty spacing.
The bank condition cannot expose account details on additional document types.

The **Terms** value deliberately uses the concise payment-term name rather than the editable rich-text **Description on
the Invoice** (`account.payment.term.note`). That rich-text note remains absent from this block; the moved invoice
narration and legal or fiscal-position notes retain their original content. The existing `payment_communication`,
`payment_terms_note_id`, and `payment_term` inheritance anchors remain attached to their corresponding rows so
compatible extensions can continue to locate them.

The consolidated section uses one full-width, fixed-layout table with the same shared `.o_lgr_key_value_table` class as
the context-aware document details. Its labels use 15% and its values 85% of the width. Cells use `.875rem` text, `1.2`
line height, `.5mm` vertical padding, and a `2mm` right gutter after the label. All labels are bold, all values use
normal weight, and long values wrap. The structural table is marked `o_ignore_layout_styling`, so Odoo's six selectable
document-table themes do not add borders, backgrounds, or competing spacing. Fixed layout provides predictable column
alignment in Odoo's wkhtmltopdf renderer, and the heading/table block uses best-effort page-break avoidance.

Odoo's existing early-payment discount and installment subtree remains immediately after the consolidated table and
outside its page-break wrapper, allowing long schedules to paginate independently. The parent payment wrapper is emitted
only when consolidated details exist; schedules remain covered because they require a payment term. A single
non-collapsing 6 mm gap separates the complete Payment Details content, including any schedule, from the first active
bank or payment-link QR-code section. The gap is omitted when Payment Details is absent and is not duplicated when both
QR types are active. If the space beside the right-floating totals becomes too narrow, the complete payment group may
flow below the totals.

The bank-transfer QR renders its generated QR image without Odoo's separate white-circle logo overlay. Its encoded
payment payload, generation and visibility conditions, dimensions, position, three-line instruction, and 6 mm spacing
remain unchanged. The distinct payment-link QR retains its existing Odoo overlay and clickable-link behavior. Odoo's
separate **Configure Document Layout** preview is not changed by this invoice-template customization. Existing stored
PDF attachments retain their earlier appearance until Odoo regenerates or replaces them through its normal workflow.

This is presentation-only behavior. It does not change payment terms, references, bank records, calculations, payment
processing, or EDI output. The new literal labels are English until corresponding entries are added to an LGR
translation catalog. Previously generated PDF attachments remain unchanged until Odoo regenerates or replaces them
through its normal workflow.

Country or Studio views that inject additional visible wording inside Odoo's original payment-communication paragraph
must extend the LGR consolidated section explicitly. The standard Dutch SaaS 19.3 invoice route adds no such wording;
country routes that select a separate statutory primary invoice template continue to bypass LGR unchanged.

## Typography

Every report article rendered through the LGR external layout uses `.875rem` as its regular body-text size. This aligns
invoice and Sales document bodies, line tables, totals, Terms and Conditions, fiscal and legal notes, shipping
information, QR instructions, and payment details with the existing compact document-detail typography. Odoo's normal
body line height remains unchanged; the shared key/value tables retain their explicit `1.2` line height.

The established hierarchy remains intact: the visible document title is `1.5rem`, the footer is `.8rem`, and Odoo's
`.small` text remains proportionally smaller than its surrounding content. Semi-bold (`600`) invoice section rows,
italic note rows, and explicit font sizes embedded in rich-text fields continue to apply. Font family selection remains
company-configured, including Odoo's default Lato. Selecting Open Sans activates LGR's registration of Odoo's bundled
SemiBold face at weight `600`; no font family is forced and other company fonts are unchanged. Built-in layouts and
reports not rendered through LGR keep their original body size.

## Context-aware document details

The Accounting helper covers customer invoices, customer credit notes, sales receipts, vendor bills, vendor credit
notes, and purchase receipts, including their applicable draft, cancelled, posted, pro-forma, and self-billing contexts.
It uses Odoo's existing field conditions and formatting and can display:

| Order | Detail                           |
|-------|----------------------------------|
| 1     | Context-specific document number |
| 2     | Context-specific document date   |
| 3     | Due date                         |
| 4     | Delivery date                    |
| 5     | Taxable-supply date              |
| 6     | Source document (outgoing only)  |
| 7     | Customer or vendor code          |
| 8     | Reference                        |
| 9     | Incoterm and location            |

The Sales helper covers quotations, sales orders, and Sales pro-forma invoices and can display:

| Order | Detail                           |
|-------|----------------------------------|
| 1     | Context-specific document number |
| 2     | Customer reference               |
| 3     | Context-specific document date   |
| 4     | Expiration date                  |
| 5     | Delivery date                    |
| 6     | Incoterm and location            |
| 7     | Contact                          |

Each detail occupies one label/value row, and the complete row is omitted when its value is unavailable. The Accounting,
Sales, and preview tables retain the shared default geometry of 20% labels and 80% values. The consolidated Payment
Details table uses 15% labels and 85% values. All tables retain a 2 mm label gutter, `.875rem` text, `1.2` line height,
`.5mm` vertical cell padding, top alignment, and normal wrapping. The generic layout preview displays its dummy invoice
number, invoice date, and due date in the same single-column table. Active invoice and quotation previews use their
Accounting and Sales helpers and real record values.

All seven Accounting and Sales detail dates use the fixed `d MMMM yyyy` presentation. Month names follow the report
partner's language, so the same date renders as `1 January 2026` in English and `1 januari 2026` in Dutch. Date and
Datetime values continue to use Odoo's date widget, preserving its language and timezone handling.

Accounting number and date labels are selected in this order, without changing the fields that supply their values:

| Condition                                   | Number label       | Date label       |
|---------------------------------------------|--------------------|------------------|
| Outgoing invoice with a debit origin        | Debit Note Number  | Debit Note Date  |
| Other outgoing invoice                      | Invoice Number     | Invoice Date     |
| Outgoing or incoming refund                 | Credit Note Number | Credit Note Date |
| Sales or purchase receipt                   | Receipt Number     | Receipt Date     |
| Pro-forma incoming invoice                  | Bill Number        | Bill Date        |
| Non-pro-forma self-billing incoming invoice | Invoice Number     | Invoice Date     |
| Other incoming invoice                      | Bill Number        | Bill Date        |

The document number continues to come from `account.move.name`, with `/` suppressed, and `account.move.ref` continues to
appear separately as `Reference`. The partner reference is labelled `Customer Code` for outgoing documents and
`Vendor Code` for incoming documents. The optional Source row is limited to outgoing customer invoices, credit notes,
and sales receipts; incoming documents retain their stored Odoo source data but do not display it in LGR.

The visible title carries qualifiers such as draft, cancelled, pro-forma, vendor, and self-billing, so those qualifiers
are not repeated in the compact detail labels. The pro-forma incoming-invoice rule deliberately precedes the
self-billing rule: a pro-forma incoming self-billing invoice retains Odoo's `Proforma Vendor Bill` title and uses
`Bill Number` / `Bill Date`, while a non-pro-forma self-billing incoming invoice uses `Invoice Number` / `Invoice Date`.
If the optional `account_debit_note` module is installed, outgoing invoices with a debit origin use the debit-note pair;
field-presence detection provides this compatibility without adding that module as a dependency.

Sales terminology remains aligned with Odoo: Sales pro-formas use `Pro Forma Invoice Number` / `Issued Date`, quotations
use `Quotation Number` / `Quotation Date`, and orders use `Order Number` / `Order Date`.

Odoo's original `#informations` nodes remain in their report templates so other inherited views can still target them.
When LGR receives a details fragment, an LGR-scoped article class hides the original block to prevent duplication. Other
document layouts continue to show the original block unchanged.

Fields added by a localization or Studio only to the original `#informations` block do not automatically move into LGR's
table. Extend the appropriate LGR helper when such a field should appear in the masthead. The standard Dutch SaaS 19.3
invoice template path is covered. This statement describes the inherited report path, not a legal-compliance
certification. LGR intentionally omits some structured company fields, including the registration number, so each
organization remains responsible for verifying that its complete document content meets its applicable invoicing
requirements.

## Recipient mappings

The layout resolves recipients and their headings as follows. Headings come solely from these mappings; reports without
a mapped context do not display a recipient heading:

| Report context                            | Recipient                           | Heading    |
|-------------------------------------------|-------------------------------------|------------|
| Customer invoice, credit note, or receipt | `account.move.partner_id`           | To         |
| Vendor bill, credit note, or receipt      | `account.move.partner_id`           | From       |
| Quotation or sales order                  | `sale.order.partner_invoice_id`     | To         |
| Document-layout preview                   | Existing preview `address` fragment | To         |
| Other reports                             | Existing `address` fragment         | No heading |

For record-based recipients, the selected invoice/postal address is displayed with the commercial entity's name, a
half-line gap, and `VAT <number>` when available. Pre-rendered fallback `address` fragments remain caller-controlled and
are not rewritten. Sales reports keep a separate shipping-only information block when the shipping and invoice addresses
differ. Accounting's existing shipping information block is preserved in the report body.

## QWeb caller interface

LGR continues to honor these standard Odoo caller values:

- `layout_document_title`: optional QWeb title content. LGR displays a plain-text copy without a trailing record
  identifier, while preserving the complete original value for Odoo's hidden PDF title and invoice splitting.
- `address`: the standard pre-rendered recipient/address fragment and fallback for reports without a record mapping.
- `information_block`: supplementary report information, including shipping data.
- `forced_vat`: fiscal-position VAT override used ahead of the company's VAT.

Nested report templates may additionally set:

- `lgr_recipient`: a `res.partner` record that overrides the built-in recipient mapping.
- `lgr_document_details`: trusted body-form QWeb content rendered beneath the visible title in the first-page article
  masthead. It should contain only the details table; the LGR layout owns the masthead wrapper, placement, and spacing.

The built-in reusable helper templates are:

- `lgr.account_move_document_details`
- `lgr.sale_order_document_details`
- `lgr.preview_document_details`

The LGR invoice template inherits the resolved default invoice document and therefore receives the existing Accounting
details adapter. Future invoice-design changes can call, inherit, or replace `lgr.account_move_document_details`, or
pass their own `lgr_document_details` fragment, without changing the external layout. Report-specific templates should
continue to own field selection, conditions, translatable source wording, and formatting; the shared layout owns
placement and styling.

The helpers render in Odoo's existing partner-language context, so month names, dates, and field widgets retain
localized formatting within LGR's fixed day–full-month–year date order.
Their literal labels belong to LGR's own QWeb view records, however, and therefore need an LGR `i18n/<language>.po`
catalog before they appear in a non-English language. Translations from the dependency views are not inherited merely
because a source label is identical. No non-English catalog is bundled until the required target languages and wording
are agreed.

Company data is intentionally read from structured `res.company` and `res.partner` fields rather than the rich-text
**Company Details** editor. The masthead does not display the structured company phone or registration number. Company
email is displayed without a prefix immediately after the postal address. A half-line gap then precedes
`VAT <number>`. If email is unavailable, the same gap separates the postal address and VAT. VAT is resolved as
`forced_vat or company.vat`.

## SaaS compatibility, dependencies, and scope

Odoo Online does not accept arbitrary custom Python code, so all behavior is implemented through XML/QWeb and SCSS.
Asset paths are explicit because importable modules do not expand asset globs. The stylesheet is loaded only through
`web.report_assets_common`, which serves both report previews and generated PDFs.

The module directly depends on `web`, `account`, and `sale`. Those applications must therefore be available in the
target database. Its short numeric version is series-neutral: Odoo prefixes it with the active server series, avoiding a
manual manifest-version change for each SaaS upgrade.

The custom invoice template intentionally covers the canonical `account.report_invoice_document` route. It does not
override country modules that select a different primary invoice report, and it does not adapt `account.payment` payment
receipts, Purchase, Inventory, or Repair reports. Those report families require their own focused templates or adapters
and should be added only when the corresponding applications or localized reports are in scope.

Within the canonical invoice route, consolidating Payment Details does not broaden account-data visibility: Name, IBAN,
and BIC/SWIFT retain the existing eligible reference-and-bank condition. Terms remains available whenever configured on
all supported invoice move types, while Reference retains its narrower outgoing-invoice and incoming-refund scope.
Statutory country templates that bypass the canonical branch remain unchanged.

The 11 mm PDF override is intentionally limited to all-LGR batches of the standard Accounting invoice and Sales
order/pro-forma report containers supported by this module. The single-column table can contain up to nine Accounting
rows or seven Sales rows. The complete masthead uses `page-break-inside: avoid`, but wkhtmltopdf treats this as a
best-effort constraint: unusually tall addresses or heavily wrapped values may still force or split a page break. This
accepted limitation must be tested against real company data.

## Package, install, and update on Odoo Online

1. From the `addons` directory containing `lgr`, recreate the archive from the explicit ten-file allowlist. Removing
   the previous archive first ensures that stale metadata or cache entries cannot survive an update:

   ```bash
   rm -f lgr.zip
   zip -X lgr.zip \
       lgr/__init__.py \
       lgr/__manifest__.py \
       lgr/README.md \
       lgr/data/report_layout_data.xml \
       lgr/report/external_layout_templates.xml \
       lgr/report/account_document_details.xml \
       lgr/report/invoice_report_templates.xml \
       lgr/report/sale_document_details.xml \
       lgr/report/preview_document_details_templates.xml \
       lgr/static/src/scss/lgr.scss
   ```

2. Enable developer mode and ensure **Import Module** (`base_import_module`) is installed.
3. Open **Apps > Import Module**, upload `lgr.zip`, leave **Force init** disabled, and import the module. A newly
   imported module is initialized automatically.
4. Open the company's **Configure Document Layout** dialog, select **LGR**, inspect the preview, and save.

For an update, upload a newly packaged archive with an incremented manifest version and leave **Force init** disabled.
Enable **Force init** only when you deliberately need to reload records protected by `noupdate`; LGR does not currently
declare such records. Validate imports and report changes on a non-production database first. The existing LGR layout
record, company selection, partner report preferences, and journal report preferences are retained across this `1.7.2`
update. The canonical invoice route requires no new report-action selection.

## Validation checklist

- Open the generic document-layout preview and active invoice and quotation previews. Confirm the first-page order is
  title, details, then company/recipient addresses, with the logo at the top right, an 11 mm top inset, and no
  duplicated
  `#informations` block.
- Confirm regular content in every LGR article resolves to `.875rem`, including invoice and Sales bodies, line tables,
  totals, Terms and Conditions, fiscal and legal notes, shipping information, QR instructions, and payment details.
  Verify the title remains `1.5rem`, the footer remains `.8rem`, key/value tables retain `1.2` line height, `.small`
  content remains proportionally smaller, and configured company font families continue to apply.
- Confirm the combined `lgr.report_invoice_document` architecture matches Odoo's resolved default invoice document apart
  from its independent template identity, the optional Quantity/Unit Price visibility behavior, and the existing LGR
  Accounting-details adapter.
- Confirm `lgr.report_invoice_use_lgr_document` changes exactly one `t-call`: the standard
  `account.report_invoice_document` branch in `account.report_invoice`. Verify that the branch condition, partner
  language, payment-enabled wrapper, and every localization-owned dispatcher branch remain unchanged.
- Render the same records through Odoo's canonical **Invoice PDF** action before and after the update. Compare invoice
  lines, sections and notes, discounts, taxes, totals, payment entries, QR behavior, consolidated Payment Details,
  fiscal-position data, attachment generation, portal output, pro-forma fallback, and multi-record splitting. Confirm
  the default action and specialized Accounting rendering context are retained and no second invoice report action was
  created. Use newly created invoices for this comparison, and separately confirm that an already generated PDF remains
  the unchanged stored attachment.
- Test an existing partner-specific report preference, an existing journal-specific report preference, and the normal
  fallback to **Invoice PDF**. Confirm preferences are not rewritten, a deliberately selected alternative action remains
  outside LGR routing, and the canonical action uses `lgr.report_invoice_document` when
  `_get_name_invoice_report()` returns `account.report_invoice_document`.
- Confirm the generic document-layout preview continues using its dedicated preview template. Validate future invoice
  body changes with a real invoice preview and PDF rather than treating the generic layout preview as an invoice-body
  preview.
- On invoices, credit notes, receipts, and representative vendor documents routed through LGR, confirm a checked
  `x_studio_hide_quantity` removes the Quantity and Unit Price headers and every corresponding normal, grouped,
  collapsed, and converted-UoM cell without leaving an empty column. Confirm an unchecked or missing field preserves
  both standard columns and their primary quantity/UoM values.
- With Quantity visible, test ordinary and grouped or collapsed-price product rows whose selected UoM is identical to
  and differs from the product/default UoM. Confirm only the primary quantity and selected unit render, with no muted
  secondary conversion or leftover line break. Repeat in desktop/mobile HTML and A4/Letter PDFs for users with and
  without the UoM display group. Confirm collapsed-composition summaries retain their sole intended quantity and that
  stored quantities, conversions, calculations, exports, and EDI/UBL data remain unchanged. Confirm Sales reports, the
  generic document-layout preview, and statutory templates outside the LGR route are unaffected.
- Exercise ordinary and grouped or collapsed invoice section rows in desktop/mobile HTML and A4/Letter PDFs across all
  six Odoo document-table styles. Confirm each `.o_line_section` cell resolves to exactly `#f0f0f0`, retains readable
  normal report text color, and resolves to `font-weight: 600` for both ordinary and grouped or collapsed rows,
  including their amount or total cells. With Open Sans selected in **Configure Document Layout**, confirm the bundled
  `Open_Sans-SemiBold.ttf` loads in HTML and PDF output and is visibly distinct from Regular `400` and Bold `700`.
  Confirm subsection and every other invoice-table row type remain unchanged, then select another company font and
  confirm that LGR neither forces Open Sans nor changes that font family's available weights.
- Exercise the option with products, sections, subsections, notes, discounts, taxes, grouped compositions, and collapsed
  prices in desktop/mobile HTML, A4/Letter PDFs, and mixed checked/unchecked batches. Confirm Discount, Taxes, Amount,
  and totals remain visible, and that the option leaves stored quantities and unit prices, calculations, exports, and
  EDI/UBL data unchanged.
- Test ordinary product rows with no additional description, one description line, and multiple description lines.
  Confirm an exact translated-product-name match retains the inherited `.875rem` product text and renders every
  following description line at `.75rem`, normal `400` weight, normal report color, `1.25` line height, and without an
  added margin. Repeat with default codes, variants, translated product names, grouped or collapsed-price rows, and
  desktop/mobile HTML and A4/Letter PDF output.
- Test manually edited labels that do and do not satisfy the exact translated-name-plus-newline prefix contract, along
  with productless and imported lines. Confirm nonmatching content uses Odoo's complete original rendering without
  truncation or duplication. Confirm sections, subsections, notes, collapsed-composition summaries, stored line data,
  calculations, exports, and EDI/UBL output remain unchanged.
- Confirm Terms and Conditions render once as the first left-side block below the invoice table. Verify the bold `Note`
  label has no colon, and that both the label and narration match the normal configured report text color while
  deliberate rich-text colors remain effective. Confirm the label appears exactly 12 mm below the table, is separated
  from the narration by its `2mm` bottom margin, uses `.875rem` text and `1.2` line height, and retains the existing 24
  mm gap below the narration. Test absent, short,
  multiline, list-based, long, and explicitly formatted rich-text narration beside both short and tall totals, verifying
  that it does not overlap the totals and flows below them only when needed. When narration is absent, confirm neither
  the label nor its spacing is emitted and `#payment_term` retains `mt-3`.
- Confirm a bold **Payment Details** heading uses a `1.5mm` bottom margin above the consolidated table when Reference or
  Terms is visible. Verify the heading uses `.875rem`, `1.2` line height, and the normal configured report color; with
  the unchanged `.5mm` top padding in the first table row, confirm approximately `2mm` to the first visible row text.
  Confirm the available rows appear in exact **Name**, **IBAN**, **BIC/SWIFT**, **Reference**, **Terms** order with bold
  labels and normal-weight values.
- Validate bank + BIC + Reference + Terms, bank without BIC, Reference without bank, Terms only, Reference without
  Terms, and neither value. Confirm missing rows collapse cleanly; a reference-only or terms-only record retains its
  heading and table; and a record with neither emits no heading, table, or empty section spacing.
- Exercise customer invoices, customer credit notes, sales receipts, vendor bills, vendor credit notes, and purchase
  receipts across draft, posted, cancelled, pro-forma, and self-billing contexts where applicable. Confirm Name, IBAN,
  and BIC/SWIFT remain restricted to outgoing invoices and incoming refunds with both a payment reference and selected
  partner bank; Reference retains its existing outgoing-invoice and incoming-refund scope and remains visible without a
  bank; and Terms appears whenever configured without exposing bank data on other document types.
- Verify Terms uses the translated payment-term name, the former rich-text payment-term note remains absent, and the
  `payment_communication`, `payment_terms_note_id`, and `payment_term` anchors remain present in their corresponding
  rows. Test simple terms, early-payment discounts, and single and multiple installments; confirm their existing subtree
  follows the table unchanged, remains outside its page-break wrapper, and can paginate independently.
- Test both QR types separately, both enabled, neither enabled, and zero residual. Confirm exactly 6 mm precedes the
  first active bank or payment-link QR whenever Payment Details exists, the gap is not duplicated, and no gap is emitted
  when Payment Details is absent. Also test long wrapping values and page breaks near the invoice-line table in HTML and
  A4/Letter PDFs.
- Confirm the bank-transfer QR instruction renders exactly three lines—`Scan the payment`, `details with your`, and
  `banking application`—while the payment-link QR wording remains unchanged.
- Confirm the bank-transfer QR retains its generated image and encoded payment payload but contains no white-circle Odoo
  overlay. Verify the payment-link QR retains its existing overlay and clickable-link behavior, the generic Configure
  Document Layout preview remains unchanged, and an existing stored PDF is unchanged until regenerated.
- Confirm Accounting, Sales, and preview key/value tables remain `20%` label / `80%` value and the consolidated Payment
  Details table uses `15% / 85%`. Verify every table retains `.875rem` text, `1.2` line height, `.5mm` vertical padding,
  and the `2mm` label/value gutter.
- Test the Payment Details group beside short and tall right-floating totals. Confirm its single table does not overlap
  and that the group may move below the totals when the remaining width is insufficient.
  Exercise all six Odoo document-table styles and verify `o_ignore_layout_styling` keeps every structural key/value
  table visually unchanged.
- Populate both masthead `account.move.ref` and Payment Details `account.move.payment_reference`; confirm both distinct
  values render with their intentionally duplicated **Reference** label.
- Confirm invoice narration content, fiscal and legal notes, totals, payment calculations, stored payment and bank data,
  printed payments, QR generation, and EDI output remain unchanged apart from the documented presentation changes.
- Preview and export invoices, credit notes, receipts, vendor documents, quotations, orders, Sales pro-formas, and the
  supported draft, cancelled, posted, self-billing, and separate invoice/shipping-address cases.
- Confirm each visible title retains its translated document-type wording without the record identifier or trailing `#`,
  while the document number appears in the single-column details table and the complete hidden title remains available
  for invoice splitting.
- Confirm every Accounting number/date pair follows the precedence table. Include ordinary and pro-forma incoming
  self-billing invoices and, when `account_debit_note` is installed, ordinary and pro-forma outgoing debit notes. Also
  confirm normal invoice rendering when that optional module is absent.
- Confirm document numbers still use `account.move.name`, `/` remains suppressed, reversal-generated values in
  `account.move.ref` remain generically labelled `Reference`, and partner references use `Customer Code` or
  `Vendor Code` according to document direction.
- Confirm Source appears only when populated on outgoing customer invoices, credit notes, and sales receipts, and
  remains hidden on vendor bills, vendor credits, and purchase receipts. Confirm Sales and preview terminology is
  unchanged.
- Confirm every Accounting and Sales detail date uses `d MMMM yyyy`, including localized month names and Sales Datetime
  values around midnight and year boundaries. Test missing and long detail values, partner-language field formatting and
  any installed LGR label translations,
  child invoice addresses, oversized logos, forced VAT, all six table styles, multiple companies, long addresses and
  wrapped detail values, and both A4 and Letter paper formats. Confirm company and recipient VAT render as
  `VAT <number>` without a colon, and test every missing email/VAT combination. Confirm company email follows the postal
  address without a gap and that the half-line gap always precedes a rendered company VAT row.
- Confirm the title/details and details/addresses gaps are 6 mm, the completed masthead has exactly 24 mm of
  non-collapsing space before shipping information or the report body, and the company email-to-VAT—or address-to-VAT
  when email is absent—gap is half the configured detail-line height.
- Verify real single-page and multipage PDFs: the complete masthead appears only on the first page, the footer and
  `Page X of Y` repeat, later pages do not reserve masthead height, and invoice splitting still works. Record any break
  caused by unusually tall masthead content as the accepted wkhtmltopdf limitation.
- Confirm an all-LGR Accounting or Sales batch receives an 11 mm top margin and zero header spacing. Test a mixed batch
  containing LGR and built-in layouts and confirm the incoming paper-format margins and header spacing are preserved;
  allow additional top whitespace on its LGR pages. Then test a batch using only built-in layouts and confirm its
  original margins, title placement, and `#informations` block remain unchanged.
- Confirm every rendered record retains one invisible technical header, one article, and one footer, so multi-document
  footer selection remains correctly indexed.
- Confirm the rebuilt archive contains exactly the ten allowlisted regular files, reports version `1.7.2`, and contains
  no `.DS_Store`, `__MACOSX`, cache, or bytecode entries.
- Import version `1.7.2` into a staging Odoo Online database with **Force init** disabled and confirm the company's
  existing LGR selection and report preferences persist before updating production.
