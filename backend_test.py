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