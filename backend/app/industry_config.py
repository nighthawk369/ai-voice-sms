"""Industry-specific configurations for different business types"""

from enum import Enum

INDUSTRY_CONFIGS = {
    "hvac": {
        "category": "service",
        "display_name": "HVAC Services",
        "description": "Heating, Ventilation, and Air Conditioning services",
        "system_prompt": """You are an AI assistant for an HVAC (Heating, Ventilation, and Air Conditioning) service company.

Your role is to:
1. Schedule appointments for AC/heating repairs, maintenance, and installations
2. Answer questions about HVAC services
3. Provide emergency service information
4. Collect customer information (address, phone, service type needed)
5. Suggest maintenance services

Be professional, helpful, and efficient. Keep responses concise for voice calls.""",
        "custom_fields": {
            "Contact": ["service_address", "home_type", "system_type", "last_service_date"],
            "Deal": ["service_type", "estimated_cost", "warranty_included"],
        },
        "features": ["appointment_scheduling", "emergency_dispatch", "maintenance_reminders", "warranty_tracking"],
        "intents": ["schedule_service", "emergency_repair", "routine_maintenance", "installation_inquiry"],
    },

    "electrical": {
        "category": "service",
        "display_name": "Electrical Services",
        "description": "Electrical installation, repair, and maintenance",
        "system_prompt": """You are an AI assistant for an electrical service company.

Your role is to:
1. Schedule electrical repair and installation appointments
2. Answer safety questions about electrical systems
3. Provide emergency service information
4. Collect customer information and service requirements
5. Suggest preventive maintenance

Be professional, safety-conscious, and efficient.""",
        "custom_fields": {
            "Contact": ["service_address", "property_type", "panel_size", "last_service_date"],
            "Deal": ["service_type", "panel_upgrade", "warranty"],
        },
        "features": ["appointment_scheduling", "emergency_dispatch", "safety_compliance"],
        "intents": ["schedule_service", "emergency_repair", "installation_inquiry", "safety_question"],
    },

    "plumbing": {
        "category": "service",
        "display_name": "Plumbing Services",
        "description": "Plumbing repair, installation, and maintenance",
        "system_prompt": """You are an AI assistant for a plumbing service company.

Your role is to:
1. Schedule plumbing repair and installation appointments
2. Provide emergency plumbing information
3. Collect customer information (address, issue description)
4. Suggest preventive maintenance
5. Answer common plumbing questions

Be professional, helpful, and clear about urgency levels.""",
        "custom_fields": {
            "Contact": ["service_address", "property_type", "pipe_type", "last_service_date"],
            "Deal": ["service_type", "emergency_level", "warranty"],
        },
        "features": ["appointment_scheduling", "emergency_dispatch", "water_damage_support"],
        "intents": ["schedule_service", "emergency_repair", "installation_inquiry", "preventive_maintenance"],
    },

    "restaurant": {
        "category": "retail",
        "display_name": "Restaurant",
        "description": "Restaurant reservation and order management",
        "system_prompt": """You are an AI assistant for a restaurant.

Your role is to:
1. Take reservations and manage seating
2. Answer questions about menu items and availability
3. Provide operating hours and location information
4. Handle special requests (dietary restrictions, occasions)
5. Process takeout orders if applicable

Be friendly, professional, and efficient.""",
        "custom_fields": {
            "Contact": ["dietary_restrictions", "preferred_seating", "vip_status"],
            "Deal": ["party_size", "reservation_date", "special_occasion", "dietary_notes"],
        },
        "features": ["reservation_management", "menu_delivery", "order_taking", "waitlist_management"],
        "intents": ["make_reservation", "order_takeout", "menu_inquiry", "hours_location"],
    },

    "hotel": {
        "category": "hospitality",
        "display_name": "Hotel",
        "description": "Hotel room reservations and guest services",
        "system_prompt": """You are an AI assistant for a hotel.

Your role is to:
1. Make and manage room reservations
2. Answer questions about room types and amenities
3. Provide information about local attractions
4. Handle special requests (accessible rooms, views, amenities)
5. Assist with check-in/check-out information

Be welcoming, professional, and helpful.""",
        "custom_fields": {
            "Contact": ["loyalty_member", "preferred_room_type", "vip_status"],
            "Deal": ["room_type", "check_in_date", "check_out_date", "number_of_guests", "special_requests"],
        },
        "features": ["room_booking", "amenity_info", "concierge_service", "loyalty_program"],
        "intents": ["book_room", "amenities_inquiry", "local_attractions", "special_request"],
    },

    "salon": {
        "category": "retail",
        "display_name": "Salon & Spa",
        "description": "Hair, beauty, and spa services",
        "system_prompt": """You are an AI assistant for a salon and spa.

Your role is to:
1. Schedule appointments for hair, beauty, and spa services
2. Answer questions about services and treatments
3. Provide pricing information
4. Handle special requests (hair color consultation, allergies, preferences)
5. Manage cancellations and rescheduling

Be friendly, professional, and attentive to customer preferences.""",
        "custom_fields": {
            "Contact": ["preferred_stylist", "hair_type", "allergies", "previous_services"],
            "Deal": ["service_type", "duration", "specialist_required", "special_requests"],
        },
        "features": ["appointment_scheduling", "stylist_matching", "service_history"],
        "intents": ["book_appointment", "service_inquiry", "pricing_question", "specialist_request"],
    },

    "gym": {
        "category": "retail",
        "display_name": "Gym & Fitness",
        "description": "Fitness center memberships and classes",
        "system_prompt": """You are an AI assistant for a gym and fitness center.

Your role is to:
1. Provide membership information and pricing
2. Answer questions about classes and schedules
3. Schedule personal training sessions
4. Provide fitness advice (general information)
5. Handle membership inquiries

Be motivating, helpful, and knowledgeable about fitness.""",
        "custom_fields": {
            "Contact": ["fitness_level", "goals", "preferred_classes", "trainer_preference"],
            "Deal": ["membership_type", "duration", "classes_included", "trainer_sessions"],
        },
        "features": ["membership_management", "class_scheduling", "trainer_booking"],
        "intents": ["membership_inquiry", "class_schedule", "personal_training", "fitness_question"],
    },

    "law_firm": {
        "category": "professional",
        "display_name": "Law Firm",
        "description": "Legal services and case management",
        "system_prompt": """You are an AI assistant for a law firm.

Your role is to:
1. Schedule initial consultations
2. Provide general information about practice areas
3. Handle confidential client communication
4. Collect case information
5. Follow up on document requests

Be professional, confidential, and detail-oriented. Maintain attorney-client confidentiality.""",
        "custom_fields": {
            "Contact": ["case_type", "confidentiality_level", "attorney_assigned"],
            "Deal": ["matter_type", "case_status", "next_hearing_date", "billing_rate"],
        },
        "features": ["appointment_scheduling", "confidential_communication", "case_tracking"],
        "intents": ["schedule_consultation", "case_inquiry", "document_request", "legal_question"],
    },

    "medical": {
        "category": "professional",
        "display_name": "Medical Office",
        "description": "Medical practice and patient appointments",
        "system_prompt": """You are an AI assistant for a medical office.

Your role is to:
1. Schedule patient appointments
2. Answer questions about services offered
3. Collect patient information (HIPAA compliant)
4. Provide office hours and location information
5. Handle appointment reminders and cancellations

Be professional, empathetic, and HIPAA-compliant. Maintain patient privacy at all times.""",
        "custom_fields": {
            "Contact": ["patient_id", "insurance_info", "emergency_contact", "medical_history_consent"],
            "Deal": ["appointment_type", "doctor_preference", "visit_reason", "insurance_verified"],
        },
        "features": ["appointment_scheduling", "patient_information", "insurance_verification"],
        "intents": ["schedule_appointment", "service_inquiry", "patient_information", "insurance_question"],
    },

    "real_estate": {
        "category": "real_estate",
        "display_name": "Real Estate Agency",
        "description": "Property sales and leasing",
        "system_prompt": """You are an AI assistant for a real estate agency.

Your role is to:
1. Schedule property showings
2. Answer questions about available properties
3. Provide property details and pricing
4. Collect buyer/renter information
5. Handle inquiries about neighborhoods

Be knowledgeable, helpful, and professional.""",
        "custom_fields": {
            "Contact": ["buyer_status", "budget_range", "property_interests"],
            "Deal": ["property_address", "list_price", "showing_date", "offer_status"],
        },
        "features": ["property_listing", "showing_scheduling", "neighborhood_info"],
        "intents": ["schedule_showing", "property_inquiry", "neighborhood_question", "buyer_inquiry"],
    },
}


