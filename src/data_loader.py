"""
Data loading and processing module for the AI Asset Management Chatbot.
Comprehensive version that properly handles ALL nested data from ALL JSON files.
"""

import json
import streamlit as st
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
from langchain_core.documents import Document


class DataLoader:
    """Handles loading and processing of JSON asset data with comprehensive field inclusion."""
    
    def __init__(self, config):
        """Initialize data loader with configuration."""
        self.config = config
    
    def load_and_process_data(self) -> Tuple[Optional[Dict[str, Any]], Optional[List[Document]]]:
        """
        Load and process ALL JsonData files into joined, searchable documents.
        Returns a tuple of (joined_data_dict, documents).
        Properly handles nested data structures in JSON files.
        """
        try:
            base_dir = Path(self.config.JSON_DIR)
            if not base_dir.exists():
                return None, None
            
            # Helper to load a JSON file (assume UTF-8/UTF-8-SIG)
            def load_json(file_path: Path) -> Optional[Any]:
                if not file_path.exists():
                    return None
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        return json.load(f)
                except Exception:
                    with open(file_path, 'r', encoding='utf-8-sig') as f:
                        return json.load(f)

            # Load ALL datasets
            assets = load_json(base_dir / 'Assests.json') or []
            work_orders = load_json(base_dir / 'WorkOrders.json') or []
            work_requests = load_json(base_dir / 'WorkRequests.json') or []
            work_types = load_json(base_dir / 'WorkTypes.json') or []
            work_priorities = load_json(base_dir / 'WorkPriorities.json') or []
            invoices = load_json(base_dir / 'Invoice.json') or []
            invoice_lines = load_json(base_dir / 'InvoiceLines.json') or []
            purchase_orders = load_json(base_dir / 'PurchaseOrders.json') or []
            po_lines = load_json(base_dir / 'PurchaseOrderLines.json') or []
            po_batches = load_json(base_dir / 'PurchaseOrderBatches.json') or []
            vendors = load_json(base_dir / 'Vendors.json') or []
            vendor_types = load_json(base_dir / 'VendorTypes.json') or []
            customers = load_json(base_dir / 'customers.json') or []
            employees = load_json(base_dir / 'Employees.json') or []
            phones = load_json(base_dir / 'phones.json') or []
            addresses = load_json(base_dir / 'Addresses.json') or []
            parts = load_json(base_dir / 'parts.json') or []
            service_items = load_json(base_dir / 'ServiceItems.json') or []
            custom_field_defs = load_json(base_dir / 'CustomFields.json') or []

            # Build lookup maps for relationships
            work_type_by_id = {wt.get('workTypeId'): wt for wt in work_types}
            prio_by_id = {wp.get('priorityId'): wp for wp in work_priorities}
            vendor_by_id = {v.get('vendorId'): v for v in vendors}
            vendor_type_label = {vt.get('typeId'): vt for vt in vendor_types}
            customer_by_key = {c.get('customerKey'): c for c in customers}
            employee_by_name = {e.get('employeeName'): e for e in employees}
            employee_by_key = {e.get('employeeKey'): e for e in employees}
            asset_by_id = {a.get('assetId'): a for a in assets}
            custom_def_by_key = {d.get('customFieldKey'): d for d in custom_field_defs}
            parts_by_id = {p.get('partId'): p for p in parts}

            # Group children for relationships
            wos_by_asset = {}
            for wo in work_orders:
                asset_id = wo.get('assetId')
                if asset_id:
                    wos_by_asset.setdefault(asset_id, []).append(wo)

            inv_lines_by_invoice = {}
            for il in invoice_lines:
                inv_lines_by_invoice.setdefault(il.get('invoiceNumber'), []).append(il)

            invoices_by_customer = {}
            invoices_by_wo_key = {}
            for inv in invoices:
                invoices_by_customer.setdefault(inv.get('customerKey'), []).append(inv)
                if inv.get('originatingWorkOrderKey') is not None:
                    invoices_by_wo_key.setdefault(inv.get('originatingWorkOrderKey'), []).append(inv)

            po_lines_by_po_key = {}
            for pl in po_lines:
                po_lines_by_po_key.setdefault(pl.get('purchaseOrderKey'), []).append(pl)

            po_batches_by_po_key = {}
            for pb in po_batches:
                po_batches_by_po_key.setdefault(pb.get('purchaseOrderKey'), []).append(pb)

            # Utilities
            def resolve_custom_fields(custom_fields: List[Dict[str, Any]]) -> List[str]:
                out = []
                for cf in custom_fields or []:
                    key = cf.get('customFieldKey')
                    val = cf.get('value')
                    name = cf.get('fieldName') or (custom_def_by_key.get(key) or {}).get('fieldName')
                    if name and (val is not None and val != ""):
                        out.append(f"{name}: {val}")
                return out

            def format_all_fields(data: Dict[str, Any], prefix: str = "") -> List[str]:
                """Format ALL fields from a data object into text lines."""
                lines = []
                for key, value in data.items():
                    if value is not None and value != "":
                        if isinstance(value, (list, dict)):
                            if value:  # Only include non-empty collections
                                lines.append(f"{prefix}{key}: {json.dumps(value, default=str)}")
                        else:
                            lines.append(f"{prefix}{key}: {value}")
                return lines

            def format_nested_arrays(data: Dict[str, Any], array_fields: List[str]) -> List[str]:
                """Format nested arrays as readable text."""
                lines = []
                for field in array_fields:
                    if field in data and data[field]:
                        lines.append(f"{field.title()}:")
                        for item in data[field]:
                            if isinstance(item, dict):
                                item_lines = []
                                for k, v in item.items():
                                    if v is not None and v != "":
                                        item_lines.append(f"  {k}: {v}")
                                if item_lines:
                                    lines.append(f"  - {', '.join(item_lines)}")
                            else:
                                lines.append(f"  - {item}")
                return lines

            # Create Documents (comprehensive summaries)
            documents: List[Document] = []

            # Global summary document
            try:
                total_assets = len(assets)
                entities = {}
                statuses = {}
                categories = {}
                for a in assets:
                    entities[a.get('entityName', 'Unknown')] = entities.get(a.get('entityName', 'Unknown'), 0) + 1
                    statuses[a.get('statusId', 'Unknown')] = statuses.get(a.get('statusId', 'Unknown'), 0) + 1
                    categories[a.get('categoryId', 'Unknown')] = categories.get(a.get('categoryId', 'Unknown'), 0) + 1

                lines: List[str] = []
                lines.append("DOC: GLOBAL SUMMARY - System Overview and Statistics")
                lines.append("")
                lines.append("ENTITY COUNTS:")
                lines.append(f"Total assets: {total_assets}")
                lines.append(f"Total customers: {len(customers)}")
                lines.append(f"Total vendors: {len(vendors)}")
                lines.append(f"Total employees: {len(employees)}")
                lines.append(f"Total work orders: {len(work_orders)}")
                lines.append(f"Total invoices: {len(invoices)}")
                lines.append(f"Total purchase orders: {len(purchase_orders)}")
                lines.append(f"Total parts: {len(parts)}")
                lines.append(f"Total service items: {len(service_items)}")
                lines.append("")
                if entities:
                    lines.append("Assets by entity:")
                    for k, v in sorted(entities.items()):
                        lines.append(f"  {k}: {v}")
                if statuses:
                    lines.append("Assets by status:")
                    for k, v in sorted(statuses.items()):
                        lines.append(f"  {k}: {v}")
                if categories:
                    lines.append("Assets by category:")
                    for k, v in sorted(categories.items()):
                        lines.append(f"  {k}: {v}")
                documents.append(Document(page_content="\n".join(lines), metadata={"doc_type": "global_summary"}))
            except Exception:
                pass

            # Customers summary document (ensures full list is retrievable)
            try:
                lines: List[str] = []
                lines.append("DOC: CUSTOMERS SUMMARY")
                lines.append(f"Total customers: {len(customers)}")
                lines.append("Customers:")
                for c in customers:
                    name = c.get('customerName') or c.get('fileAsName') or c.get('customerId')
                    cid = c.get('customerId')
                    ckey = c.get('customerKey')
                    email = c.get('emailAddress')
                    status = c.get('statusId')
                    lines.append(
                        f"  - customerKey={ckey} customerId={cid} name={name} status={status} email={email}"
                    )
                documents.append(Document(page_content="\n".join(lines), metadata={"doc_type": "customers_summary"}))
            except Exception:
                pass

            # COMPREHENSIVE ASSETS - Include ALL fields including nested data
            for a in assets:
                asset_id = a.get('assetId')
                customer_key = a.get('customerKey')
                customer = customer_by_key.get(customer_key) if customer_key else None
                related_wos = wos_by_asset.get(asset_id, [])
                
                text_parts: List[str] = []
                text_parts.append("DOC: ASSET")
                
                # Include ALL asset fields
                text_parts.extend(format_all_fields(a, ""))
                
                # Format nested custom fields properly
                if 'customFields' in a and a['customFields']:
                    text_parts.append("Custom Fields:")
                    for cf in a['customFields']:
                        if cf.get('value') is not None and cf.get('value') != "":
                            field_name = cf.get('fieldName', 'Unknown Field')
                            field_value = cf.get('value')
                            text_parts.append(f"  {field_name}: {field_value}")
                
                # Add customer info if available
                if customer:
                    text_parts.append(f"Customer Details: {customer.get('customerName')} (customerKey {customer_key})")
                    text_parts.append(f"Customer Email: {customer.get('emailAddress')}")
                    text_parts.append(f"Customer Status: {customer.get('statusId')}")
                
                # Add work orders
                if related_wos:
                    text_parts.append(f"Work Orders for this asset: {len(related_wos)}")
                    for wo in related_wos[:5]:
                        wt = work_type_by_id.get(wo.get('workTypeId'))
                        pr = prio_by_id.get(wo.get('priorityId'))
                        text_parts.append(f"  WO #{wo.get('workOrderNumber')} [{wo.get('statusId')}] Type={wo.get('workTypeId')} Priority={wo.get('priorityId')}")
                
                doc = Document(page_content="\n".join(text_parts), metadata={"doc_type": "asset", "assetId": asset_id})
                documents.append(doc)

            # COMPREHENSIVE WORK ORDERS - Include ALL fields
            for wo in work_orders:
                asset = asset_by_id.get(wo.get('assetId'))
                wt = work_type_by_id.get(wo.get('workTypeId'))
                pr = prio_by_id.get(wo.get('priorityId'))
                assigned_emp = employee_by_name.get(wo.get('assigned'))
                invoices_for_wo = invoices_by_wo_key.get(wo.get('workOrderKey'), [])
                
                text_parts = ["DOC: WORK ORDER"]
                # Include ALL work order fields
                text_parts.extend(format_all_fields(wo, ""))
                
                # Add related asset info
                if asset:
                    text_parts.append(f"Asset Details: {asset.get('description')} (ID: {asset.get('assetId')})")
                
                # Add work type details
                if wt:
                    text_parts.append(f"Work Type Details: {json.dumps(wt, default=str)}")
                
                # Add priority details
                if pr:
                    text_parts.append(f"Priority Details: {json.dumps(pr, default=str)}")
                
                # Add assigned employee details
                if assigned_emp:
                    text_parts.append(f"Assigned Employee Details: {json.dumps(assigned_emp, default=str)}")
                
                # Add linked invoices
                if invoices_for_wo:
                    text_parts.append(f"Linked Invoices: {[inv.get('invoiceNumber') for inv in invoices_for_wo]}")
                
                doc = Document(page_content="\n".join(text_parts), metadata={"doc_type": "work_order", "workOrderNumber": wo.get('workOrderNumber')})
                documents.append(doc)

            # COMPREHENSIVE PURCHASE ORDERS - Include ALL fields
            for po in purchase_orders:
                v = vendor_by_id.get(po.get('vendorId'))
                lines = po_lines_by_po_key.get(po.get('purchaseOrderKey'), [])
                batches = po_batches_by_po_key.get(po.get('purchaseOrderKey'), [])
                
                text_parts = ["DOC: PURCHASE ORDER"]
                # Include ALL purchase order fields
                text_parts.extend(format_all_fields(po, ""))
                
                # Add vendor details
                if v:
                    text_parts.append(f"Vendor Details: {json.dumps(v, default=str)}")
                
                # Add line items
                if lines:
                    text_parts.append(f"Line Items ({len(lines)}):")
                    for pl in lines:
                        text_parts.append(f"  Line: {json.dumps(pl, default=str)}")
                
                # Add batches
                if batches:
                    text_parts.append(f"Batches ({len(batches)}):")
                    for pb in batches:
                        text_parts.append(f"  Batch: {json.dumps(pb, default=str)}")
                
                doc = Document(page_content="\n".join(text_parts), metadata={"doc_type": "purchase_order", "purchaseOrderNumber": po.get('purchaseOrderNumber')})
                documents.append(doc)

            # COMPREHENSIVE INVOICES - Include ALL fields
            for inv in invoices:
                lines = inv_lines_by_invoice.get(inv.get('invoiceNumber'), [])
                cust = customer_by_key.get(inv.get('customerKey'))
                
                text_parts = ["DOC: INVOICE"]
                # Include ALL invoice fields
                text_parts.extend(format_all_fields(inv, ""))
                
                # Format nested custom fields
                if 'customFields' in inv and inv['customFields']:
                    text_parts.append("Custom Fields:")
                    for cf in inv['customFields']:
                        if cf.get('value') is not None and cf.get('value') != "":
                            field_name = cf.get('fieldName', 'Unknown Field')
                            field_value = cf.get('value')
                            text_parts.append(f"  {field_name}: {field_value}")
                
                # Add customer details
                if cust:
                    text_parts.append(f"Customer Details: {json.dumps(cust, default=str)}")
                
                # Add line items
                if lines:
                    text_parts.append(f"Invoice Lines ({len(lines)}):")
                    for il in lines:
                        text_parts.append(f"  Line: {json.dumps(il, default=str)}")
                
                doc = Document(page_content="\n".join(text_parts), metadata={"doc_type": "invoice", "invoiceNumber": inv.get('invoiceNumber')})
                documents.append(doc)

            # COMPREHENSIVE VENDORS - Include ALL fields including nested data
            for v in vendors:
                text_parts = ["DOC: VENDOR"]
                # Include ALL vendor fields
                text_parts.extend(format_all_fields(v, ""))
                
                # Format nested addresses and phones
                if 'addresses' in v and v['addresses']:
                    text_parts.append("Addresses:")
                    for addr in v['addresses']:
                        addr_text = []
                        for k, val in addr.items():
                            if val is not None and val != "":
                                addr_text.append(f"{k}: {val}")
                        if addr_text:
                            text_parts.append(f"  - {', '.join(addr_text)}")
                
                if 'phones' in v and v['phones']:
                    text_parts.append("Phone Numbers:")
                    for phone in v['phones']:
                        phone_text = []
                        for k, val in phone.items():
                            if val is not None and val != "":
                                phone_text.append(f"{k}: {val}")
                        if phone_text:
                            text_parts.append(f"  - {', '.join(phone_text)}")
                
                doc = Document(page_content="\n".join(text_parts), metadata={"doc_type": "vendor", "vendorId": v.get('vendorId')})
                documents.append(doc)

            # COMPREHENSIVE CUSTOMERS - Include ALL fields including nested data
            for c in customers:
                text_parts = ["DOC: CUSTOMER"]
                # Include ALL customer fields
                text_parts.extend(format_all_fields(c, ""))
                
                # Format nested addresses and phones
                if 'addresses' in c and c['addresses']:
                    text_parts.append("Addresses:")
                    for addr in c['addresses']:
                        addr_text = []
                        for k, val in addr.items():
                            if val is not None and val != "":
                                addr_text.append(f"{k}: {val}")
                        if addr_text:
                            text_parts.append(f"  - {', '.join(addr_text)}")
                
                if 'phones' in c and c['phones']:
                    text_parts.append("Phone Numbers:")
                    for phone in c['phones']:
                        phone_text = []
                        for k, val in phone.items():
                            if val is not None and val != "":
                                phone_text.append(f"{k}: {val}")
                        if phone_text:
                            text_parts.append(f"  - {', '.join(phone_text)}")
                
                # Format nested custom fields
                if 'customFields' in c and c['customFields']:
                    text_parts.append("Custom Fields:")
                    for cf in c['customFields']:
                        if cf.get('value') is not None and cf.get('value') != "":
                            field_name = cf.get('fieldName', 'Unknown Field')
                            field_value = cf.get('value')
                            text_parts.append(f"  {field_name}: {field_value}")
                
                doc = Document(page_content="\n".join(text_parts), metadata={"doc_type": "customer", "customerKey": c.get('customerKey')})
                documents.append(doc)

            # COMPREHENSIVE EMPLOYEES - Include ALL fields including nested data
            for e in employees:
                text_parts = ["DOC: EMPLOYEE"]
                # Include ALL employee fields
                text_parts.extend(format_all_fields(e, ""))
                
                # Format nested addresses and phones
                if 'addresses' in e and e['addresses']:
                    text_parts.append("Addresses:")
                    for addr in e['addresses']:
                        addr_text = []
                        for k, val in addr.items():
                            if val is not None and val != "":
                                addr_text.append(f"{k}: {val}")
                        if addr_text:
                            text_parts.append(f"  - {', '.join(addr_text)}")
                
                if 'phones' in e and e['phones']:
                    text_parts.append("Phone Numbers:")
                    for phone in e['phones']:
                        phone_text = []
                        for k, val in phone.items():
                            if val is not None and val != "":
                                phone_text.append(f"{k}: {val}")
                        if phone_text:
                            text_parts.append(f"  - {', '.join(phone_text)}")
                
                # Format nested custom fields
                if 'customFields' in e and e['customFields']:
                    text_parts.append("Custom Fields:")
                    for cf in e['customFields']:
                        if cf.get('value') is not None and cf.get('value') != "":
                            field_name = cf.get('fieldName', 'Unknown Field')
                            field_value = cf.get('value')
                            text_parts.append(f"  {field_name}: {field_value}")
                
                doc = Document(page_content="\n".join(text_parts), metadata={"doc_type": "employee", "employeeKey": e.get('employeeKey')})
                documents.append(doc)

            # COMPREHENSIVE PARTS - Include ALL fields
            for p in parts:
                text_parts = ["DOC: PART"]
                # Include ALL part fields
                text_parts.extend(format_all_fields(p, ""))
                
                doc = Document(page_content="\n".join(text_parts), metadata={"doc_type": "part", "partId": p.get('partId')})
                documents.append(doc)

            # COMPREHENSIVE SERVICE ITEMS - Include ALL fields
            for si in service_items:
                text_parts = ["DOC: SERVICE ITEM"]
                # Include ALL service item fields
                text_parts.extend(format_all_fields(si, ""))
                
                doc = Document(page_content="\n".join(text_parts), metadata={"doc_type": "service_item", "serviceKey": si.get('serviceKey')})
                documents.append(doc)

            # COMPREHENSIVE WORK REQUESTS - Include ALL fields
            for wr in work_requests:
                text_parts = ["DOC: WORK REQUEST"]
                # Include ALL work request fields
                text_parts.extend(format_all_fields(wr, ""))
                
                doc = Document(page_content="\n".join(text_parts), metadata={"doc_type": "work_request", "requestId": wr.get('requestId')})
                documents.append(doc)

            # COMPREHENSIVE WORK TYPES - Include ALL fields
            for wt in work_types:
                text_parts = ["DOC: WORK TYPE"]
                # Include ALL work type fields
                text_parts.extend(format_all_fields(wt, ""))
                
                doc = Document(page_content="\n".join(text_parts), metadata={"doc_type": "work_type", "workTypeId": wt.get('workTypeId')})
                documents.append(doc)

            # COMPREHENSIVE WORK PRIORITIES - Include ALL fields
            for wp in work_priorities:
                text_parts = ["DOC: WORK PRIORITY"]
                # Include ALL work priority fields
                text_parts.extend(format_all_fields(wp, ""))
                
                doc = Document(page_content="\n".join(text_parts), metadata={"doc_type": "work_priority", "priorityId": wp.get('priorityId')})
                documents.append(doc)

            # COMPREHENSIVE VENDOR TYPES - Include ALL fields
            for vt in vendor_types:
                text_parts = ["DOC: VENDOR TYPE"]
                # Include ALL vendor type fields
                text_parts.extend(format_all_fields(vt, ""))
                
                doc = Document(page_content="\n".join(text_parts), metadata={"doc_type": "vendor_type", "typeId": vt.get('typeId')})
                documents.append(doc)

            # COMPREHENSIVE CUSTOM FIELD DEFINITIONS - Include ALL fields
            for cf in custom_field_defs:
                text_parts = ["DOC: CUSTOM FIELD DEFINITION"]
                # Include ALL custom field definition fields
                text_parts.extend(format_all_fields(cf, ""))
                
                doc = Document(page_content="\n".join(text_parts), metadata={"doc_type": "custom_field_def", "customFieldKey": cf.get('customFieldKey')})
                documents.append(doc)

            # COMPREHENSIVE ADDRESSES - Include ALL fields (standalone addresses)
            for addr in addresses:
                text_parts = ["DOC: ADDRESS"]
                # Include ALL address fields
                text_parts.extend(format_all_fields(addr, ""))
                
                doc = Document(page_content="\n".join(text_parts), metadata={"doc_type": "address", "addressKey": addr.get('addressKey')})
                documents.append(doc)

            # COMPREHENSIVE PHONES - Include ALL fields (standalone phones)
            for phone in phones:
                text_parts = ["DOC: PHONE"]
                # Include ALL phone fields
                text_parts.extend(format_all_fields(phone, ""))
                
                doc = Document(page_content="\n".join(text_parts), metadata={"doc_type": "phone", "phoneKey": phone.get('phoneKey')})
                documents.append(doc)

            # COMPREHENSIVE INVOICE LINES - Include ALL fields
            for il in invoice_lines:
                text_parts = ["DOC: INVOICE LINE"]
                # Include ALL invoice line fields
                text_parts.extend(format_all_fields(il, ""))
                
                doc = Document(page_content="\n".join(text_parts), metadata={"doc_type": "invoice_line", "invoiceNumber": il.get('invoiceNumber')})
                documents.append(doc)

            # COMPREHENSIVE PURCHASE ORDER LINES - Include ALL fields
            for pol in po_lines:
                text_parts = ["DOC: PURCHASE ORDER LINE"]
                # Include ALL purchase order line fields
                text_parts.extend(format_all_fields(pol, ""))
                
                doc = Document(page_content="\n".join(text_parts), metadata={"doc_type": "purchase_order_line", "purchaseOrderKey": pol.get('purchaseOrderKey')})
                documents.append(doc)

            # COMPREHENSIVE PURCHASE ORDER BATCHES - Include ALL fields
            for pob in po_batches:
                text_parts = ["DOC: PURCHASE ORDER BATCH"]
                # Include ALL purchase order batch fields
                text_parts.extend(format_all_fields(pob, ""))
                
                doc = Document(page_content="\n".join(text_parts), metadata={"doc_type": "purchase_order_batch", "purchaseOrderKey": pob.get('purchaseOrderKey')})
                documents.append(doc)

            # Return comprehensive joined data
            joined = {
                "assets": assets,
                "work_orders": work_orders,
                "work_requests": work_requests,
                "work_types": work_types,
                "work_priorities": work_priorities,
                "invoices": invoices,
                "invoice_lines": invoice_lines,
                "purchase_orders": purchase_orders,
                "po_lines": po_lines,
                "po_batches": po_batches,
                "vendors": vendors,
                "vendor_types": vendor_types,
                "customers": customers,
                "employees": employees,
                "phones": phones,
                "addresses": addresses,
                "parts": parts,
                "service_items": service_items,
                "custom_field_defs": custom_field_defs,
            }

            return joined, documents

        except Exception as e:
            import traceback
            print(f"Error in load_and_process_data: {e}")
            print(f"Traceback: {traceback.format_exc()}")
            return None, None
    
    def _create_asset_text(self, asset_data: Dict[str, Any]) -> str:
        """Create comprehensive text representation of an asset."""
        text_parts = []
        
        # Basic information
        basic_fields = [
            ('assetId', 'Asset ID'),
            ('entityName', 'Entity'),
            ('description', 'Description'),
            ('manufacturer', 'Manufacturer'),
            ('model', 'Model'),
            ('categoryId', 'Category'),
            ('typeId', 'Type'),
            ('statusId', 'Status'),
            ('customer', 'Customer'),
            ('groupId', 'Group'),
            ('serialNumber', 'Serial Number'),
            ('barcode', 'Barcode'),
            ('purchaseDate', 'Purchase Date'),
            ('purchaseCost', 'Purchase Cost')
        ]
        
        for field_key, field_label in basic_fields:
            value = asset_data.get(field_key, 'N/A')
            text_parts.append(f"{field_label}: {value}")
        
        # Custom fields
        custom_fields = asset_data.get('customFields', [])
        if custom_fields:
            text_parts.append("Custom Fields:")
            for field in custom_fields:
                field_name = field.get('fieldName', 'Unknown')
                field_value = field.get('value', 'N/A')
                if field_value and field_value != 'N/A':
                    text_parts.append(f"  {field_name}: {field_value}")
        
        return "\n".join(text_parts)
    
    def _extract_metadata(self, asset_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract relevant metadata from asset data."""
        return {
            'assetId': asset_data.get('assetId', ''),
            'entityName': asset_data.get('entityName', ''),
            'manufacturer': asset_data.get('manufacturer', ''),
            'customer': asset_data.get('customer', ''),
            'categoryId': asset_data.get('categoryId', ''),
            'typeId': asset_data.get('typeId', ''),
            'statusId': asset_data.get('statusId', ''),
            'description': asset_data.get('description', ''),
            'purchaseDate': asset_data.get('purchaseDate', ''),
            'purchaseCost': asset_data.get('purchaseCost', ''),
            'serialNumber': asset_data.get('serialNumber', ''),
            'barcode': asset_data.get('barcode', ''),
            'model': asset_data.get('model', ''),
            'groupId': asset_data.get('groupId', ''),
            'customFields': asset_data.get('customFields', [])
        }