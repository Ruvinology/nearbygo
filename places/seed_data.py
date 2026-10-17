"""
Initial data for DR-07: the ten approved proposal locations.

Distances are the verified radius distances from the SRS (Section 6.1).
Coordinates are approximate public locations of each landmark, good enough
for map markers; refine them in the admin if needed.

Descriptions are original text written for this project (OR-04). Practical
details are deliberately cautious and every place starts as "not verified"
(info_verified_on is empty): an administrator should confirm hours, fees and
facilities with each venue and then set the verified date (BR-07, FR-PD-06).
"""

CATEGORIES = [
    {
        "name": "Nature / Recreation",
        "slug": "nature-recreation",
        "colour": "lagoon",
        "icon": "water",
        "display_order": 1,
        "description": "Beaches and lakes for walks, swimming where it is safe, and sunsets.",
    },
    {
        "name": "Religious / Heritage",
        "slug": "religious-heritage",
        "colour": "saffron",
        "icon": "flower1",
        "display_order": 2,
        "description": "Temples and churches that are still places of worship. Dress modestly and be respectful.",
    },
    {
        "name": "Historical / Cultural",
        "slug": "historical-cultural",
        "colour": "brick",
        "icon": "bank",
        "display_order": 3,
        "description": "Historic buildings and grounds that tell the story of the area.",
    },
    {
        "name": "Museum / Educational",
        "slug": "museum-educational",
        "colour": "indigo",
        "icon": "easel",
        "display_order": 4,
        "description": "Places to learn something, good for students and families.",
    },
    {
        "name": "Nature / Wildlife",
        "slug": "nature-wildlife",
        "colour": "leaf",
        "icon": "binoculars",
        "display_order": 5,
        "description": "Wetlands and green spaces for bird watching and quiet walks.",
    },
]

# Images live in places/seed_images/ and are copied into MEDIA_ROOT by
# `python manage.py seed_places`. They are illustrations supplied for the
# project, so the credit says so (OR-04). Change it in the admin if you
# replace a picture with a real photograph.
IMAGE_CREDIT = "AI-generated illustration"

TEMPLE_TIPS = (
    "Wear clothes that cover your shoulders and knees, and remove shoes and hats before entering "
    "the shrine areas. White clothing is customary for worshippers. Do not pose with your back to "
    "a Buddha statue for photographs."
)

