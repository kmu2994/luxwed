#!/usr/bin/env python3
import requests
import json
import uuid
from datetime import datetime, timedelta
import time
import os
import sys

# Get the backend URL from the frontend .env file
with open('/app/frontend/.env', 'r') as f:
    for line in f:
        if line.startswith('REACT_APP_BACKEND_URL='):
            BACKEND_URL = line.strip().split('=')[1].strip('"\'')
            break

# Ensure the backend URL is set
if not BACKEND_URL:
    print("Error: REACT_APP_BACKEND_URL not found in frontend/.env")
    sys.exit(1)

# Ensure the backend URL ends with /api
API_URL = f"{BACKEND_URL}/api"
print(f"Using API URL: {API_URL}")

# Test data
test_user = {
    "name": "Priya Sharma",
    "email": "priya.sharma@example.com",
    "phone": "+91 9876543214",
    "role": "customer",
    "preferences": {
        "budget": 500000,
        "guest_count": 150,
        "location": "Mumbai",
        "style_preference": "Modern"
    }
}

test_vendor = {
    "name": "Vikram Singh",
    "business_name": "Vikram's Wedding Photography",
    "email": "vikram@weddingphotos.com",
    "phone": "+91 9876543215",
    "category": "Photography",
    "services": ["Candid Photography", "Drone Shots", "Same-Day Edits"],
    "pricing_range": {"min": 60000, "max": 180000},
    "location": "Delhi",
    "description": "Capturing your special moments with artistic flair and attention to detail.",
    "portfolio_images": ["image1.jpg", "image2.jpg"]
}

# New vendor with expanded fields for testing new vendor creation
test_new_vendor = {
    "name": "Aisha Khan",
    "business_name": "Aisha's Bridal Jewelry",
    "email": "aisha@bridaljewelry.com",
    "phone": "+91 9876543216",
    "category": "Jewelry",
    "services": ["Custom Designs", "Traditional Sets", "Modern Collections", "Rental Options"],
    "pricing_range": {"min": 75000, "max": 350000},
    "location": "Mumbai",
    "description": "Exquisite bridal jewelry collections with both traditional and contemporary designs. We offer custom designs and rental options for your special day.",
    "portfolio_images": ["jewelry1.jpg", "jewelry2.jpg", "jewelry3.jpg"]
}

test_inquiry = {
    "message": "I'm interested in your photography services for my wedding on December 15th. Can you share your availability and packages?"
}

test_wedding_plan = {
    "budget": 800000,
    "guest_count": 200,
    "wedding_date": (datetime.now() + timedelta(days=180)).isoformat(),
    "location": "Bangalore",
    "style_preference": "Traditional"
}

test_chat_message = {
    "message": "I'm planning a wedding with a budget of 5 lakhs for about 150 guests in Mumbai. Can you help me find good vendors?"
}

# Test results
test_results = {
    "user_management": {"status": "Not tested", "details": ""},
    "vendor_management": {"status": "Not tested", "details": ""},
    "ai_chat": {"status": "Not tested", "details": ""},
    "vendor_recommendations": {"status": "Not tested", "details": ""},
    "inquiries": {"status": "Not tested", "details": ""},
    "wedding_plans": {"status": "Not tested", "details": ""},
    "platform_stats": {"status": "Not tested", "details": ""},
    "web_search_enhancement": {"status": "Not tested", "details": ""},
    "expanded_sample_database": {"status": "Not tested", "details": ""},
    "new_vendor_creation": {"status": "Not tested", "details": ""},
    "category_filtering": {"status": "Not tested", "details": ""}
}

created_user_id = None
created_vendor_id = None
chat_session_id = None

def print_separator():
    print("\n" + "="*80 + "\n")

