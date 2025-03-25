import os
import re
import pickle
from flask import Flask, request, render_template, redirect, url_for
from werkzeug.utils import secure_filename
from pdfminer.high_level import extract_text

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"pdf", "txt"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Ensure upload directory exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Utility functions
def extract_text_from_file(file_path):
    return extract_text(file_path)

def extract_email_from_resume(text):
    email = None
    pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
    match = re.search(pattern, text)
    if match:
        email = match.group()
    return email

def extract_contact_number_from_resume(text):
    contact_number = None
    pattern = r"\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"
    match = re.search(pattern, text)
    if match:
        contact_number = match.group()
    return contact_number

def extract_name_from_resume(text):
    name = None
    pattern = r"(\b[A-Z][a-z]+\b)\s(\b[A-Z][a-z]+\b)"
    match = re.search(pattern, text)
    if match:
        name = match.group()
    return name

def cleanResume(txt):
    cleanText = re.sub(r'http\S+\s', ' ', txt)  # Remove URLs
    cleanText = re.sub(r'@\S+', ' ', cleanText)  # Remove mentions
    cleanText = re.sub(r'#\S+', ' ', cleanText)  # Remove hashtags
    cleanText = re.sub(r'RT|CC', ' ', cleanText)  # Remove RT, CC
    cleanText = re.sub(r'[%s]' % re.escape("!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~"), ' ', cleanText)  # Remove punctuation
    cleanText = re.sub(r'[^\x00-\x7f]', ' ', cleanText)  # Remove non-ASCII characters
    cleanText = re.sub(r'\s+', ' ', cleanText)  # Remove multiple spaces
    cleanText = cleanText.replace('\r\n', ' ')  # Remove line breaks
    cleanText = cleanText.strip().lower()  # Trim spaces and convert to lowercase
    return cleanText

def extract_education_from_resume(text):
    education = []
    text = text.replace("\x0c", " ").replace("\n", " ")
    degree_keywords = [
        r"B\.?Sc", r"M\.?Sc", r"Ph\.?D", r"B\.?Tech", r"M\.?Tech", r"B\.?E", r"M\.?E",
        r"Bachelor of Science", r"Master of Science", r"Doctor of Philosophy",
        r"Bachelor of Technology", r"Master of Technology", r"Bachelor of Engineering", r"Master of Engineering"
    ]
    education_keywords = ["Computer Science",
    "Chemical Engineering",
    "Physics",
    "Mathematics",
    "Biology",
    "Chemistry",
    "Electrical Engineering",
    "Mechanical Engineering",
    "Civil Engineering",
    "Aerospace Engineering",
     "Environmental Science",
    "Psychology",
    "Sociology",
    "Political Science",
    "Economics",
    "Business Administration",
    "Finance",
    "Marketing",
    "Accounting",
    "Human Resources",
    "Information Technology",
    "Data Science",
    "Artificial Intelligence",
    "Cybersecurity",
    "Software Engineering",
    "Biotechnology",
    "Biomedical Engineering",
    "Architecture",
    "Urban Planning",
    "Geology",
    "Astronomy",
    "Statistics",
    "Philosophy",
    "History",
    "Literature",
    "Linguistics",
    "Anthropology",
    "Geography",
    "Education",
    "Nursing",
    "Pharmacy",
    "Medicine",
    "Dentistry",
    "Veterinary Science",
    "Agriculture",
    "Food Science",
    "Public Health",
    "Law",
    "Criminology",
    "Journalism",
    "Media Studies",
    "Film Studies",
    "Fine Arts",
    "Graphic Design",
    "Music",
    "Theater",
    "Dance",
    "Religious Studies",
    "Environmental Engineering",
    "Renewable Energy",
    "Robotics",
    "Nanotechnology",
    "Marine Biology",
    "Forensic Science",
    "Cognitive Science",
    "Neuroscience",
    "Public Administration",
    "International Relations",
    "Social Work",
    "Hospitality Management",
     "Event Management",
    "Fashion Design",
    "Interior Design",
    "Game Design",
    "Animation",
    "Supply Chain Management",
    "Logistics",
    "Aviation",
    "Pilot Training",
    "Culinary Arts",
    "Project Management",
    "Industrial Engineering",
    "Materials Science",
    "Nuclear Engineering",
    "Petroleum Engineering",
    "Telecommunications",
    "Network Engineering",
    "Database Management",
    "Web Development",
    "Mobile App Development",
    "Cloud Computing",
    "Teaching"
    "Machine Learning",
    "Deep Learning",
    "Natural Language Processing",
    "Computer Vision",
    "Blockchain Technology",
    "Quantum Computing",
    "Cryptography",
    "Digital Marketing",
    "E-commerce",
    "Entrepreneurship",
    "Risk Management",
    "Quality Assurance",
    "Operations Research",
    "Actuarial Science",
    "Astrophysics",
    "Particle Physics",
    "Geophysics",
    "Meteorology",
    "Oceanography",
    "Ecology",
    "Zoology",
    "Botany",
    "Genetics",
    "Microbiology",
    "Immunology",
    "Virology",
    "Epidemiology",
    "Toxicology",
    "Biochemistry",
    "Molecular Biology",
    "Cell Biology",
    "Evolutionary Biology",
    "Marine Science",
    "Wildlife Conservation",
    "Forestry",
    "Horticulture",
    "Soil Science",
    "Agronomy",
    "Animal Science",
    "Electric Vehicles",
    "Sustainable Agriculture",
    "Organic Farming",
    "Aquaculture",
    "Fisheries Science",
    "Food Technology",
    "Brewing Science",
    "Wine Science",
    "Culinary Science",
    "Food Safety",
    "Packaging Technology",
    "Textile Engineering",
    "Fashion Technology",
    "Leather Technology",
    "Paper Technology",
    "Polymer Science",
    "Composite Materials",
    "Nanomaterials",
    "Biomaterials",
    "Metallurgy"]  

    for degree in degree_keywords:
        for field in education_keywords:
            pattern = rf"(?i)\b({degree})\s*(in|of)?\s*({field})\b"
            match = re.search(pattern, text)
            if match:
                education.append(match.group())
    return education

