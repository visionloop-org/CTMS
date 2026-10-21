# Color System & Theming Tokens
## Semantic Tokens, Outdoor Sunlight Mode & Statutory PESO Color Palettes

---

## 1. Core Semantic UI Tokens

The CTMS interface utilizes curated, accessible color palettes designed to satisfy WCAG 2.1 AAA contrast levels ($\ge 7:1$) for mission-critical industrial text.

```
+--------------------------------------------------------------------------------------------------+
|                                    SEMANTIC UI COLOR PALETTE                                     |
+--------------------------------------------------------------------------------------------------+
|  Primary (Deep Cobalt)       #1E40AF    Dark blue for main CTAs, active headers, app bars        |
|  Primary Hover / Pressed     #1E3A8A    High-contrast pressed state for touch feedback           |
|  Surface / Neutral Dark      #0F172A    Dark slate background for high-contrast viewing          |
|  Surface Card Neutral        #1E293B    Card background elevation in dark mode                   |
|  Surface Neutral Light       #F8FAFC    Clean, non-reflective light canvas                       |
|  Border / Divider            #CBD5E1    Crisp outline separation between serial records          |
+--------------------------------------------------------------------------------------------------+
|  SAFETY & ACTION STATUS TOKENS:                                                                  |
|  • Success / Validated       #15803D    Green: Valid scan, hydro-test active, verified POD       |
|  • Safety Hazard / Reject    #DC2626    Crimson: PESO test overdue, quarantine, leaking valve    |
|  • Warning / Due Soon        #D97706    Amber: Test due in <30 days, grace period expiring       |
|  • Information / Notice      #0284C7    Sky Blue: Outward dispatch, route notes                  |
+--------------------------------------------------------------------------------------------------+
```

---

## 2. Statutory PESO Gas Identification Color Codes

Under Indian Standard **IS 4376 / PESO Gas Cylinder Rules**, high-pressure cylinders must be painted in distinct statutory body and shoulder colors to prevent accidental cross-filling or life-threatening administration of the wrong gas in hospitals.

The UI mirrors these exact physical cylinder colors in asset cards, batch headers, and delivery manifests:

```
+---------------------------------------------------------------------------------------------------+
| Gas Type (Schema Enum)        | Body Hex  | Shoulder Hex | UI Chip Styling (Preview)              |
+-------------------------------+-----------+--------------+----------------------------------------+
| OXYGEN_MEDICAL                | #0F172A   | #FFFFFF      | [Black Body / White Collar]            |
| OXYGEN_INDUSTRIAL             | #0F172A   | #FFFFFF      | [Black Body / White Collar]            |
| NITROGEN_COMMERCIAL / UHP     | #64748B   | #0F172A      | [Medium Grey Body / Black Collar]      |
| ARGON                         | #1E3A8A   | #059669      | [Dark Blue Body / Peacock Green Collar]|
| CO2 (Carbon Dioxide)          | #0F172A   | #94A3B8      | [Black Body / Silver Metallic Collar]  |
| DISSOLVED_ACETYLENE           | #7F1D1D   | #7F1D1D      | [Maroon Body / Maroon Collar]          |
| HYDROGEN                      | #B91C1C   | #B91C1C      | [Signal Red Body / Signal Red Collar]  |
| HELIUM                        | #78350F   | #78350F      | [Middle Brown Body / Brown Collar]     |
| NITROUS_OXIDE                 | #1D4ED8   | #1D4ED8      | [French Blue Body / Blue Collar]       |
+-------------------------------+-----------+--------------+----------------------------------------+
```

### Jetpack Compose Gas Color Implementation
```kotlin
enum class GasColorCode(val bodyHex: Long, val shoulderHex: Long, val textColorHex: Long) {
    OXYGEN_MEDICAL(0xFF0F172AL, 0xFFFFFFFFL, 0xFF000000L),
    OXYGEN_INDUSTRIAL(0xFF0F172AL, 0xFFFFFFFFL, 0xFF000000L),
    NITROGEN(0xFF64748BL, 0xFF0F172AL, 0xFFFFFFFFL),
    ARGON(0xFF1E3A8AL, 0xFF059669L, 0xFFFFFFFFL),
    CO2(0xFF0F172AL, 0xFF94A3B8L, 0xFFFFFFFFL),
    DISSOLVED_ACETYLENE(0xFF7F1D1DL, 0xFF7F1D1DL, 0xFFFFFFFFL),
    HYDROGEN(0xFFB91C1CL, 0xFFB91C1CL, 0xFFFFFFFFL);

    val bodyColor get() = Color(bodyHex)
    val shoulderColor get() = Color(shoulderHex)
}
```

---

## 3. Ownership Distinction Colors (COC vs POC vs VOC)

To uphold **Prime Invariant #3 (Multi-Ownership Integrity)**, ownership is visually unmistakable across every list, chip, and manifest:

```
+---------------------------------------------------------------------------------------------------+
| Ownership Category           | Primary Token | Background   | Text Color | Visual Purpose         |
+------------------------------+---------------+--------------+------------+------------------------+
| Company-Owned (COC)          | #6D28D9       | #EDE9FE      | #4C1D95    | Purple badge: Company  |
|                              | (Deep Violet) | (Soft Lilac) |            | asset, rental applies  |
+------------------------------+---------------+--------------+------------+------------------------+
| Party/Customer-Owned (POC)   | #0369A1       | #E0F2FE      | #075985    | Ocean Blue: Zero rent, |
|                              | (Ocean Cyan)  | (Pale Sky)   |            | return to same client  |
+------------------------------+---------------+--------------+------------+------------------------+
| Vendor-Owned (VOC)           | #B45309       | #FEF3C7      | #78350F    | Amber badge: Upstream  |
|                              | (Warm Ochre)  | (Pale Gold)  |            | supplier leased asset  |
+------------------------------+---------------+--------------+------------+------------------------+
```

---

## 4. Outdoor High-Contrast Sunlight Mode

Drivers on open trucks face severe sun glare. The **Sunlight Mode** toggles automatically via ambient light sensor or 1-tap header icon:
- Replaces subtle gray backgrounds with pure, stark `#FFFFFF` and `#000000`.
- Borders expand from $1\text{ dp}$ to $2.5\text{ dp}$ solid black.
- All non-essential shadows and blurred elevations are removed to maximize visual sharpness.
- Font weight jumps from `Medium (500)` to `Bold (700)`.
