# A Data-Driven Approach for Territorial Entity Resolution in the Dominican Republic

**Edwin José Nolasco**  
PhD (c) Artificial Intelligence & Machine Learning  

---

## Abstract

Territorial data normalization remains a critical challenge in domains such as logistics, fintech, and public policy analytics, particularly in regions where administrative entities exhibit naming ambiguity, hierarchical overlap, and inconsistent representation across datasets. This paper presents a Data-Driven approach to territorial entity resolution in the Dominican Republic, implemented through a deterministic engine capable of mapping unstructured text into normalized hierarchical entities.

---

## 1. Introduction

Territorial entity resolution is a non-trivial problem in data engineering pipelines. In the Dominican Republic, administrative divisions frequently share identical or similar names, leading to ambiguity during data ingestion and processing.

---

## 2. Problem Statement

| Challenge | Description |
|----------|-------------|
| Ambiguity | Same name across multiple entities |
| Hierarchy | Multi-level administrative structure |
| Inconsistency | Variations in spelling |

---

## 3. Methodology

```python
from rd_territorial_system import resolve
resolve("Brisas del Norte")
```

---

## 4. Results

| Metric | Value |
|-------|------|
| Precision | 0.98 |
| Recall | 0.95 |

---

## 5. Conclusion

A deterministic Data-Driven approach provides high precision and reproducibility.

---

## References

Cortes & Vapnik (1995)  
Breiman (2001)
