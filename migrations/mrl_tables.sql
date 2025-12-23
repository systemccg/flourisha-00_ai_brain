-- ============================================================================
-- MyRemoteLender Airtable → Supabase Migration
-- Generated from Airtable schema export
-- 18 tables, 458 fields
-- ============================================================================

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- Table: Conditions (37 fields)
-- ============================================================================
CREATE TABLE IF NOT EXISTS mrl_conditions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    airtable_id TEXT UNIQUE NOT NULL,  -- Original Airtable record ID
    condid TEXT, -- condID (formula)
    condnrecid TEXT, -- condnRecID (formula)
    humncondreviewstatus TEXT, -- humnCondReviewStatus (singleSelect)
    humncondfeedback TEXT, -- humnCondFeedback (singleLineText)
    aicondphase TEXT, -- aiCondPhase (singleLineText)
    aicondrefnum INTEGER, -- aiCondRefNum (number)
    aicondname TEXT, -- aiCondName (singleLineText)
    reldoctypecond TEXT[], -- relDocTypeCond (multipleRecordLinks)
    recmreqactionforcond JSONB, -- recmReqActionForCond (multipleLookupValues)
    finalreqactionforcond TEXT, -- finalReqActionForCond (richText)
    recmguidelines JSONB, -- recmGuidelines (multipleLookupValues)
    recmkeyoutput JSONB, -- recmKeyOutput (multipleLookupValues)
    lenderusage TEXT[], -- lenderUsage (multipleRecordLinks)
    lenderloannum TEXT[], -- lenderLoanNum (multipleRecordLinks)
    recmcategory JSONB, -- recmCategory (multipleLookupValues)
    recmrequester JSONB, -- recmRequester (multipleLookupValues)
    c_req_dt JSONB, -- c-Req# (dT) (multipleLookupValues)
    recmsubmitter JSONB, -- recmSubmitter (multipleLookupValues)
    mksubmitter TEXT, -- mkSubmitter (singleLineText)
    c_sub_dt JSONB, -- c-Sub# (dT) (multipleLookupValues)
    condautonum SERIAL, -- condAutoNum (autoNumber)
    c_ai_docmatch_status TEXT, -- c-AI-DocMatch Status (singleSelect)
    datecreated TIMESTAMPTZ DEFAULT NOW(), -- dateCreated (createdTime)
    aidocmatchcomments TEXT, -- aiDocMatchComments (richText)
    docsmatched TEXT[], -- docsMatched (multipleRecordLinks)
    datedocadded JSONB, -- dateDocAdded (multipleLookupValues)
    datematched DATE, -- dateMatched (date)
    datemodified TIMESTAMPTZ DEFAULT NOW(), -- dateModified (lastModifiedTime)
    aicondcategory TEXT, -- aiCondCategory (multilineText)
    aidocguidelines TEXT, -- aiDocGuidelines (richText)
    ailoanthreadid JSONB, -- aiLoanThreadID (multipleLookupValues)
    condloanrecid JSONB, -- condLoanRecID (multipleLookupValues)
    acctabbr TEXT[], -- acctAbbr (multipleRecordLinks)
    propertyshortaddress_from_lenderloannum JSONB, -- propertyShortAddress (from LenderLoanNum) (multipleLookupValues)
    relcontactlastname JSONB, -- relContactLastName (multipleLookupValues)
    relcontactfirstname JSONB, -- relContactFirstName (multipleLookupValues)
    last_modified_by TEXT, -- Last modified by (lastModifiedBy)
    tenant_id TEXT DEFAULT 'default',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    sync_status TEXT DEFAULT 'synced'
);

-- Index for Airtable ID lookups
CREATE INDEX IF NOT EXISTS idx_mrl_conditions_airtable_id ON mrl_conditions(airtable_id);
CREATE INDEX IF NOT EXISTS idx_mrl_conditions_tenant ON mrl_conditions(tenant_id);

-- ============================================================================
-- Table: Doc Types (24 fields)
-- ============================================================================
CREATE TABLE IF NOT EXISTS mrl_doc_types (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    airtable_id TEXT UNIQUE NOT NULL,  -- Original Airtable record ID
    doctype TEXT, -- docType (singleLineText)
    fav BOOLEAN DEFAULT FALSE, -- Fav (checkbox)
    categories TEXT[], -- Categories (multipleRecordLinks)
    categoryname JSONB, -- categoryName (multipleLookupValues)
    recmrequestor TEXT[], -- recmRequestor (multipleRecordLinks)
    recmreqnum JSONB, -- recmReqNum (multipleLookupValues)
    submitter TEXT[], -- Submitter (multipleRecordLinks)
    recmsub JSONB, -- recmSub# (multipleLookupValues)
    recmreqactioncond TEXT, -- recmReqActionCond (richText)
    recmguidelines TEXT, -- recmGuidelines (richText)
    recmkeyoutput TEXT, -- recmKeyOutput (richText)
    added_by_lpaa TEXT, -- Added by LPAA (singleSelect)
    catrequestor JSONB, -- catRequestor (multipleLookupValues)
    catsubmitter JSONB, -- catSubmitter (multipleLookupValues)
    relconditions TEXT[], -- relConditions (multipleRecordLinks)
    reldocuments TEXT[], -- relDocuments (multipleRecordLinks)
    lender_usage TEXT, -- Lender Usage (singleLineText)
    recmrequester JSONB, -- recmRequester (multipleLookupValues)
    recmsubmitter JSONB, -- recmSubmitter (multipleLookupValues)
    doctyperecid TEXT, -- docTypeRecID (formula)
    acctabbr TEXT[], -- acctAbbr (multipleRecordLinks)
    lastmodifiedby TEXT, -- lastModifiedBy (lastModifiedBy)
    lastmodifiedtime TIMESTAMPTZ DEFAULT NOW(), -- lastModifiedTime (lastModifiedTime)
    numrelconditions JSONB, -- numRelConditions (rollup)
    tenant_id TEXT DEFAULT 'default',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    sync_status TEXT DEFAULT 'synced'
);

-- Index for Airtable ID lookups
CREATE INDEX IF NOT EXISTS idx_mrl_doc_types_airtable_id ON mrl_doc_types(airtable_id);
CREATE INDEX IF NOT EXISTS idx_mrl_doc_types_tenant ON mrl_doc_types(tenant_id);

-- ============================================================================
-- Table: Documents (51 fields)
-- ============================================================================
CREATE TABLE IF NOT EXISTS mrl_documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    airtable_id TEXT UNIQUE NOT NULL,  -- Original Airtable record ID
    docname TEXT, -- docName (multilineText)
    docdoctype TEXT[], -- docDocType (multipleRecordLinks)
    lenderloannum TEXT[], -- lenderLoanNum (multipleRecordLinks)
    propertyshortaddress TEXT, -- propertyShortAddress (singleLineText)
    borrower_legalentityname TEXT, -- borrower.legalEntityName (singleLineText)
    borrower_contactfirstname TEXT, -- borrower.contactFirstName (singleLineText)
    borrower_contactlastname TEXT, -- borrower.contactLastName (singleLineText)
    matchedcondns TEXT[], -- matchedCondns (multipleRecordLinks)
    docmatchstatus TEXT, -- docMatchStatus (singleSelect)
    aimatchsummary TEXT, -- aiMatchSummary (richText)
    humndocreviewstatus TEXT, -- humnDocReviewStatus (singleSelect)
    humndocfeedback TEXT, -- humnDocFeedback (singleLineText)
    linkshared TEXT, -- linkShared  (url)
    doccategory TEXT, -- docCategory (singleLineText)
    dateadded TIMESTAMPTZ DEFAULT NOW(), -- dateAdded (createdTime)
    recmguidelines JSONB, -- recmGuidelines (multipleLookupValues)
    recmkeyoutput JSONB, -- recmKeyOutput (multipleLookupValues)
    issuingcompanyname TEXT, -- issuingCompanyName (singleLineText)
    accountholdername TEXT, -- accountHolderName (singleLineText)
    accountnumber TEXT, -- accountNumber (singleLineText)
    additionalholdername TEXT, -- additionalHolderName (singleLineText)
    datedocissued DATE, -- dateDocIssued (date)
    datedoceffective DATE, -- dateDocEffective (date)
    totalbalance DECIMAL, -- totalBalance (number)
    totalearnest INTEGER, -- totalEarnest (number)
    purchaseprice DECIMAL, -- purchasePrice (number)
    daterangestart DATE, -- dateRangeStart (date)
    daterangeend DATE, -- dateRangeEnd (date)
    propertyaddress TEXT, -- propertyAddress (multilineText)
    borrower_contactemail TEXT, -- borrower.contactEmail (email)
    borrower_contactresidenceaddress TEXT, -- borrower.contactResidenceAddress (multilineText)
    borrower_contactphone TEXT, -- borrower.contactPhone (phoneNumber)
    docrecid TEXT, -- docRecID (formula)
    alldocproperties TEXT, -- allDocProperties (richText)
    sourcelink TEXT, -- sourceLink (singleLineText)
    docdrivefileid TEXT, -- docDriveFileID (singleLineText)
    docopenfileid TEXT, -- docOpenFileID (singleLineText)
    docnameoriginal TEXT, -- docNameOriginal (singleLineText)
    docloanrecid JSONB, -- docLoanRecID (multipleLookupValues)
    uploaded_by TEXT, -- Uploaded By (multilineText)
    attachedfile TEXT, -- attachedFile (multipleAttachments)
    docnameingested TEXT, -- docNameIngested (singleLineText)
    sourcecontentid TEXT, -- sourceContentID (singleLineText)
    sourcesenderemail TEXT, -- sourceSenderEmail (singleLineText)
    sourcesenderfirstname TEXT, -- sourceSenderFirstName (singleLineText)
    sourcesubjectline TEXT, -- sourceSubjectLine (singleLineText)
    categories_from_docdoctype JSONB, -- Categories (from docDocType) (multipleLookupValues)
    acctabbr TEXT[], -- acctAbbr (multipleRecordLinks)
    lastmodified TIMESTAMPTZ DEFAULT NOW(), -- lastModified (lastModifiedTime)
    properties TEXT[], -- Properties (multipleRecordLinks)
    agreements TEXT[], -- Agreements (multipleRecordLinks)
    tenant_id TEXT DEFAULT 'default',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    sync_status TEXT DEFAULT 'synced'
);

-- Index for Airtable ID lookups
CREATE INDEX IF NOT EXISTS idx_mrl_documents_airtable_id ON mrl_documents(airtable_id);
CREATE INDEX IF NOT EXISTS idx_mrl_documents_tenant ON mrl_documents(tenant_id);

-- ============================================================================
-- Table: Agreements (24 fields)
-- ============================================================================
CREATE TABLE IF NOT EXISTS mrl_agreements (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    airtable_id TEXT UNIQUE NOT NULL,  -- Original Airtable record ID
    agmtname TEXT, -- agmtName (singleLineText)
    agmtrecid TEXT, -- agmtRecID (formula)
    agmttype TEXT, -- agmtType (singleSelect)
    relproperty TEXT[], -- relProperty (multipleRecordLinks)
    relcompany TEXT[], -- relCompany (multipleRecordLinks)
    relprimarycontact JSONB, -- relPrimaryContact (multipleLookupValues)
    agmtsubtype TEXT, -- agmtSubType  (singleLineText)
    agmtnum TEXT, -- agmtNum (singleLineText)
    agmteffectivedate DATE, -- agmtEffectiveDate (date)
    agmtenddate DATE, -- agmtEndDate (date)
    lenderloannum TEXT[], -- lenderLoanNum (multipleRecordLinks)
    agmtdoclink TEXT[], -- agmtDocLink (multipleRecordLinks)
    agmtrate DECIMAL, -- agmtRate (percent)
    agmttotalamt DECIMAL, -- agmtTotalAmt (currency)
    agmtdeposit DECIMAL, -- agmtDeposit (currency)
    agmtnotes TEXT, -- agmtNotes (multilineText)
    offerorlegalname TEXT[], -- offerorLegalName (multipleRecordLinks)
    offerormgmtagent TEXT[], -- offerorMgmtAgent (multipleRecordLinks)
    offerorprimarycontact TEXT[], -- offerorPrimaryContact (multipleRecordLinks)
    offerorothernames TEXT[], -- offerorOtherNames (multipleRecordLinks)
    offereelegalname TEXT[], -- offereeLegalName (multipleRecordLinks)
    offereeprimarycontact TEXT[], -- offereePrimaryContact (multipleRecordLinks)
    offereeemail JSONB, -- offereeEmail (multipleLookupValues)
    offereeothernames TEXT[], -- offereeOtherNames (multipleRecordLinks)
    tenant_id TEXT DEFAULT 'default',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    sync_status TEXT DEFAULT 'synced'
);

