# Process App Example: transforming P2P CSV files
The file [P2P.zip](P2P.zip) contains 3 CSV files extracted from a Procure to Pay application (like SAP).

Each file in [P2P.zip](P2P.zip) includes events (steps) from the processes involved in the end-to-end P2P process:
- procurement.csv
- requisition.csv
- invoice.csv

The data transformation python [code](P2P_data_xform_lab.py) shows how to extract these files from [P2P.zip](P2P.zip), and how to use Pandas to transform these data sources in a Process Mining event log, by creating specific fields and merging tables.
