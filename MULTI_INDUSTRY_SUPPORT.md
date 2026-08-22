# Multi-Industry Support - AI Voice & SMS Platform

## Overview

The AI Voice & SMS platform is **designed to be industry-agnostic** but can be customized with industry-specific workflows, prompts, and features. This document outlines how to support multiple business types during onboarding and how to configure industry-specific behavior.

---

## Supported Industries

### Service-Based Businesses
✅ **HVAC (Heating, Ventilation, Air Conditioning)**
✅ **Electrical Services**
✅ **Plumbing Services**
✅ **Roofing Services**
✅ **Landscaping & Lawn Care**
✅ **General Contractors**
✅ **Home Cleaning Services**

### Retail & E-Commerce
✅ **Restaurants & Cafes**
✅ **Retail Stores**
✅ **Salons & Spas**
✅ **Gyms & Fitness Centers**
✅ **Boutiques & Fashion**

### Professional Services
✅ **Law Firms**
✅ **Medical/Dental Offices**
✅ **Consulting Firms**
✅ **Accounting/Tax Services**
✅ **Insurance Agencies**

### Hospitality & Travel
✅ **Hotels & Motels**
✅ **Bed & Breakfasts**
✅ **Travel Agencies**
✅ **Event Venues**
✅ **Tour Operators**

### Education & Training
✅ **Tutoring Centers**
✅ **Language Schools**
✅ **Coding Bootcamps**
✅ **Fitness Training**
✅ **Music Lessons**

### Real Estate
✅ **Real Estate Agencies**
✅ **Property Management**
✅ **Apartment Leasing**
✅ **Commercial Brokers**

---

## Implementation Strategy

### 1. Database Changes

Add `business_type` field to Organization model:

```python
# backend/app/models.py

class BusinessType(str, Enum):
    # Service
    HVAC = "hvac"
    ELECTRICAL = "electrical"
    PLUMBING = "plumbing"
    ROOFING = "roofing"
    LANDSCAPING = "landscaping"
    CLEANING = "cleaning"
    GENERAL_CONTRACTOR = "general_contractor"
    
    # Retail
    RESTAURANT = "restaurant"
    RETAIL = "retail"
    SALON = "salon"
    GYM = "gym"
    BOUTIQUE = "boutique"
    
    # Professional
    LAW_FIRM = "law_firm"
    MEDICAL = "medical"
    DENTAL = "dental"
    CONSULTING = "consulting"
    ACCOUNTING = "accounting"
    INSURANCE = "insurance"
    
    # Hospitality
    HOTEL = "hotel"
    BED_BREAKFAST = "bed_breakfast"
    TRAVEL = "travel"
    EVENT_VENUE = "event_venue"
    
    # Education
    TUTORING = "tutoring"
    LANGUAGE_SCHOOL = "language_school"
    BOOTCAMP = "bootcamp"
    FITNESS = "fitness"
    MUSIC = "music"
    
    # Real Estate
    REAL_ESTATE = "real_estate"
    PROPERTY_MANAGEMENT = "property_management"
    APARTMENT_LEASING = "apartment_leasing"

class Organization(Base):
    __tablename__ = "organizations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(255), nullable=False, index=True)
    business_type = Column(String(50), nullable=False, default=BusinessType.GENERAL_CONTRACTOR)
    industry_category = Column(String(50), nullable=False)  # "service", "retail", "professional", etc.
    timezone = Column(String(50), default="America/New_York")
    locale = Column(String(10), default="en_US")
    
    # Industry-specific settings
    custom_fields = Column(JSON, default={})  # Store industry-specific data
    features_enabled = Column(JSON, default={})  # Track which features are enabled
    workflows_enabled = Column(JSON, default={})  # Track which workflows are active
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

### 2. Pydantic Schemas

Update validation schemas:

```python
# backend/app/schemas.py

class BusinessTypeEnum(str, Enum):
    HVAC = "hvac"
    ELECTRICAL = "electrical"
    # ... all other types

class OrganizationCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    business_type: BusinessTypeEnum
    timezone: str = "America/New_York"
    locale: str = "en_US"
    
    class Config:
        use_enum_values = True

class OrganizationRead(BaseModel):
    id: UUID
    name: str
    business_type: str
    industry_category: str
    timezone: str
    created_at: datetime
    
    class Config:
        from_attributes = True
```

### 3. Industry Configuration Files

Create industry-specific configuration:

```python
# backend/app/industry_config.py

INDUSTRY_CONFIGS = {
    "hvac": {
        "category": "service",
        "display_name": "HVAC Services",
        "system_prompt_template": """You are an AI assistant for an HVAC (Heating, Ventilation, and Air Conditioning) service company.
        
Your role is to:
1. Schedule appointments for AC/heating repairs, maintenance, and installations
2. Answer questions about HVAC services
3. Provide emergency service information
4. Collect customer information (address, phone, service type needed)
5. Suggest maintenance services

Be professional, helpful, and efficient. Keep responses concise for voice calls.""",
        
        "intents": [
            "schedule_service",
            "emergency_repair",
            "routine_maintenance",
            "installation_inquiry",
            "warranty_question",
        ],
        
        "custom_fields": {
            "Contact": ["service_address", "home_type", "system_type", "last_service_date"],
            "Deal": ["service_type", "estimated_cost", "warranty_included"],
        },
        
        "features": [
            "appointment_scheduling",
            "emergency_dispatch",
            "maintenance_reminders",
            "warranty_tracking",
            "service_history",
        ],
        
        "suggested_workflows": [
            "appointment_confirmation_sms",
            "service_reminder_24h",
            "post_service_followup",
            "maintenance_schedule",
        ],
        
        "default_service_types": [
            "AC Repair",
            "Heating Repair",
            "Maintenance",
            "Installation",
            "Emergency Service",
        ],
    },
    
    "restaurant": {
        "category": "retail",
        "display_name": "Restaurant",
        "system_prompt_template": """You are an AI assistant for a restaurant.
        
Your role is to:
1. Take reservations and manage seating
2. Answer questions about menu items
3. Provide operating hours and location information
4. Handle special requests
5. Process takeout and delivery orders (if applicable)

Be friendly, professional, and efficient.""",
        
        "intents": [
            "make_reservation",
            "order_takeout",
            "menu_inquiry",
            "hours_location",
            "special_request",
        ],
        
        "custom_fields": {
            "Contact": ["dietary_restrictions", "preferred_seating", "vip_status"],
            "Deal": ["party_size", "reservation_date", "special_occasion"],
        },
        
        "features": [
            "reservation_management",
            "table_tracking",
            "menu_delivery",
            "order_taking",
            "waitlist_management",
        ],
        
        "suggested_workflows": [
            "reservation_confirmation",
            "ready_notification",
            "loyalty_program",
            "feedback_request",
        ],
    },
    
    "hotel": {
        "category": "hospitality",
        "display_name": "Hotel",
        "system_prompt_template": """You are an AI assistant for a hotel.
        
Your role is to:
1. Make and manage room reservations
2. Answer questions about amenities
3. Provide information about local attractions
4. Handle special requests
5. Assist with check-in/check-out questions

Be welcoming, professional, and helpful.""",
        
        "intents": [
            "book_room",
            "amenities_inquiry",
            "local_attractions",
            "special_request",
            "checkin_checkout",
        ],
        
        "custom_fields": {
            "Contact": ["loyalty_member", "preferences", "vip_status"],
            "Deal": ["room_type", "check_in_date", "check_out_date", "guests"],
        },
        
        "features": [
            "room_booking",
            "amenity_info",
            "concierge_service",
            "loyalty_program",
            "special_request_handling",
        ],
        
        "suggested_workflows": [
            "booking_confirmation",
            "welcome_message",
            "checkout_reminder",
            "feedback_survey",
        ],
    },
    
    # Add more industries...
}