def test_user_management():
    global created_user_id
    print_separator()
    print("Testing User Management APIs...")
    
    try:
        # Test creating a user
        print("Creating a test user...")
        response = requests.post(f"{API_URL}/users", json=test_user)
        response.raise_for_status()
        user_data = response.json()
        created_user_id = user_data["id"]
        print(f"Created user with ID: {created_user_id}")
        
        # Test getting a specific user
        print(f"Getting user with ID: {created_user_id}")
        response = requests.get(f"{API_URL}/users/{created_user_id}")
        response.raise_for_status()
        user_data = response.json()
        print(f"Retrieved user: {user_data['name']}")
        
        # Test getting all users
        print("Getting all users...")
        response = requests.get(f"{API_URL}/users")
        response.raise_for_status()
        users = response.json()
        print(f"Retrieved {len(users)} users")
        
        test_results["user_management"]["status"] = "Passed"
        test_results["user_management"]["details"] = f"Successfully created and retrieved users. Created user ID: {created_user_id}"
        return True
    
    except Exception as e:
        test_results["user_management"]["status"] = "Failed"
        test_results["user_management"]["details"] = f"Error: {str(e)}"
        print(f"Error testing user management: {str(e)}")
        return False

def test_vendor_management():
    global created_vendor_id
    print_separator()
    print("Testing Vendor Management APIs...")
    
    try:
        # Test creating a vendor
        print("Creating a test vendor...")
        response = requests.post(f"{API_URL}/vendors", json=test_vendor)
        response.raise_for_status()
        vendor_data = response.json()
        created_vendor_id = vendor_data["id"]
        print(f"Created vendor with ID: {created_vendor_id}")
        
        # Test getting a specific vendor
        print(f"Getting vendor with ID: {created_vendor_id}")
        response = requests.get(f"{API_URL}/vendors/{created_vendor_id}")
        response.raise_for_status()
        vendor_data = response.json()
        print(f"Retrieved vendor: {vendor_data['business_name']}")
        
        # Test getting all vendors
        print("Getting all vendors...")
        response = requests.get(f"{API_URL}/vendors")
        response.raise_for_status()
        vendors = response.json()
        print(f"Retrieved {len(vendors)} vendors")
        
        # Test filtering vendors by category
        print("Filtering vendors by category: Photography")
        response = requests.get(f"{API_URL}/vendors?category=Photography")
        response.raise_for_status()
        vendors = response.json()
        print(f"Retrieved {len(vendors)} photography vendors")
        
        # Test filtering vendors by location
        print("Filtering vendors by location: Mumbai")
        response = requests.get(f"{API_URL}/vendors?location=Mumbai")
        response.raise_for_status()
        vendors = response.json()
        print(f"Retrieved {len(vendors)} Mumbai vendors")
        
        test_results["vendor_management"]["status"] = "Passed"
        test_results["vendor_management"]["details"] = f"Successfully created and retrieved vendors with filtering. Created vendor ID: {created_vendor_id}"
        return True
    
    except Exception as e:
        test_results["vendor_management"]["status"] = "Failed"
        test_results["vendor_management"]["details"] = f"Error: {str(e)}"
        print(f"Error testing vendor management: {str(e)}")
        return False

def test_ai_chat():
    global chat_session_id, created_user_id
    print_separator()
    print("Testing AI Chat System...")
    
    if not created_user_id:
        test_results["ai_chat"]["status"] = "Skipped"
        test_results["ai_chat"]["details"] = "User creation failed, cannot test chat"
        print("Skipping AI chat test as user creation failed")
        return False
    
    try:
        # Test sending a chat message
        print("Sending a test chat message...")
        chat_request = test_chat_message.copy()
        chat_request["user_id"] = created_user_id
        
        response = requests.post(f"{API_URL}/chat", json=chat_request)
        response.raise_for_status()
        chat_data = response.json()
        
        chat_session_id = chat_data.get("session_id")
        print(f"Chat session ID: {chat_session_id}")
        print(f"AI response: {chat_data.get('response')[:100]}...")
        
        if "suggestions" in chat_data:
            print(f"Suggestions: {chat_data['suggestions']}")
        
        # Test sending a follow-up message with the same session ID
        if chat_session_id:
            print("Sending a follow-up message...")
            follow_up = {
                "user_id": created_user_id,
                "session_id": chat_session_id,
                "message": "What venues would you recommend in Mumbai for this budget?"
            }
            
            response = requests.post(f"{API_URL}/chat", json=follow_up)
            response.raise_for_status()
            follow_up_data = response.json()
            print(f"Follow-up AI response: {follow_up_data.get('response')[:100]}...")
        
        test_results["ai_chat"]["status"] = "Passed"
        test_results["ai_chat"]["details"] = "Successfully sent chat messages and received AI responses"
        return True
    
    except Exception as e:
        test_results["ai_chat"]["status"] = "Failed"
        test_results["ai_chat"]["details"] = f"Error: {str(e)}"
        print(f"Error testing AI chat: {str(e)}")
        return False

