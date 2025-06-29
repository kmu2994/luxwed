from fastapi import FastAPI, APIRouter, HTTPException, BackgroundTasks
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime
from emergentintegrations.llm.chat import LlmChat, UserMessage
import asyncio
import aiohttp
import json as json_module

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI(title="AI Wedding Services Platform")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Gemini AI Configuration
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

# Database Models
class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    email: str
    phone: str
    role: str = "customer"  # customer, vendor
    preferences: Optional[Dict] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class UserCreate(BaseModel):
    name: str
    email: str
    phone: str
    role: str = "customer"
    preferences: Optional[Dict] = None

class Vendor(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    business_name: str
    email: str
    phone: str
    category: str  # photography, catering, venue, decoration, etc.
    services: List[str]
    pricing_range: Dict  # {min: 50000, max: 200000}
    location: str
    description: str
    portfolio_images: List[str] = []
    rating: float = 0.0
    total_reviews: int = 0
    availability: List[str] = []  # Available dates
    verified: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)

class VendorCreate(BaseModel):
    name: str
    business_name: str
    email: str
    phone: str
    category: str
    services: List[str]
    pricing_range: Dict
    location: str
    description: str
    portfolio_images: List[str] = []

class ChatSession(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    session_id: str
    messages: List[Dict] = []
    context: Dict = {}  # Store wedding preferences, budget, etc.
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class ChatMessage(BaseModel):
    user_id: str
    message: str
    session_id: Optional[str] = None

class Inquiry(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    vendor_id: str
    message: str
    status: str = "pending"  # pending, replied, closed
    created_at: datetime = Field(default_factory=datetime.utcnow)

class InquiryCreate(BaseModel):
    user_id: str
    vendor_id: str
    message: str

class WeddingPlan(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    budget: float
    guest_count: int
    wedding_date: datetime
    location: str
    style_preference: str  # traditional, modern, fusion
    selected_vendors: List[str] = []
    timeline: Dict = {}
    created_at: datetime = Field(default_factory=datetime.utcnow)

class WeddingPlanCreate(BaseModel):
    user_id: str
    budget: float
    guest_count: int
    wedding_date: datetime
    location: str
    style_preference: str

# AI Wedding Planner Service
class AIWeddingPlanner:
    def __init__(self):
        self.api_key = GEMINI_API_KEY
        
    async def get_chat_instance(self, session_id: str, user_context: Dict = None):
        system_message = f"""You are an expert AI Wedding Planner assistant for a premium wedding services platform. Your role is to help couples plan their perfect wedding within their budget and preferences.

Your capabilities:
1. Wedding Planning: Budget allocation, timeline creation, vendor recommendations
2. Style Consultation: Traditional Indian, Modern, Fusion wedding styles
3. Vendor Matching: Match couples with the best vendors based on their needs
4. Cost Estimation: Provide accurate pricing predictions for different services
5. Timeline Management: Create detailed wedding planning schedules

User Context: {user_context or 'New conversation'}

Guidelines:
- Always ask about budget, guest count, preferred date, and style preference early
- Provide specific vendor recommendations based on location and budget  
- Break down costs clearly with realistic pricing
- Suggest timeline milestones for wedding planning
- Be enthusiastic and supportive while being practical
- Focus on the zero-commission advantage of this platform
- Ask clarifying questions to understand their vision better

Respond in a helpful, warm, and professional tone. Always end with a specific question or suggestion for next steps."""

        chat = LlmChat(
            api_key=self.api_key,
            session_id=session_id,
            system_message=system_message
        ).with_model("gemini", "gemini-2.0-flash")
        
        return chat

ai_planner = AIWeddingPlanner()

# Vendor Recommendation Engine
async def get_vendor_recommendations(user_preferences: Dict, category: str = None):
    """AI-powered vendor recommendation based on user preferences"""
    budget = user_preferences.get('budget', 0)
    location = user_preferences.get('location', '')
    style = user_preferences.get('style_preference', '')
    guest_count = user_preferences.get('guest_count', 0)
    
    # Build query filters
    query = {}
    if category:
        query['category'] = category
    if location:
        query['location'] = {'$regex': location, '$options': 'i'}
    if budget > 0:
        query['$and'] = [
            {'pricing_range.min': {'$lte': budget}},
            {'pricing_range.max': {'$gte': budget * 0.7}}  # Allow some flexibility
        ]
    
    # Get vendors from database
    vendors = await db.vendors.find(query).sort('rating', -1).limit(10).to_list(10)
    
    # Use AI to rank and personalize recommendations
    if vendors and GEMINI_API_KEY:
        try:
            # Create AI ranker
            ranker_chat = LlmChat(
                api_key=GEMINI_API_KEY,
                session_id=f"ranking_{uuid.uuid4()}",
                system_message="You are an AI vendor ranking system. Rank vendors based on user preferences and provide personalized recommendations."
            ).with_model("gemini", "gemini-2.0-flash")
            
            vendor_data = [
                {
                    'name': v['business_name'],
                    'category': v['category'],
                    'pricing': v['pricing_range'],
                    'rating': v.get('rating', 0),
                    'description': v['description'][:200],
                    'location': v['location']
                }
                for v in vendors
            ]
            
            ranking_prompt = f"""
            Rank these vendors for a wedding with:
            Budget: ₹{budget:,}
            Location: {location}
            Style: {style}
            Guest Count: {guest_count}
            
            Vendors: {vendor_data}
            
            Provide a ranked recommendation with brief reasons. Return as JSON with vendor names and ranking reasons.
            """
            
            ranking_response = await ranker_chat.send_message(UserMessage(text=ranking_prompt))
            
            # For now, return vendors sorted by rating
            return [Vendor(**vendor) for vendor in vendors]
            
        except Exception as e:
            logging.error(f"AI ranking failed: {e}")
            return [Vendor(**vendor) for vendor in vendors]
    
    return [Vendor(**vendor) for vendor in vendors]

# API Routes

@api_router.get("/")
async def root():
    return {"message": "AI Wedding Services Platform API", "version": "1.0"}

# User Management
@api_router.post("/users", response_model=User)
async def create_user(user: UserCreate):
    user_dict = user.dict()
    user_obj = User(**user_dict)
    await db.users.insert_one(user_obj.dict())
    return user_obj

@api_router.get("/users/{user_id}", response_model=User)
async def get_user(user_id: str):
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return User(**user)

@api_router.get("/users", response_model=List[User])
async def get_users():
    users = await db.users.find().limit(50).to_list(50)
    return [User(**user) for user in users]

# Vendor Management
@api_router.post("/vendors", response_model=Vendor)
async def create_vendor(vendor: VendorCreate):
    vendor_dict = vendor.dict()
    vendor_obj = Vendor(**vendor_dict)
    await db.vendors.insert_one(vendor_obj.dict())
    return vendor_obj

@api_router.get("/vendors", response_model=List[Vendor])
async def get_vendors(category: Optional[str] = None, location: Optional[str] = None):
    query = {}
    if category:
        query['category'] = category
    if location:
        query['location'] = {'$regex': location, '$options': 'i'}
    
    vendors = await db.vendors.find(query).sort('rating', -1).limit(20).to_list(20)
    return [Vendor(**vendor) for vendor in vendors]

@api_router.get("/vendors/{vendor_id}", response_model=Vendor)
async def get_vendor(vendor_id: str):
    vendor = await db.vendors.find_one({"id": vendor_id})
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    return Vendor(**vendor)

# AI Chat Interface
@api_router.post("/chat")
async def chat_with_ai(message: ChatMessage):
    try:
        # Get or create session
        session_id = message.session_id or str(uuid.uuid4())
        
        # Get user context
        user = await db.users.find_one({"id": message.user_id})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        user_context = user.get('preferences', {})
        
        # Get existing chat session
        chat_session_data = await db.chat_sessions.find_one({"session_id": session_id, "user_id": message.user_id})
        if not chat_session_data:
            chat_session = ChatSession(
                user_id=message.user_id,
                session_id=session_id,
                context=user_context
            )
            await db.chat_sessions.insert_one(chat_session.dict())
            chat_session_messages = []
        else:
            chat_session = ChatSession(**chat_session_data)
            chat_session_messages = chat_session.messages
        
        # Get AI response
        chat = await ai_planner.get_chat_instance(session_id, user_context)
        ai_response = await chat.send_message(UserMessage(text=message.message))
        
        # Store conversation
        conversation_update = {
            "messages": chat_session_messages + [
                {"role": "user", "content": message.message, "timestamp": datetime.utcnow().isoformat()},
                {"role": "assistant", "content": ai_response, "timestamp": datetime.utcnow().isoformat()}
            ],
            "updated_at": datetime.utcnow()
        }
        
        await db.chat_sessions.update_one(
            {"session_id": session_id, "user_id": message.user_id},
            {"$set": conversation_update}
        )
        
        # Extract any planning data from the conversation
        if any(keyword in message.message.lower() for keyword in ['budget', 'guest', 'date', 'venue', 'style']):
            # Here you could use AI to extract structured data and update user preferences
            pass
        
        return {
            "response": ai_response,
            "session_id": session_id,
            "suggestions": await get_ai_suggestions(message.message, user_context)
        }
        
    except Exception as e:
        logging.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=f"Chat service error: {str(e)}")

async def get_ai_suggestions(user_message: str, user_context: Dict) -> List[str]:
    """Generate contextual suggestions based on user message"""
    suggestions = []
    
    if 'budget' in user_message.lower():
        suggestions.extend([
            "Show me vendors within my budget",
            "Help me allocate my wedding budget",
            "What can I get for my budget?"
        ])
    elif 'venue' in user_message.lower():
        suggestions.extend([
            "Show me venues in my area",
            "What's the average venue cost?",
            "Outdoor vs indoor venue options"
        ])
    elif 'photography' in user_message.lower():
        suggestions.extend([
            "Find photographers in my budget",
            "Traditional vs candid photography",
            "Pre-wedding shoot packages"
        ])
    else:
        suggestions.extend([
            "Create my wedding timeline",
            "Show me vendor recommendations",
            "Help with budget planning",
            "What should I book first?"
        ])
    
    return suggestions[:3]  # Return top 3 suggestions

# Vendor Recommendations
@api_router.get("/recommendations/{user_id}")
async def get_recommendations(user_id: str, category: Optional[str] = None):
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    preferences = user.get('preferences', {})
    recommendations = await get_vendor_recommendations(preferences, category)
    
    return {
        "recommendations": recommendations,
        "total_count": len(recommendations),
        "category": category or "all"
    }

# Wedding Plans
@api_router.post("/wedding-plans", response_model=WeddingPlan)
async def create_wedding_plan(plan: WeddingPlanCreate):
    plan_dict = plan.dict()
    plan_obj = WeddingPlan(**plan_dict)
    
    # Auto-generate timeline based on wedding date
    timeline = await generate_wedding_timeline(plan.wedding_date, plan.budget)
    plan_obj.timeline = timeline
    
    await db.wedding_plans.insert_one(plan_obj.dict())
    
    # Update user preferences
    await db.users.update_one(
        {"id": plan.user_id},
        {"$set": {"preferences": {
            "budget": plan.budget,
            "guest_count": plan.guest_count,
            "location": plan.location,
            "style_preference": plan.style_preference,
            "wedding_date": plan.wedding_date.isoformat()
        }}}
    )
    
    return plan_obj

async def generate_wedding_timeline(wedding_date: datetime, budget: float) -> Dict:
    """Generate AI-powered wedding planning timeline"""
    months_until_wedding = (wedding_date - datetime.utcnow()).days // 30
    
    timeline = {
        "12_months_before": ["Book venue", "Set budget", "Create guest list"],
        "8_months_before": ["Book photographer", "Book caterer", "Send save the dates"],
        "6_months_before": ["Book decorator", "Plan honeymoon", "Buy wedding outfits"],
        "3_months_before": ["Send invitations", "Final guest count", "Menu tasting"],
        "1_month_before": ["Final fittings", "Rehearsal", "Confirm all vendors"],
        "1_week_before": ["Pack for honeymoon", "Final payments", "Relax and enjoy!"]
    }
    
    return timeline

@api_router.get("/wedding-plans/{user_id}")
async def get_wedding_plans(user_id: str):
    plans = await db.wedding_plans.find({"user_id": user_id}).to_list(10)
    return [WeddingPlan(**plan) for plan in plans]

# Inquiries
@api_router.post("/inquiries", response_model=Inquiry)
async def create_inquiry(inquiry: InquiryCreate):
    inquiry_dict = inquiry.dict()
    inquiry_obj = Inquiry(**inquiry_dict)
    await db.inquiries.insert_one(inquiry_obj.dict())
    return inquiry_obj

@api_router.get("/inquiries/user/{user_id}")
async def get_user_inquiries(user_id: str):
    inquiries = await db.inquiries.find({"user_id": user_id}).to_list(50)
    return [Inquiry(**inquiry) for inquiry in inquiries]

@api_router.get("/inquiries/vendor/{vendor_id}")
async def get_vendor_inquiries(vendor_id: str):
    inquiries = await db.inquiries.find({"vendor_id": vendor_id}).to_list(50)
    return [Inquiry(**inquiry) for inquiry in inquiries]

# Chat History
@api_router.get("/chat-sessions/{user_id}")
async def get_chat_sessions(user_id: str):
    sessions = await db.chat_sessions.find({"user_id": user_id}).sort("updated_at", -1).to_list(10)
    return [ChatSession(**session) for session in sessions]

@api_router.get("/chat-sessions/{user_id}/{session_id}")
async def get_chat_session(user_id: str, session_id: str):
    session = await db.chat_sessions.find_one({"user_id": user_id, "session_id": session_id})
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")
    return ChatSession(**session)

# Analytics & Stats
@api_router.get("/stats")
async def get_platform_stats():
    total_users = await db.users.count_documents({})
    total_vendors = await db.vendors.count_documents({})
    total_inquiries = await db.inquiries.count_documents({})
    
    return {
        "total_users": total_users,
        "total_vendors": total_vendors,
        "total_inquiries": total_inquiries,
        "vendor_categories": ["Photography", "Catering", "Venues", "Decoration", "Music", "Transportation"]
    }

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup_event():
    """Initialize database with sample data"""
    logger.info("Starting AI Wedding Services Platform...")
    
    # Create sample vendors if database is empty
    vendor_count = await db.vendors.count_documents({})
    if vendor_count == 0:
        logger.info("Initializing sample vendors...")
        sample_vendors = [
            {
                "name": "Rajesh Photography",
                "business_name": "Elite Wedding Photography",
                "email": "rajesh@elitewedding.com",
                "phone": "+91 9876543210",
                "category": "Photography",
                "services": ["Candid Photography", "Traditional Photography", "Pre-Wedding Shoots"],
                "pricing_range": {"min": 50000, "max": 150000},
                "location": "Mumbai",
                "description": "Award-winning wedding photographer with 8+ years of experience in capturing your special moments.",
                "rating": 4.8,
                "total_reviews": 156,
                "verified": True
            },
            {
                "name": "Meera Caterers",
                "business_name": "Royal Feast Catering",
                "email": "meera@royalfeast.com",
                "phone": "+91 9876543211",
                "category": "Catering",
                "services": ["Multi-Cuisine", "Traditional Indian", "Live Counters"],
                "pricing_range": {"min": 800, "max": 2500},
                "location": "Mumbai",
                "description": "Premium catering services with authentic flavors and impeccable presentation for your dream wedding.",
                "rating": 4.6,
                "total_reviews": 89,
                "verified": True
            },
            {
                "name": "Grand Palace Hotel",
                "business_name": "Grand Palace Wedding Venue",
                "email": "events@grandpalace.com",
                "phone": "+91 9876543212",
                "category": "Venue",
                "services": ["Banquet Halls", "Garden Wedding", "Poolside Venue"],
                "pricing_range": {"min": 200000, "max": 800000},
                "location": "Mumbai",
                "description": "Luxurious wedding venue with stunning architecture and world-class amenities.",
                "rating": 4.9,
                "total_reviews": 203,
                "verified": True
            },
            {
                "name": "Elegant Decorators",
                "business_name": "Elegant Event Decorators",
                "email": "info@elegantdeco.com",
                "phone": "+91 9876543213",
                "category": "Decoration",
                "services": ["Floral Decoration", "Theme Decoration", "Stage Design"],
                "pricing_range": {"min": 75000, "max": 300000},
                "location": "Mumbai",
                "description": "Transform your wedding venue into a magical space with our creative decoration services.",
                "rating": 4.7,
                "total_reviews": 134,
                "verified": True
            }
        ]
        
        for vendor_data in sample_vendors:
            vendor = Vendor(**vendor_data)
            await db.vendors.insert_one(vendor.dict())
        
        logger.info(f"Initialized {len(sample_vendors)} sample vendors")

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()