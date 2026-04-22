from datetime import datetime
import json
from textual_plotext import PlotextPlot
from textual import on
from textual.app import App 
from textual.widgets import Digits, Header, Button, Input, Label, ListView, ListItem,TabbedContent,TabPane,Header
from textual.containers import CenterMiddle, Container,Center, Horizontal, VerticalGroup
import os

class Timer(Digits):
    def __init__(self):
        super().__init__()
        self.update("0")
        self.total_time = 0

    def run_timer (self):
        self.active_timer = self.set_interval(60,self.change_value)

    def change_value (self):
        self.total_time += 1
        self.update(str(self.total_time))
        task_time = self.app.query_one("#tasklist", ListView).highlighted_child
        if isinstance(task_time, TaskItem):
            if task_time.task_time == self.total_time:
                os.system("paplay /home/jacob/Downloads/faaah.mp3 &")

    def stop_timer(self):
        self.active_timer.stop()

    pass

class StopWatch(VerticalGroup):

    def compose(self):
        yield Button("Start", id="start", variant="success")
        yield Button("Stop", id="stop", variant="error")
        yield Timer()

    @on(Button.Pressed,"#stop")
    def stop_timer(self):
        task = self.app.query_one("#tasklist", ListView).highlighted_child
        self.query_one("#stop",Button).display = False
        self.query_one("#start", Button).display = True
        timer = self.query_one(Timer)
        if isinstance(task,TaskItem):
            task.completetime += int(timer.total_time)
            self.app.daily_time[int(self.app.today)] += int(timer.total_time)
            task.query_one(Label).update(task.refresh_label())
            task.set_task()
        timer.stop_timer()
        timer.total_time = 0
        timer.update("0")


    @on(Button.Pressed,"#start")
    def start_timer(self):
        self.query_one("#start",Button).display = False
        self.query_one("#stop", Button).display = True
        timer = self.query_one(Timer)
        timer.run_timer()


class TaskItem(ListItem):
    def __init__(self, name: str, time: int, complete: bool, completetime: int):
        super().__init__(Label(f"[Minutes: {time} | Name: {name} | Completed Time {completetime}]"))
        self.task_time = time
        self.task_name = name
        self.complete = complete
        self.completetime = completetime
        self.set_task()
   
    def refresh_label(self):
        label =f"[Minutes: {self.task_time} |{self.task_name}| Completed Minutes {self.completetime} ]"
        return label

    def set_task(self):
        if self.complete == False:
            self.styles.background = None
        else:
            self.styles.background = "green"


