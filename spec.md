# Georgia State University  
## CSC 4210/6210 Computer Architecture  
### Spring Semester 2026  

# Processor Design Semester Project - Task2

**Release Date:** 03-10-2026  
**Due Date:** 03-20-2026  

## Truth Table → Boolean Equation → K-Map Simplification

You are designing combinational logic as part of a processor datapath. In real hardware design, logic often begins as a truth table which must be converted into a Boolean equation and simplified for efficient implementation.

---

## Section 1 — Input System

1. Allow user argument to specify the number of input variables (n ≥ 2)  
2. Accept a truth table provided by the user  
3. You may design any input method (console input, file input, interactive prompt, etc.)  
4. Validate the truth table:  
   a. The table must contain 2ⁿ rows  
   b. Each input combination must appear exactly once  
   c. Output values must be 0 or 1  

---

## Section 2 — Boolean Expression & Simplification

1. Convert the truth table into a Boolean equation:  
   a. The user must be able to select one of the following forms:  
      i. SOP (Sum of Products), POS (Product of Sums)  
      ii. Optionally you have choice to choose from SOP/POS  
   b. The program must:  
      i. Generate the canonical equation (SOP or POS)  
      ii. Optionally you have choice to choose from SOP/POS  
      iii. List the corresponding minterms or maxterms  

2. Simplify the Boolean equation  
   a. For functions with 2–4 variables, construct a Karnaugh Map (K-Map) and perform grouping to derive the simplified Boolean expression.  

---

## Section 3 — Validation

1. Validate the simplified expression by evaluating it for all input combinations and comparing it with the original truth table  

---

## Program Output

1. Truth table  
2. Canonical equation (SOP or POS)  
3. Minterm / Maxterm list  
4. K-Map grouping  
5. Simplified Boolean expression  
6. Validation result (PASS / FAIL)  

---

## Deliverables

1. Source code (Python preferred)  
2. README with instructions  
3. Submit code to GitHub  
4. 1–2 minute demo video explaining code and displaying input/output  
   a. Either upload it to iCollege or storage of your choice with necessary viewing permissions  
5. Can video recordings be uploaded to YouTube? Yes or No.  