-- Index for Airtable ID lookups
CREATE INDEX IF NOT EXISTS idx_mrl_agreements_airtable_id ON mrl_agreements(airtable_id);
CREATE INDEX IF NOT EXISTS idx_mrl_agreements_tenant ON mrl_agreements(tenant_id);

-- ============================================================================
-- Table: Loans (45 fields)
-- ============================================================================
CREATE TABLE IF NOT EXISTS mrl_loans (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    airtable_id TEXT UNIQUE NOT NULL,  -- Original Airtable record ID
    lenderloannum TEXT, -- lenderLoanNum (singleLineText)
    humnloanreviewstatus TEXT, -- humnLoanReviewStatus (singleSelect)
    humnloanfeedback TEXT, -- humnLoanFeedback (multilineText)
    legalentityname TEXT, -- legalEntityName (singleLineText)
    contactfirstname TEXT, -- contactFirstName (singleLineText)
    contactlastname TEXT, -- contactLastName (singleLineText)
    contactemail TEXT, -- contactEmail (singleLineText)
    contactphone TEXT, -- contactPhone (phoneNumber)
    contactresidenceaddress TEXT, -- contactResidenceAddress (singleLineText)
    loanofficer TEXT, -- loanOfficer (singleLineText)
    loanofficeremail TEXT, -- loanOfficerEmail (email)
    loanpurpose TEXT, -- loanPurpose (singleSelect)
    lendername JSONB, -- lenderName (multipleLookupValues)
    loanamount DECIMAL, -- loanAmount (currency)
    propertyshortaddress TEXT, -- propertyShortAddress (singleLineText)
    propertyaddress TEXT, -- propertyAddress (singleLineText)
    intrate DECIMAL, -- intRate (number)
    loanstatus TEXT, -- loanStatus (singleSelect)
    dateregistered DATE, -- dateRegistered (date)
    datesubmitted DATE, -- dateSubmitted (date)
    dateclosing DATE, -- dateClosing (date)
    datelockexpires DATE, -- dateLockExpires (date)
    datelocked DATE, -- dateLocked (date)
    datefinalapproval DATE, -- dateFinalApproval (date)
    dateapprovalexpires DATE, -- dateApprovalExpires (date)
    loanrecid TEXT, -- loanRecID (formula)
    loanclickupid TEXT, -- loanClickupID (singleLineText)
    loanopenthreadid TEXT, -- loanOpenThreadID (singleLineText)
    loandrivefolderid TEXT, -- loanDriveFolderID (singleLineText)
    allloanproperties TEXT, -- allLoanProperties (multilineText)
    reldocs TEXT[], -- relDocs (multipleRecordLinks)
    relconditions TEXT[], -- relConditions (multipleRecordLinks)
    loanuploaderintro TEXT, -- loanUploaderIntro (multilineText)
    contactfullname TEXT, -- contactFullName (singleLineText)
    loanprogram TEXT, -- loanProgram (singleSelect)
    rellenderorderindex TEXT, -- relLenderOrderIndex (singleLineText)
    propertycity TEXT, -- propertyCity (singleLineText)
    propertystate TEXT, -- propertyState (singleLineText)
    propertyzip TEXT, -- propertyZip (singleLineText)
    acctabbr TEXT[], -- acctAbbr (multipleRecordLinks)
    properties TEXT[], -- Properties (multipleRecordLinks)
    intratepercent TEXT, -- intRatePercent (formula)
    agreements TEXT[], -- Agreements (multipleRecordLinks)
    loanamount_copy DECIMAL, -- loanAmount copy (currency)
    dateloaneffective DATE, -- dateLoanEffective (date)
    tenant_id TEXT DEFAULT 'default',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    sync_status TEXT DEFAULT 'synced'
);

-- Index for Airtable ID lookups
CREATE INDEX IF NOT EXISTS idx_mrl_loans_airtable_id ON mrl_loans(airtable_id);
CREATE INDEX IF NOT EXISTS idx_mrl_loans_tenant ON mrl_loans(tenant_id);

-- ============================================================================
-- Table: Categories (9 fields)
-- ============================================================================
CREATE TABLE IF NOT EXISTS mrl_categories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    airtable_id TEXT UNIQUE NOT NULL,  -- Original Airtable record ID
    categoryname TEXT, -- categoryName (singleLineText)
    catrequestor TEXT[], -- catRequestor (multipleRecordLinks)
    catsubmitter TEXT[], -- catSubmitter (multipleRecordLinks)
    cat_req JSONB, -- Cat-Req# (multipleLookupValues)
    cat_sub JSONB, -- Cat-Sub# (multipleLookupValues)
    notes TEXT, -- Notes (multilineText)
    doc_types TEXT[], -- Doc Types (multipleRecordLinks)
    acctabbr TEXT[], -- acctAbbr (multipleRecordLinks)
    numdocsusing JSONB, -- numDocsUsing (rollup)
    tenant_id TEXT DEFAULT 'default',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    sync_status TEXT DEFAULT 'synced'
);

-- Index for Airtable ID lookups
CREATE INDEX IF NOT EXISTS idx_mrl_categories_airtable_id ON mrl_categories(airtable_id);
CREATE INDEX IF NOT EXISTS idx_mrl_categories_tenant ON mrl_categories(tenant_id);

-- ============================================================================
-- Table: Roles (11 fields)
-- ============================================================================
CREATE TABLE IF NOT EXISTS mrl_roles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    airtable_id TEXT UNIQUE NOT NULL,  -- Original Airtable record ID
    name TEXT, -- Name (singleLineText)
    curolenum INTEGER, -- cuRoleNum (number)
    primaryroletype TEXT, -- primaryRoleType (singleSelect)
    notes TEXT, -- Notes (multilineText)
    requester_doctypes TEXT[], -- Requester DocTypes (multipleRecordLinks)
    submitter_doctypes TEXT[], -- Submitter DocTypes (multipleRecordLinks)
    categories_as_requester TEXT[], -- Categories as Requester (multipleRecordLinks)
    categories_as_submitter TEXT[], -- Categories as Submitter (multipleRecordLinks)
    acctabbr TEXT[], -- acctAbbr (multipleRecordLinks)
    comptype TEXT[], -- compType (multipleRecordLinks)
    contacts TEXT[], -- Contacts (multipleRecordLinks)
    tenant_id TEXT DEFAULT 'default',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    sync_status TEXT DEFAULT 'synced'
);

-- Index for Airtable ID lookups
CREATE INDEX IF NOT EXISTS idx_mrl_roles_airtable_id ON mrl_roles(airtable_id);
CREATE INDEX IF NOT EXISTS idx_mrl_roles_tenant ON mrl_roles(tenant_id);

-- ============================================================================
-- Table: Properties (44 fields)
-- ============================================================================
CREATE TABLE IF NOT EXISTS mrl_properties (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    airtable_id TEXT UNIQUE NOT NULL,  -- Original Airtable record ID
    propertyshortaddress TEXT, -- propertyShortAddress (singleLineText)
    propnickname TEXT, -- propNickName (singleLineText)
    propcode TEXT, -- propCode (formula)
    propusage TEXT, -- propUsage (singleSelect)
    propsequence TEXT, -- propSequence (singleSelect)
    propertytype TEXT, -- propertyType (singleSelect)
    owner TEXT[], -- Owner (multipleRecordLinks)
    propstatus TEXT, -- propStatus (singleSelect)
    propertyaddress TEXT, -- propertyAddress (singleLineText)
    propertyaddress2 TEXT, -- propertyAddress2 (singleLineText)
    propertycity TEXT, -- propertyCity (singleLineText)
    propertystate TEXT, -- propertyState (singleLineText)
    propertyzip TEXT, -- propertyZip (singleLineText)
    propertycounty TEXT, -- propertyCounty (singleLineText)
    relateddocs TEXT[], -- relatedDocs (multipleRecordLinks)
    loans TEXT[], -- Loans (multipleRecordLinks)
    intratepercent JSONB, -- intRatePercent (multipleLookupValues)
    loanamount JSONB, -- loanAmount (multipleLookupValues)
    acctabbr TEXT[], -- acctAbbr (multipleRecordLinks)
    linkrehabplan TEXT[], -- linkRehabPlan (multipleRecordLinks)
    repairs TEXT, -- Repairs (singleLineText)
    squarefootage INTEGER, -- squareFootage (number)
    grosssqft INTEGER, -- grossSqFt (number)
    origbeds INTEGER, -- origBeds (number)
    origbaths INTEGER, -- origBaths (number)
    numparkingspots INTEGER, -- numParkingSpots (number)
    yearbuilt INTEGER, -- yearBuilt (number)
    ageofproperty TEXT, -- ageOfProperty (formula)
    yearsowned TEXT, -- yearsOwned (formula)
    legaldescription TEXT, -- legalDescription (singleLineText)
    milestobus DECIMAL, -- milesToBus (number)
    purchaseprice DECIMAL, -- purchasePrice (currency)
    pricepersqft TEXT, -- pricePerSqFt (formula)
    datepurchased DATE, -- datePurchased (date)
    dateinservice DATE, -- dateInService (date)
    bedswithsharedbath INTEGER, -- bedsWithSharedBath (number)
    bedswithprivatebath INTEGER, -- bedsWithPrivateBath (number)
    totalbeds TEXT, -- totalBeds (formula)
    totalbaths INTEGER, -- totalBaths (number)
    estrehabcosts DECIMAL, -- estRehabCosts (currency)
    actrehabcosts DECIMAL, -- actRehabCosts (currency)
    property_components TEXT[], -- Property Components (multipleRecordLinks)
    relissues TEXT[], -- relIssues (multipleRecordLinks)
    issue_items TEXT[], -- Issue Items (multipleRecordLinks)
    tenant_id TEXT DEFAULT 'default',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    sync_status TEXT DEFAULT 'synced'
);

-- Index for Airtable ID lookups
CREATE INDEX IF NOT EXISTS idx_mrl_properties_airtable_id ON mrl_properties(airtable_id);
CREATE INDEX IF NOT EXISTS idx_mrl_properties_tenant ON mrl_properties(tenant_id);

-- ============================================================================
-- Table: Property Components (15 fields)
-- ============================================================================
CREATE TABLE IF NOT EXISTS mrl_property_components (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    airtable_id TEXT UNIQUE NOT NULL,  -- Original Airtable record ID
    propcomponent TEXT, -- propComponent (multilineText)
    propcmpntid TEXT, -- propCmpntID (formula)
    relproperty TEXT[], -- relProperty (multipleRecordLinks)
    relrepairs TEXT, -- relRepairs (singleLineText)
    relcompanies TEXT[], -- relCompanies (multipleRecordLinks)
    lifespanyears INTEGER, -- lifespanYears (number)
    dateinstallation DATE, -- dateInstallation (date)
    datelastrepaired DATE, -- dateLastRepaired (date)
    datelastchecked DATE, -- dateLastChecked (date)
    monthsbetweenchecks INTEGER, -- monthsBetweenChecks (number)
    nextscheduledcheck TEXT, -- nextScheduledCheck (formula)
    xeroaccountcode TEXT, -- xeroAccountCode (singleLineText)
    xerotrackingcategory TEXT, -- xeroTrackingCategory (singleLineText)
    acctabbr TEXT[], -- acctAbbr (multipleRecordLinks)
    issue_items TEXT[], -- Issue Items (multipleRecordLinks)
    tenant_id TEXT DEFAULT 'default',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    sync_status TEXT DEFAULT 'synced'
);

-- Index for Airtable ID lookups
CREATE INDEX IF NOT EXISTS idx_mrl_property_components_airtable_id ON mrl_property_components(airtable_id);
CREATE INDEX IF NOT EXISTS idx_mrl_property_components_tenant ON mrl_property_components(tenant_id);

