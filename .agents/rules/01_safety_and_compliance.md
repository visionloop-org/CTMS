# Rule: Safety, PESO & Regulatory Compliance Invariants

## Prime Safety Directives for All Agents & Developers

1. **Zero-Tolerance Hydrostatic Test Interlock:**
   - Under statutory PESO (Petroleum and Explosives Safety Organization) and SMPV rules, high-pressure gas cylinders must undergo hydrostatic stretch testing every 5 years (or every 2 years for corrosive/specialty gases).
   - **Hard Rule:** Any cylinder where `CurrentDate >= hydro_test_due_date` MUST be immediately locked from filling, batching, and dispatch.
   - Any API or UI flow attempting to assign an overdue cylinder to a filling batch or mark it as `PLANT_FILLED` must return an HTTP `403 FORBIDDEN` with error code `HYDRO_TEST_OVERDUE`.
   - Never implement a feature that permits overriding this lock without verified administrative credentials and an official PESO test certificate upload.

2. **Gas Type Cross-Contamination Guard:**
   - Cylinders dedicated to oxidizers (e.g., Oxygen, Nitrous Oxide) must NEVER be filled with combustible or inert gases, and vice-versa.
   - State transition and pre-fill validators must assert:
     ```kotlin
     require(cylinder.currentGasType == manifold.gasType) {
         "Gas type mismatch: Cannot fill ${manifold.gasType} into ${cylinder.currentGasType} cylinder"
     }
     ```

3. **Tare Weight Loss Tolerance:**
   - If a cylinder's measured empty weight deviates from its stamped tare weight by $>5\%$, it indicates structural wall erosion or internal corrosion.
   - The system must automatically quarantine the cylinder with status `QUARANTINED_DAMAGED` and alert the plant inspector.

4. **Medical Oxygen Batch Integrity:**
   - For all Medical Oxygen (IP) cylinders:
     - Batch number, filling pressure, ambient temperature, operator ID, and purity percentage ($\ge 99.5\%$) must be recorded.
     - Dispatch manifests and Delivery Challans must link directly to the approved Laboratory Purity Certificate.
