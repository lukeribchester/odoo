# LGR

An importable custom document layout for Odoo Online. The module adds **LGR** to Odoo's document-layout selector without
modifying any of Odoo's built-in layouts. Installation does not automatically select LGR for a company.

## Layout behavior

The repeating document header contains:

- An optional context-aware document title at the top left. When omitted, no empty title space is reserved.
- Structured company details in the left information column: the legal entity name, postal address, KvK number, VAT
  number, email address, and phone number. Missing optional values and their labels are omitted.
- Recipient details in the adjacent information column: its heading, legal entity name, postal address, and VAT number
  when available.
- The company logo at the top right. The information area expands when no logo is configured.

The repeating footer displays `company.report_footer` on the left. Generated PDFs show `Page X of Y` on the right; the
document-layout preview shows `Page 1 of 1`. Normal HTML reports omit the counter because Odoo cannot provide a reliable
total page count there.

The layout preserves Odoo's report article metadata, document slot, hidden PDF title, address/information blocks,
configured font and colors, and all six built-in table styles. Structural header and footer tables are deliberately
excluded from document-table styling.

## Recipient mappings

Unless a caller supplies an explicit LGR override, the layout resolves recipients as follows:

| Report context                            | Recipient                           | Heading                       |
|-------------------------------------------|-------------------------------------|-------------------------------|
| Customer invoice, credit note, or receipt | `account.move.partner_id`           | Bill to                       |
| Vendor bill, credit note, or receipt      | `account.move.partner_id`           | Supplier                      |
| Quotation or sales order                  | `sale.order.partner_invoice_id`     | Bill to                       |
| Document-layout preview                   | Existing preview `address` fragment | Bill to                       |
| Other reports                             | Existing `address` fragment         | Caller heading, or no heading |

For record-based recipients, the selected invoice/postal address is displayed with the commercial entity's name and VAT
number. Sales reports keep a separate shipping-only information block when the shipping and invoice addresses differ.
Accounting's existing shipping information block is preserved.

## QWeb caller interface

LGR continues to honor these standard Odoo caller values:

- `layout_document_title`: optional QWeb title content shown at the top left.
- `address`: the standard pre-rendered recipient/address fragment and fallback for reports without a record mapping.
- `information_block`: supplementary report information, including shipping data.
- `forced_vat`: fiscal-position VAT override used ahead of the company's VAT.

Future nested report templates may additionally set:

- `lgr_recipient`: a `res.partner` record that overrides the built-in recipient mapping.
- `lgr_recipient_title`: optional translated QWeb content or text that overrides the built-in recipient heading.

Company data is intentionally read from structured `res.company` and
`res.partner` fields rather than the rich-text **Company Details** editor. KvK is read from
`additional_identifiers["NL_KVK"]` when present, with
`company_registry` as the legacy fallback. Company VAT is resolved as
`forced_vat or company.vat`.

## SaaS compatibility and dependencies

Odoo Online does not accept arbitrary custom Python code, so all behavior is implemented through XML/QWeb and SCSS.
Asset paths are explicit because importable modules do not expand asset globs. The stylesheet is loaded only through
`web.report_assets_common`, which serves both report previews and generated PDFs.

The module directly depends on `web`, `account`, and `sale`. Those applications must therefore be available in the
target database. Its short numeric version is series-neutral: Odoo prefixes it with the active server series, avoiding a
manual manifest-version change for each SaaS upgrade.

Replace the manifest's `Your Company` author placeholder with the owning organization's name before the first production
import.

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
declare such records. Validate imports and report changes on a non-production database first.

## Validation checklist

- Preview and export invoices, credit notes, vendor documents, quotations, and sales orders, including separate invoice
  and shipping addresses.
- Test with and without titles, logos, KvK, VAT, email, phone, recipient VAT, and recipient addresses.
- Cover `NL_KVK`, the legacy registry fallback, fiscal-position VAT overrides, child invoice addresses, long values,
  oversized logos, and multiple companies.
- Exercise every built-in table style and both supported paper formats.
- Verify real single-page and multipage PDFs: the complete header/footer repeats,
  `Page X of Y` is exact, and content does not overlap either section.
- Confirm that selecting LGR is company-specific and leaves Odoo's default layouts unchanged.
