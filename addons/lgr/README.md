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
- Structured company details in the left information column: the legal entity name, postal address, a half-line gap,
  unprefixed email address, and `VAT <number>`. If email is missing, the gap precedes VAT instead. Missing optional
  values are omitted.
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
blocks, configured font and colors, and all six built-in table styles. Structural layout and document-details tables are
excluded from document-table styling. The original complete title remains in Odoo's invisible article heading for PDF
invoice splitting even though the cleaned visible title is rendered in the first-page masthead.

## Custom invoice template and canonical routing

`lgr.report_invoice_document` is a primary inheritance of `account.report_invoice_document`. It provides an independent
invoice-design surface while retaining Odoo's resolved default invoice architecture, including compatible extension
views. Version 1.5.0 established this routing and stable customization point; version 1.5.2 includes the focused body
behavior provided by the optional Studio-controlled quantity and unit-price setting described below. Version 1.6.0 adds
the structured payment and bank details described below.

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

### Structured payment and bank details

The LGR invoice body keeps payment information in Odoo's existing left-aligned `#payment_term` area beneath the invoice
line table and alongside the right-floating totals. The first structured section renders available values in this order:

1. **Payment Reference:** `account.move.payment_reference`
2. **Payment Terms:** the translated `account.payment.term.name`
3. Odoo's existing early-payment discount and installment details

The Payment Terms value deliberately uses the concise payment-term name rather than the editable rich-text **Description
on the Invoice** (`account.payment.term.note`). That rich-text note is no longer printed in this block; the invoice's
separate narration and legal or fiscal-position notes remain unchanged.

When Odoo's existing bank condition is met, a second section renders:

1. **Name:** the invoice company's name
2. **IBAN:** the selected partner-bank account number
3. **BIC/SWIFT:** the selected bank account's associated BIC/SWIFT code, when available

The bank section retains Odoo's existing scope: it is shown only for an outgoing invoice or incoming refund that has
both a payment reference and a selected partner bank. All labels are bold and values use normal weight. A non-collapsing
6 mm gap separates the payment and bank sections, and another 6 mm gap separates the bank section from the first active
bank or payment-link QR-code section. These gaps are omitted when the adjacent section is absent. Each section stays
left aligned, permits long values to wrap, and uses best-effort page-break avoidance for wkhtmltopdf.

This is presentation-only behavior. It does not change payment terms, references, bank records, calculations, payment
processing, or EDI output. The new literal labels are English until corresponding entries are added to an LGR
translation catalog. Previously generated PDF attachments remain unchanged until Odoo regenerates or replaces them
through its normal workflow.

Country or Studio views that inject additional visible wording inside Odoo's original payment-communication paragraph
must extend the LGR structured sections explicitly. The standard Dutch SaaS 19.3 invoice route adds no such wording;
country routes that select a separate statutory primary invoice template continue to bypass LGR unchanged.

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

Each detail occupies one label/value row, and the complete row is omitted when its value is unavailable. Long values
wrap instead of being truncated. Labels occupy 20% of the table, values occupy 80%, and a 2 mm right padding on the
label cell provides the minimum gutter. This split is optimized for labels of up to approximately 14 characters; longer
labels and translations may wrap. The generic layout preview displays its dummy invoice number, invoice date, and due
date in the same single-column table. Active invoice and quotation previews use their Accounting and Sales helpers and
real record values.

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
email is displayed without a prefix. After the postal address, a half-line gap precedes the email, followed immediately
by `VAT <number>`. If email is unavailable, the gap precedes VAT instead. VAT is resolved as
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
record, company selection, partner report preferences, and journal report preferences are retained across this `1.6.0`
update. The canonical invoice route requires no new report-action selection.

## Validation checklist

- Open the generic document-layout preview and active invoice and quotation previews. Confirm the first-page order is
  title, details, then company/recipient addresses, with the logo at the top right, an 11 mm top inset, and no
  duplicated
  `#informations` block.
- Confirm the combined `lgr.report_invoice_document` architecture matches Odoo's resolved default invoice document apart
  from its independent template identity, the optional Quantity/Unit Price visibility behavior, and the existing LGR
  Accounting-details adapter.
- Confirm `lgr.report_invoice_use_lgr_document` changes exactly one `t-call`: the standard
  `account.report_invoice_document` branch in `account.report_invoice`. Verify that the branch condition, partner
  language, payment-enabled wrapper, and every localization-owned dispatcher branch remain unchanged.
- Render the same records through Odoo's canonical **Invoice PDF** action before and after the update. Compare invoice
  lines, sections and notes, discounts, taxes, totals, payment entries, QR behavior, structured payment and bank
  details,
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
  both standard columns.
- Exercise the option with products, sections, subsections, notes, discounts, taxes, grouped compositions, and collapsed
  prices in desktop/mobile HTML, A4/Letter PDFs, and mixed checked/unchecked batches. Confirm Discount, Taxes, Amount,
  and totals remain visible, and that the option leaves stored quantities and unit prices, calculations, exports, and
  EDI/UBL data unchanged.
- Confirm the structured payment section displays available **Payment Reference:** and **Payment Terms:** rows in that
  order, with bold labels and normal-weight values. Verify Payment Terms uses the translated payment-term name, the
  former rich-text payment-term note is absent, and early-payment discount and installment details remain intact.
- On outgoing invoices and incoming refunds, confirm the bank section displays **Name:**, **IBAN:**, and an optional
  **BIC/SWIFT:** row in that order when both a payment reference and partner bank are present. Verify representative
  vendor documents and records missing either prerequisite do not acquire the bank section.
- Test payment reference, payment term, bank account, and BIC independently present and missing. Confirm there is
  exactly 6 mm between adjacent payment and bank sections and between the bank section and the first active bank or
  payment-link QR code, with no empty gap when the adjacent section is absent. Test both QR types, both enabled, neither
  enabled, zero residual, long wrapping values, and page breaks near the invoice-line table in HTML and A4/Letter PDFs.
- Confirm invoice narration, fiscal and legal notes, totals, payment calculations, stored payment and bank data, and EDI
  output remain unchanged by the structured presentation.
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
  `VAT <number>` without a colon, and test every missing email/VAT combination.
- Confirm the title/details and details/addresses gaps are 6 mm, the completed masthead has exactly 24 mm of
  non-collapsing space before shipping information or the report body, and the address-to-email/VAT gap is half the
  configured detail-line height.
- Verify real single-page and multipage PDFs: the complete masthead appears only on the first page, the footer and
  `Page X of Y` repeat, later pages do not reserve masthead height, and invoice splitting still works. Record any break
  caused by unusually tall masthead content as the accepted wkhtmltopdf limitation.
- Confirm an all-LGR Accounting or Sales batch receives an 11 mm top margin and zero header spacing. Test a mixed batch
  containing LGR and built-in layouts and confirm the incoming paper-format margins and header spacing are preserved;
  allow additional top whitespace on its LGR pages. Then test a batch using only built-in layouts and confirm its
  original margins, title placement, and `#informations` block remain unchanged.
- Confirm every rendered record retains one invisible technical header, one article, and one footer, so multi-document
  footer selection remains correctly indexed.
- Confirm the rebuilt archive contains exactly the ten allowlisted regular files, reports version `1.6.0`, and contains
  no `.DS_Store`, `__MACOSX`, cache, or bytecode entries.
- Import version `1.6.0` into a staging Odoo Online database with **Force init** disabled and confirm the company's
  existing LGR selection and report preferences persist before updating production.
