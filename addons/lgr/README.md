# LGR

An importable custom document layout for Odoo Online. The module adds **LGR** to Odoo's document-layout selector without
modifying any of Odoo's built-in layouts. Installation does not automatically select LGR for a company.

## Layout behavior

The repeating document header starts with a context-aware masthead above the company and recipient addresses. It
contains:

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

The title, details, company and recipient information, and logo repeat together on every generated PDF page. In the
layout preview their order is title, details, then the address columns, with 6 mm separating each masthead section and
the logo remaining at the top right. The complete header is outside the report article and therefore reduces the body
area available on each page.

For Accounting and Sales PDFs whose batch contains at least one document using LGR, the module requests a 110 mm top
margin and 110 mm header spacing through Odoo's supported report-rendering values. This reservation applies to the whole
PDF batch so mixed-company batches remain safe. A custom paper format is not required. Batches using only built-in
layouts retain Odoo's existing margin and spacing values.

The repeating footer displays `company.report_footer` on the left. Generated PDFs show `Page X of Y` on the right; the
document-layout preview shows `Page 1 of 1`. Normal HTML reports omit the counter because Odoo cannot provide a reliable
total page count there.

The layout preserves Odoo's report article metadata, document slot, complete hidden PDF title, address and information
blocks, configured font and colors, and all six built-in table styles. Structural layout and document-details tables are
excluded from document-table styling. The original complete title remains in Odoo's invisible article heading for PDF
invoice splitting even though the cleaned visible title is rendered in the repeating header.

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
- `lgr_document_details`: trusted body-form QWeb content rendered beneath the visible title in the repeating header. It
  should contain only the details table; the LGR layout owns the masthead wrapper, spacing, and repetition behavior.

The built-in reusable helper templates are:

- `lgr.account_move_document_details`
- `lgr.sale_order_document_details`
- `lgr.preview_document_details`

A future custom invoice template can call, inherit, or replace `lgr.account_move_document_details`, or pass its own
`lgr_document_details` fragment, without changing the external layout. Report-specific templates should continue to own
field selection, conditions, translatable source wording, and formatting; the shared layout owns placement and styling.

The helpers render in Odoo's existing partner-language context, so month names, dates, and field widgets retain
localized formatting within LGR's fixed day–full-month–year date order.
Their literal labels belong to LGR's own QWeb view records, however, and therefore need an LGR `i18n/<language>.po`
catalog before they appear in a non-English language. Translations from the dependency views are not inherited merely
because a source label is identical. No non-English catalog is bundled until the required target languages and wording
are agreed.

Company data is intentionally read from structured `res.company` and `res.partner` fields rather than the rich-text
**Company Details** editor. The header does not display the structured company phone or registration number. Company
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

This implementation intentionally does not adapt `account.payment` payment receipts, Purchase, Inventory, Repair, or
country modules that select a different primary invoice report. Those report families require their own small adapters
and should be added only when the corresponding applications or localized reports are in scope.

The 110 mm reservation is intentionally limited to the standard Accounting invoice and Sales order/pro-forma report
containers supported by this module. The single-column table can contain up to nine Accounting rows or seven Sales rows.
With the current typography, unusually tall addresses or wrapped values can exceed the fixed reservation and overlap the
body; this accepted limitation must be tested against real company data. Reserving this space can increase the number of
pages in a report.

## Package, install, and update on Odoo Online

1. From the `addons` directory containing `lgr`, recreate the archive from the explicit nine-file allowlist. Removing
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
record and company selection are retained across this `1.3.9` update.

## Validation checklist

- Open the generic document-layout preview and active invoice and quotation previews. Confirm the order is title,
  details, then company/recipient addresses, with the logo at the top right and no duplicated `#informations` block.
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
- Confirm the title/details and details/addresses gaps are both 6 mm, and the address-to-email/VAT gap is half the
  configured detail-line height.
- Verify real single-page and multipage PDFs: the complete header and footer repeat, `Page X of Y` is exact, and invoice
  splitting still works. Inspect header/body clearance and record any overflow from unusually tall content as the known
  fixed-margin limitation.
- Test a mixed-company batch containing LGR and built-in layouts and confirm the whole PDF receives the 110 mm
  reservation. Then test a batch using only built-in layouts and confirm its original margins, title placement, and
  `#informations` block remain unchanged.
- Confirm the rebuilt archive contains exactly the nine allowlisted regular files, reports version `1.3.9`, and contains
  no `.DS_Store`, `__MACOSX`, cache, or bytecode entries.
- Import version `1.3.9` into a staging Odoo Online database with **Force init** disabled and confirm the company's
  existing LGR selection persists before updating production.