-- ============================================================================
-- Table: Companies (61 fields)
-- ============================================================================
CREATE TABLE IF NOT EXISTS mrl_companies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    airtable_id TEXT UNIQUE NOT NULL,  -- Original Airtable record ID
    compname TEXT, -- compName (singleLineText)
    cuorder TEXT, -- cuOrder (singleLineText)
    acctabbr TEXT[], -- acctAbbr (multipleRecordLinks)
    comprecid TEXT, -- compRecId (formula)
    comptype TEXT[], -- compType (multipleRecordLinks)
    compkeywords TEXT, -- compKeywords (multilineText)
    description TEXT, -- description (multilineText)
    websiteurl TEXT, -- websiteUrl (url)
    hsrecordid TEXT, -- hsRecordId (multilineText)
    aboutus TEXT, -- aboutUs (multilineText)
    annualrevenue DECIMAL, -- annualRevenue (currency)
    labels TEXT[], -- labels (multipleSelects)
    closedate DATE, -- closeDate (date)
    compowner TEXT, -- compOwner (multilineText)
    countryregion TEXT, -- countryRegion (singleSelect)
    createdate TEXT, -- createDate (multilineText)
    createdbyuserid TEXT, -- createdByUserId (multilineText)
    facebookcomppage TEXT, -- facebookcompPage (multilineText)
    facebookfans TEXT, -- facebookFans (multilineText)
    firstcontactcreatedate TEXT, -- firstContactCreateDate (multilineText)
    idealcustomerprofiletier TEXT, -- idealCustomerProfileTier (multilineText)
    industry TEXT, -- industry (multilineText)
    ispublic BOOLEAN DEFAULT FALSE, -- isPublic (checkbox)
    lastactivitydate TEXT, -- lastActivityDate (multilineText)
    latestsource TEXT, -- latestSource (multilineText)
    latestsourcetimestamp TEXT, -- latestSourceTimestamp (multilineText)
    leadstatus TEXT, -- leadStatus (multilineText)
    lifecyclestage TEXT, -- lifecycleStage (multilineText)
    linkedinbio TEXT, -- linkedInBio (multilineText)
    linkedincompanypage TEXT, -- linkedInCompanyPage (url)
    linkedinuid TEXT, -- linkedInUid (singleLineText)
    logourl TEXT, -- logoUrl (url)
    streetaddress TEXT, -- streetAddress (singleLineText)
    streetaddress2 TEXT, -- streetAddress2 (singleLineText)
    city TEXT, -- city (singleLineText)
    stateregion TEXT, -- stateRegion (singleLineText)
    postalcode TEXT, -- postalCode (multilineText)
    targetaccount TEXT, -- targetAccount (multilineText)
    timezone TEXT, -- timeZone (multilineText)
    totalmoneyraised TEXT, -- totalMoneyRaised (multilineText)
    twitterbio TEXT, -- twitterBio (multilineText)
    twitterfollowers TEXT, -- twitterFollowers (multilineText)
    twitterhandle TEXT, -- twitterHandle (multilineText)
    webtechnologies TEXT, -- webTechnologies (multilineText)
    relprimarycontact TEXT[], -- relPrimaryContact (multipleRecordLinks)
    firstname_from_assoccontact JSONB, -- firstName (from assocContact) (multipleLookupValues)
    lastname_from_assoccontact JSONB, -- lastName (from assocContact) (multipleLookupValues)
    email_from_assoccontact JSONB, -- email (from assocContact) (multipleLookupValues)
    phonenumber_from_assoccontact JSONB, -- phoneNumber (from assocContact) (multipleLookupValues)
    associateddeal TEXT, -- associatedDeal (multilineText)
    contacts TEXT, -- contacts (multilineText)
    agreements TEXT[], -- Agreements (multipleRecordLinks)
    agreements_2 TEXT[], -- Agreements 2 (multipleRecordLinks)
    agreements_3 TEXT[], -- Agreements 3 (multipleRecordLinks)
    properties TEXT[], -- Properties (multipleRecordLinks)
    agreements_4 TEXT[], -- Agreements 4 (multipleRecordLinks)
    conditions TEXT[], -- Conditions (multipleRecordLinks)
    property_components TEXT[], -- Property Components (multipleRecordLinks)
    relothercontacts TEXT[], -- relOtherContacts (multipleRecordLinks)
    primaryphone JSONB, -- primaryPhone (multipleLookupValues)
    primaryemail JSONB, -- primaryEmail (multipleLookupValues)
    tenant_id TEXT DEFAULT 'default',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    sync_status TEXT DEFAULT 'synced'
);

-- Index for Airtable ID lookups
CREATE INDEX IF NOT EXISTS idx_mrl_companies_airtable_id ON mrl_companies(airtable_id);
CREATE INDEX IF NOT EXISTS idx_mrl_companies_tenant ON mrl_companies(tenant_id);

-- ============================================================================
-- Table: Company Types (8 fields)
-- ============================================================================
CREATE TABLE IF NOT EXISTS mrl_company_types (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    airtable_id TEXT UNIQUE NOT NULL,  -- Original Airtable record ID
    comptype TEXT, -- compType (singleLineText)
    company_type TEXT, -- Company Type (singleLineText)
    description TEXT, -- Description (multilineText)
    comptyperecid TEXT, -- compTypeRecID (formula)
    acctabbr TEXT[], -- acctAbbr (multipleRecordLinks)
    companies TEXT[], -- Companies (multipleRecordLinks)
    contact_types TEXT, -- Contact Types (singleLineText)
    roles TEXT[], -- Roles (multipleRecordLinks)
    tenant_id TEXT DEFAULT 'default',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    sync_status TEXT DEFAULT 'synced'
);

-- Index for Airtable ID lookups
CREATE INDEX IF NOT EXISTS idx_mrl_company_types_airtable_id ON mrl_company_types(airtable_id);
CREATE INDEX IF NOT EXISTS idx_mrl_company_types_tenant ON mrl_company_types(tenant_id);

-- ============================================================================
-- Table: Contacts (53 fields)
-- ============================================================================
CREATE TABLE IF NOT EXISTS mrl_contacts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    airtable_id TEXT UNIQUE NOT NULL,  -- Original Airtable record ID
    contactfullnameid TEXT, -- contactFullNameId (formula)
    contactrecid TEXT, -- contactRecID (formula)
    firstname TEXT, -- firstName (singleLineText)
    lastname TEXT, -- lastName (singleLineText)
    nickname TEXT, -- nickName (multilineText)
    contactrole TEXT[], -- contactRole (multipleRecordLinks)
    email TEXT, -- email (email)
    phonenumber TEXT, -- phoneNumber (phoneNumber)
    relcompanies TEXT[], -- relCompanies (multipleRecordLinks)
    streetaddress TEXT, -- streetAddress (multilineText)
    city TEXT, -- city (singleLineText)
    stateregion TEXT, -- stateRegion (multilineText)
    zippostal TEXT, -- zipPostal (singleLineText)
    countryregion TEXT, -- countryRegion (multilineText)
    contactowner TEXT, -- contactOwner (singleCollaborator)
    relannualrevenue JSONB, -- relAnnualRevenue (multipleLookupValues)
    labels TEXT, -- labels (multilineText)
    buyingrole TEXT, -- buyingRole (singleSelect)
    datebecamealead DATE, -- dateBecameALead (date)
    dateofbirth DATE, -- dateOfBirth (date)
    dateoffirstengagement TEXT, -- dateOfFirstEngagement (multilineText)
    employmentrole TEXT, -- employmentRole (multilineText)
    employmentseniority TEXT, -- employmentSeniority (multilineText)
    employmentsubrole TEXT, -- employmentSubRole (multilineText)
    facebookclickid TEXT, -- facebookClickId (multilineText)
    gender TEXT, -- gender (multilineText)
    hubspotscore TEXT, -- hubSpotScore (multilineText)
    latestsource TEXT, -- latestSource (multilineText)
    latestsourcedate TEXT, -- latestSourceDate (multilineText)
    linkedin TEXT, -- linkedIn (multilineText)
    linkedinuid TEXT, -- linkedInUid (multilineText)
    message TEXT, -- message (multilineText)
    preferredlanguage TEXT, -- preferredLanguage (multilineText)
    recordsource TEXT, -- recordSource (multilineText)
    relationshipstatus TEXT, -- relationshipStatus (multilineText)
    school TEXT, -- school (multilineText)
    salutation TEXT, -- salutation (multilineText)
    seniority TEXT, -- seniority (multilineText)
    timezone TEXT, -- timeZone (singleLineText)
    timezone_copy TEXT, -- timeZone copy (multilineText)
    twittername TEXT, -- twitterName (singleLineText)
    whatsappphonenumber TEXT, -- whatsAppPhoneNumber (phoneNumber)
    workemail TEXT, -- workEmail (multilineText)
    associateddealcreateattribution TEXT, -- associatedDealCreateAttribution (multilineText)
    associatedcompany2 TEXT, -- associatedCompany2 (multilineText)
    ruleresponsible TEXT, -- ruleResponsible (multilineText)
    acctabbr TEXT[], -- acctAbbr (multipleRecordLinks)
    hubrecordid INTEGER, -- hubRecordID (number)
    relagmtofferorprimarycontact TEXT[], -- relAgmtOfferorPrimaryContact (multipleRecordLinks)
    relagmtofferorothernames TEXT[], -- relAgmtOfferorOtherNames (multipleRecordLinks)
    relagmtoffereeprimarycontact TEXT[], -- relAgmtOffereePrimaryContact (multipleRecordLinks)
    relagmtoffereeothernames TEXT[], -- relAgmtOffereeOtherNames (multipleRecordLinks)
    relcompanies_copy TEXT[], -- relCompanies copy (multipleRecordLinks)
    tenant_id TEXT DEFAULT 'default',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    sync_status TEXT DEFAULT 'synced'
);

-- Index for Airtable ID lookups
CREATE INDEX IF NOT EXISTS idx_mrl_contacts_airtable_id ON mrl_contacts(airtable_id);
CREATE INDEX IF NOT EXISTS idx_mrl_contacts_tenant ON mrl_contacts(tenant_id);

-- ============================================================================
-- Table: Messages (6 fields)
-- ============================================================================
CREATE TABLE IF NOT EXISTS mrl_messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    airtable_id TEXT UNIQUE NOT NULL,  -- Original Airtable record ID
    sender TEXT, -- Sender (multilineText)
    receiver TEXT, -- Receiver (multilineText)
    message_body TEXT, -- Message Body (multilineText)
    timestamp TIMESTAMPTZ, -- Timestamp (dateTime)
    softr_record_id TEXT, -- 🔐 Softr Record ID (multilineText)
    acctabbr TEXT[], -- acctAbbr (multipleRecordLinks)
    tenant_id TEXT DEFAULT 'default',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    sync_status TEXT DEFAULT 'synced'
);

-- Index for Airtable ID lookups
CREATE INDEX IF NOT EXISTS idx_mrl_messages_airtable_id ON mrl_messages(airtable_id);
CREATE INDEX IF NOT EXISTS idx_mrl_messages_tenant ON mrl_messages(tenant_id);

-- ============================================================================
-- Table: Issue Items (18 fields)
-- ============================================================================
CREATE TABLE IF NOT EXISTS mrl_issue_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    airtable_id TEXT UNIQUE NOT NULL,  -- Original Airtable record ID
    cutaskid TEXT, -- cuTaskID (multilineText)
    issuename TEXT, -- issueName (multilineText)
    itempriority TEXT, -- itemPriority (singleSelect)
    relpropcomponent TEXT[], -- relPropComponent (multipleRecordLinks)
    relproperty TEXT[], -- relProperty (multipleRecordLinks)
    assignee TEXT, -- Assignee (singleSelect)
    duedate DATE, -- dueDate (date)
    latest_comment TEXT, -- Latest Comment (multilineText)
    property_drop_down TEXT[], -- Property (drop down) (multipleRecordLinks)
    time_logged TEXT, -- Time Logged (multilineText)
    time_logged_rolled_up TEXT, -- Time Logged Rolled Up (multilineText)
    link_url TEXT, -- Link (url) (multilineText)
    related_vendor_list_relationship TEXT, -- Related Vendor (list relationship) (singleSelect)
    start_date TEXT, -- Start Date (singleLineText)
    date_updated TEXT, -- Date Updated (singleLineText)
    category_waz TEXT, -- Category (WAZ) (singleSelect)
    summary_text TEXT, -- Summary (text) (multilineText)
    acctabbr TEXT[], -- acctAbbr (multipleRecordLinks)
    tenant_id TEXT DEFAULT 'default',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    sync_status TEXT DEFAULT 'synced'
);