def get_industry_config(business_type: str) -> dict:
    """Get configuration for a business type"""
    return INDUSTRY_CONFIGS.get(business_type, INDUSTRY_CONFIGS["hvac"])

def get_system_prompt(business_type: str, organization_name: str) -> str:
    """Get customized system prompt for an organization"""
    config = get_industry_config(business_type)
    template = config["system_prompt_template"]
    return template.replace("{company_name}", organization_name)
```

### 4. Onboarding Flow

Update signup/onboarding to include business type:

```python
# backend/app/routes.py

@router.post("/auth/signup")
async def signup(request: UserCreate, db: AsyncSession = Depends(get_db)):
    """
    Signup with business type selection
    
    Request body:
    {
        "email": "user@example.com",
        "password": "SecurePassword123!",
        "first_name": "John",
        "last_name": "Doe",
        "org_name": "My HVAC Business",
        "business_type": "hvac"
    }
    """
    
    # Create organization with business type
    organization = Organization(
        name=request.org_name,
        business_type=request.business_type,
        industry_category=INDUSTRY_CONFIGS[request.business_type]["category"],
    )
    
    db.add(organization)
    await db.commit()
    
    # Create user
    user = User(
        email=request.email,
        password=hash_password(request.password),
        first_name=request.first_name,
        last_name=request.last_name,
        organization_id=organization.id,
        role="OWNER",
    )
    
    db.add(user)
    await db.commit()
    
    return {"message": "Signup successful", "organization_id": str(organization.id)}

@router.get("/api/v1/business-types")
async def get_business_types():
    """Get list of supported business types for dropdown"""
    
    business_types = []
    for business_type, config in INDUSTRY_CONFIGS.items():
        business_types.append({
            "value": business_type,
            "label": config["display_name"],
            "category": config["category"],
            "description": config.get("description", ""),
        })
    
    return {
        "business_types": sorted(business_types, key=lambda x: x["label"]),
        "total": len(business_types),
    }
```

### 5. Frontend Onboarding UI

Update signup form to include business type dropdown:

```typescript
// frontend/app/auth/signup/page.tsx

export default function SignupPage() {
  const [formData, setFormData] = useState({
    email: "",
    password: "",
    firstName: "",
    lastName: "",
    orgName: "",
    businessType: "hvac",
  });
  
  const [businessTypes, setBusinessTypes] = useState([]);
  
  useEffect(() => {
    // Fetch business types
    fetch("/api/v1/business-types")
      .then(res => res.json())
      .then(data => setBusinessTypes(data.business_types));
  }, []);
  
  return (
    <div className="signup-form">
      <h1>Create Your Account</h1>
      
      <input
        type="email"
        placeholder="Email"
        value={formData.email}
        onChange={(e) => setFormData({...formData, email: e.target.value})}
      />
      
      <input
        type="text"
        placeholder="First Name"
        value={formData.firstName}
        onChange={(e) => setFormData({...formData, firstName: e.target.value})}
      />
      
      <input
        type="text"
        placeholder="Last Name"
        value={formData.lastName}
        onChange={(e) => setFormData({...formData, lastName: e.target.value})}
      />
      
      <input
        type="text"
        placeholder="Business Name"
        value={formData.orgName}
        onChange={(e) => setFormData({...formData, orgName: e.target.value})}
      />
      
      <select
        value={formData.businessType}
        onChange={(e) => setFormData({...formData, businessType: e.target.value})}
      >
        <option value="">Select Your Business Type</option>
        {businessTypes.map(bt => (
          <optgroup key={bt.category} label={bt.category.toUpperCase()}>
            <option value={bt.value}>{bt.label}</option>
          </optgroup>
        ))}
      </select>
      
      <button onClick={handleSignup}>Sign Up</button>
    </div>
  );
}
```

### 6. Mobile Onboarding

```typescript
// mobile/app/screens/auth/SignupScreen.tsx