class TaskApp(App):
    BINDINGS = [("t", "toggle_tabs","Switch Tabs")]
    def action_toggle_tabs(self):
        tabs = self.query_one(TabbedContent)
        if tabs.active == "tab1":
            tabs.active = "tab2"
        else:
            tabs.active = "tab1"

    def compose(self):
        yield Header()
        with Container(id="input_task"):
            with TabbedContent(id="tabs"):
                with TabPane("setup",id="tab1"):
                    yield Input(placeholder="Task Name",id="taskname")
                    yield Input(placeholder="Time in minutes",id="tasktime")
                    yield Center(Button("Add Task",id="add_btn"),)
                with TabPane("timer",id="tab2"):
                    yield CenterMiddle(StopWatch(id= "stopwatch"))


        with Container(id="list_task"):
            yield Label("Tasks:")
            yield ListView(id="tasklist")
        with Container(id="eval_task"):
            yield CenterMiddle(Label(f"How was the task"))
            yield CenterMiddle(Button("Complete", id="com_btn"))
            yield Horizontal(Button("Good", id="good_btn",variant="success"),Button("Okay", id="okay_btn"),Button("Bad", id="bad_btn",variant="error"))
            yield CenterMiddle(Button("Delete",id="delete"))
        with Container(id="graph"):
            yield PlotextPlot(id="daily_plot")


    def on_mount(self):
        self.history_log = {}
        self.today = 0 
        self.true_data = 12
        self.daily_time = [0,0,0,0,0,0,0]
        self.load_tasks()
        self.week_check()
        self.set_interval(10,self.save_tasks)
        self.set_interval(3,self.update_graph)
        self.query_one("#taskname").focus()


    @on(Button.Pressed,"#delete")
    def delete_task (self):
        selected_item = self.query_one("#tasklist", ListView).highlighted_child
        if isinstance(selected_item, TaskItem):
            self.notify(f"Just deleted {selected_item.task_name}")
            selected_item.remove()
        
    def week_check(self):
        if int(datetime.today().day) != self.true_data:
            if int(self.true_data) >= 30:
                diff = self.true_data - (self.true_data - int(datetime.today().day))
            else:
                today  = int(datetime.today().day)
                diff = today - int(self.true_data)
            self.today += diff % 7 
            if self.today >= 7:
                self.today = 0
            self.daily_time[self.today] = 0
            days = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
            self.notify(f"Now it is {days[self.today]}")
            items = self.query_one("#tasklist",ListView).children
            for tasks in items:
                if isinstance(tasks, TaskItem):
                    tasks.reset_styles()
                    tasks.complete = False
                    tasks.completetime = 0
                    tasks.refresh_label()
                    tasks.set_task()
                
   
    @on(Button.Pressed, "#com_btn")
    def task_complete(self):
        selected_item = self.query_one("#tasklist",ListView).highlighted_child
        if isinstance(selected_item, TaskItem):
            selected_item.complete = True
            selected_item.styles.background = "green"


    def update_graph(self):
        plot = self.query_one("#daily_plot", PlotextPlot)
        plt = plot.plt
        plt.clear_figure() 
        plt.plot(self.daily_time, marker="dot", color="green")
        plt.ylabel("Minutes")
        plt.xlabel("Days")
        plt.title("Weekly Progress")
        plot.refresh()



    @on(Button.Pressed,"#add_btn")
    def add_task (self):
        name = self.query_one("#taskname", Input).value
        try:
            time_val = int(self.query_one("#tasktime", Input).value or 0)
        except ValueError:
            time_val = 0

        item = TaskItem(name,time_val,False,0)
        self.query_one("#tasklist", ListView).append(item)
        self.notify(f"Added {name}")
    
    def load_tasks (self):
        try:
            with open("task.json", "r") as file:
                saved_data = json.load(file)
                self.today = saved_data["today"]
                self.true_data = saved_data["today_true"]
                self.daily_time = saved_data["graph"]
                
                for name in saved_data["tasks"]:
                    if saved_data["tasks"][name][1] == True:
                        item = TaskItem(name,saved_data["tasks"][name][0],saved_data["tasks"][name][1],saved_data["tasks"][name][2])
                        self.query_one("#tasklist", ListView).append(item)
                    else:
                        item = TaskItem(name,saved_data["tasks"][name][0],saved_data["tasks"][name][1],saved_data["tasks"][name][2])
                        self.query_one("#tasklist", ListView).append(item)
                        item.set_task()
        except (FileNotFoundError, json.JSONDecodeError):
            self.notify("Error no task where loaded")
        try:
            with open("output.json", "r") as file:
                log = json.load(file)
                self.history_log = log
        except (FileNotFoundError, json.JSONDecodeError):
            self.notify("Error no task where loaded")
            
        
            
            
    def log_rating(self, rating):
        selected = self.query_one("#tasklist", ListView).highlighted_child
        if isinstance(selected, TaskItem):
            today = datetime.today().strftime("%Y-%m-%d")
        
            day_entry = self.history_log.setdefault(today, {})
        
            if selected.task_name in day_entry:
                self.notify("This task is already logged for today")
            
            day_entry[selected.task_name] = {
                "goal_minutes": selected.task_time,
                "actual_minutes": selected.completetime,
                "completed": selected.complete,
                "rating": rating
            }
            with open("output.json", "w") as file:
                json.dump(self.history_log,file, indent=4)


    def save_tasks(self):
        data_save = {}
        data_save["tasks"] = {}
        task_data = "task.json"
        data_save["today_true"] = int(datetime.today().day)
        data_save["today"] = self.today
        data_save["graph"] = self.daily_time
        for task in self.query_one("#tasklist", ListView).children:
            if isinstance(task, TaskItem):
                data_save["tasks"][task.task_name] = [task.task_time, task.complete, task.completetime]
                task.refresh_label()
                task.set_task()
        with open(task_data, "w") as file:
            json.dump(data_save,file,indent=4)
        with open("output.json", "w") as file:
            json.dump(self.history_log,file, indent=4)


    @on(Button.Pressed,"#good_btn")
    def good_btn (self):
        selected_item = self.query_one("#tasklist",ListView).highlighted_child
        if isinstance(selected_item, TaskItem): 
            if selected_item.task_time > 70:
                selected_item.task_time += 5
                selected_item.query_one(Label).update(selected_item.refresh_label())
                self.notify(f"Increased time for {selected_item.task_name}")


                self.log_rating("Good")
                return
            else:
                selected_item.task_time += 10
                selected_item.query_one(Label).update(selected_item.refresh_label())
                self.notify(f"Increased time for {selected_item.task_name}")


                self.log_rating("Good")
                return
            
        
    @on(Button.Pressed,"#okay_btn")
    def okay_btn (self):
        self.notify("you Pressed okay")
        selected_item = self.query_one("#tasklist",ListView).highlighted_child
        if isinstance(selected_item, TaskItem):
            self.notify(f"Keeping {selected_item.task_name} the same")

            self.log_rating("Okay")
            return

            


    @on(Button.Pressed,"#bad_btn")
    def bad_btn (self):
        self.notify("you Pressed Bad")
        selected_item = self.query_one("#tasklist",ListView).highlighted_child
        if isinstance(selected_item, TaskItem):
            if selected_item.task_time <= 0:
                self.notify(f"Task is already 0")

                self.log_rating("Bad")
                return
            else:
                if selected_item.task_time > 70:
                    selected_item.task_time -= 5
                    selected_item.query_one(Label).update(selected_item.refresh_label())

                    self.notify(f"Increased time for {selected_item.task_name}")

                    self.log_rating("Bad")
                    return
                else:
                    if selected_item.task_time <= 0:
                        self.notify(f"Task is already 0")

                        self.log_rating("Bad")
                    else:
                        selected_item.task_time -= 10
                        selected_item.query_one(Label).update(selected_item.refresh_label())

                        self.notify(f"Decreased time for {selected_item.task_name}")

                        self.log_rating("Bad")
                        return


    CSS = """
    Screen {
            layout: grid;
            grid-size: 2 2;
            align: center middle;
        }
    Container {
            border: round lightblue;
            width: 100%;
            height: 100%;
            align: center middle;
            }
    Horizontal{
            align: center middle;
            width: 100%;
            height: auto;
            }
    Horizontal Button{
            margin: 0 1;
            }
    #input_task{
            height: 100%;
            }
    TabbedContent{
            height:100%;
            }
    TabPane{
            display: none;
            }
    TabPane.-active{
            display: block;
            }
    Tabs{
            dock: top;
            width: 100%;
            }
    #tab1 {
            align: center middle;
            }
    #tab2{
            align: center middle;
            }
    #stopwatch{
            align: center middle;
            width: auto;
            height: auto;
            }
    StopWatch > * {
            margin: 1 0;
            text-align: center;
            }
    Timer{
            width: auto;
            }
    #stop {
            display: none;
            }
    """





if __name__ == "__main__":
    TaskApp().run()
    
