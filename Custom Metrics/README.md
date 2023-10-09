# Custom Metrics

Custom metrics are javascript functions called for each case. The function access the events of a case to retrieve values and to compute a new metric. Custom metrics are case-level metrics.

- Refer to the documentation for more details.
- Refer also to the Advanced Filters documentation to list the functions available for each event.


## Leadtime without non-working business hours
Netleadtime computes the leadtime of a case, and removes the off-office hours and week-ends. It assumes that the activities start and end during working-hours.

[NetLeadtime.js](NetLeadtime.js)

## Case quality
This metrics associate a quality value (0-100) to each case, which would typically decrease if deviations occur.

[CaseQuality.js](CaseQuality.js)

## Case SLA
This metrics associate an SLA (double value) to each case, based on a case attribute like “priority”.

[CaseSLA.js](CaseSLA.js)


