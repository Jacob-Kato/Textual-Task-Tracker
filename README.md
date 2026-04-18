# Textual Task Tracker
A high-performance Terminal User Interface (TUI) productivity application built with Python and the Textual framework. This app tracks task goals, real-time effort via a stopwatch, and visualizes weekly progress with live line graphs.
## Features
Real-Time Visualization
    Weekly Line Graph: Integrated textual-plotext to visualize total minutes worked per day.
    Automatic Date Shifting: The app uses datetime math to detect missed days and automatically shift graph data to the correct index.
### Integrated Stopwatch
    Tabbed Interface: Switch between Task Setup and the Live Timer using a dedicated TabbedContent view.
    Precision Tracking: Minutes worked are automatically appended to specific tasks and mirrored on the daily progress graph.
    Audio Notifications: Triggers a system sound alert when a stopwatch reaches the predefined task goal.
### Dynamic Task Logic
    Performance Ratings: Adjust task duration goals dynamically based on "Good," "Okay," or "Bad" performance.
    Stateful Widgets: Custom TaskItem widgets manage their own completion status and visual styling (CSS).
### Persistence & Logging
    JSON Database: All tasks, graph history, and timestamps are saved to task.json on a 10-second background interval.
    Output Logging: Generates a detailed history log capturing snapshots of work performed, goal vs. actual time, and user ratings.
### Tech Stack
    Framework: Textual (TUI Framework)
    Graphing: Textual-Plotext
    Data: JSON for lightweight local persistence
    Logic: Python datetime and timedelta for calendar-aware automation
<img width="1426" height="785" alt="image" src="https://github.com/user-attachments/assets/3e1d6ac4-3eb9-4898-9b97-4b024448b2ac" />