export default function SignupScreen() {
  const [businessType, setBusinessType] = useState("hvac");
  const [businessTypes, setBusinessTypes] = useState([]);
  
  useEffect(() => {
    fetchBusinessTypes();
  }, []);
  
  const fetchBusinessTypes = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/v1/business-types`);
      const data = await response.json();
      setBusinessTypes(data.business_types);
    } catch (error) {
      console.error("Error fetching business types:", error);
    }
  };
  
  return (
    <SafeAreaView style={styles.container}>
      <ScrollView>
        <Text style={styles.title}>Select Your Business Type</Text>
        
        <Picker
          selectedValue={businessType}
          onValueChange={setBusinessType}
          style={styles.picker}
        >
          {businessTypes.map(bt => (
            <Picker.Item key={bt.value} label={bt.label} value={bt.value} />
          ))}
        </Picker>
        
        <TouchableOpacity style={styles.button} onPress={handleSignup}>
          <Text style={styles.buttonText}>Continue</Text>
        </TouchableOpacity>
      </ScrollView>
    </SafeAreaView>
  );
}
```

### 7. Onboarding Wizard Component

Create a multi-step onboarding wizard:

```typescript
// frontend/app/onboarding/page.tsx

export default function OnboardingWizard() {
  const [step, setStep] = useState(1);
  const [businessType, setBusinessType] = useState("");
  const [config, setConfig] = useState(null);
  
  const handleBusinessTypeSelect = (type) => {
    setBusinessType(type);
    // Load industry config
    fetch(`/api/v1/industry-config/${type}`)
      .then(res => res.json())
      .then(data => setConfig(data));
    setStep(2);
  };
  
  return (
    <div className="onboarding-wizard">
      {step === 1 && (
        <BusinessTypeSelector onSelect={handleBusinessTypeSelect} />
      )}
      
      {step === 2 && config && (
        <FeatureSetup config={config} onNext={() => setStep(3)} />
      )}
      
      {step === 3 && config && (
        <WorkflowSetup config={config} onNext={() => setStep(4)} />
      )}
      
      {step === 4 && config && (
        <CustomFieldsSetup config={config} onComplete={() => completeOnboarding()} />
      )}
    </div>
  );
}
```

---

## Industry-Specific Features

### HVAC Services
- Emergency dispatch routing
- Service history tracking
- Warranty management
- Maintenance scheduling
- System type classification

### Restaurants
- Reservation management
- Table availability tracking
- Menu delivery
- Special requests handling
- Takeout order management

### Hotels
- Room type availability
- Check-in/check-out management
- Amenity information
- Concierge requests
- Guest preferences tracking

### Retail Stores
- Product inventory
- Store location info
- Hours management
- Stock inquiries
- Special order handling

### Professional Services (Law, Accounting, etc.)
- Appointment scheduling
- Document delivery
- Confidential communication
- Case/matter tracking
- Billable hours tracking

---

## API Endpoints for Industry Support

```
GET  /api/v1/business-types                    # List all business types
POST /api/v1/organizations                     # Create org with business type
GET  /api/v1/industry-config/{business_type}  # Get industry configuration
PUT  /api/v1/organizations/{org_id}/business-type  # Change business type
GET  /api/v1/organizations/{org_id}/features  # Get enabled features
POST /api/v1/organizations/{org_id}/features  # Enable/disable features
GET  /api/v1/organizations/{org_id}/workflows # Get available workflows
POST /api/v1/organizations/{org_id}/workflows # Enable/disable workflows
```

---

## Database Migration

Add business_type field:

```sql
-- Migration: add_business_type_to_organizations

ALTER TABLE organizations ADD COLUMN business_type VARCHAR(50) DEFAULT 'general_contractor';
ALTER TABLE organizations ADD COLUMN industry_category VARCHAR(50) DEFAULT 'service';
ALTER TABLE organizations ADD COLUMN custom_fields JSON DEFAULT '{}';
ALTER TABLE organizations ADD COLUMN features_enabled JSON DEFAULT '{}';
ALTER TABLE organizations ADD COLUMN workflows_enabled JSON DEFAULT '{}';

CREATE INDEX idx_organizations_business_type ON organizations(business_type);
CREATE INDEX idx_organizations_industry_category ON organizations(industry_category);
```

---

## Testing

Test business type selection:

```python
# backend/tests/test_business_types.py

def test_signup_with_business_type():
    """Test signup with business type"""
    response = client.post(
        "/auth/signup",
        json={
            "email": "hvac@example.com",
            "password": "SecurePassword123!",
            "first_name": "John",
            "last_name": "Doe",
            "org_name": "HVAC Pro",
            "business_type": "hvac",
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["organization"]["business_type"] == "hvac"
    assert data["organization"]["industry_category"] == "service"

def test_get_business_types():
    """Test fetching business types"""
    response = client.get("/api/v1/business-types")
    
    assert response.status_code == 200
    data = response.json()
    assert "business_types" in data
    assert len(data["business_types"]) > 0
    assert "hvac" in [bt["value"] for bt in data["business_types"]]
```

---

## Implementation Checklist

### Phase 1: Data Model & API (Week 1)
- [ ] Add `business_type` to Organization model
- [ ] Create industry configuration dictionary
- [ ] Create API endpoints for business types
- [ ] Create database migration
- [ ] Update Pydantic schemas

### Phase 2: Backend Implementation (Week 2)
- [ ] Update signup flow to accept business_type
- [ ] Update AI system prompt generation
- [ ] Create industry-specific conversation templates
- [ ] Implement feature toggle system
- [ ] Add industry config endpoint

### Phase 3: Frontend Implementation (Week 3)
- [ ] Update signup form with business type dropdown
- [ ] Create onboarding wizard
- [ ] Add business type selector
- [ ] Create feature setup screens
- [ ] Add workflow selector

### Phase 4: Mobile Implementation (Week 3)
- [ ] Update React Native signup
- [ ] Add business type picker
- [ ] Implement onboarding screens
- [ ] Add industry-specific features

### Phase 5: Testing & Documentation (Week 4)
- [ ] Unit tests for business types
- [ ] Integration tests for onboarding
- [ ] E2E tests for signup flow
- [ ] Update API documentation
- [ ] Create industry-specific guides

---

## Usage Example

### Customer Signing Up (HVAC Business)

1. **Visit platform** → Click "Sign Up"
2. **Enter email/password**
3. **Enter business name** → "John's HVAC Services"
4. **Select business type** → Dropdown shows categories:
   - **SERVICE** (HVAC, Electrical, Plumbing, etc.)
   - **RETAIL** (Restaurant, Salon, Gym, etc.)
   - **PROFESSIONAL** (Law, Medical, Accounting, etc.)
   - **HOSPITALITY** (Hotel, Event Venue, etc.)
5. **Select HVAC** from SERVICE category
6. **System automatically:**
   - Sets up HVAC-specific conversation templates
   - Enables HVAC features (emergency dispatch, service history, etc.)
   - Configures custom fields (service address, system type, etc.)
   - Suggests relevant workflows
7. **Onboarding wizard guides through:**
   - Feature enablement
   - Workflow setup
   - Custom field configuration
8. **User completes setup** → Ready to use HVAC-specific features

### Customer Signing Up (Hotel Business)

Same process but:
- Selects "Hotel" from HOSPITALITY category
- Gets hotel-specific features (room booking, amenities, concierge)
- Different conversation templates
- Different custom fields (room type, check-in date, guests, etc.)

---

## Changing Business Type

Customers can change business type after signup:

```
Settings → Organization → Business Type → Select New Type
```

System will:
- Migrate features
- Update conversation templates
- Suggest new workflows
- Preserve existing data

---

## Conclusion

The AI Voice & SMS platform is **fully ready for multi-industry support** with:
- ✅ Generic core system
- ✅ Industry-specific configurations
- ✅ Customizable features per industry
- ✅ Dynamic conversation templates
- ✅ Flexible workflow system
- ✅ Onboarding wizard with business type selection

Implementation can be done incrementally, starting with the most popular industries (HVAC, Restaurant, Hotel) and expanding to others based on demand.
