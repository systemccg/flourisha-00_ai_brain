# Property Lookup Workflow

**Triggers**: "find property", "lookup property", "property details", "show me property"
**Estimated Time**: 5-30 seconds
**Prerequisites**: Odoo API access

---

## Purpose

Find property details by address, property ID, or other criteria. Returns comprehensive property information including financials, tenant data, and AI insights.

---

## Workflow Steps

### 1. Parse Query
Extract search criteria from user input:
- Property address (e.g., "123 Main Street")
- Property ID (e.g., "property 456")
- Company/LLC name (e.g., "Springfield LLC properties")
- Property type (e.g., "single family homes")

### 2. Build Odoo Search Domain
```typescript
// Example domain for address search
const domain = [
  ['address', 'ilike', searchAddress],
  ['active', '=', true]
];

// Example for company filter
if (companyName) {
  domain.push(['company_id.name', 'ilike', companyName]);
}
```

### 3. Query Odoo API
```typescript
const properties = await odoo.searchRead('real.estate.property', domain, [
  'id', 'name', 'address', 'city', 'state', 'zip_code',
  'property_type', 'company_id', 'analytic_account_id',
  'acquisition_date', 'acquisition_price', 'current_market_value',
  'bedrooms', 'bathrooms', 'square_feet',
  'google_drive_folder_id'
]);
```

### 4. Fetch Financial Data (if single property)
```typescript
if (properties.length === 1) {
  const financials = await odoo.searchRead('property.financial.metrics', [
    ['property_id', '=', properties[0].id]
  ], [
    'period_date', 'rental_income', 'total_expenses',
    'net_cash_flow', 'occupancy_rate', 'cap_rate', 'roi_ytd'
  ]);
}
```

### 5. Check Local Cache (Supabase)
```typescript
// Optional: Get supplemental data
const { data: cachedData } = await supabase
  .from('properties')
  .select('notes, tags, custom_fields')
  .eq('odoo_id', properties[0].id)
  .single();
```

### 6. Format Response
```typescript
const response = `
# Property: ${property.address}

**Property Details**:
- Type: ${property.property_type}
- Bedrooms/Bathrooms: ${property.bedrooms}/${property.bathrooms}
- Square Feet: ${property.square_feet}
- Company: ${property.company_id[1]}

**Financial Summary**:
- Acquisition Price: $${property.acquisition_price}
- Current Market Value: $${property.current_market_value}
- Latest Monthly Rent: $${latestFinancials.rental_income}
- Monthly Cash Flow: $${latestFinancials.net_cash_flow}
- YTD ROI: ${latestFinancials.roi_ytd}%

**Links**:
- Google Drive: [Property Folder](drive.google.com/drive/folders/${property.google_drive_folder_id})
- Odoo: [Property Record](${odooUrl}/web#id=${property.id}&model=real.estate.property)
`;
```

---

## Example Usage

**User**: "Find property at 123 Main Street"

**Response**:
```
# Property: 123 Main Street, Springfield, IL 62701

**Property Details**:
- Type: Single Family
- Bedrooms/Bathrooms: 3/2
- Square Feet: 1,850
- Company: Springfield Rentals LLC

**Financial Summary** (November 2025):
- Acquisition Price: $185,000 (2023-03-15)
- Current Market Value: $210,000
- Monthly Rent: $2,200
- Monthly Expenses: $1,450
- Net Cash Flow: $750
- YTD ROI: 8.5%

**Tenant**: John Doe (lease expires 2026-06-30)

**Links**:
- [Property Files](drive.google.com/drive/folders/abc123)
- [Odoo Record](odoo.example.com/web#id=123&model=real.estate.property)
```

---

## Error Handling

**Property Not Found**:
```
No properties found matching "123 Main Street"

Suggestions:
- Check address spelling
- Try partial address: "123 Main"
- Search by property ID
- List all properties: "show all properties"
```

**Multiple Matches**:
```
Found 3 properties matching "Main Street":
1. 123 Main Street, Springfield, IL
2. 456 Main Street, Shelbyville, IL
3. 789 Main Street West, Capital City, IL

Please specify which property you want to view.
```

**Odoo API Error**:
```
⚠️ Unable to connect to Odoo API

Checking local cache...
✓ Found cached data (last sync: 2025-11-14 02:30)

[Shows cached property data with warning banner]
```

---

## Extensions

**Add Market Analysis**:
Query Neo4j for comparable properties:
```cypher
MATCH (p:Property {address: $address})-[:IN_NEIGHBORHOOD]->(n:Neighborhood)
MATCH (n)<-[:IN_NEIGHBORHOOD]-(comp:Property)
WHERE comp.property_type = p.property_type
RETURN comp.address, comp.sale_price, comp.sale_date
ORDER BY comp.sale_date DESC
LIMIT 5
```

**Add AI Insights**:
```typescript
const aiAnalysis = await analyzeProperty({
  property: propertyData,
  financials: financialData,
  marketComps: comparables
});

// Append to response:
**AI Insights**:
- ${aiAnalysis.performance_assessment}
- Recommendation: ${aiAnalysis.recommendation}
- Risk Factors: ${aiAnalysis.risks.join(', ')}
```

---

**Last Updated**: 2025-11-14
**Complexity**: Low
**Average Execution Time**: 5 seconds