-- Index for Airtable ID lookups
CREATE INDEX IF NOT EXISTS idx_mrl_issue_items_airtable_id ON mrl_issue_items(airtable_id);
CREATE INDEX IF NOT EXISTS idx_mrl_issue_items_tenant ON mrl_issue_items(tenant_id);

-- ============================================================================
-- Table: Repairs (10 fields)
-- ============================================================================
CREATE TABLE IF NOT EXISTS mrl_repairs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    airtable_id TEXT UNIQUE NOT NULL,  -- Original Airtable record ID
    repair TEXT, -- repair (multilineText)
    vendor TEXT, -- vendor (singleLineText)
    documentationlink TEXT, -- documentationLink (singleLineText)
    estimatedcost TEXT, -- estimatedCost (singleLineText)
    actualcost TEXT, -- actualCost (singleLineText)
    warrantyexpiration TEXT, -- warrantyExpiration (singleLineText)
    modelnumber TEXT, -- modelNumber (singleLineText)
    serialnumber TEXT, -- serialNumber (singleLineText)
    acctabbr TEXT[], -- acctAbbr (multipleRecordLinks)
    properties TEXT, -- Properties (singleLineText)
    tenant_id TEXT DEFAULT 'default',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    sync_status TEXT DEFAULT 'synced'
);

-- Index for Airtable ID lookups
CREATE INDEX IF NOT EXISTS idx_mrl_repairs_airtable_id ON mrl_repairs(airtable_id);
CREATE INDEX IF NOT EXISTS idx_mrl_repairs_tenant ON mrl_repairs(tenant_id);

-- ============================================================================
-- Table: ai-Vector Store Docs (5 fields)
-- ============================================================================
CREATE TABLE IF NOT EXISTS mrl_ai_vector_store_docs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    airtable_id TEXT UNIQUE NOT NULL,  -- Original Airtable record ID
    name TEXT, -- Name (singleLineText)
    notes TEXT, -- Notes (multilineText)
    assignee TEXT, -- Assignee (singleCollaborator)
    status TEXT, -- Status (singleSelect)
    acctabbr TEXT[], -- acctAbbr (multipleRecordLinks)
    tenant_id TEXT DEFAULT 'default',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    sync_status TEXT DEFAULT 'synced'
);

-- Index for Airtable ID lookups
CREATE INDEX IF NOT EXISTS idx_mrl_ai_vector_store_docs_airtable_id ON mrl_ai_vector_store_docs(airtable_id);
CREATE INDEX IF NOT EXISTS idx_mrl_ai_vector_store_docs_tenant ON mrl_ai_vector_store_docs(tenant_id);

-- ============================================================================
-- Table: Account Users (12 fields)
-- ============================================================================
CREATE TABLE IF NOT EXISTS mrl_account_users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    airtable_id TEXT UNIQUE NOT NULL,  -- Original Airtable record ID
    userid INTEGER, -- UserID (number)
    email TEXT, -- Email (email)
    full_name TEXT, -- Full Name (multilineText)
    status TEXT, -- Status (singleLineText)
    roles TEXT, -- Roles (singleSelect)
    username TEXT, -- Username (singleLineText)
    work_phone TEXT, -- Work Phone (phoneNumber)
    avatar TEXT, -- Avatar (multilineText)
    department TEXT, -- Department (multilineText)
    magic_link TEXT, -- Magic Link (singleLineText)
    softr_record_id TEXT, -- 🔐 Softr Record ID (multilineText)
    acctabbr TEXT[], -- acctAbbr (multipleRecordLinks)
    tenant_id TEXT DEFAULT 'default',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    sync_status TEXT DEFAULT 'synced'
);

-- Index for Airtable ID lookups
CREATE INDEX IF NOT EXISTS idx_mrl_account_users_airtable_id ON mrl_account_users(airtable_id);
CREATE INDEX IF NOT EXISTS idx_mrl_account_users_tenant ON mrl_account_users(tenant_id);

-- ============================================================================
-- Table: Accounts (25 fields)
-- ============================================================================
CREATE TABLE IF NOT EXISTS mrl_accounts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    airtable_id TEXT UNIQUE NOT NULL,  -- Original Airtable record ID
    acctabbr TEXT, -- acctAbbr (singleLineText)
    acctname TEXT, -- acctName (singleLineText)
    notes TEXT, -- Notes (multilineText)
    assignee TEXT, -- Assignee (singleCollaborator)
    tenantid TEXT, -- tenantID (formula)
    ai_vector_store_docs TEXT[], -- ai-Vector Store Docs (multipleRecordLinks)
    application_users TEXT[], -- Application Users (multipleRecordLinks)
    messages TEXT[], -- Messages (multipleRecordLinks)
    properties TEXT[], -- Properties (multipleRecordLinks)
    contacts TEXT, -- Contacts (singleLineText)
    conditions TEXT[], -- Conditions (multipleRecordLinks)
    doc_types TEXT[], -- Doc Types (multipleRecordLinks)
    documents TEXT[], -- Documents (multipleRecordLinks)
    loans TEXT[], -- Loans (multipleRecordLinks)
    categories TEXT[], -- Categories (multipleRecordLinks)
    roles TEXT[], -- Roles (multipleRecordLinks)
    lenders TEXT, -- Lenders (singleLineText)
    companies TEXT, -- Companies (singleLineText)
    company_types TEXT[], -- Company Types (multipleRecordLinks)
    companies_2 TEXT[], -- Companies 2 (multipleRecordLinks)
    contacts_2 TEXT[], -- Contacts 2 (multipleRecordLinks)
    property_components TEXT[], -- Property Components (multipleRecordLinks)
    repairs TEXT[], -- Repairs (multipleRecordLinks)
    issues TEXT[], -- Issues (multipleRecordLinks)
    contact_types TEXT, -- Contact Types (singleLineText)
    tenant_id TEXT DEFAULT 'default',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    sync_status TEXT DEFAULT 'synced'
);

-- Index for Airtable ID lookups
CREATE INDEX IF NOT EXISTS idx_mrl_accounts_airtable_id ON mrl_accounts(airtable_id);
CREATE INDEX IF NOT EXISTS idx_mrl_accounts_tenant ON mrl_accounts(tenant_id);

-- ============================================================================
-- Field Mappings Table (for sync)
-- ============================================================================
CREATE TABLE IF NOT EXISTS mrl_field_mappings (
    id SERIAL PRIMARY KEY,
    table_name TEXT NOT NULL,
    airtable_field_id TEXT NOT NULL,
    airtable_field_name TEXT NOT NULL,
    supabase_column_name TEXT NOT NULL,
    field_type TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(table_name, airtable_field_id)
);

