# Profile API - Native JSON Structure

## Overview
The `/api/v1/astrology/profile` endpoint now returns Kerykeion's native JSON structure with minimal filtering. No custom models, no pre-computed interpretations - just clean astrological data for AI to interpret.

## Response Structure

```json
{
  "natal_chart": {
    // 10 core planets (Sun through Pluto)
    "sun": { ...Kerykeion native planet data },
    "moon": { ...Kerykeion native planet data },
    // ... mercury, venus, mars, jupiter, saturn, uranus, neptune, pluto
    
    // Essential points
    "ascendant": { ...Kerykeion native point data },
    "descendant": { ...Kerykeion native point data },
    "medium_coeli": { ...Kerykeion native point data },
    "imum_coeli": { ...Kerykeion native point data },
    "chiron": { ...Kerykeion native point data },
    "mean_north_lunar_node": { ...Kerykeion native point data },
    "mean_south_lunar_node": { ...Kerykeion native point data },
    "mean_lilith": { ...Kerykeion native point data },
    
    // 12 houses
    "houses": {
      "first_house": { ...Kerykeion native house data },
      // ... all 12 houses
    },
    
    // Birth metadata
    "birth_data": {
      "name": "Subject",
      "date": "1990-03-15T14:30:00-05:00",
      "location": {
        "city": null,
        "nation": null,
        "lat": 40.7,
        "lng": -74.0,
        "timezone": "America/New_York"
      },
      "lunar_phase": { ...Kerykeion native lunar phase data }
    }
  },
  
  "natal_aspects": [
    // Filtered to orb < 6° (tight aspects only)
    {
      "p1_name": "Sun",
      "p2_name": "Mercury",
      "aspect": "conjunction",
      "orbit": 3.14,
      "aspect_movement": "Separating",
      // ...other Kerykeion native aspect fields
    }
    // ~45 aspects for typical chart
  ],
  
  "current_transits": {
    "date": "2025-10-30T14:52:35.753606",
    
    "planets": {
      // Current positions of 10 major planets
      "sun": { ...Kerykeion native planet data },
      "moon": { ...Kerykeion native planet data },
      // ... all 10 planets
    },
    
    "aspects_to_natal": [
      // Transit planet to natal planet aspects
      // Filtered to orb < 8° (wider orb for transits)
      {
        "p1_name": "Saturn",  // Transit planet
        "p2_name": "Sun",     // Natal planet
        "aspect": "conjunction",
        "orbit": 0.90,
        // ...other Kerykeion native aspect fields
      }
      // ~90 aspects for typical chart
    ],
    
    "current_sky_aspects": [
      // Aspects between transiting planets
      // Filtered to orb < 6°
      {
        "p1_name": "Jupiter",
        "p2_name": "Uranus",
        "aspect": "square",
        "orbit": 1.20,
        // ...other Kerykeion native aspect fields
      }
      // ~44 aspects for typical chart
    ]
  }
}
```

## Size Comparison

### Before (Manual Extraction)
- **2,047 lines** for natal chart + transits
- Custom Pydantic models
- Manual field extraction

### After (Kerykeion Native)
- **1,120 lines** for natal chart alone (45% reduction)
- **3,304 lines** with full transits
- Native Kerykeion JSON structure
- Filtered aspects (tight orbs only)

## Kerykeion Native Planet Data

Each planet/point includes:

```json
{
  "name": "Sun",
  "quality": "Mutable",
  "element": "Water",
  "sign": "Pis",
  "sign_num": 11,
  "position": 24.95,           // Degree within sign (0-30)
  "abs_pos": 354.95,           // Absolute zodiac degree (0-360)
  "emoji": "♓️",
  "point_type": "AstrologicalPoint",
  "house": "Eighth_House",
  "retrograde": false,
  "speed": 0.996,              // Daily motion
  "declination": -2.01         // Celestial latitude
}
```

## Kerykeion Native Aspect Data

Each aspect includes:

```json
{
  "p1_name": "Sun",
  "p1_owner": "Subject",
  "p1_abs_pos": 354.95,
  "p2_name": "Mercury",
  "p2_owner": "Subject",
  "p2_abs_pos": 351.82,
  "aspect": "conjunction",
  "orbit": 3.14,                    // Orb (deviation from exact)
  "aspect_degrees": 0,              // Exact aspect angle
  "diff": 3.14,                     // Actual angular difference
  "p1": 0,                          // Internal index
  "p2": 2,                          // Internal index
  "aspect_movement": "Separating"   // Applying or Separating
}
```

## Filtering

### Natal Aspects
- **Orb < 6°** only
- Reduces from ~100 aspects to ~45
- Focuses on strongest influences

### Transit-to-Natal Aspects
- **Orb < 8°** (wider for transits)
- Major transiting planets to natal planets
- ~90 aspects typically

### Current Sky Aspects
- **Orb < 6°**
- Aspects between transiting planets
- ~44 aspects typically

## API Endpoint

```bash
POST /api/v1/astrology/profile
Content-Type: application/json

{
  "year": 1990,
  "month": 3,
  "day": 15,
  "hour": 14,
  "minute": 30,
  "latitude": 40.7,
  "longitude": -74.0,
  "timezone": "America/New_York",
  "transit_date": "2025-10-30T14:52:35"  // Optional, defaults to now
}
```

## Benefits

✅ **No custom code** - Uses Kerykeion's battle-tested JSON serialization  
✅ **Smaller context** - 45% reduction for natal data  
✅ **AI-friendly** - Raw data, AI handles interpretation  
✅ **Filtered aspects** - Only meaningful aspects (tight orbs)  
✅ **Type-safe** - Kerykeion's Pydantic models ensure correctness  
✅ **Future-proof** - Automatically gets Kerykeion updates  

## Next Steps

This profile endpoint provides the **base context** for every AI conversation about astrology. The AI receives:
1. Complete natal chart with all essential data
2. Current transits and their aspects to natal chart
3. Current sky aspects

No pre-computed interpretations - the AI has all the raw astrological data it needs to provide personalized insights.
