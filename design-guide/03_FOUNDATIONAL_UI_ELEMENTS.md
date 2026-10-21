# Foundational UI Elements
## Buttons, Form Inputs, Bottom Sheets, Status Badges & Floating Indicators

---

## 1. Action Buttons & Touch Target Standards

Drivers wear industrial work gloves and operate while standing or in moving vehicles. All primary action touch targets are enlarged to a minimum height of **$56\text{ dp}$** with an interior padding of at least $16\text{ dp}$.

```
+--------------------------------------------------------------------------------------------------+
|                                    STANDARD ACTION BUTTONS                                       |
+--------------------------------------------------------------------------------------------------+
|  Primary Action (56dp)       [   START DELIVERY SCAN (20 CYLINDERS)   ]  #1E40AF (White Text)    |
|  Secondary Action (56dp)     [      + COLLECT EMPTY CYLINDERS        ]  Outline 2dp (#1E40AF)   |
|  Critical / Hazard (56dp)    [       FLAG AS DAMAGED / REJECT        ]  #DC2626 (White Text)    |
|  Quick Scan Floating Action  (  [QR] SCAN  )                             Circular 64dp FAB       |
+--------------------------------------------------------------------------------------------------+
```

### Jetpack Compose Primary Button Specification
```kotlin
@Composable
fun IndustrialPrimaryButton(
    text: String,
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
    enabled: Boolean = true,
    icon: ImageVector? = null
) {
    Button(
        onClick = onClick,
        enabled = enabled,
        modifier = modifier
            .fillMaxWidth()
            .height(56.dp),
        shape = RoundedCornerShape(8.dp),
        colors = ButtonDefaults.buttonColors(
            containerColor = Color(0xFF1E40AF),
            contentColor = Color.White,
            disabledContainerColor = Color(0xFF94A3B8)
        ),
        elevation = ButtonDefaults.buttonElevation(defaultElevation = 2.dp)
    ) {
        if (icon != null) {
            Icon(imageVector = icon, contentDescription = null, modifier = Modifier.size(24.dp))
            Spacer(modifier = Modifier.width(12.dp))
        }
        Text(text = text.uppercase(), style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold)
    }
}
```

---

## 2. Input Fields & Numeric Steppers

### 2.1 Large Text Input ($56\text{ dp}$ Height)
- Floating label with clear placeholder.
- Trailing 1-tap clear button (`X`) for fast clearing.
- Auto-capitalization for alphanumeric serial numbers.

### 2.2 Numerical Keypad Optimization
When entering quantities, tare weights, or OTP codes, the native numeric keypad (`KeyboardType.Number` or `KeyboardType.Decimal`) displays automatically with oversized digits.

---

## 3. Status Badges & Chips

Badges visually encode state without requiring user reading time:

```
+---------------------------------------------------------------------------------------------------+
| Status Enum                  | Background  | Text Color  | Visual Spec                            |
+------------------------------+-------------+-------------+----------------------------------------+
| PLANT_EMPTY                  | #F1F5F9     | #475569     | Subtle grey pill: Empty inventory      |
| PLANT_FILLED                 | #DCFCE7     | #15803D     | Crisp green pill: Ready for dispatch   |
| IN_TRANSIT_OUTWARD           | #E0F2FE     | #0369A1     | Sky blue pill: En route to customer    |
| CUSTOMER_HELD                | #EDE9FE     | #6D28D9     | Violet pill: Holding timer active      |
| QUARANTINED_DAMAGED          | #FEE2E2     | #B91C1C     | Crimson pill: Safety lockout active    |
| MAINTENANCE_TESTING          | #FEF3C7     | #B45309     | Amber pill: At hydro-test station      |
+---------------------------------------------------------------------------------------------------+
```

---

## 4. Modal Bottom Sheets

Secondary workflows (such as flagging collar damage or selecting customer delivery bays) appear as swipeable bottom sheets:
- **Sheet Radius:** Rounded top corners ($16\text{ dp}$).
- **Drag Handle:** Prominent horizontal handle ($4\times 36\text{ dp}$) centered at the top.
- **Dismissibility:** Swipe down to dismiss, or tap persistent top-right close icon.

---

## 5. Offline Floating Status Indicator

When network connectivity drops, the application displays a persistent, non-intrusive floating indicator pinned below the top app bar:

```
+--------------------------------------------------------------------------------------------------+
| [!] WORKING OFFLINE — 14 SCANS SAVED TO ROOM DB (AUTO-SYNC ENQUEUED)            [SYNC NOW]       |
+--------------------------------------------------------------------------------------------------+
```
- **Offline Active:** Amber background (`#FEF3C7`), text color `#92400E`, shows exact count of pending outbox records.
- **Sync in Progress:** Blue background (`#E0F2FE`) with circular spinning progress indicator.
- **Sync Complete:** Green transient banner (`#DCFCE7`) displayed for 3 seconds before auto-dismissing: *"All transactions synced with Zoho Books."*
