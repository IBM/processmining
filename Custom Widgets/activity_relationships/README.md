# Activity Relationships Custom Widget
This custom widget displays the predecessors and the successors of all the activities. For each relationship, it shows:
- frequency
- average pathtime

This widget is useful to complement the activity relationship view in IBM Process Mining.

Caution: by default the widget computes the calendar duration. It does not take into consideration the business hours.

An approximation of the business pathtime (removing non-business hours and week ends) if available, but it does not take into consideration the actual project business hours settings. You might find differences with the waiting time computed by process mining.