-- Insert field mappings
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_conditions', 'fldG8yb1ujdnSVRIL', 'condID', 'condid', 'formula') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_conditions', 'fld0d6DpR6lKazhKE', 'condnRecID', 'condnrecid', 'formula') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_conditions', 'fldEd1ItJFnFUBT7L', 'humnCondReviewStatus', 'humncondreviewstatus', 'singleSelect') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_conditions', 'flddhQRa3N3AoN2vL', 'humnCondFeedback', 'humncondfeedback', 'singleLineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_conditions', 'fldjsMuZ9XTJpSuHv', 'aiCondPhase', 'aicondphase', 'singleLineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_conditions', 'fld03Qt42zz30ol4x', 'aiCondRefNum', 'aicondrefnum', 'number') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_conditions', 'fldm0OyiGX6d7abpk', 'aiCondName', 'aicondname', 'singleLineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_conditions', 'fldU8nFuksNa92lxX', 'relDocTypeCond', 'reldoctypecond', 'multipleRecordLinks') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_conditions', 'fldZIGUpGpZWMfYY5', 'recmReqActionForCond', 'recmreqactionforcond', 'multipleLookupValues') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_conditions', 'fldaiONCmNvIIH5DJ', 'finalReqActionForCond', 'finalreqactionforcond', 'richText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_conditions', 'fldNIhMe0dzE3xxQA', 'recmGuidelines', 'recmguidelines', 'multipleLookupValues') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_conditions', 'fldS7TO55BdkJPUAy', 'recmKeyOutput', 'recmkeyoutput', 'multipleLookupValues') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_conditions', 'fldWfScEVttdTZaKp', 'lenderUsage', 'lenderusage', 'multipleRecordLinks') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_conditions', 'fldT3Xr1zAwjhypLd', 'lenderLoanNum', 'lenderloannum', 'multipleRecordLinks') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_conditions', 'fldTNmitQxu1zmoqL', 'recmCategory', 'recmcategory', 'multipleLookupValues') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_conditions', 'fldESfjJUFL9oU5kA', 'recmRequester', 'recmrequester', 'multipleLookupValues') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_conditions', 'fldLd1HdG89qrAjo1', 'c-Req# (dT)', 'c_req_dt', 'multipleLookupValues') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_conditions', 'fldhFCH26hdXQdxUN', 'recmSubmitter', 'recmsubmitter', 'multipleLookupValues') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_conditions', 'flduwKLvhkwrIOqA3', 'mkSubmitter', 'mksubmitter', 'singleLineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_conditions', 'fldEd9bzbRo6CsDbr', 'c-Sub# (dT)', 'c_sub_dt', 'multipleLookupValues') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_conditions', 'fldDJsmJ0u0wZnBUg', 'condAutoNum', 'condautonum', 'autoNumber') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_conditions', 'fld2uwj7IFuXw1VTO', 'c-AI-DocMatch Status', 'c_ai_docmatch_status', 'singleSelect') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_conditions', 'fldNjvNxXIc2DDtc9', 'dateCreated', 'datecreated', 'createdTime') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_conditions', 'fldUqtzayEfvsRGPO', 'aiDocMatchComments', 'aidocmatchcomments', 'richText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_conditions', 'fldurEPcISsWvALGd', 'docsMatched', 'docsmatched', 'multipleRecordLinks') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_conditions', 'fldBzUYzTFpXNoiTK', 'dateDocAdded', 'datedocadded', 'multipleLookupValues') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_conditions', 'fldvgm8YbQ3y2D3Eq', 'dateMatched', 'datematched', 'date') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_conditions', 'fldOGStLILM1je4sy', 'dateModified', 'datemodified', 'lastModifiedTime') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_conditions', 'fldKet4gupwkxnWGK', 'aiCondCategory', 'aicondcategory', 'multilineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_conditions', 'fldnkggQeWTkwl4Lx', 'aiDocGuidelines', 'aidocguidelines', 'richText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_conditions', 'fld2AyFRM3UKhypXF', 'aiLoanThreadID', 'ailoanthreadid', 'multipleLookupValues') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_conditions', 'fldDSy7STXCYIYIw8', 'condLoanRecID', 'condloanrecid', 'multipleLookupValues') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_conditions', 'fldoHPYhmt3WiVNIx', 'acctAbbr', 'acctabbr', 'multipleRecordLinks') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_conditions', 'fldVEOcZi3HbPePlj', 'propertyShortAddress (from LenderLoanNum)', 'propertyshortaddress_from_lenderloannum', 'multipleLookupValues') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_conditions', 'fldyFYdhc4tB5l3hd', 'relContactLastName', 'relcontactlastname', 'multipleLookupValues') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_conditions', 'fldsrEuyI6smOkxmF', 'relContactFirstName', 'relcontactfirstname', 'multipleLookupValues') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_conditions', 'fldHhbJZiDJOxAG3X', 'Last modified by', 'last_modified_by', 'lastModifiedBy') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_doc_types', 'fldtXZ1N4QgBwpt1a', 'docType', 'doctype', 'singleLineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_doc_types', 'fldWL3j6KkjMNW7m8', 'Fav', 'fav', 'checkbox') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_doc_types', 'fldpqG3avAGxwIk5I', 'Categories', 'categories', 'multipleRecordLinks') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_doc_types', 'fldVbCstPxV2gvUuP', 'categoryName', 'categoryname', 'multipleLookupValues') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_doc_types', 'fldUre1i16tLGR2Us', 'recmRequestor', 'recmrequestor', 'multipleRecordLinks') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_doc_types', 'fldSeLGZr41ztBtzL', 'recmReqNum', 'recmreqnum', 'multipleLookupValues') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_doc_types', 'fldB8c4vATHITeJoo', 'Submitter', 'submitter', 'multipleRecordLinks') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_doc_types', 'fldacxIr1ABMGmnRv', 'recmSub#', 'recmsub', 'multipleLookupValues') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_doc_types', 'fldc1oA2bVxHPKfyH', 'recmReqActionCond', 'recmreqactioncond', 'richText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_doc_types', 'flddJ6kF0N3qnbBmY', 'recmGuidelines', 'recmguidelines', 'richText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_doc_types', 'fldFdUvAOYhXOudqa', 'recmKeyOutput', 'recmkeyoutput', 'richText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_doc_types', 'fldZli2HjACQm75mu', 'Added by LPAA', 'added_by_lpaa', 'singleSelect') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_doc_types', 'fldz4FnUzQYUfacIx', 'catRequestor', 'catrequestor', 'multipleLookupValues') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_doc_types', 'fldeL2jlQXYgf9E6h', 'catSubmitter', 'catsubmitter', 'multipleLookupValues') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_doc_types', 'fldGuj7aF6HOmr801', 'relConditions', 'relconditions', 'multipleRecordLinks') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_doc_types', 'fldinFpGbeSvRJkWu', 'relDocuments', 'reldocuments', 'multipleRecordLinks') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_doc_types', 'fldH7QSWNctZbsGC9', 'Lender Usage', 'lender_usage', 'singleLineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_doc_types', 'fldOdhLSmghOZaEAC', 'recmRequester', 'recmrequester', 'multipleLookupValues') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_doc_types', 'fld4K4RwYZJ3Rib2p', 'recmSubmitter', 'recmsubmitter', 'multipleLookupValues') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_doc_types', 'fldka4N8eCMpOCX53', 'docTypeRecID', 'doctyperecid', 'formula') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_doc_types', 'fldOXqsrQgwQLAxtH', 'acctAbbr', 'acctabbr', 'multipleRecordLinks') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_doc_types', 'fldgXOc9too6aJvk0', 'lastModifiedBy', 'lastmodifiedby', 'lastModifiedBy') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_doc_types', 'fld3DFlBoff90D9QR', 'lastModifiedTime', 'lastmodifiedtime', 'lastModifiedTime') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_doc_types', 'fldhlbIeYmaDEEXJ3', 'numRelConditions', 'numrelconditions', 'rollup') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_documents', 'fldJ3rtADg2ePQpRR', 'docName', 'docname', 'multilineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_documents', 'fldQDbvkygQJQlfcb', 'docDocType', 'docdoctype', 'multipleRecordLinks') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_documents', 'fld2VlvYX6areRBgJ', 'lenderLoanNum', 'lenderloannum', 'multipleRecordLinks') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_documents', 'fld4F6Y0TIi6VLhyu', 'propertyShortAddress', 'propertyshortaddress', 'singleLineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_documents', 'fldkDGLU8ImGJF8TM', 'borrower.legalEntityName', 'borrower_legalentityname', 'singleLineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_documents', 'fldnNDoxtkPE3nafb', 'borrower.contactFirstName', 'borrower_contactfirstname', 'singleLineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_documents', 'fldjJcDViC8ff5EYq', 'borrower.contactLastName', 'borrower_contactlastname', 'singleLineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_documents', 'fldkmIuMMI9UZlM5Y', 'matchedCondns', 'matchedcondns', 'multipleRecordLinks') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_documents', 'fldzoPNHT6HSIuMbz', 'docMatchStatus', 'docmatchstatus', 'singleSelect') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_documents', 'fldYbE0ICdULkBN1D', 'aiMatchSummary', 'aimatchsummary', 'richText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_documents', 'fld8W593GUsDxkLye', 'humnDocReviewStatus', 'humndocreviewstatus', 'singleSelect') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_documents', 'flde8qczKT7V3Yx1t', 'humnDocFeedback', 'humndocfeedback', 'singleLineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_documents', 'fldHfCuahBpLtERCJ', 'linkShared ', 'linkshared', 'url') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_documents', 'fldInhvhdob5HMJpn', 'docCategory', 'doccategory', 'singleLineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_documents', 'fldmK5Lb9uOvXMtiK', 'dateAdded', 'dateadded', 'createdTime') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_documents', 'fldbLtRH4lgZr02Fy', 'recmGuidelines', 'recmguidelines', 'multipleLookupValues') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_documents', 'fldbg1iTNaWxmyL8n', 'recmKeyOutput', 'recmkeyoutput', 'multipleLookupValues') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_documents', 'fldxmuddPxpiD7Mlo', 'issuingCompanyName', 'issuingcompanyname', 'singleLineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_documents', 'fldUup0oY24bLvGYe', 'accountHolderName', 'accountholdername', 'singleLineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_documents', 'fldy357pMXVIdjXsw', 'accountNumber', 'accountnumber', 'singleLineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_documents', 'fldaoXrD0c4Vk3G38', 'additionalHolderName', 'additionalholdername', 'singleLineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_documents', 'fld53Muv6gKDu8fBM', 'dateDocIssued', 'datedocissued', 'date') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_documents', 'fldW8TCk5mMgBA1d1', 'dateDocEffective', 'datedoceffective', 'date') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_documents', 'fldj57kDAPH8cZVE3', 'totalBalance', 'totalbalance', 'number') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_documents', 'fldYARmh4niuhXIJK', 'totalEarnest', 'totalearnest', 'number') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_documents', 'fld1Bn6EKSGtCeKcS', 'purchasePrice', 'purchaseprice', 'number') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_documents', 'fldhI7m2IPdYXEF9h', 'dateRangeStart', 'daterangestart', 'date') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_documents', 'fldbfyIwtpsXGtc1G', 'dateRangeEnd', 'daterangeend', 'date') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_documents', 'fldrrrGvJtlpkSVGP', 'propertyAddress', 'propertyaddress', 'multilineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_documents', 'fldIOxFmPhJONAAuj', 'borrower.contactEmail', 'borrower_contactemail', 'email') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_documents', 'fldVAIOKkZ82lB7iF', 'borrower.contactResidenceAddress', 'borrower_contactresidenceaddress', 'multilineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_documents', 'fldCy3zZJ6355xuZ9', 'borrower.contactPhone', 'borrower_contactphone', 'phoneNumber') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_documents', 'fldAMbN0zJ2yMAyTa', 'docRecID', 'docrecid', 'formula') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_documents', 'fldYaDliRirPRYI53', 'allDocProperties', 'alldocproperties', 'richText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_documents', 'fldWyt1Fkr7NTSJ1K', 'sourceLink', 'sourcelink', 'singleLineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_documents', 'fld1sHr5LKcjWVa24', 'docDriveFileID', 'docdrivefileid', 'singleLineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_documents', 'fldmV66afGWdG9Lu7', 'docOpenFileID', 'docopenfileid', 'singleLineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_documents', 'fldTGklg4RBMgAef3', 'docNameOriginal', 'docnameoriginal', 'singleLineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_documents', 'fldr3j2U81dFnJi3K', 'docLoanRecID', 'docloanrecid', 'multipleLookupValues') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_documents', 'fld2GSCNhruqRL9F3', 'Uploaded By', 'uploaded_by', 'multilineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_documents', 'fldKShAUD6EkyjRqI', 'attachedFile', 'attachedfile', 'multipleAttachments') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_documents', 'fldRagVX7XGl8l1EQ', 'docNameIngested', 'docnameingested', 'singleLineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_documents', 'fldSLWsnlkvLwlP6Z', 'sourceContentID', 'sourcecontentid', 'singleLineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_documents', 'fldmdUWdBN862O4Bm', 'sourceSenderEmail', 'sourcesenderemail', 'singleLineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_documents', 'fldFb4CDQ7Sm57nDU', 'sourceSenderFirstName', 'sourcesenderfirstname', 'singleLineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_documents', 'fldc5SXh6lWJWM9x3', 'sourceSubjectLine', 'sourcesubjectline', 'singleLineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_documents', 'flduLKlPhsUjDV2Jn', 'Categories (from docDocType)', 'categories_from_docdoctype', 'multipleLookupValues') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_documents', 'fldC60mYxLsXmTW67', 'acctAbbr', 'acctabbr', 'multipleRecordLinks') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_documents', 'fldpGFbvkRaMU9B1Q', 'lastModified', 'lastmodified', 'lastModifiedTime') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_documents', 'fldJgOeQzokKl1yqD', 'Properties', 'properties', 'multipleRecordLinks') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_documents', 'fldjMkQXXC2HAVrHe', 'Agreements', 'agreements', 'multipleRecordLinks') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_agreements', 'fldGmnvw3DafHLNt7', 'agmtName', 'agmtname', 'singleLineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_agreements', 'fldm1Eo7RJ9Ovhlpd', 'agmtRecID', 'agmtrecid', 'formula') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_agreements', 'fldUE7NdDP9mlk7RE', 'agmtType', 'agmttype', 'singleSelect') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_agreements', 'fld34lgcVZ9MZLhbY', 'relProperty', 'relproperty', 'multipleRecordLinks') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_agreements', 'flduN5P4WDAX5vjxf', 'relCompany', 'relcompany', 'multipleRecordLinks') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_agreements', 'fldY76Tu9FCEUueA5', 'relPrimaryContact', 'relprimarycontact', 'multipleLookupValues') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_agreements', 'fldJnYDodPp8F76Oi', 'agmtSubType ', 'agmtsubtype', 'singleLineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_agreements', 'fldfHmWId9XlnDTB7', 'agmtNum', 'agmtnum', 'singleLineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_agreements', 'fld49cX6ndFPqmCpu', 'agmtEffectiveDate', 'agmteffectivedate', 'date') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_agreements', 'fldBMRUiqUoIbnTce', 'agmtEndDate', 'agmtenddate', 'date') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_agreements', 'fldZUW0Hd2UM7MhPI', 'lenderLoanNum', 'lenderloannum', 'multipleRecordLinks') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_agreements', 'fldmFGEeBfT2z86k6', 'agmtDocLink', 'agmtdoclink', 'multipleRecordLinks') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_agreements', 'fldYqYF65Ux9fQPg3', 'agmtRate', 'agmtrate', 'percent') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_agreements', 'fldFNbMHrDiMI6VOo', 'agmtTotalAmt', 'agmttotalamt', 'currency') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_agreements', 'fldvXcNqgtKLt3M1f', 'agmtDeposit', 'agmtdeposit', 'currency') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_agreements', 'fldXTUiPuEtpmKINy', 'agmtNotes', 'agmtnotes', 'multilineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_agreements', 'fldm1r5buHyhWe0vh', 'offerorLegalName', 'offerorlegalname', 'multipleRecordLinks') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_agreements', 'fldeK9CaEEfJjZTkA', 'offerorMgmtAgent', 'offerormgmtagent', 'multipleRecordLinks') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_agreements', 'fldXI5TsRQAuuZadM', 'offerorPrimaryContact', 'offerorprimarycontact', 'multipleRecordLinks') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_agreements', 'fldZwL9NxXw2UYP2a', 'offerorOtherNames', 'offerorothernames', 'multipleRecordLinks') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_agreements', 'fldVuLRKRRBZJsDSR', 'offereeLegalName', 'offereelegalname', 'multipleRecordLinks') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_agreements', 'fldhzZQS0QHcIf5cD', 'offereePrimaryContact', 'offereeprimarycontact', 'multipleRecordLinks') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_agreements', 'fldSE4F3ArMwEbXTi', 'offereeEmail', 'offereeemail', 'multipleLookupValues') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_agreements', 'fldgHoOnRAmR6dHPb', 'offereeOtherNames', 'offereeothernames', 'multipleRecordLinks') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_loans', 'fldVzvizUBrHfwc62', 'lenderLoanNum', 'lenderloannum', 'singleLineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_loans', 'fldkp2ie5KX9W35UY', 'humnLoanReviewStatus', 'humnloanreviewstatus', 'singleSelect') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_loans', 'fldeWIh5cLKIS23In', 'humnLoanFeedback', 'humnloanfeedback', 'multilineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_loans', 'fldKjmVUwIxbCcNUl', 'legalEntityName', 'legalentityname', 'singleLineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_loans', 'fldZ1WgxN8YiK29QD', 'contactFirstName', 'contactfirstname', 'singleLineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_loans', 'fldKlke8hrZ6BvoZL', 'contactLastName', 'contactlastname', 'singleLineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_loans', 'fldG3DMpd9SUSCanl', 'contactEmail', 'contactemail', 'singleLineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_loans', 'fldWn1gHbXyvsEIey', 'contactPhone', 'contactphone', 'phoneNumber') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_loans', 'fldNAx3OfX7Ku5dOi', 'contactResidenceAddress', 'contactresidenceaddress', 'singleLineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_loans', 'fldL9elRmENq05aXm', 'loanOfficer', 'loanofficer', 'singleLineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_loans', 'fld8KWyTt0rDnXKuI', 'loanOfficerEmail', 'loanofficeremail', 'email') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_loans', 'fldLVeE0kBggdKGXi', 'loanPurpose', 'loanpurpose', 'singleSelect') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_loans', 'fldZkEcVYSk1yJzu8', 'lenderName', 'lendername', 'multipleLookupValues') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_loans', 'fldU0gAZXsxgNZmDb', 'loanAmount', 'loanamount', 'currency') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_loans', 'fldO8FswW800vMN48', 'propertyShortAddress', 'propertyshortaddress', 'singleLineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_loans', 'fld8GWGgx7lQAUgFx', 'propertyAddress', 'propertyaddress', 'singleLineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_loans', 'fldbtbxxIxDeXOURy', 'intRate', 'intrate', 'number') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_loans', 'fldoO7O9ndj4Lxlu9', 'loanStatus', 'loanstatus', 'singleSelect') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_loans', 'fld0KQrLr5UnsMhak', 'dateRegistered', 'dateregistered', 'date') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_loans', 'fldEIY97Qf529bwzl', 'dateSubmitted', 'datesubmitted', 'date') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_loans', 'fldwGiwMyahFoFMJC', 'dateClosing', 'dateclosing', 'date') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_loans', 'fldNjNqiYBeaNl4vE', 'dateLockExpires', 'datelockexpires', 'date') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_loans', 'fldlGMAt4evZrnMSC', 'dateLocked', 'datelocked', 'date') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_loans', 'fldZmakgUxJJ2uf9U', 'dateFinalApproval', 'datefinalapproval', 'date') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_loans', 'fldHEeKVbLnFqUSL2', 'dateApprovalExpires', 'dateapprovalexpires', 'date') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_loans', 'fldL4oMdZqfLcfIDy', 'loanRecID', 'loanrecid', 'formula') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_loans', 'fldhkCBbNYxlJalvn', 'loanClickupID', 'loanclickupid', 'singleLineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_loans', 'fldgdF9beLT3bYL5G', 'loanOpenThreadID', 'loanopenthreadid', 'singleLineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_loans', 'fldOQZqf75yNCST1Q', 'loanDriveFolderID', 'loandrivefolderid', 'singleLineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_loans', 'fldjN02mEtZnQbZDV', 'allLoanProperties', 'allloanproperties', 'multilineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_loans', 'fldhkxgP3mWOTYa86', 'relDocs', 'reldocs', 'multipleRecordLinks') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_loans', 'fldFiy5rD6RgbxyDu', 'relConditions', 'relconditions', 'multipleRecordLinks') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_loans', 'fldAinbBUaM2oFg6h', 'loanUploaderIntro', 'loanuploaderintro', 'multilineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_loans', 'flddjlwUtFbOdKCXS', 'contactFullName', 'contactfullname', 'singleLineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_loans', 'fldg4bdpsEZJbdeEt', 'loanProgram', 'loanprogram', 'singleSelect') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_loans', 'fld45Cq1obSFfRVfM', 'relLenderOrderIndex', 'rellenderorderindex', 'singleLineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_loans', 'fldwgF2fL1Omr4Ii0', 'propertyCity', 'propertycity', 'singleLineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_loans', 'fldSSA6mVPQc7pcQE', 'propertyState', 'propertystate', 'singleLineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_loans', 'fldv8YAyMGDYXOfto', 'propertyZip', 'propertyzip', 'singleLineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_loans', 'fldPFxBZy5oFFdlxB', 'acctAbbr', 'acctabbr', 'multipleRecordLinks') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_loans', 'fldORR6op5M7Q3t5O', 'Properties', 'properties', 'multipleRecordLinks') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_loans', 'fldoMb5JV2V2BRzaT', 'intRatePercent', 'intratepercent', 'formula') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_loans', 'fldcJacbgBpT6P98P', 'Agreements', 'agreements', 'multipleRecordLinks') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_loans', 'fld0Ia0C6oBgcUUnC', 'loanAmount copy', 'loanamount_copy', 'currency') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_loans', 'fldi5FVIxfXM47fgQ', 'dateLoanEffective', 'dateloaneffective', 'date') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_categories', 'fldx6IaYJ1YCrxbHC', 'categoryName', 'categoryname', 'singleLineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_categories', 'fldashKsT3G3w5Nft', 'catRequestor', 'catrequestor', 'multipleRecordLinks') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_categories', 'fldpQAgX3BNkcYGKC', 'catSubmitter', 'catsubmitter', 'multipleRecordLinks') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_categories', 'fldeG3P7f7IhDYWKb', 'Cat-Req#', 'cat_req', 'multipleLookupValues') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_categories', 'fldSikslsoTlX1its', 'Cat-Sub#', 'cat_sub', 'multipleLookupValues') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_categories', 'fldmL22MIwc3yoY3V', 'Notes', 'notes', 'multilineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_categories', 'fldSfShxqMO40uQlv', 'Doc Types', 'doc_types', 'multipleRecordLinks') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_categories', 'fldK886CxJaSgBEQK', 'acctAbbr', 'acctabbr', 'multipleRecordLinks') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_categories', 'fldUbupA0nGFLfVId', 'numDocsUsing', 'numdocsusing', 'rollup') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_roles', 'fldbWzWydDBjexcju', 'Name', 'name', 'singleLineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_roles', 'fldM2iUuTIU5vvK2O', 'cuRoleNum', 'curolenum', 'number') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_roles', 'fldp68Lyd50sPpLlG', 'primaryRoleType', 'primaryroletype', 'singleSelect') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_roles', 'fldKKcNc5XjTK514b', 'Notes', 'notes', 'multilineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_roles', 'fld3xmdAUTDief0iF', 'Requester DocTypes', 'requester_doctypes', 'multipleRecordLinks') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_roles', 'fldkIJiFwr5m3Dk2h', 'Submitter DocTypes', 'submitter_doctypes', 'multipleRecordLinks') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_roles', 'fldjFfKmpNslX4bVw', 'Categories as Requester', 'categories_as_requester', 'multipleRecordLinks') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_roles', 'fldIcbDySZSDZGF6X', 'Categories as Submitter', 'categories_as_submitter', 'multipleRecordLinks') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_roles', 'fld4ZkyLgQ2dwkDJV', 'acctAbbr', 'acctabbr', 'multipleRecordLinks') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_roles', 'flddJvhXraXlMprOh', 'compType', 'comptype', 'multipleRecordLinks') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_roles', 'fldqGGudSZwEdCMN4', 'Contacts', 'contacts', 'multipleRecordLinks') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_properties', 'fldjRtMD5ujxvtSJy', 'propertyShortAddress', 'propertyshortaddress', 'singleLineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_properties', 'fldsRVEK0GXGj5IDY', 'propNickName', 'propnickname', 'singleLineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_properties', 'fld08XbSdGXNHVBXh', 'propCode', 'propcode', 'formula') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_properties', 'fldmkoyJUC6GGpbyj', 'propUsage', 'propusage', 'singleSelect') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_properties', 'fld0hmiovPM0IEhOR', 'propSequence', 'propsequence', 'singleSelect') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_properties', 'fld8bHqP2Sxn8RuQV', 'propertyType', 'propertytype', 'singleSelect') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_properties', 'fldOGcWwM1PaZtjwU', 'Owner', 'owner', 'multipleRecordLinks') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_properties', 'fldYxyvPAsOJ0nCBa', 'propStatus', 'propstatus', 'singleSelect') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_properties', 'fldY4galXs9mD6J4H', 'propertyAddress', 'propertyaddress', 'singleLineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_properties', 'fldbyZm3luuqzj02I', 'propertyAddress2', 'propertyaddress2', 'singleLineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_properties', 'fldPVWMsAAGUPSzjq', 'propertyCity', 'propertycity', 'singleLineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_properties', 'fld6ZXfJVwFQSCMMQ', 'propertyState', 'propertystate', 'singleLineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_properties', 'fldQU4fZAB4Y6sBST', 'propertyZip', 'propertyzip', 'singleLineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_properties', 'fldykyKeCZzc8E2CE', 'propertyCounty', 'propertycounty', 'singleLineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_properties', 'fldxjd2KJ36QWW2wS', 'relatedDocs', 'relateddocs', 'multipleRecordLinks') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_properties', 'fld1W8Ml6Ia1rfeHE', 'Loans', 'loans', 'multipleRecordLinks') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_properties', 'fldqYpAXU0jy6FFVP', 'intRatePercent', 'intratepercent', 'multipleLookupValues') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_properties', 'fldjqiZjTgb4p8cDg', 'loanAmount', 'loanamount', 'multipleLookupValues') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_properties', 'fldvJ8sKCQBVKXiaR', 'acctAbbr', 'acctabbr', 'multipleRecordLinks') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_properties', 'fldtWH5lD3WKSmHvi', 'linkRehabPlan', 'linkrehabplan', 'multipleRecordLinks') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_properties', 'fldgnXlfRyh7Noi9e', 'Repairs', 'repairs', 'singleLineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_properties', 'fldUc5nEI6ViseZyl', 'squareFootage', 'squarefootage', 'number') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_properties', 'fldCJdgfFueYxhPWU', 'grossSqFt', 'grosssqft', 'number') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_properties', 'fldLoNdmbuwoimFd8', 'origBeds', 'origbeds', 'number') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_properties', 'fldDxir6TEl5KFsWB', 'origBaths', 'origbaths', 'number') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_properties', 'flddiFiMyirThWOHo', 'numParkingSpots', 'numparkingspots', 'number') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_properties', 'flddMMD1kfEF86nNK', 'yearBuilt', 'yearbuilt', 'number') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_properties', 'fld3l6yGjquR4b9RU', 'ageOfProperty', 'ageofproperty', 'formula') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_properties', 'fld5pRJ4rTzGiRxHG', 'yearsOwned', 'yearsowned', 'formula') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_properties', 'fldupvZjtRi5MxsVF', 'legalDescription', 'legaldescription', 'singleLineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_properties', 'fldmbZmNvM3XMbRP9', 'milesToBus', 'milestobus', 'number') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_properties', 'fldGPPGEb9Xic70rg', 'purchasePrice', 'purchaseprice', 'currency') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_properties', 'fldY7kT715lCpLpLh', 'pricePerSqFt', 'pricepersqft', 'formula') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_properties', 'fldJznunKgA8yxdKC', 'datePurchased', 'datepurchased', 'date') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_properties', 'fldwCz8iHJxFfxKEv', 'dateInService', 'dateinservice', 'date') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_properties', 'flddZJiJIx3iILsKf', 'bedsWithSharedBath', 'bedswithsharedbath', 'number') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_properties', 'fldcZQQ4pOpU6RjB9', 'bedsWithPrivateBath', 'bedswithprivatebath', 'number') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_properties', 'fldR2PSFN9NvAp8CS', 'totalBeds', 'totalbeds', 'formula') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_properties', 'fld91zaAuusfCiGjl', 'totalBaths', 'totalbaths', 'number') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_properties', 'fldVVIjAUBVSgbBRZ', 'estRehabCosts', 'estrehabcosts', 'currency') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_properties', 'fldOuLRHqrVu6BkU4', 'actRehabCosts', 'actrehabcosts', 'currency') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_properties', 'fldGOKu8O9icWBZ5o', 'Property Components', 'property_components', 'multipleRecordLinks') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_properties', 'fldZD85wAYmO50Zyq', 'relIssues', 'relissues', 'multipleRecordLinks') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_properties', 'fldb49RyZDZIAt6vR', 'Issue Items', 'issue_items', 'multipleRecordLinks') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_property_components', 'fldHj7U6pQhGeFlij', 'propComponent', 'propcomponent', 'multilineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_property_components', 'fldtcHl3uOXILi7y1', 'propCmpntID', 'propcmpntid', 'formula') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_property_components', 'fldnW0zIDosbdbKRr', 'relProperty', 'relproperty', 'multipleRecordLinks') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_property_components', 'fldbwBRtH1QlJnhNP', 'relRepairs', 'relrepairs', 'singleLineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_property_components', 'fldr8szGjOWmyJpQH', 'relCompanies', 'relcompanies', 'multipleRecordLinks') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_property_components', 'fldz57RWoQv6CWtVM', 'lifespanYears', 'lifespanyears', 'number') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_property_components', 'fld5w5FHzXZ5sTNOZ', 'dateInstallation', 'dateinstallation', 'date') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_property_components', 'fldOFGKZBNIoQwQJi', 'dateLastRepaired', 'datelastrepaired', 'date') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_property_components', 'fldPa6Gs6i3yUlLO6', 'dateLastChecked', 'datelastchecked', 'date') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_property_components', 'fldEIz9KKnef5Duo2', 'monthsBetweenChecks', 'monthsbetweenchecks', 'number') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_property_components', 'fld84KoC5jMJjLmrE', 'nextScheduledCheck', 'nextscheduledcheck', 'formula') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_property_components', 'fldEdYq2uA40oCFZw', 'xeroAccountCode', 'xeroaccountcode', 'singleLineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_property_components', 'fldcRJqLW3lhzDjx0', 'xeroTrackingCategory', 'xerotrackingcategory', 'singleLineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_property_components', 'fld31fxWnQmdMLRFY', 'acctAbbr', 'acctabbr', 'multipleRecordLinks') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_property_components', 'fldv8Mn4NU8GteB0T', 'Issue Items', 'issue_items', 'multipleRecordLinks') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_companies', 'fld07w1P0PrCH2ybb', 'compName', 'compname', 'singleLineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_companies', 'fldhti6sV1zcXgKMW', 'cuOrder', 'cuorder', 'singleLineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_companies', 'fldTVqe8EyUe3vXP2', 'acctAbbr', 'acctabbr', 'multipleRecordLinks') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_companies', 'fldJHthVHGPnq93Fz', 'compRecId', 'comprecid', 'formula') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_companies', 'fldP2pK2VkBWUO0gC', 'compType', 'comptype', 'multipleRecordLinks') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_companies', 'fldRQYcWUfpfZx1kK', 'compKeywords', 'compkeywords', 'multilineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_companies', 'fldbsPDzk3knlJgou', 'description', 'description', 'multilineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_companies', 'fldsJe4Y9o0d49kT7', 'websiteUrl', 'websiteurl', 'url') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_companies', 'flddec8OSbUkjlYCe', 'hsRecordId', 'hsrecordid', 'multilineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_companies', 'fldYaVAqUA9RhYhYe', 'aboutUs', 'aboutus', 'multilineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_companies', 'fldV2Ii80E29O45ed', 'annualRevenue', 'annualrevenue', 'currency') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_companies', 'fld5n5QoJkvHE2pyt', 'labels', 'labels', 'multipleSelects') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_companies', 'fldOvaD5T3fOUp7Dy', 'closeDate', 'closedate', 'date') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_companies', 'fldjZW1iUwAOWO1Lq', 'compOwner', 'compowner', 'multilineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_companies', 'fldPxF9sMKEOFmuy2', 'countryRegion', 'countryregion', 'singleSelect') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_companies', 'fldFZjekuR9w5bM4P', 'createDate', 'createdate', 'multilineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_companies', 'fldJHAGr71Qg35H35', 'createdByUserId', 'createdbyuserid', 'multilineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_companies', 'fldIRviP05i3Rm7HG', 'facebookcompPage', 'facebookcomppage', 'multilineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_companies', 'fldRClpFTFhog7fRI', 'facebookFans', 'facebookfans', 'multilineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_companies', 'fldiEKEW4kG0yi48Q', 'firstContactCreateDate', 'firstcontactcreatedate', 'multilineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_companies', 'flds9Rp9mPETIAXL3', 'idealCustomerProfileTier', 'idealcustomerprofiletier', 'multilineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_companies', 'fld0ox9LYnyDiQ2HN', 'industry', 'industry', 'multilineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_companies', 'fldHDjC1gYXHLYyVz', 'isPublic', 'ispublic', 'checkbox') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_companies', 'fld7a1rYjljwbH8Oy', 'lastActivityDate', 'lastactivitydate', 'multilineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_companies', 'fld94D1Gd3NFW9JuA', 'latestSource', 'latestsource', 'multilineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_companies', 'fldmNKiJtJYiCNWQq', 'latestSourceTimestamp', 'latestsourcetimestamp', 'multilineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_companies', 'fldMr2HYvd4dXYOVP', 'leadStatus', 'leadstatus', 'multilineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_companies', 'fld68aIsfY1HJpJYp', 'lifecycleStage', 'lifecyclestage', 'multilineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_companies', 'fldAwWcILiwSbZO18', 'linkedInBio', 'linkedinbio', 'multilineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_companies', 'fld1r2xffdT4seYbS', 'linkedInCompanyPage', 'linkedincompanypage', 'url') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_companies', 'fldQuiKItoGkCSrN4', 'linkedInUid', 'linkedinuid', 'singleLineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_companies', 'fldl4MFkXHJG1Yxq5', 'logoUrl', 'logourl', 'url') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_companies', 'fldXIRfvUEnHmvyS7', 'streetAddress', 'streetaddress', 'singleLineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_companies', 'fldkUT6ZCvF4PBAYA', 'streetAddress2', 'streetaddress2', 'singleLineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_companies', 'fldjKuF2KjBAVlyNJ', 'city', 'city', 'singleLineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_companies', 'fldrK0AojAh46DrYD', 'stateRegion', 'stateregion', 'singleLineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_companies', 'fld8DuLzJUKD5tKXI', 'postalCode', 'postalcode', 'multilineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_companies', 'fldpg0RFW1I3HP9qj', 'targetAccount', 'targetaccount', 'multilineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_companies', 'fldboovxipBwxeEX9', 'timeZone', 'timezone', 'multilineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_companies', 'fldSpG8iLz4qTMbmF', 'totalMoneyRaised', 'totalmoneyraised', 'multilineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_companies', 'fldT5T7xOlPMMFsLe', 'twitterBio', 'twitterbio', 'multilineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_companies', 'fldtvzNAdLxi1ONrM', 'twitterFollowers', 'twitterfollowers', 'multilineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_companies', 'fldAT1UZm80F6wlNW', 'twitterHandle', 'twitterhandle', 'multilineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_companies', 'fldBIp3qaDo7NvRHU', 'webTechnologies', 'webtechnologies', 'multilineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_companies', 'fldalWCYXuJ5mr0U0', 'relPrimaryContact', 'relprimarycontact', 'multipleRecordLinks') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_companies', 'fldw6MVGdfc8agjS3', 'firstName (from assocContact)', 'firstname_from_assoccontact', 'multipleLookupValues') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_companies', 'fldMJOnbvl1rwvimX', 'lastName (from assocContact)', 'lastname_from_assoccontact', 'multipleLookupValues') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_companies', 'fldZkUGLMXe5F1Dux', 'email (from assocContact)', 'email_from_assoccontact', 'multipleLookupValues') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_companies', 'fldciJhN3kyK8RpTO', 'phoneNumber (from assocContact)', 'phonenumber_from_assoccontact', 'multipleLookupValues') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_companies', 'fldlRUxndOJTRNbMI', 'associatedDeal', 'associateddeal', 'multilineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_companies', 'fldI1z8svby0MECRq', 'contacts', 'contacts', 'multilineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_companies', 'fldK3SoRiqEed48P8', 'Agreements', 'agreements', 'multipleRecordLinks') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_companies', 'fldSgrUee0unCIVdB', 'Agreements 2', 'agreements_2', 'multipleRecordLinks') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_companies', 'fldh6cq6jtsSGjxAC', 'Agreements 3', 'agreements_3', 'multipleRecordLinks') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_companies', 'fldKEycySJ90C6IAw', 'Properties', 'properties', 'multipleRecordLinks') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_companies', 'fldx8spVFfyr1dSTr', 'Agreements 4', 'agreements_4', 'multipleRecordLinks') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_companies', 'fldqA4UX4wrz1DBKR', 'Conditions', 'conditions', 'multipleRecordLinks') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_companies', 'fldvrG4r6E2kDCE8K', 'Property Components', 'property_components', 'multipleRecordLinks') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_companies', 'fld7zoeMJcoi4HQ8X', 'relOtherContacts', 'relothercontacts', 'multipleRecordLinks') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_companies', 'fldyi4tyISXuhoM48', 'primaryPhone', 'primaryphone', 'multipleLookupValues') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_companies', 'fldlNMHEBvRPnyzMQ', 'primaryEmail', 'primaryemail', 'multipleLookupValues') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_company_types', 'fldHcAMAamVEzbDUj', 'compType', 'comptype', 'singleLineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_company_types', 'fldMpXAUmc841qajm', 'Company Type', 'company_type', 'singleLineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_company_types', 'fldswjVcLdGRobvtP', 'Description', 'description', 'multilineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_company_types', 'fld5Sg7gMBufUYznr', 'compTypeRecID', 'comptyperecid', 'formula') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_company_types', 'fldDqR36QkulpnZ0q', 'acctAbbr', 'acctabbr', 'multipleRecordLinks') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_company_types', 'fldFnoJPUvBef2S8f', 'Companies', 'companies', 'multipleRecordLinks') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_company_types', 'fld1PwPxG4rZ444Tn', 'Contact Types', 'contact_types', 'singleLineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_company_types', 'fldsleewgjNo8aNVk', 'Roles', 'roles', 'multipleRecordLinks') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_contacts', 'fld9jIEyfzzkBELuk', 'contactFullNameId', 'contactfullnameid', 'formula') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_contacts', 'fldrAymvJfcqWGUQd', 'contactRecID', 'contactrecid', 'formula') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_contacts', 'fldFVcxjDyKTWjIio', 'firstName', 'firstname', 'singleLineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_contacts', 'fldhRl4zsDr4xaqv8', 'lastName', 'lastname', 'singleLineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_contacts', 'fld8KdXgGyLgvEjbP', 'nickName', 'nickname', 'multilineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_contacts', 'fldP8jixCoxV7I6kj', 'contactRole', 'contactrole', 'multipleRecordLinks') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_contacts', 'fld4U3qgbKufop1sQ', 'email', 'email', 'email') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_contacts', 'fldGT15qD8Nra4HeL', 'phoneNumber', 'phonenumber', 'phoneNumber') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_contacts', 'fldfSumhz42ER4p7q', 'relCompanies', 'relcompanies', 'multipleRecordLinks') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_contacts', 'fldY7U95TlJgo5W8Y', 'streetAddress', 'streetaddress', 'multilineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_contacts', 'fldjDzLLOl2WUGz62', 'city', 'city', 'singleLineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_contacts', 'fldbBlOfFIqiivfXe', 'stateRegion', 'stateregion', 'multilineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_contacts', 'flda2khujiZbS2vcW', 'zipPostal', 'zippostal', 'singleLineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_contacts', 'fldgGxE1bus7BFE0E', 'countryRegion', 'countryregion', 'multilineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_contacts', 'fldk0PkjrKGFI53Ce', 'contactOwner', 'contactowner', 'singleCollaborator') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_contacts', 'fldpZBiHF0wf63ccb', 'relAnnualRevenue', 'relannualrevenue', 'multipleLookupValues') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_contacts', 'fldyRZ6sAmzcrVFtf', 'labels', 'labels', 'multilineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_contacts', 'fldTChgOc20zVKqp8', 'buyingRole', 'buyingrole', 'singleSelect') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_contacts', 'fldkQUdmxB442fuY2', 'dateBecameALead', 'datebecamealead', 'date') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_contacts', 'fldWuAnRtMaSuphjZ', 'dateOfBirth', 'dateofbirth', 'date') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_contacts', 'fldtvwX8JLBQT10oY', 'dateOfFirstEngagement', 'dateoffirstengagement', 'multilineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_contacts', 'fldT9pYgly89rJTmD', 'employmentRole', 'employmentrole', 'multilineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_contacts', 'fldKDlZjZhhPCNr5n', 'employmentSeniority', 'employmentseniority', 'multilineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_contacts', 'fldIBscdiWWQsKmAv', 'employmentSubRole', 'employmentsubrole', 'multilineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_contacts', 'fldAonOiPJvLB7kQY', 'facebookClickId', 'facebookclickid', 'multilineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_contacts', 'fldMJHTkYo5p4aP0x', 'gender', 'gender', 'multilineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_contacts', 'fldfHrUKGJtngKlkl', 'hubSpotScore', 'hubspotscore', 'multilineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_contacts', 'fldJ6jRDCT7TQwj6I', 'latestSource', 'latestsource', 'multilineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_contacts', 'fld4GFN2gjxCi1wnt', 'latestSourceDate', 'latestsourcedate', 'multilineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_contacts', 'fldK4lQvUfg0DE6rW', 'linkedIn', 'linkedin', 'multilineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_contacts', 'fldB3DMxRwc4J8QXr', 'linkedInUid', 'linkedinuid', 'multilineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_contacts', 'fldR4bLOBAqu2i98c', 'message', 'message', 'multilineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_contacts', 'fld0UV5MrVSaMb0lD', 'preferredLanguage', 'preferredlanguage', 'multilineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_contacts', 'fldBuA3IPcOjDT383', 'recordSource', 'recordsource', 'multilineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_contacts', 'fldFxwJnpDOU5taTJ', 'relationshipStatus', 'relationshipstatus', 'multilineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_contacts', 'fldDJOWEKuCl8EBAX', 'school', 'school', 'multilineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_contacts', 'fldxv0u6uwB4R9H2k', 'salutation', 'salutation', 'multilineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_contacts', 'fldCxiYS5T63dwvYS', 'seniority', 'seniority', 'multilineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_contacts', 'fldmF39HsMh9LxK4a', 'timeZone', 'timezone', 'singleLineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_contacts', 'fldRFaQD07VWxH9uY', 'timeZone copy', 'timezone_copy', 'multilineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_contacts', 'fldulMmKOT7DMdY1Y', 'twitterName', 'twittername', 'singleLineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_contacts', 'fldUGwT5VWu7Kmyug', 'whatsAppPhoneNumber', 'whatsappphonenumber', 'phoneNumber') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_contacts', 'fldQ9ORZzNmZ4NccA', 'workEmail', 'workemail', 'multilineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_contacts', 'fldZvMLtVORftyblE', 'associatedDealCreateAttribution', 'associateddealcreateattribution', 'multilineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_contacts', 'fldRwLEowC3HRMpmG', 'associatedCompany2', 'associatedcompany2', 'multilineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_contacts', 'fldMsGNfXkRSQYIT7', 'ruleResponsible', 'ruleresponsible', 'multilineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_contacts', 'fldHE3izpJKakeIeC', 'acctAbbr', 'acctabbr', 'multipleRecordLinks') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_contacts', 'fld5dYnzV7pvNOLSX', 'hubRecordID', 'hubrecordid', 'number') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_contacts', 'fld3TsZnoXCpQpHpE', 'relAgmtOfferorPrimaryContact', 'relagmtofferorprimarycontact', 'multipleRecordLinks') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_contacts', 'fldAVtF0WLIL5BlN1', 'relAgmtOfferorOtherNames', 'relagmtofferorothernames', 'multipleRecordLinks') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_contacts', 'fldGoCZAoeMjSsB21', 'relAgmtOffereePrimaryContact', 'relagmtoffereeprimarycontact', 'multipleRecordLinks') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_contacts', 'fldnoK03sT3k6Osjw', 'relAgmtOffereeOtherNames', 'relagmtoffereeothernames', 'multipleRecordLinks') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_contacts', 'fldzEz7zVYS6rFdO9', 'relCompanies copy', 'relcompanies_copy', 'multipleRecordLinks') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_messages', 'flds38UwbuJhcxBxE', 'Sender', 'sender', 'multilineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_messages', 'fldKHNiP3Nfn33dDk', 'Receiver', 'receiver', 'multilineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_messages', 'fldt7LyByB6gV8X4y', 'Message Body', 'message_body', 'multilineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_messages', 'fldfCKJGaSvm5IQHR', 'Timestamp', 'timestamp', 'dateTime') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_messages', 'fldSR0hz0RgVZTo0D', '🔐 Softr Record ID', 'softr_record_id', 'multilineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_messages', 'fldvDL1Vvh73rRic1', 'acctAbbr', 'acctabbr', 'multipleRecordLinks') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_issue_items', 'fldoQKtmnUUpRwU4C', 'cuTaskID', 'cutaskid', 'multilineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_issue_items', 'fldMNpbTfEDOGwRrn', 'issueName', 'issuename', 'multilineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_issue_items', 'fldSG9qWJdBToZ7ys', 'itemPriority', 'itempriority', 'singleSelect') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_issue_items', 'fldFzLgU6lUfcBwNv', 'relPropComponent', 'relpropcomponent', 'multipleRecordLinks') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_issue_items', 'flde9g7hSUxd2sqtr', 'relProperty', 'relproperty', 'multipleRecordLinks') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_issue_items', 'fldZdcinymKxjtfY7', 'Assignee', 'assignee', 'singleSelect') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_issue_items', 'fldlR2rMFNsBwEUEp', 'dueDate', 'duedate', 'date') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_issue_items', 'fldaAapnh7mWcsceD', 'Latest Comment', 'latest_comment', 'multilineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_issue_items', 'fldSgPoGBjyaePEPH', 'Property (drop down)', 'property_drop_down', 'multipleRecordLinks') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_issue_items', 'fldgjRbhCSBk0t4LQ', 'Time Logged', 'time_logged', 'multilineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_issue_items', 'fldRhH8wokw6fLTAG', 'Time Logged Rolled Up', 'time_logged_rolled_up', 'multilineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_issue_items', 'fldylzMCr6Y5GHO3s', 'Link (url)', 'link_url', 'multilineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_issue_items', 'fldJHzlm0TzvC4syK', 'Related Vendor (list relationship)', 'related_vendor_list_relationship', 'singleSelect') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_issue_items', 'fldZRtRGFvXSsNMB4', 'Start Date', 'start_date', 'singleLineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_issue_items', 'fldJygT46tUtogL1u', 'Date Updated', 'date_updated', 'singleLineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_issue_items', 'fldEiBLtlE0ieIAxG', 'Category (WAZ)', 'category_waz', 'singleSelect') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_issue_items', 'fldmQrBON9ToxAbLY', 'Summary (text)', 'summary_text', 'multilineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_issue_items', 'fldgUEMqTxYFq8K1x', 'acctAbbr', 'acctabbr', 'multipleRecordLinks') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_repairs', 'fldfSpbYwo0vcttYx', 'repair', 'repair', 'multilineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_repairs', 'fldwxPtshgTPA3nYi', 'vendor', 'vendor', 'singleLineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_repairs', 'fldgyUvW06BQMwU1q', 'documentationLink', 'documentationlink', 'singleLineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_repairs', 'fld2n1PCBOdccGYva', 'estimatedCost', 'estimatedcost', 'singleLineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_repairs', 'fldxHLSirnMP1rzvK', 'actualCost', 'actualcost', 'singleLineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_repairs', 'fldbzM4LlnzFJ8Kh9', 'warrantyExpiration', 'warrantyexpiration', 'singleLineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_repairs', 'fldVH6Y0RSnWQvv3i', 'modelNumber', 'modelnumber', 'singleLineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_repairs', 'fld8nyUC9L5Ma1Lsg', 'serialNumber', 'serialnumber', 'singleLineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_repairs', 'fldwripF20d6VIoxq', 'acctAbbr', 'acctabbr', 'multipleRecordLinks') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_repairs', 'fldme3EfgMmgUGBtu', 'Properties', 'properties', 'singleLineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_ai_vector_store_docs', 'fldfipKMEjAeoUUF9', 'Name', 'name', 'singleLineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_ai_vector_store_docs', 'fldv2h02fDzFeFeKx', 'Notes', 'notes', 'multilineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_ai_vector_store_docs', 'fldmVf8vOQ54IfmuS', 'Assignee', 'assignee', 'singleCollaborator') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_ai_vector_store_docs', 'fldn2iCtQr8LRLJkt', 'Status', 'status', 'singleSelect') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_ai_vector_store_docs', 'fldeoBERZZYDU0jCA', 'acctAbbr', 'acctabbr', 'multipleRecordLinks') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_account_users', 'fldyC7IDLU5CeraNF', 'UserID', 'userid', 'number') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_account_users', 'fldYkhAY5Yzfb6IUK', 'Email', 'email', 'email') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_account_users', 'fldH7LkCFjSMhv1It', 'Full Name', 'full_name', 'multilineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_account_users', 'fldVA1vddOVxSKlXf', 'Status', 'status', 'singleLineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_account_users', 'fldSqiTOrl5mKXte1', 'Roles', 'roles', 'singleSelect') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_account_users', 'fldEqkMeu9rhpoDlZ', 'Username', 'username', 'singleLineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_account_users', 'fldGv3WlaLPLTKx9D', 'Work Phone', 'work_phone', 'phoneNumber') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_account_users', 'fld0ntvxT3DKVPSbf', 'Avatar', 'avatar', 'multilineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_account_users', 'fldq9NgL68ctdxqz1', 'Department', 'department', 'multilineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_account_users', 'fldtw059FTvvrq4G7', 'Magic Link', 'magic_link', 'singleLineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_account_users', 'fldoD2G5xgXbK3or1', '🔐 Softr Record ID', 'softr_record_id', 'multilineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_account_users', 'fldc3xhtcqLfzQtKv', 'acctAbbr', 'acctabbr', 'multipleRecordLinks') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_accounts', 'fldjiqgfHXet1Qbp9', 'acctAbbr', 'acctabbr', 'singleLineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_accounts', 'fldIhGs2qMN189wVK', 'acctName', 'acctname', 'singleLineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_accounts', 'fldQ8jbBBjcVjuJPZ', 'Notes', 'notes', 'multilineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_accounts', 'fldMjK4Ip8HqR7AQP', 'Assignee', 'assignee', 'singleCollaborator') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_accounts', 'fld8isv5JxbkOZaWp', 'tenantID', 'tenantid', 'formula') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_accounts', 'fldtsQSvmrfGo5fqQ', 'ai-Vector Store Docs', 'ai_vector_store_docs', 'multipleRecordLinks') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_accounts', 'fldC6MCs2ZW7laMBe', 'Application Users', 'application_users', 'multipleRecordLinks') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_accounts', 'fld69omoPaS7KbBd1', 'Messages', 'messages', 'multipleRecordLinks') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_accounts', 'fldDQODRm6eFRl0Ks', 'Properties', 'properties', 'multipleRecordLinks') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_accounts', 'fld2g3yVReG5LKQ68', 'Contacts', 'contacts', 'singleLineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_accounts', 'fldlu5JqO1I5NjqiC', 'Conditions', 'conditions', 'multipleRecordLinks') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_accounts', 'fldVqmKqbg8cC5pNA', 'Doc Types', 'doc_types', 'multipleRecordLinks') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_accounts', 'fldQBKTsGRaTwPmyC', 'Documents', 'documents', 'multipleRecordLinks') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_accounts', 'fldMRJ4u2WeOcQltX', 'Loans', 'loans', 'multipleRecordLinks') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_accounts', 'fldc3Ljgmzmv8h3OI', 'Categories', 'categories', 'multipleRecordLinks') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_accounts', 'fldJaHutm7yuMDSlo', 'Roles', 'roles', 'multipleRecordLinks') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_accounts', 'fldDmO65MUE76dFaV', 'Lenders', 'lenders', 'singleLineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_accounts', 'fld0QSQoRfE5UMWWy', 'Companies', 'companies', 'singleLineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_accounts', 'fldDF8GijeagadD0x', 'Company Types', 'company_types', 'multipleRecordLinks') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_accounts', 'fldOI2vq0SNAO3Abj', 'Companies 2', 'companies_2', 'multipleRecordLinks') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_accounts', 'fldYuLNxj9gN9WLkm', 'Contacts 2', 'contacts_2', 'multipleRecordLinks') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_accounts', 'fldkCu84vmHTcXa0I', 'Property Components', 'property_components', 'multipleRecordLinks') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_accounts', 'fld31YOI5NvS4K5mT', 'Repairs', 'repairs', 'multipleRecordLinks') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_accounts', 'fldtnlP1EuM4s8wEz', 'Issues', 'issues', 'multipleRecordLinks') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;
INSERT INTO mrl_field_mappings (table_name, airtable_field_id, airtable_field_name, supabase_column_name, field_type) VALUES ('mrl_accounts', 'fldPRtmAa5YnroOYR', 'Contact Types', 'contact_types', 'singleLineText') ON CONFLICT (table_name, airtable_field_id) DO NOTHING;

-- ============================================================================
-- Migration complete!
-- Tables created: 18
-- Field mappings: 458
-- ============================================================================