# LGR

An importable custom document layout for Odoo Online. The module adds **LGR** to Odoo's document-layout selector without
modifying any of Odoo's built-in layouts. Installation does not automatically select LGR for a company.

## Layout behavior

The first page starts with a document masthead in the normal report flow. It contains:

- An optional context-aware document title. Odoo's translated document-type wording is preserved while a trailing
  document identifier and separator are removed. Receipts use the title `Receipt`; no empty title space is reserved when
  no title remains.
- An optional context-aware details grid directly beneath the title. Accounting, Sales, and the generic layout preview
  provide built-in detail fragments. If a fragment exists without a title, it starts at the top left without an empty
  title row.

Because the masthead is part of the report article, its title and details appear only once and participate in normal
page flow. It is kept together where possible and does not require a custom paper format.

The repeating document header contains:

- Structured company details in the left information column: the legal entity name, postal address, raw email address, a
  one-line gap, and the raw VAT number. Missing optional values are omitted.
- Recipient details in the adjacent information column: its mapped heading, legal entity name, postal address, and raw
  VAT number when available.
- The company logo at the top right. The information area expands when no logo is configured.

The repeating footer displays `company.report_footer` on the left. Generated PDFs show `Page X of Y` on the right; the
document-layout preview shows `Page 1 of 1`. Normal HTML reports omit the counter because Odoo cannot provide a reliable
total page count there.

The layout preserves Odoo's report article metadata, document slot, complete hidden PDF title, address and information
blocks, configured font and colors, and all six built-in table styles. Structural layout and document-details tables are
excluded from document-table styling.

## Context-aware document details

The Accounting helper covers customer invoices, customer credit notes, sales receipts, vendor bills, vendor credit
notes, and purchase receipts, including their applicable draft, cancelled, posted, pro-forma, and self-billing contexts.
It uses Odoo's existing field conditions and formatting and can display:

| Row | Left detail                      | Right detail                   |
|-----|----------------------------------|--------------------------------|
| 1   | Context-specific document number | Context-specific document date |
| 2   | Due date                         | Delivery date                  |
| 3   | Taxable-supply date              | Source document                |
| 4   | Customer code                    | Reference                      |
| 5   | Incoterm and location            | —                              |

The Sales helper covers quotations, sales orders, and Sales pro-forma invoices and can display:

| Row | Left detail                      | Right detail          |
|-----|----------------------------------|-----------------------|
| 1   | Context-specific document number | Customer reference    |
| 2   | Context-specific document date   | Expiration date       |
| 3   | Delivery date                    | Incoterm and location |
| 4   | Contact                          | —                     |

Missing pairs are omitted, and a row is omitted when neither pair has a value. Long values wrap instead of being
truncated. The generic layout preview displays its dummy invoice number, invoice date, and due date in the same grid.
Active invoice and quotation previews use their Accounting and Sales helpers and real record values.

Odoo's original `#informations` nodes remain in their report templates so other inherited views can still target them.
When LGR receives a details fragment, an LGR-scoped article class hides the original block to prevent duplication. Other
document layouts continue to show the original block unchanged.

Fields added by a localization or Studio only to the original `#informations` block do not automatically move into LGR's
grid. Extend the appropriate LGR helper when such a field should appear in the masthead. The standard Dutch SaaS 19.3
invoice path is covered.

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

For record-based recipients, the selected invoice/postal address is displayed with the commercial entity's name and VAT
number. Sales reports keep a separate shipping-only information block when the shipping and invoice addresses differ.
Accounting's existing shipping information block is preserved and follows the first-page masthead.

## QWeb caller interface

LGR continues to honor these standard Odoo caller values:

- `layout_document_title`: optional QWeb title content. LGR displays a plain-text copy without a trailing record
  identifier, while preserving the complete original value for Odoo's hidden PDF title and invoice splitting.
- `address`: the standard pre-rendered recipient/address fragment and fallback for reports without a record mapping.
- `information_block`: supplementary report information, including shipping data.
- `forced_vat`: fiscal-position VAT override used ahead of the company's VAT.

Nested report templates may additionally set:

- `lgr_recipient`: a `res.partner` record that overrides the built-in recipient mapping.
- `lgr_document_details`: trusted body-form QWeb content rendered beneath the visible title. It should contain only the
  details table; the LGR layout owns the masthead wrapper, spacing, and first-page behavior.

The built-in reusable helper templates are:

- `lgr.account_move_document_details`
- `lgr.sale_order_document_details`
- `lgr.preview_document_details`

A future custom invoice template can call, inherit, or replace `lgr.account_move_document_details`, or pass its own
`lgr_document_details` fragment, without changing the external layout. Report-specific templates should continue to own
field selection, conditions, translatable source wording, and formatting; the shared layout owns placement and styling.

The helpers render in Odoo's existing partner-language context, so dates and field widgets retain localized formatting.
Their literal labels belong to LGR's own QWeb view records, however, and therefore need an LGR `i18n/<language>.po`
catalog before they appear in a non-English language. Translations from the dependency views are not inherited merely
because a source label is identical. No non-English catalog is bundled until the required target languages and wording
are agreed.

Company data is intentionally read from structured `res.company` and `res.partner` fields rather than the rich-text
**Company Details** editor. The header does not display the structured company phone or registration number. Company
email and VAT are displayed without prefixes; VAT is resolved as `forced_vat or company.vat` and follows the email and
one-line gap.

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

## Package, install, and update on Odoo Online

1. From the directory containing the addon, create an archive whose top-level directory is `lgr`:

   ```bash
   zip -FSr lgr.zip lgr \
       -x '*/__pycache__/*' '*.pyc' '*.DS_Store'
   ```

2. Enable developer mode and ensure **Import Module** (`base_import_module`) is installed.
3. Open **Apps > Import Module**, upload `lgr.zip`, leave **Force init** disabled, and import the module. A newly
   imported module is initialized automatically.
4. Open the company's **Configure Document Layout** dialog, select **LGR**, inspect the preview, and save.

For an update, upload a newly packaged archive with an incremented manifest version and leave **Force init** disabled.
Enable **Force init** only when you deliberately need to reload records protected by `noupdate`; LGR does not currently
declare such records. Validate imports and report changes on a non-production database first. The existing LGR layout
record and company selection are retained across this `1.3.0` update.

## Validation checklist

- Open the generic document-layout preview and active invoice and quotation previews. Confirm the title and details
  appear once at the top of the article and the original `#informations` block is not duplicated.
- Preview and export invoices, credit notes, receipts, vendor documents, quotations, orders, Sales pro-formas, and the
  supported draft, cancelled, posted, self-billing, and separate invoice/shipping-address cases.
- Confirm each visible title retains its translated document-type wording without the record identifier or trailing `#`,
  while the document number appears in the details grid and the complete hidden title remains available for invoice
  splitting.
- Test missing and long detail values, partner-language date/field formatting and any installed LGR label translations,
  child invoice addresses, oversized logos, forced VAT, all six table styles, multiple companies, and both supported
  paper formats.
- Verify real single-page and multipage PDFs: title and details appear on the first page only; company/recipient header
  and footer repeat; `Page X of Y` is exact; and content does not overlap or split unexpectedly.
- Temporarily select a built-in layout and confirm its original title and `#informations` block remain unchanged.
- Import version `1.3.0` into a staging Odoo Online database with **Force init** disabled and confirm the company's
  existing LGR selection persists before updating production.