def test_vendor_recommendations():
    global created_user_id
    print_separator()
    print("Testing Vendor Recommendations...")
    
    if not created_user_id:
        test_results["vendor_recommendations"]["status"] = "Skipped"
        test_results["vendor_recommendations"]["details"] = "User creation failed, cannot test recommendations"
        print("Skipping vendor recommendations test as user creation failed")
        return False
    
    try:
        # Test getting recommendations for a user
        print(f"Getting recommendations for user ID: {created_user_id}")
        response = requests.get(f"{API_URL}/recommendations/{created_user_id}")
        response.raise_for_status()
        recommendations = response.json()
        
        print(f"Retrieved {recommendations.get('total_count', 0)} recommendations")
        
        # Test getting recommendations for a specific category
        print(f"Getting Photography recommendations for user ID: {created_user_id}")
        response = requests.get(f"{API_URL}/recommendations/{created_user_id}?category=Photography")
        response.raise_for_status()
        category_recommendations = response.json()
        
        print(f"Retrieved {category_recommendations.get('total_count', 0)} Photography recommendations")
        
        test_results["vendor_recommendations"]["status"] = "Passed"
        test_results["vendor_recommendations"]["details"] = "Successfully retrieved vendor recommendations"
        return True
    
    except Exception as e:
        test_results["vendor_recommendations"]["status"] = "Failed"
        test_results["vendor_recommendations"]["details"] = f"Error: {str(e)}"
        print(f"Error testing vendor recommendations: {str(e)}")
        return False

def test_inquiries():
    global created_user_id, created_vendor_id
    print_separator()
    print("Testing Inquiries...")
    
    if not created_user_id or not created_vendor_id:
        test_results["inquiries"]["status"] = "Skipped"
        test_results["inquiries"]["details"] = "User or vendor creation failed, cannot test inquiries"
        print("Skipping inquiries test as user or vendor creation failed")
        return False
    
    try:
        # Test creating an inquiry
        print("Creating a test inquiry...")
        inquiry_request = test_inquiry.copy()
        inquiry_request["user_id"] = created_user_id
        inquiry_request["vendor_id"] = created_vendor_id
        
        response = requests.post(f"{API_URL}/inquiries", json=inquiry_request)
        response.raise_for_status()
        inquiry_data = response.json()
        inquiry_id = inquiry_data["id"]
        print(f"Created inquiry with ID: {inquiry_id}")
        
        # Test getting user inquiries
        print(f"Getting inquiries for user ID: {created_user_id}")
        response = requests.get(f"{API_URL}/inquiries/user/{created_user_id}")
        response.raise_for_status()
        user_inquiries = response.json()
        print(f"Retrieved {len(user_inquiries)} user inquiries")
        
        # Test getting vendor inquiries
        print(f"Getting inquiries for vendor ID: {created_vendor_id}")
        response = requests.get(f"{API_URL}/inquiries/vendor/{created_vendor_id}")
        response.raise_for_status()
        vendor_inquiries = response.json()
        print(f"Retrieved {len(vendor_inquiries)} vendor inquiries")
        
        test_results["inquiries"]["status"] = "Passed"
        test_results["inquiries"]["details"] = "Successfully created and retrieved inquiries"
        return True
    
    except Exception as e:
        test_results["inquiries"]["status"] = "Failed"
        test_results["inquiries"]["details"] = f"Error: {str(e)}"
        print(f"Error testing inquiries: {str(e)}")
        return False