PLACES = [
    {
        "name": "Rankoth Viharaya, Panadura",
        "slug": "rankoth-viharaya-panadura",
        "image": "rankoth-viharaya-panadura.jpg",
        "image_alt": "A white stupa with temple buildings, trees and palms around a sunlit courtyard at Rankoth Viharaya.",
        "image_credit": IMAGE_CREDIT,
        "category": "religious-heritage",
        "latitude": "6.711600",
        "longitude": "79.905500",
        "distance_km": "1.9",
        "summary": "Panadura's best-known Buddhist temple, linked to the famous Panadura Debate of 1873.",
        "description": (
            "Rankoth Viharaya sits close to the centre of Panadura and is the town's most recognised temple. "
            "Its large stupa topped with a golden pinnacle is visible from the main road.\n\n"
            "The temple is remembered for its role in the Panadura Debate of 1873, a public debate between "
            "Buddhist and Christian scholars that became an important moment in the Buddhist revival in Sri Lanka. "
            "Today it is an active place of worship, especially busy on Poya (full moon) days."
        ),
        "opening_hours": "",
        "entrance_fee": "No entrance fee for worshippers and visitors (donations welcome)",
        "visit_duration_minutes": 45,
        "best_time_to_visit": "Early morning or evening, when it is cooler and the evening pooja takes place",
        "travel_tips": TEMPLE_TIPS,
        "transport": "Short tuk-tuk ride or walk from Panadura town and railway station.",
        "family_suitability": "Suitable for all ages. Keep children close near the main road.",
    },
    {
        "name": "Panadura Beach",
        "slug": "panadura-beach",
        "image": "panadura-beach.jpg",
        "image_alt": "The sun setting over the sea at Panadura Beach, with waves washing onto wet golden sand.",
        "image_credit": IMAGE_CREDIT,
        "category": "nature-recreation",
        "latitude": "6.708800",
        "longitude": "79.897800",
        "distance_km": "2.6",
        "summary": "A local stretch of sand on the edge of town, good for an evening walk and the sunset.",
        "description": (
            "Panadura Beach is the closest beach to the town centre and is mostly used by local families. "
            "It is quieter than the resort beaches further south and is a pleasant place to watch the sun go down "
            "over the Indian Ocean.\n\n"
            "Sea conditions on the west coast change with the monsoon, so check local advice before swimming."
        ),
        "opening_hours": "Open access",
        "entrance_fee": "Free",
        "visit_duration_minutes": 60,
        "best_time_to_visit": "Late afternoon to sunset",
        "travel_tips": "Swim only where locals swim and when the sea is calm. Bring water and sun protection.",
        "transport": "Tuk-tuk from Panadura town in about 10 minutes.",
        "family_suitability": "Good for a walk with children. Supervise children closely near the water.",
    },
    {
        "name": "Bolgoda South Lake",
        "slug": "bolgoda-south-lake",
        "image": "bolgoda-south-lake.jpg",
        "image_alt": "Morning mist over the still water of Bolgoda South Lake, with palm-lined banks reflected at sunrise.",
        "image_credit": IMAGE_CREDIT,
        "category": "nature-recreation",
        "latitude": "6.700500",
        "longitude": "79.933000",
        "distance_km": "4.0",
        "summary": "The southern basin of the Bolgoda Lake system, with calm water and mangrove-lined banks.",
        "description": (
            "Bolgoda Lake is one of the largest natural lakes in Sri Lanka, made up of a north and a south lake "
            "joined by a narrow channel. The south lake lies just east of Panadura.\n\n"
            "Its sheltered banks are lined with mangroves and home to water birds. Boat rides and water sports are "
            "run by private operators around the lake, and several lakeside hotels have restaurants with views of the water."
        ),
        "opening_hours": "",
        "entrance_fee": "",
        "visit_duration_minutes": 120,
        "best_time_to_visit": "Morning, for calm water and birds",
        "travel_tips": "Use only licensed boat operators and wear the life jacket they provide.",
        "transport": "Tuk-tuk or car from Panadura, about 15 minutes.",
        "family_suitability": "Good for families. Life jackets are essential for children on boats.",
    },
    {
        "name": "Wadduwa Beach",
        "slug": "wadduwa-beach",
        "image": "wadduwa-beach.jpg",
        "image_alt": "Waves rolling onto a wide, palm-fringed sandy beach at Wadduwa in the late afternoon sun.",
        "image_credit": IMAGE_CREDIT,
        "category": "nature-recreation",
        "latitude": "6.665000",
        "longitude": "79.924500",
        "distance_km": "5.5",
        "summary": "A long, palm-fringed beach south of Panadura, lined with resort hotels.",
        "description": (
            "Wadduwa Beach is a wide, sandy beach backed by coconut palms. Several resort hotels face the sea here, "
            "which makes it a popular stop for a meal or a relaxed afternoon by the water.\n\n"
            "The beach is long enough for a good walk, and it is usually less crowded than beaches closer to Colombo."
        ),
        "opening_hours": "Open access",
        "entrance_fee": "Free (hotel facilities are for guests or paying visitors)",
        "visit_duration_minutes": 120,
        "best_time_to_visit": "Late afternoon to sunset, December to April for calmer seas",
        "travel_tips": "Watch for red flags and currents. Hotels may let non-guests use restaurants and pools for a fee.",
        "transport": "Train to Wadduwa station on the coastal line, or about 15 minutes by tuk-tuk from Panadura.",
        "family_suitability": "Good for families. Supervise children closely near the water.",
        "food": "yes",
    },
    {
        "name": "Holy Emmanuel Church, Moratuwa",
        "slug": "holy-emmanuel-church-moratuwa",
        "image": "holy-emmanuel-church-moratuwa.jpg",
        "image_alt": "The tall white Gothic spire and front of Holy Emmanuel Church, Moratuwa, in golden evening light.",
        "image_credit": IMAGE_CREDIT,
        "category": "religious-heritage",
        "latitude": "6.774500",
        "longitude": "79.882500",
        "distance_km": "9.8",
        "summary": "A large Gothic Revival church, one of the landmarks of Moratuwa.",
        "description": (
            "Holy Emmanuel Church is one of the best-known churches in Moratuwa, admired for its tall spires and "
            "Gothic Revival style. It reflects the long Christian history of the coastal towns between Colombo and Kalutara.\n\n"
            "The church is an active parish, so visitors are welcome outside service times."
        ),
        "opening_hours": "",
        "entrance_fee": "No entrance fee",
        "visit_duration_minutes": 30,
        "best_time_to_visit": "Outside service times",
        "travel_tips": "Dress modestly and keep quiet inside, especially during services.",
        "transport": "Train or bus along the Galle Road to Moratuwa, then a short tuk-tuk ride.",
        "family_suitability": "Suitable for all ages.",
    },
    {
        "name": "Richmond Castle, Kalutara",
        "slug": "richmond-castle-kalutara",
        "image": "richmond-castle-kalutara.jpg",
        "image_alt": "The white two-storey Richmond Castle mansion with arched verandas, a lawn and a curved driveway.",
        "image_credit": IMAGE_CREDIT,
        "category": "historical-cultural",
        "latitude": "6.601500",
        "longitude": "79.975300",
        "distance_km": "12.8",
        "summary": "An early 20th-century mansion mixing Indian and British styles, set in large grounds near the river.",
        "description": (
            "Richmond Castle was completed in 1910 for Don Arthur de Silva Wijesinghe Siriwardena, a local landowner "
            "and philanthropist. The two-storey mansion combines Indian and British architecture, with a grand "
            "staircase, carved timber and stained glass.\n\n"
            "The house stands in large grounds near the Kalu Ganga, about 2 km inland from Kalutara town, and is now "
            "held by the Public Trustee of Sri Lanka. Visitors can see the main rooms and walk around the grounds."
        ),
        "opening_hours": "",
        "entrance_fee": "",
        "visit_duration_minutes": 60,
        "best_time_to_visit": "Morning",
        "travel_tips": "Follow the guide's instructions and ask before taking photographs inside.",
        "transport": "Car or tuk-tuk from Kalutara town, inland from the Galle Road.",
        "family_suitability": "Interesting for older children and students of history.",
    },
    {
        "name": "Kalutara Bodhiya and Chaitya",
        "slug": "kalutara-bodhiya-and-chaitya",
        "image": "kalutara-bodhiya-and-chaitya.jpg",
        "image_alt": "The white Kalutara Chaitya and temple buildings beside the river, reflected in the water at sunset.",
        "image_credit": IMAGE_CREDIT,
        "category": "religious-heritage",
        "latitude": "6.586900",
        "longitude": "79.960300",
        "distance_km": "13.7",
        "summary": "A major Buddhist site at the mouth of the Kalu Ganga, with a hollow white stupa you can walk inside.",
        "description": (
            "The Kalutara Bodhiya is one of the most visited Buddhist sites on the west coast. Travellers along the "
            "Galle Road often stop here to make an offering for a safe journey.\n\n"
            "Across the road stands the Kalutara Chaitya, a large white stupa that is hollow inside. Its interior is "
            "decorated with paintings of the Buddha's life, and the site looks out over the river mouth."
        ),
        "opening_hours": "",
        "entrance_fee": "No entrance fee (donations welcome)",
        "visit_duration_minutes": 60,
        "best_time_to_visit": "Evening, when the lamps are lit",
        "travel_tips": TEMPLE_TIPS,
        "transport": "On the Galle Road at the northern entrance to Kalutara. Buses towards Galle stop nearby.",
        "family_suitability": "Suitable for all ages. It can be very crowded on Poya days.",
        "parking": "yes",
    },
    {
        "name": "Sri Lanka Air Force Museum, Ratmalana",
        "slug": "sri-lanka-air-force-museum-ratmalana",
        "image": "sri-lanka-air-force-museum-ratmalana.jpg",
        "image_alt": "A jet fighter, a transport plane and a helicopter on display on the lawn at the Air Force Museum.",
        "image_credit": IMAGE_CREDIT,
        "category": "museum-educational",
        "latitude": "6.824200",
        "longitude": "79.891700",
        "distance_km": "13.8",
        "summary": "A collection of aircraft, engines and uniforms that tells the story of the Sri Lanka Air Force.",
        "description": (
            "The Sri Lanka Air Force Museum at Ratmalana shows the history of military aviation in the country, from "
            "the Royal Ceylon Air Force to today. Indoor galleries display uniforms, models, engines and photographs, "
            "and a number of retired aircraft and helicopters are parked outside.\n\n"
            "It is a good choice for students, families and anyone interested in aviation or engineering."
        ),
        "opening_hours": "",
        "entrance_fee": "",
        "visit_duration_minutes": 90,
        "best_time_to_visit": "Weekday mornings are usually quieter",
        "travel_tips": "Photography rules can differ inside and outside, so ask the staff first.",
        "transport": "Near Ratmalana airport, off the Galle Road. Ratmalana railway station is nearby.",
        "family_suitability": "Very popular with children.",
    },
    {
        "name": "Bellanwila-Attidiya Bird Sanctuary",
        "slug": "bellanwila-attidiya-bird-sanctuary",
        "image": "bellanwila-attidiya-bird-sanctuary.jpg",
        "image_alt": "An egret in the marsh at Bellanwila-Attidiya at dawn, with a wooden viewing hut and city towers in the distance.",
        "image_credit": IMAGE_CREDIT,
        "category": "nature-wildlife",
        "latitude": "6.832000",
        "longitude": "79.892000",
        "distance_km": "16.1",
        "summary": "A protected urban wetland where you can spot herons, kingfishers and migratory birds.",
        "description": (
            "Bellanwila-Attidiya is a marshland sanctuary on the southern edge of Colombo. Despite being surrounded by "
            "the city, it shelters a wide range of resident and migratory water birds, as well as monitor lizards and fish.\n\n"
            "A short trail and viewing points let visitors watch the wetland. It is a useful place for students to see "
            "how urban wetlands help control floods."
        ),
        "opening_hours": "",
        "entrance_fee": "",
        "visit_duration_minutes": 90,
        "best_time_to_visit": "Early morning, especially from October to April when migrant birds arrive",
        "travel_tips": "Bring binoculars, insect repellent and water. Stay on paths, as the ground can be wet.",
        "transport": "Tuk-tuk from Dehiwala or Boralesgamuwa.",
        "family_suitability": "Good for older children who enjoy nature. Keep children away from the water's edge.",
    },
    {
        "name": "Mount Lavinia Beach",
        "slug": "mount-lavinia-beach",
        "image": "mount-lavinia-beach.jpg",
        "image_alt": "Sunset over Mount Lavinia Beach, with waves on the sand and the hotel on the headland.",
        "image_credit": IMAGE_CREDIT,
        "category": "nature-recreation",
        "latitude": "6.838500",
        "longitude": "79.863000",
        "distance_km": "16.5",
        "summary": "A lively city beach beside the historic Mount Lavinia Hotel, with seafood restaurants on the sand.",
        "description": (
            "Mount Lavinia Beach is one of the best-known beaches near Colombo. The historic Mount Lavinia Hotel, once a "
            "colonial governor's residence, stands on the headland at its northern end.\n\n"
            "The beach is busy in the evenings, when restaurants set out tables on the sand and the sun sets over the sea."
        ),
        "opening_hours": "Open access",
        "entrance_fee": "Free",
        "visit_duration_minutes": 120,
        "best_time_to_visit": "Evening, for the sunset and dinner on the beach",
        "travel_tips": "Swim only between flags and when lifeguards are present. Agree prices before ordering at beach stalls.",
        "transport": "Train to Mount Lavinia station on the coastal line, then a short walk.",
        "family_suitability": "Good for families in the early evening.",
        "food": "yes",
    },
]