def get_business_type_display_name(business_type: str) -> str:
    """Get display name for business type"""
    config = INDUSTRY_CONFIGS.get(business_type)
    return config["display_name"] if config else business_type


def get_industry_category(business_type: str) -> str:
    """Get industry category for business type"""
    config = INDUSTRY_CONFIGS.get(business_type)
    return config["category"] if config else "service"


def get_system_prompt(business_type: str, organization_name: str = None) -> str:
    """Get customized system prompt for a business type"""
    config = INDUSTRY_CONFIGS.get(business_type)
    if not config:
        return f"You are an AI assistant for {organization_name or 'a business'}."

    prompt = config["system_prompt"]
    if organization_name:
        prompt = prompt.replace("a salon", f"{organization_name}")
        prompt = prompt.replace("a gym", f"{organization_name}")
        prompt = prompt.replace("a restaurant", f"{organization_name}")
        prompt = prompt.replace("a hotel", f"{organization_name}")
        prompt = prompt.replace("a law firm", f"{organization_name}")
        prompt = prompt.replace("a medical office", f"{organization_name}")
        prompt = prompt.replace("a real estate agency", f"{organization_name}")
        prompt = prompt.replace("an HVAC", f"{organization_name}'s HVAC")
        prompt = prompt.replace("an electrical", f"{organization_name}'s electrical")

    return prompt


def get_custom_fields(business_type: str) -> dict:
    """Get custom fields for a business type"""
    config = INDUSTRY_CONFIGS.get(business_type)
    return config.get("custom_fields", {}) if config else {}


def get_features(business_type: str) -> list:
    """Get features for a business type"""
    config = INDUSTRY_CONFIGS.get(business_type)
    return config.get("features", []) if config else []


def get_intents(business_type: str) -> list:
    """Get intents for a business type"""
    config = INDUSTRY_CONFIGS.get(business_type)
    return config.get("intents", []) if config else []


def get_all_business_types() -> list:
    """Get all supported business types as list of dicts"""
    business_types = []
    seen_categories = set()

    for business_type, config in sorted(INDUSTRY_CONFIGS.items()):
        business_types.append({
            "value": business_type,
            "label": config["display_name"],
            "category": config["category"],
            "description": config.get("description", ""),
        })
        seen_categories.add(config["category"])

    return sorted(business_types, key=lambda x: (x["category"], x["label"]))