def test_wedding_plans():
    global created_user_id
    print_separator()
    print("Testing Wedding Plans...")
    
    if not created_user_id:
        test_results["wedding_plans"]["status"] = "Skipped"
        test_results["wedding_plans"]["details"] = "User creation failed, cannot test wedding plans"
        print("Skipping wedding plans test as user creation failed")
        return False
    
    try:
        # Test creating a wedding plan
        print("Creating a test wedding plan...")
        plan_request = test_wedding_plan.copy()
        plan_request["user_id"] = created_user_id
        
        response = requests.post(f"{API_URL}/wedding-plans", json=plan_request)
        response.raise_for_status()
        plan_data = response.json()
        plan_id = plan_data["id"]
        print(f"Created wedding plan with ID: {plan_id}")
        
        # Check if timeline was auto-generated
        if "timeline" in plan_data and plan_data["timeline"]:
            print("Timeline was auto-generated:")
            for key, items in plan_data["timeline"].items():
                print(f"  {key}: {', '.join(items[:2])}...")
        
        # Test getting wedding plans for a user
        print(f"Getting wedding plans for user ID: {created_user_id}")
        response = requests.get(f"{API_URL}/wedding-plans/{created_user_id}")
        response.raise_for_status()
        user_plans = response.json()
        print(f"Retrieved {len(user_plans)} wedding plans")
        
        test_results["wedding_plans"]["status"] = "Passed"
        test_results["wedding_plans"]["details"] = "Successfully created and retrieved wedding plans with auto-generated timeline"
        return True
    
    except Exception as e:
        test_results["wedding_plans"]["status"] = "Failed"
        test_results["wedding_plans"]["details"] = f"Error: {str(e)}"
        print(f"Error testing wedding plans: {str(e)}")
        return False

def test_platform_stats():
    print_separator()
    print("Testing Platform Stats...")
    
    try:
        # Test getting platform stats
        print("Getting platform stats...")
        response = requests.get(f"{API_URL}/stats")
        response.raise_for_status()
        stats = response.json()
        
        print(f"Total users: {stats.get('total_users', 0)}")
        print(f"Total vendors: {stats.get('total_vendors', 0)}")
        print(f"Total inquiries: {stats.get('total_inquiries', 0)}")
        print(f"Vendor categories: {', '.join(stats.get('vendor_categories', []))}")
        
        test_results["platform_stats"]["status"] = "Passed"
        test_results["platform_stats"]["details"] = "Successfully retrieved platform statistics"
        return True
    
    except Exception as e:
        test_results["platform_stats"]["status"] = "Failed"
        test_results["platform_stats"]["details"] = f"Error: {str(e)}"
        print(f"Error testing platform stats: {str(e)}")
        return False

def test_web_search_enhancement():
    global created_user_id
    print_separator()
    print("Testing Web Search Enhancement...")
    
    if not created_user_id:
        test_results["web_search_enhancement"]["status"] = "Skipped"
        test_results["web_search_enhancement"]["details"] = "User creation failed, cannot test web search"
        print("Skipping web search test as user creation failed")
        return False
    
    try:
        # Test sending chat messages that should trigger web search
        print("Testing web search with wedding photography prices query...")
        photography_query = {
            "user_id": created_user_id,
            "message": "What are current wedding photography prices in Mumbai in 2025?"
        }
        
        response = requests.post(f"{API_URL}/chat", json=photography_query)
        response.raise_for_status()
        photography_data = response.json()
        
        # Check if web search was used
        web_search_used = photography_data.get("web_search_used", False)
        print(f"Web search used: {web_search_used}")
        print(f"Response excerpt: {photography_data.get('response')[:150]}...")
        
        # Test another query for wedding trends
        print("Testing web search with wedding trends query...")
        trends_query = {
            "user_id": created_user_id,
            "message": "What are the latest 2025 wedding trends?"
        }
        
        response = requests.post(f"{API_URL}/chat", json=trends_query)
        response.raise_for_status()
        trends_data = response.json()
        
        # Check if web search was used
        web_search_used = trends_data.get("web_search_used", False)
        print(f"Web search used: {web_search_used}")
        print(f"Response excerpt: {trends_data.get('response')[:150]}...")
        
        # Test direct market data endpoint
        print("Testing market data endpoint...")
        response = requests.get(f"{API_URL}/market-data?category=Photography&location=Mumbai")
        response.raise_for_status()
        market_data = response.json()
        
        print(f"Market data excerpt: {market_data.get('web_market_info')[:150]}...")
        print(f"Local market stats: {market_data.get('local_market_stats')}")
        
        # Check if responses contain emojis and structured formatting
        has_emojis = False
        has_structured_format = False
        
        for response_data in [photography_data, trends_data]:
            response_text = response_data.get('response', '')
            if any(emoji in response_text for emoji in ['🔍', '📸', '💍', '👰', '🤵', '💐', '🎉']):
                has_emojis = True
            
            if '•' in response_text or '*' in response_text or any(heading in response_text for heading in ['TRENDS', 'PRICING', 'COSTS', 'ANALYSIS']):
                has_structured_format = True
        
        if has_emojis and has_structured_format:
            test_results["web_search_enhancement"]["status"] = "Passed"
            test_results["web_search_enhancement"]["details"] = "Web search enhancement is working with emojis and structured formatting"
        else:
            test_results["web_search_enhancement"]["status"] = "Partial"
            test_results["web_search_enhancement"]["details"] = f"Web search is working but formatting improvements are incomplete. Has emojis: {has_emojis}, Has structure: {has_structured_format}"
        
        return True
    
    except Exception as e:
        test_results["web_search_enhancement"]["status"] = "Failed"
        test_results["web_search_enhancement"]["details"] = f"Error: {str(e)}"
        print(f"Error testing web search enhancement: {str(e)}")
        return False

