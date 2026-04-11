# Region-Based OCR Accuracy Improvements
## Status: ✅ Plan Approved - Implementation Started

### Phase 1: OCRService Updates (IN PROGRESS)
- [✅] 1.1 Add _detect_document_type()
- [✅] 1.2 Add _try_rotations()
- [✅] 1.3 BALANCED strict + fallback regions (40/40 split, PSM7/6, CLAHE)

- [✅] 1.4 Enhanced preprocessing + fallbacks

**Phase 1 ✅ COMPLETE & FIXED** (user feedback: strictness balanced)

### Phase 2: ParserService Updates (Pending Phase 1)
- [ ] 2.1 Strict region-only extraction

### Phase 3: Integration + Tests (Pending Phase 1-2)
- [ ] 3.1 Update expense_service integration
- [ ] 3.2 Add 4 new tests
- [ ] 3.3 Test with Backend/uploads/ receipts

### Phase 4: Validation (Pending Phase 1-3)
- [ ] 4.1 Run pytest
- [ ] 4.2 Manual test accuracy (target 80-90%)

**Current: Phase 1 ✅ Approved by user**

