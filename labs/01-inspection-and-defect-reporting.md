# Lab 1: Code inspection and defect reporting

**Aim:** inspect inherited code systematically, report defects so that someone else could act on them, and prioritise them by risk.
**Time:** about 75 minutes.
**Assignment 1 criterion:** Inspection, Completion and Defect Resolution.

## The requirements

The bookings feature was meant to meet these requirements. Inspection compares what the code **does** with what it **should** do.

| ID | Requirement |
|---|---|
| R1 | A logged-in user can book between 1 and 4 places at an upcoming event. |
| R2 | Bookings must never exceed the event's capacity. |
| R3 | A user can hold only one booking per event. |
| R4 | Events that have already started cannot be booked. |
| R5 | Users can view, filter and cancel **their own** bookings only. |
| R6 | The organiser can see the attendee list, including any notes. |
| R7 | The event page shows the correct number of places left. |

## 1. Create a defect report template

Good defect reports are consistent. Create the file `.github/ISSUE_TEMPLATE/defect.md`:

```markdown
---
name: Defect report
about: Report a defect found during inspection or testing
labels: defect
---

**Summary**

**Steps to reproduce**
1.

**Expected result**

**Actual result**

**Severity** (Critical / High / Medium / Low):

**ISO/IEC 25010 characteristic** (e.g. functional correctness, security, reliability, usability, maintainability):

**Requirement affected:**

**Evidence** (screenshot, failing test, log):
```

Commit and push it:

```bash
git add .github/ISSUE_TEMPLATE/defect.md
git commit -m "Add defect report template"
git push
```

## 2. Inspect with a checklist

Open `app/bookings.py`, `app/templates/event.html` and `app/templates/my_bookings.html` side by side. Work through each question below for every function and template. Write down anything suspicious, even if you are not sure yet.

| Area | Questions to ask |
|---|---|
| Requirements | Is every requirement R1 to R7 implemented? Completely? |
| Boundaries | What happens at 0, 1, the maximum and one above it? At exactly full capacity? |
| Input | What if a field is missing, empty, negative, very long, or not a number? |
| Authorisation | Can a user act on something that belongs to someone else? |
| Injection | Is user input ever built into SQL or HTML as a string? Look for `text(`, f-strings and `|safe`. |
| Consistency | Is the same rule calculated in more than one place? Do they agree? |
| Errors | What does the user see when something goes wrong? Could anything cause a 500 error? |
| Maintainability | Is the code readable? Is anything duplicated or doing too much? |

Tip: you are reviewing code that an AI helped to write. AI-generated code usually *looks* plausible, so read what it actually does, line by line.

## 3. Confirm by trying it

A suspicion is not a defect until you can reproduce it. Run the app and try your ideas in the browser.

**Worked example.** In `book()` the capacity check is:

```python
remaining = event.capacity - booked
if party_size > remaining + 1:
```

That `+ 1` looks wrong. To confirm it, log in as `bob` and open **CI Pipelines Q&A**, which has a capacity of 4. Book 4 places. Then book 1 more. The second booking succeeds, so the event now has 5 people booked for 4 places.

## 4. Report it

Open **Issues → New issue → Defect report** and fill it in. For the worked example:

> **Summary:** Bookings can exceed event capacity by one place
> **Steps to reproduce:** 1. Log in as bob. 2. Open "CI Pipelines Q&A" (capacity 4). 3. Book 4 places. 4. Book 1 more place.
> **Expected result:** The second booking is rejected with "not enough places left".
> **Actual result:** The booking is accepted; 5 places are booked for an event of 4.
> **Severity:** High
> **ISO/IEC 25010 characteristic:** Functional suitability (functional correctness)
> **Requirement affected:** R2
> **Evidence:** `book()` in app/bookings.py checks `party_size > remaining + 1`.

You can also create issues from the terminal: `gh issue create`.

## 5. Your turn

Find and report **at least four more** defects using the checklist. Between them, try to cover:

- one missing or incomplete requirement;
- one input that can crash the app (a 500 error);
- one problem with who is allowed to do what;
- one inconsistency between two parts of the feature.

There are more than four to find.

## 6. Prioritise

Not every defect matters equally. For each issue, consider **impact** (what is the worst that happens?) and **likelihood** (how easily could it happen?). Add a label such as `priority: high` and be ready to explain your order: security and data problems usually come before cosmetic ones.

## Checkpoint

You should have a defect template in the repository and at least five well-written issues, each with steps to reproduce, severity, a quality characteristic and a priority.

## Apply it to Assignment 1

Write down the requirements your assignment feature was meant to meet (Appendix A of the brief), then run the same checklist over your draft. Log every confirmed defect as an issue using the same template.

## Stretch

Read the [ISO/IEC 25010 product quality model](https://iso25000.com/index.php/en/iso-25000-standards/iso-25010) and add a characteristic you had not considered to one of your reports.