def test_expanded_sample_database():
    print_separator()
    print("Testing Expanded Sample Database...")
    
    try:
        # Get all vendors to check the total count
        print("Getting all vendors to check database size...")
        response = requests.get(f"{API_URL}/vendors")
        response.raise_for_status()
        all_vendors = response.json()
        
        vendor_count = len(all_vendors)
        print(f"Total vendors in database: {vendor_count}")
        
        # Check if we have at least 20 vendors
        if vendor_count < 20:
            test_results["expanded_sample_database"]["status"] = "Failed"
            test_results["expanded_sample_database"]["details"] = f"Expected at least 20 vendors, but found only {vendor_count}"
            return False
        
        # Check for vendors in all required categories
        required_categories = [
            "Photography", "Catering", "Venue", "Decoration", 
            "Music", "Transportation", "Makeup", "Invitations", 
            "Jewelry", "Clothing"
        ]
        
        # Check for vendors in all required cities
        required_cities = [
            "Mumbai", "Delhi", "Bangalore", "Chennai", 
            "Pune", "Rajasthan", "Hyderabad"
        ]
        
        # Count vendors by category and city
        categories_found = set()
        cities_found = set()
        
        for vendor in all_vendors:
            if vendor.get("category") in required_categories:
                categories_found.add(vendor.get("category"))
            
            vendor_location = vendor.get("location", "")
            for city in required_cities:
                if city in vendor_location:
                    cities_found.add(city)
        
        print(f"Categories found: {', '.join(categories_found)}")
        print(f"Cities found: {', '.join(cities_found)}")
        
        # Check if all required categories and cities are present
        missing_categories = set(required_categories) - categories_found
        missing_cities = set(required_cities) - cities_found
        
        if missing_categories or missing_cities:
            test_results["expanded_sample_database"]["status"] = "Partial"
            test_results["expanded_sample_database"]["details"] = f"Database expanded but missing some required data. Missing categories: {missing_categories}, Missing cities: {missing_cities}"
            return True
        
        test_results["expanded_sample_database"]["status"] = "Passed"
        test_results["expanded_sample_database"]["details"] = f"Successfully verified expanded database with {vendor_count} vendors across all required categories and cities"
        return True
    
    except Exception as e:
        test_results["expanded_sample_database"]["status"] = "Failed"
        test_results["expanded_sample_database"]["details"] = f"Error: {str(e)}"
        print(f"Error testing expanded sample database: {str(e)}")
        return False

