# SQA1 labs: from draft to production quality

These labs take you through the quality assurance process you will use in **Assignment 1**, step by step, on a different application.

The Ada Events site in this repository has one new feature, **bookings**, drafted quickly by a colleague with an AI coding assistant. It runs, but it has problems. Across the labs you will inspect it, report its defects, test it, secure it, measure and improve it, put quality gates around it, and decide whether it is ready to release.

> The defects here are **not** the ones in your assignment. The labs teach the techniques and tools; applying them to your assignment feature is up to you.

## The labs

| Lab | Topic | Time | Assignment 1 criterion |
|---|---|---|---|
| [0](00-setup.md) | Set up and explore | 30 min | All |
| [1](01-inspection-and-defect-reporting.md) | Code inspection and defect reporting | 75 min | Inspection, Completion and Defect Resolution |
| [2](02-testing-and-regression-tests.md) | Testing and regression tests | 75 min | Testing |
| [3](03-test-effectiveness.md) | Coverage, mutation testing and testable design | 90 min | Testing; Code Quality |
| [4](04-security-assurance.md) | Security assurance | 75 min | Security Assurance |
| [5](05-code-quality-and-measurement.md) | Code quality and measurement | 60 min | Code Quality and Measurement |
| [6](06-ci-quality-gates.md) | Continuous integration as a quality gate | 75 min | CI/CD and Git Practices |
| [7](07-ai-verification-and-release.md) | Verifying AI output and making a release recommendation | 75 min | All, especially the release recommendation |

Do the labs in order: each one builds on the code you changed in the previous one.

## How each lab works

- **Worked example:** follow the steps exactly. You will see the technique applied to one defect.
- **Your turn:** apply the same technique yourself to another defect or requirement.
- **Apply it to Assignment 1:** a short prompt to carry the technique across to your assignment feature.
- **Stretch:** optional extras if you finish early.

## Ground rules

- Work on a branch for every change, and merge through a pull request. This is good practice and it builds the evidence you will need in Assignment 1.
- Commit little and often, with clear messages.
- AI tools are allowed in the labs. Lab 7 looks at how to verify what they produce.
- Stop your codespace when you finish a session.
