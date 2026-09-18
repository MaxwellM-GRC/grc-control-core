# Portfolio Glossary

This glossary defines shared terms used across the Automated GRC proof of
concept portfolio. It is written for control owners, reviewers, and auditors.
Technical implementation details remain in each POC's evidence contract and
production design documentation.

## Continuous or near real time assurance

An approach that evaluates control evidence repeatedly as business activity
occurs or on a frequent schedule, rather than relying only on a point in time
test. Event triggered monitoring is closer to real time; scheduled monitoring
provides near real time assurance.

## Evidence source details

The record of where evidence came from, what period it covers, when it was
collected, and the checks used to confirm it has not changed. These details
allow a reviewer to understand and repeat the review.

## Evidence validation check

A check performed before control evaluation to confirm that required evidence
is present, covers the defined review period, contains the required records and
fields, and has not changed after collection. The review stops when this check
cannot be completed successfully.

## Complete population check

A comparison of the records evaluated by the control to the defined population
in scope. It identifies records that were omitted, unexpected, or evaluated
more than once so a clean result cannot be based on an incomplete population.

## Finding

A condition identified by the control that requires review or response. A
finding is not automatically a final risk decision or a conclusion that a
control failed; authorized people assess and decide the response.

## Exception

A documented departure from an approved requirement. An exception may be
accepted only through the organization's authorized approval process and for
the approved time period.

## Consistent finding identifier

A repeatable identifier assigned to the same condition. It allows repeated
monitoring runs to update one case instead of creating duplicate cases.

## Last complete collection point

The latest point through which all required evidence was collected and
validated successfully. It advances only after a complete collection, helping
the next run avoid skipped activity when a source fails, arrives late, or is
incomplete.

## Ready for review

Contains the information an authorized reviewer needs to assess and act on an
item, including the condition, evidence references, accountable owner,
response target, and closure requirements.

## Human approval boundary

The limit of automation. Automation may collect evidence, identify conditions,
and route cases, but authorized people make and record remediation, risk
acceptance, and closure decisions.