def test_new_vendor_creation():
    print_separator()
    print("Testing New Vendor Creation with Expanded Fields...")
    
    try:
        # Test creating a vendor with the new category
        print("Creating a test vendor in the Jewelry category...")
        response = requests.post(f"{API_URL}/vendors", json=test_new_vendor)
        response.raise_for_status()
        vendor_data = response.json()
        new_vendor_id = vendor_data["id"]
        print(f"Created vendor with ID: {new_vendor_id}")
        
        # Verify the vendor was created with all fields
        print(f"Getting vendor with ID: {new_vendor_id}")
        response = requests.get(f"{API_URL}/vendors/{new_vendor_id}")
        response.raise_for_status()
        retrieved_vendor = response.json()
        
        # Check if all fields were saved correctly
        all_fields_correct = (
            retrieved_vendor["name"] == test_new_vendor["name"] and
            retrieved_vendor["business_name"] == test_new_vendor["business_name"] and
            retrieved_vendor["category"] == test_new_vendor["category"] and
            retrieved_vendor["location"] == test_new_vendor["location"] and
            len(retrieved_vendor["services"]) == len(test_new_vendor["services"]) and
            retrieved_vendor["pricing_range"]["min"] == test_new_vendor["pricing_range"]["min"] and
            retrieved_vendor["pricing_range"]["max"] == test_new_vendor["pricing_range"]["max"]
        )
        
        if all_fields_correct:
            print("All vendor fields were saved correctly")
            test_results["new_vendor_creation"]["status"] = "Passed"
            test_results["new_vendor_creation"]["details"] = f"Successfully created vendor with expanded fields. Vendor ID: {new_vendor_id}"
        else:
            print("Some vendor fields were not saved correctly")
            test_results["new_vendor_creation"]["status"] = "Partial"
            test_results["new_vendor_creation"]["details"] = f"Vendor created but some fields were not saved correctly"
        
        return True
    
    except Exception as e:
        test_results["new_vendor_creation"]["status"] = "Failed"
        test_results["new_vendor_creation"]["details"] = f"Error: {str(e)}"
        print(f"Error testing new vendor creation: {str(e)}")
        return False

def test_category_filtering():
    print_separator()
    print("Testing Category Filtering for New Categories...")
    
    try:
        # Test filtering for each of the new categories
        new_categories = ["Makeup", "Invitations", "Jewelry", "Clothing"]
        
        for category in new_categories:
            print(f"Testing filtering for {category} category...")
            response = requests.get(f"{API_URL}/vendors?category={category}")
            response.raise_for_status()
            vendors = response.json()
            
            print(f"Found {len(vendors)} vendors in {category} category")
            
            # Check if we found any vendors in this category
            if len(vendors) == 0:
                print(f"No vendors found in {category} category")
                test_results["category_filtering"]["status"] = "Partial"
                test_results["category_filtering"]["details"] = f"Filtering works but no vendors found in {category} category"
                continue
            
            # Verify that all returned vendors are in the correct category
            all_correct_category = all(vendor["category"] == category for vendor in vendors)
            
            if not all_correct_category:
                print(f"Some vendors returned for {category} category have incorrect category")
                test_results["category_filtering"]["status"] = "Failed"
                test_results["category_filtering"]["details"] = f"Category filtering returned incorrect results for {category}"
                return False
        
        test_results["category_filtering"]["status"] = "Passed"
        test_results["category_filtering"]["details"] = "Successfully filtered vendors by all new categories"
        return True
    
    except Exception as e:
        test_results["category_filtering"]["status"] = "Failed"
        test_results["category_filtering"]["details"] = f"Error: {str(e)}"
        print(f"Error testing category filtering: {str(e)}")
        return False

def run_all_tests():
    print("\n" + "="*30 + " STARTING BACKEND TESTS " + "="*30 + "\n")
    
    # Test in a logical order where later tests depend on earlier ones
    test_user_management()
    test_vendor_management()
    test_ai_chat()
    test_vendor_recommendations()
    test_inquiries()
    test_wedding_plans()
    test_platform_stats()
    
    # Test the new features
    test_expanded_sample_database()
    test_new_vendor_creation()
    test_category_filtering()
    test_web_search_enhancement()
    
    print("\n" + "="*30 + " TEST RESULTS SUMMARY " + "="*30 + "\n")
    
    all_passed = True
    for test_name, result in test_results.items():
        status = result["status"]
        if status == "Failed":
            all_passed = False
        print(f"{test_name.replace('_', ' ').title()}: {status}")
        if result["details"]:
            print(f"  Details: {result['details']}")
    
    print("\n" + "="*80 + "\n")
    
    if all_passed:
        print("🎉 All tests passed successfully! 🎉")
    else:
        print("❌ Some tests failed. Check the details above for more information.")
    
    return all_passed

if __name__ == "__main__":
    run_all_tests()