def extract_skills(text):
    skills_list = [    "Python", "Java", "C++", "JavaScript", "SQL", "R", "Go", "Swift", "Kotlin", "Rust", "TypeScript",
    "C#", "PHP", "Ruby", "Perl", "HTML", "CSS", "Software Engineering", "DevOps", "Docker",
    "Kubernetes", "CI/CD", "Microservices", "API Development", "Version Control (Git)",
    "Agile Methodologies", "Scrum", "Kanban", "Testing & Debugging", "Cloud Computing",
    "Machine Learning", "Deep Learning", "Data Science", "Artificial Intelligence", "Big Data",
    "Computer Vision", "NLP (Natural Language Processing)", "Reinforcement Learning", "Data Mining",
    "Statistical Modeling", "Data Visualization", "Data Wrangling", "Predictive Analytics",
    "Time Series Analysis", "A/B Testing",
    "TensorFlow", "PyTorch", "Scikit-Learn", "Keras", "OpenCV", "Hugging Face", "Pandas", "NumPy",
    "React", "Angular", "Vue.js", "Django", "Flask", "Node.js", "Spring Boot", ".NET",
    "MySQL", "PostgreSQL", "MongoDB", "AWS (Amazon Web Services)", "Azure (Microsoft Azure)",
    "Google Cloud Platform (GCP)", "Hadoop", "Spark", "NoSQL", "Database Administration",
    "Cloud Architecture", "Serverless Computing", "Data Warehousing",
    "Frontend Development", "Backend Development", "Full-Stack Development", "UI/UX Design",
    "Responsive Design", "Web Security", "SEO (Search Engine Optimization)", "Content Management Systems (CMS)",
    "Cybersecurity", "Network Security", "Ethical Hacking", "Penetration Testing", "Information Security",
    "Cryptography", "Security Auditing", "Incident Response",
    "Network Administration", "System Administration", "Linux", "Windows Server", "Cloud Networking",
    "Virtualization", "IT Infrastructure",
    "Data Analytics", "Business Intelligence (BI)", "Product Management", "Statistics", "Financial Analysis",
    "Market Research", "Business Strategy", "Project Management", "Risk Management", "Supply Chain Management",
    "Sales & Marketing", "Digital Marketing", "E-commerce", "Financial Modeling",
    "Graphic Design", "UX/UI Design", "Video Editing", "Animation", "3D Modeling", "Content Creation",
    "Copywriting", "Photography", "Illustration",
    "Mechanical Engineering", "Electrical Engineering", "Civil Engineering", "Aerospace Engineering",
    "Chemical Engineering", "Manufacturing Processes", "CAD (Computer-Aided Design)",
    "CAM (Computer-Aided Manufacturing)", "Quality Control",
    "Medical Terminology", "Patient Care", "Electronic Health Records (EHR)", "Clinical Research",
    "Healthcare Administration", "Biotechnology", "Pharmacology",
    "Legal Research", "Contract Law", "Compliance", "Regulatory Affairs", "Intellectual Property",
    "Curriculum Development", "Instructional Design", "Training & Development", "Educational Technology",
    "Communication", "Leadership", "Problem-Solving", "Project Management", "Teamwork",
    "Critical Thinking", "Time Management", "Adaptability", "Negotiation", "Presentation Skills",
    "Emotional Intelligence", "Customer Service", "Public Speaking",
    "Accounting", "Financial Reporting", "Auditing", "Investment Management", "Financial Planning",
    "Logistics Management", "Supply Chain Optimization", "Transportation Planning", "Inventory Management",
    "Robotics", "Automation", "Embedded Systems", "PLC Programming", "Industrial Automation", "IoT (Internet of Things)",
    "Environmental Impact Assessment", "Sustainability", "GIS (Geographic Information Systems)", "Climate Science", "Hospitality Management", "Tourism Management", "Event Planning", "Culinary Arts", "Customer Service", "Travel Planning", "Hotel Operations","Public Policy", "Government Administration", "Urban Planning", "Public Safety", "Emergency Management", "Diplomacy",
    "Software Development", "Database Management", "Cloud Services","SQL Developer", "Data Analysis", "AI/ML", "Web Development", "Mobile Development", "System Security", "Network Engineering", "IT Management", "Business Analysis", "Financial Management", "Creative Design", "Engineering Design", "Healthcare Management", "Legal Services", "Educational Leadership", "Soft Skills", "Financial Accounting", "Supply Chain Logistics", "Industrial Robotics", "Environmental Science", "Hospitality Operations", "Public Administration", "Mobile App Development", "API Design", "Statistical Analysis", "Cloud Security", "Information Technology", "Business Planning", "Graphic Design Software", "Mechanical Design", "Medical Coding", "Contract Negotiation", "Online Learning", "Interpersonal Skills", "Financial Modeling", "Warehouse Management", "Robotic Process Automation", "Environmental Policy", "Restaurant Management", "Government Policy", "Mobile UI Design", "Database Design", "Predictive Modeling", "Network Security Protocols", "IT Project Management", "Strategic Planning", "Digital Design", "Electrical Design", "Medical Billing", "Legal Compliance", "Learning Management Systems", "Verbal Communication", "Financial Reporting Standards", "Logistics Planning", "Robotics Engineering", "Environmental Management", "Hotel Management", "Public Relations", "Mobile Testing", "Data Engineering", "Machine Learning Algorithms", "Cybersecurity Protocols", "IT Service Management", "Business Development", "Visual Design", "Civil Design", "Medical Records Management", "Legal Documentation", "E-Learning Development", "Written Communication", "Financial Risk Management", "Inventory Control", "Robotics Simulation", "Environmental Regulations", "Resort Management", "Political Science", "Mobile Development Frameworks", "Data Governance", "Deep Learning Frameworks", "Security Information and Event Management (SIEM)", "IT Governance", "Market Analysis", "User Interface Design", "Aerospace Design", "Medical Device Development", "Legal Writing", "Online Training", "Active Listening", "Financial Auditing", "Transportation Management", "Robotics System Integration", "Environmental Sustainability", "Casino Management", "International Relations",
    "Blockchain Development", "Smart Contract Development", "Solidity", "Ethereum", "Cryptocurrency",
    "Quantum Computing", "Quantum Algorithms", "Quantum Cryptography", "Edge Computing", "Fog Computing",
    "AR/VR Development", "Augmented Reality", "Virtual Reality", "Unity", "Unreal Engine",
    "Game Development", "Game Design", "Game Mechanics", "Level Design", "Game Physics",
    "Digital Twin Technology", "Simulation Modeling", "Process Automation", "RPA (Robotic Process Automation)",
    "Low-Code Development", "No-Code Development", "Power Platform", "OutSystems", "Mendix",
    "Digital Transformation", "Business Process Reengineering", "Change Management", "Organizational Development",
    "Human Resources Management", "Talent Acquisition", "Employee Engagement", "Performance Management",
    "Workforce Planning", "Compensation & Benefits", "Diversity & Inclusion", "Corporate Social Responsibility",
    "Sustainability Reporting", "Carbon Footprint Analysis", "Circular Economy", "Green Energy Solutions",
    "Renewable Energy Systems", "Solar Energy", "Wind Energy", "Hydropower", "Bioenergy",
    "Geospatial Analysis", "Remote Sensing", "Cartography", "Drone Technology", "Satellite Imagery",
    "Urban Design", "Landscape Architecture", "Smart Cities", "Transportation Engineering", "Traffic Management",
    "Disaster Recovery", "Crisis Management", "Business Continuity Planning", "Risk Assessment", "Compliance Management",
    "Regulatory Compliance", "Corporate Governance", "Internal Auditing", "Fraud Detection", "Anti-Money Laundering",
    "Behavioral Economics", "Consumer Psychology", "Market Segmentation", "Brand Management", "Product Lifecycle Management",
    "Innovation Management", "Design Thinking", "Lean Startup Methodology", "Business Model Innovation", "Corporate Venturing",
    "Social Media Marketing", "Influencer Marketing", "Content Strategy", "Email Marketing", "Affiliate Marketing",
    "Video Marketing", "Podcast Production", "Live Streaming", "Community Management", "Crowdfunding",
    "User Research", "Usability Testing", "Interaction Design", "Prototyping", "Wireframing",
    "Motion Graphics", "Sound Design", "Game Audio", "3D Animation", "Character Rigging",
    "Industrial Design", "Product Design", "Ergonomics", "Material Science", "Rapid Prototyping",
    "Nanotechnology", "Biomedical Engineering", "Tissue Engineering", "Genetic Engineering", "Bioinformatics",
    "Clinical Trials", "Medical Imaging", "Telemedicine", "Health Informatics", "Medical Device Regulation",
    "Intellectual Property Law", "Patent Law", "Trademark Law", "Corporate Law", "International Law",
    "Alternative Dispute Resolution", "Arbitration", "Mediation", "Litigation", "Legal Tech",
    "Educational Psychology", "Classroom Management", "Special Education", "Adult Learning Theory", "Gamification in Education",
    "Cultural Competence", "Global Leadership", "Cross-Cultural Communication", "International Business", "Foreign Policy Analysis",
    "Behavioral Finance", "Portfolio Management", "Derivatives Trading", "Quantitative Finance", "Fintech",
    "Supply Chain Analytics", "Procurement Management", "Vendor Management", "Demand Planning", "Operations Research",
    "Human-Computer Interaction", "Cognitive Science", "Neuroscience", "Artificial General Intelligence", "Explainable AI",
    "Ethical AI", "AI Governance", "AI Policy", "AI Ethics", "AI Safety",
    "Space Exploration", "Astrophysics", "Planetary Science", "Rocket Science", "Satellite Communication",
    "Marine Biology", "Oceanography", "Environmental Chemistry", "Wildlife Conservation", "Ecosystem Restoration",
    "Culinary Science", "Food Technology", "Nutrition Science", "Food Safety", "Gastronomy",
    "Event Marketing", "Festival Management", "Convention Planning", "Exhibition Design", "Cultural Event Management",
    "Public Health", "Epidemiology", "Health Policy", "Global Health", "Health Economics",
    "Nonprofit Management", "Fundraising", "Grant Writing", "Social Entrepreneurship", "Impact Investing",
    "Military Science", "Defense Strategy", "Intelligence Analysis", "Counterterrorism", "Peacekeeping Operations",
    "Journalism", "Investigative Reporting", "Broadcast Journalism", "Digital Journalism", "Media Ethics",
    "Creative Writing", "Screenwriting", "Playwriting", "Poetry", "Literary Criticism",
    "Music Production", "Sound Engineering", "Music Theory", "Songwriting", "Audio Post-Production",
    "Fashion Design", "Textile Design", "Fashion Merchandising", "Fashion Marketing", "Sustainable Fashion",
    "Sports Management", "Athletic Training", "Sports Analytics", "Sports Marketing", "Event Sports Management",
    "Real Estate Development", "Property Management", "Real Estate Finance", "Urban Redevelopment", "Commercial Real Estate",
    "Aviation Management", "Air Traffic Control", "Aircraft Maintenance", "Airline Operations", "Aviation Safety",
    "Maritime Operations", "Shipping Logistics", "Port Management", "Marine Engineering", "Naval Architecture",
    "Pharmaceutical Sciences", "Drug Discovery", "Pharmacovigilance", "Regulatory Science", "Clinical Pharmacy",
    "Veterinary Medicine", "Animal Nutrition", "Animal Behavior", "Veterinary Surgery", "Wildlife Medicine",
    "Criminology", "Forensic Science", "Criminal Psychology", "Law Enforcement", "Corrections Management",
    "Archaeology", "Anthropology", "Cultural Heritage Management", "Museum Studies", "Art Conservation",
    "Philosophy", "Ethics", "Logic", "Political Philosophy", "Philosophy of Science",
    "Theology", "Religious Studies", "Comparative Religion", "Spiritual Counseling", "Interfaith Dialogue",
    "Astronomy", "Cosmology", "Planetary Geology", "Space Technology", "Astrobiology",
    "Meteorology", "Climate Modeling", "Weather Forecasting", "Atmospheric Science", "Hydrology",
    "Geology", "Mineralogy", "Paleontology", "Seismology", "Geotechnical Engineering",
    "Actuarial Science", "Risk Modeling", "Insurance Underwriting", "Reinsurance", "Pension Fund Management",
    "Library Science", "Information Management", "Archival Studies", "Digital Preservation", "Knowledge Management",
    "Disability Studies", "Rehabilitation Counseling", "Assistive Technology", "Inclusive Education", "Disability Rights",
    "Gerontology", "Aging Studies", "Elder Care", "Long-Term Care Administration", "Palliative Care",
    "Youth Development", "Child Psychology", "Adolescent Counseling", "Family Therapy", "Parenting Education",
    "Addiction Studies", "Substance Abuse Counseling", "Behavioral Therapy", "Mental Health Counseling", "Trauma-Informed Care",
    "Art Therapy", "Music Therapy", "Dance Therapy", "Drama Therapy", "Expressive Arts Therapy",
    "Forensic Psychology", "Criminal Profiling", "Victimology", "Juvenile Justice", "Restorative Justice",
    "International Development", "Global Poverty Alleviation", "Humanitarian Aid", "Refugee Studies", "Development Economics",
    "Peace Studies", "Conflict Resolution", "Mediation & Negotiation", "Post-Conflict Reconstruction", "Human Rights Advocacy",
    "Gender Studies", "Feminist Theory", "Queer Theory", "Masculinity Studies", "Intersectionality",
    "Disability Advocacy", "Accessibility Design", "Universal Design", "Inclusive Technology", "Disability Policy",
    "Animal Rights", "Animal Welfare", "Vegan Studies", "Animal Ethics", "Wildlife Advocacy",
    "Environmental Justice", "Climate Activism", "Environmental Policy Advocacy", "Sustainable Development", "Green Technology",
    "Space Law", "Space Policy", "Space Resource Management", "Space Tourism", "Space Colonization",
    "Digital Ethics", "Data Privacy", "Cybersecurity Ethics", "AI Ethics", "Technology Policy",
    "Futurism", "Trend Analysis", "Scenario Planning", "Strategic Foresight", "Innovation Forecasting",
    "Cultural Studies", "Media Studies", "Popular Culture", "Subculture Studies", "Globalization Studies",
    "Postcolonial Studies", "Decolonial Theory", "Indigenous Studies", "Global South Studies", "Transnationalism",
    "Migrant Studies", "Diaspora Studies", "Transborder Studies", "Citizenship Studies", "Immigration Policy",
    "Urban Sociology", "Rural Studies", "Community Development", "Social Policy", "Urban Anthropology",
    "Digital Humanities", "Computational Linguistics", "Text Mining", "Digital Archiving", "Cultural Analytics",
    "Performance Studies", "Theater Arts", "Dance Studies", "Performance Art", "Cultural Performance",
    "Visual Studies", "Art History", "Film Studies", "Photography Studies", "Visual Culture",
    "Sound Studies", "Acoustics", "Audio Culture", "Sound Art", "Sonic Ecology",
    "Food Studies", "Culinary History", "Food Anthropology", "Food Policy", "Gastronomic Tourism",
    "Wine Studies", "Brewing Science", "Distillation Techniques", "Beverage Management", "Sommelier Studies",
    "Cannabis Studies", "Cannabis Cultivation", "Cannabis Policy", "Medical Cannabis", "Cannabis Business",
    "Esports Management", "Gaming Culture", "Streaming Technology", "Esports Marketing", "Game Analytics",
    "Digital Currencies", "Central Bank Digital Currencies (CBDCs)", "Decentralized Finance (DeFi)", "NFTs (Non-Fungible Tokens)", "Tokenomics",
    "Metaverse Development", "Virtual Economies", "Digital Identity", "Virtual Reality Commerce", "Augmented Reality Marketing",
    "Space Economy", "Asteroid Mining", "Space Manufacturing", "Space Agriculture", "Space Medicine",
    "Ocean Economy", "Blue Economy", "Marine Biotechnology", "Offshore Energy", "Aquaculture",
    "Circular Design", "Sustainable Fashion Design", "Eco-Product Design", "Zero-Waste Design", "Biomimicry",
    "Regenerative Agriculture", "Permaculture", "Agroecology", "Soil Science", "Sustainable Farming",
    "Climate Resilience", "Disaster Risk Reduction", "Climate Adaptation", "Resilience Planning", "Community Resilience",
    "Digital Literacy", "Media Literacy", "Information Literacy", "Critical Digital Skills", "Technology Literacy",
    "Emotional Resilience", "Mindfulness", "Stress Management", "Wellness Coaching", "Positive Psychology",
    "Holistic Health", "Integrative Medicine", "Functional Medicine", "Ayurveda", "Traditional Chinese Medicine",
    "Yoga Studies", "Meditation Studies", "Spiritual Wellness", "Energy Healing", "Mind-Body Practices",
    "Adventure Tourism", "Ecotourism", "Cultural Tourism", "Heritage Tourism", "Sustainable Tourism",
    "Dark Tourism", "Thanatourism", "War Tourism", "Disaster Tourism", "Memorial Tourism",
    "Luxury Brand Management", "High-Net-Worth Individuals (HNWI) Services", "Luxury Marketing", "Luxury Retail", "Luxury Hospitality",
    "Personal Branding", "Influencer Branding", "Executive Coaching", "Leadership Branding", "Career Branding",
    "Digital Nomadism", "Remote Work Management", "Distributed Teams", "Virtual Collaboration", "Remote Work Tools",
    "Gig Economy", "Freelance Management", "Platform Economy", "On-Demand Services", "Independent Work",
    "Future of Work", "Workplace Automation", "Human-Machine Collaboration", "Skills of the Future", "Workplace Innovation",
    "Social Innovation", "Social Impact Measurement", "Social Enterprise Management", "Community Innovation", "Grassroots Innovation",
    "Civic Technology", "E-Governance", "Digital Democracy", "Open Government", "Citizen Engagement",
    "Smart Governance", "Public Sector Innovation", "Government Technology", "Policy Innovation", "Digital Transformation in Government",
    "Urban Innovation", "Smart Infrastructure", "Urban Mobility", "Resilient Cities", "Sustainable Urbanism",
    "Rural Innovation", "Agricultural Technology", "Rural Development", "Community-Based Tourism", "Rural Entrepreneurship",
    "Indigenous Innovation", "Traditional Knowledge", "Indigenous Technology", "Cultural Innovation", "Indigenous Entrepreneurship",
    "Disability Innovation", "Assistive Technology Design", "Inclusive Innovation", "Accessible Technology", "Disability Entrepreneurship",
    "Youth Innovation", "Student Entrepreneurship", "Youth-Led Innovation", "Education Innovation", "Youth Empowerment",
    "Gender Innovation", "Women-Led Innovation", "Gender-Inclusive Design", "Feminist Innovation", "Gender Equality in Tech",
    "Climate Innovation", "Clean Technology", "Climate Tech Startups", "Carbon Capture", "Climate-Resilient Infrastructure",
    "Ocean Innovation", "Marine Technology", "Ocean Conservation Tech", "Blue Tech Startups", "Sustainable Ocean Solutions",
    "Space Innovation", "Space Tech Startups", "Commercial Spaceflight", "Space Exploration Tech", "Space Sustainability",
    "Health Innovation", "Digital Health", "Health Tech Startups", "Medical Innovation", "Personalized Medicine",
    "Education Innovation", "EdTech Startups", "Online Learning Platforms", "Gamified Learning", "Lifelong Learning",
    "Financial Innovation", "Fintech Startups", "Digital Banking", "Blockchain in Finance", "Financial Inclusion",
    "Legal Innovation", "Legal Tech Startups", "AI in Law", "Online Dispute Resolution", "Access to Justice",
    "Creative Innovation", "Creative Tech Startups", "Digital Art", "Interactive Media", "Immersive Experiences",
    "Social Media Innovation", "Social Media Startups", "Content Creation Tools", "Influencer Platforms", "Community Building Platforms",
    "Gaming Innovation", "Gaming Startups", "Game Streaming", "Game Development Tools", "Gaming Communities",
    "Sports Innovation", "Sports Tech Startups", "Athlete Performance Tech", "Fan Engagement", "Sports Analytics",
    "Food Innovation", "Food Tech Startups", "Alternative Proteins", "Food Delivery Tech", "Sustainable Food Solutions",
    "Fashion Innovation", "Fashion Tech Startups", "Wearable Technology", "Sustainable Fashion Tech", "Digital Fashion",
    "Travel Innovation", "Travel Tech Startups", "Smart Tourism", "Sustainable Travel", "Travel Experience Platforms",
    "Real Estate Innovation", "PropTech Startups", "Smart Homes", "Sustainable Housing", "Real Estate Marketplaces",
    "Energy Innovation", "Energy Tech Startups", "Renewable Energy Tech", "Energy Storage", "Smart Grids",
    "Transportation Innovation", "Mobility Startups", "Electric Vehicles", "Autonomous Vehicles", "Smart Transportation",
    "Logistics Innovation", "Logistics Tech Startups", "Supply Chain Tech", "Last-Mile Delivery", "Warehouse Automation",
    "Manufacturing Innovation", "Industry 4.0", "Smart Manufacturing", "Additive Manufacturing", "Industrial IoT",
    "Construction Innovation", "Construction Tech Startups", "Modular Construction", "Sustainable Building", "Construction Robotics",
    "Agriculture Innovation", "AgTech Startups", "Precision Agriculture", "Vertical Farming", "Agricultural Drones",
    "Healthcare Innovation", "Health Tech Startups", "Telehealth", "Wearable Health Tech", "AI in Healthcare",
    "Education Innovation", "EdTech Startups", "Personalized Learning", "Virtual Classrooms", "Education Analytics",
    "Financial Innovation", "Fintech Startups", "Digital Wallets", "Cryptocurrency Exchanges", "Robo-Advisors",
    "Legal Innovation", "Legal Tech Startups", "Contract Automation", "Legal Research Tools", "Online Legal Services",
    "Creative Innovation", "Creative Tech Startups", "Digital Storytelling", "Interactive Art", "Immersive Media",
    "Social Media Innovation", "Social Media Startups", "Content Moderation Tools", "Social Listening", "Community Management Tools",
    "Gaming Innovation", "Gaming Startups", "Game Monetization", "Game Distribution Platforms", "Gaming Hardware",
    "Sports Innovation", "Sports Tech Startups", "Sports Wearables", "Fan Experience Tech", "Sports Betting Platforms",
    "Food Innovation", "Food Tech Startups", "Food Safety Tech", "Food Traceability", "Food Waste Solutions",
    "Fashion Innovation", "Fashion Tech Startups", "Virtual Try-On", "Fashion Rental Platforms", "Sustainable Fashion Marketplaces",
    "Travel Innovation", "Travel Tech Startups", "Travel Planning Tools", "Sustainable Travel Platforms", "Local Experience Marketplaces",
    "Real Estate Innovation", "PropTech Startups", "Co-Living Spaces", "Real Estate Crowdfunding", "Smart Building Management",
    "Energy Innovation", "Energy Tech Startups", "Energy Efficiency Tech", "Renewable Energy Marketplaces", "Energy Trading Platforms",
    "Transportation Innovation", "Mobility Startups", "Ride-Sharing Platforms", "Micro-Mobility Solutions", "Smart Traffic Management",
    "Logistics Innovation", "Logistics Tech Startups", "Autonomous Delivery", "Supply Chain Visibility", "Logistics Optimization",
    "Manufacturing Innovation", "Manufacturing Startups", "Industrial Automation", "Predictive Maintenance", "Digital Twins",
    "Construction Innovation", "Construction Startups", "3D Printing in Construction", "Smart Construction Sites", "Construction Management Software",
    "Agriculture Innovation", "AgTech Startups", "Soil Health Monitoring", "Crop Management Tools", "Agricultural Robotics",
    "Healthcare Innovation", "Health Tech Startups", "Remote Patient Monitoring", "AI Diagnostics", "Health Data Analytics",
    "Education Innovation", "EdTech Startups", "Learning Management Systems", "Educational Games", "Teacher Support Tools",
    "Financial Innovation", "Fintech Startups", "Peer-to-Peer Lending", "Digital Insurance", "Financial Planning Tools",
    "Legal Innovation", "Legal Tech Startups", "Legal Document Automation", "Online Legal Marketplaces", "Legal Analytics",
    "Creative Innovation", "Creative Tech Startups", "Digital Content Creation", "Interactive Storytelling", "Immersive Art Installations",
    "Social Media Innovation", "Social Media Startups", "Social Media Analytics", "Influencer Marketing Platforms", "Community Engagement Tools",
    "Gaming Innovation", "Gaming Startups", "Game Development Platforms", "Game Testing Tools", "Gaming Content Creation",
    "Sports Innovation", "Sports Tech Startups", "Sports Training Tech", "Fan Engagement Platforms", "Sports Media Platforms",
    "Food Innovation", "Food Tech Startups", "Food Delivery Platforms", "Meal Kit Services", "Food Subscription Services",
    "Fashion Innovation", "Fashion Tech Startups", "Fashion Design Tools", "Sustainable Fashion Platforms", "Fashion Rental Services",
    "Travel Innovation", "Travel Tech Startups", "Travel Booking Platforms", "Sustainable Travel Services", "Local Experience Platforms",
    "Real Estate Innovation", "PropTech Startups", "Real Estate Investment Platforms", "Smart Home Devices", "Property Management Tools",
    "Energy Innovation", "Energy Tech Startups", "Energy Monitoring Tools", "Renewable Energy Solutions", "Energy Management Platforms",
    "Transportation Innovation", "Mobility Startups", "Public Transportation Tech", "Smart Mobility Solutions", "Transportation Analytics",
    "Logistics Innovation", "Logistics Tech Startups", "Logistics Tracking Tools", "Supply Chain Analytics", "Logistics Management Platforms",
    "Manufacturing Innovation", "Manufacturing Startups", "Industrial Robotics", "Smart Factories", "Manufacturing Analytics",
    "Construction Innovation", "Construction Startups", "Construction Safety Tech", "Smart Construction Tools", "Construction Analytics",
    "Agriculture Innovation", "AgTech Startups", "Agricultural Data Analytics", "Farm Management Tools", "Agricultural Supply Chain Tech",
    "Healthcare Innovation", "Health Tech Startups", "Health Monitoring Devices", "AI in Medical Imaging", "Healthcare Management Platforms",
    "Education Innovation", "EdTech Startups", "Online Learning Tools", "Educational Content Platforms", "Student Engagement Tools",
    "Financial Innovation", "Fintech Startups", "Digital Payment Platforms", "Investment Platforms", "Financial Analytics",
    "Legal Innovation", "Legal Tech Startups", "Legal Research Platforms", "Online Legal Services", "Legal Case Management Tools",
    "Creative Innovation", "Creative Tech Startups", "Digital Art Platforms", "Interactive Media Tools", "Immersive Experience Platforms",
    "Social Media Innovation", "Social Media Startups", "Social Media Management Tools", "Content Creation Platforms", "Community Building Tools",
    "Gaming Innovation", "Gaming Startups", "Game Streaming Platforms", "Game Development Tools", "Gaming Community Platforms",
    "Sports Innovation", "Sports Tech Startups", "Sports Performance Tools", "Fan Engagement Platforms", "Sports Analytics Platforms",
    "Food Innovation", "Food Tech Startups", "Food Safety Platforms", "Food Traceability Tools", "Food Waste Management Platforms",
    "Fashion Innovation", "Fashion Tech Startups", "Fashion Design Platforms", "Sustainable Fashion Tools", "Fashion Rental Platforms",
    "Travel Innovation", "Travel Tech Startups", "Travel Planning Platforms", "Sustainable Travel Tools", "Local Experience Platforms",
    "Real Estate Innovation", "PropTech Startups", "Real Estate Investment Tools", "Smart Home Platforms", "Property Management Platforms",
    "Energy Innovation", "Energy Tech Startups", "Energy Monitoring Platforms", "Renewable Energy Tools", "Energy Management Tools",
    "Transportation Innovation", "Mobility Startups", "Public Transportation Tools", "Smart Mobility Platforms", "Transportation Management Tools",
    "Logistics Innovation", "Logistics Tech Startups", "Logistics Tracking Platforms", "Supply Chain Management Tools", "Logistics Analytics Platforms",
    "Manufacturing Innovation", "Manufacturing Startups", "Industrial Robotics Platforms", "Smart Factory Tools", "Manufacturing Analytics Platforms",
    "Construction Innovation", "Construction Startups", "Construction Safety Platforms", "Smart Construction Tools", "Construction Analytics Platforms",
    "Agriculture Innovation", "AgTech Startups", "Agricultural Data Platforms", "Farm Management Platforms", "Agricultural Supply Chain Tools",
    "Healthcare Innovation", "Health Tech Startups", "Health Monitoring Platforms", "AI in Medical Imaging Tools", "Healthcare Management Tools",
    "Education Innovation", "EdTech Startups", "Online Learning Platforms", "Educational Content Tools", "Student Engagement Platforms",
    "Financial Innovation", "Fintech Startups", "Digital Payment Tools", "Investment Platforms", "Financial Analytics Tools",
    "Legal Innovation", "Legal Tech Startups", "Legal Research Tools", "Online Legal Services", "Legal Case Management Platforms",
    "Creative Innovation", "Creative Tech Startups", "Digital Art Tools", "Interactive Media Platforms", "Immersive Experience Tools",
    "Social Media Innovation", "Social Media Startups", "Social Media Management Platforms", "Content Creation Tools", "Community Building Platforms",
    "Gaming Innovation", "Gaming Startups", "Game Streaming Tools", "Game Development Platforms", "Gaming Community Tools",
    "Sports Innovation", "Sports Tech Startups"]  # Blank list as per request 
    skills = []
    for skill in skills_list:
        pattern = r"(?i)\b" + re.escape(skill) + r"\b" if " " not in skill else r"(?i)\b" + re.escape(skill) + r"\b|\b" + re.escape(skill) + r"\b"
        match = re.search(pattern, text)
        if match:
            skills.append(skill)
    return skills

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        if "file" not in request.files:
            return redirect(request.url)

        file = request.files["file"]

        if file.filename == "":
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(file_path)

            text = extract_text_from_file(file_path)

            extracted_data = {
                "Name": extract_name_from_resume(text),
                "Email": extract_email_from_resume(text),
                "Phone Number": extract_contact_number_from_resume(text),
                "Education": extract_education_from_resume(text),
                "Skills": extract_skills(text),
            }

            os.remove(file_path)  # Delete file after processing

            return render_template("result.html", data=extracted_data)

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)