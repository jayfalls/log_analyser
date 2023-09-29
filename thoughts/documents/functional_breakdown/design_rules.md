##### up:: [Functional Breakdown](../functional_breakdown.md)

##### related:: [Third Day](../days/29Sept2023.md)

# Design Rules

# Backend

The analyser should be designed as a backend, this will allow for:

- **Easy access**: Gives the option for team members and clients likewise to access the tool.

- **Centralisable data**: Gives way to automatically collecting logs, this can have many benefits such as catching fail states before they occur, analysing log data if log generators are offline/damaged/stolen, finding larger/underlying patterns and trends between different operators etc...

- **Storable Inferences**: Rather than just throwing away the parsed logs and analysed data, it can be saved to later provide further insights

- **Puzzle Piece**: Allows the tool to fit into a larger toolbox

- **Automatic Detection/Insights**: If logs from all clients are collected and processed through this backend, it can provide automatic monitoring and detection of events

# Don't Make it Perfect, Just Make It

The deadline is tight, and I am inexperienced in making this type of program. There are many things that can easily cause scope creep. As such, these general directives should serve to meet the deadline on time:

- Focus on what matters. Don't go on tangents, only implement what is required by the design doc
  
  - Add ideas for future improvements to the sentiments folder

- Don't overthink architecture, do what comes naturally. When the project is complete, you'll have the proper hindsight to consider a scalable architecture

- Don't worry too much about Big O

- Don't worry too much about edge-cases
