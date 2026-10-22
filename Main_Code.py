import tkinter as tk
from tkinter import ttk, messagebox

class PageReplacementSimulator:
    def __init__(self, root):
        self.root = root
        self.root.title("Page Replacement Algorithm Simulator")
        self.root.geometry("1180x820")
        self.root.minsize(900, 650)

        self.colors = {
            "navy": "#102A43", "navy_light": "#183B56", "teal": "#16B8A6",
            "teal_dark": "#0D9488", "background": "#F2F6F8", "white": "#FFFFFF",
            "text": "#243B53", "muted": "#627D98", "line": "#D9E2EC",
            "fault": "#E76F51", "hit": "#16B8A6", "blue": "#3C78A8",
            "gold": "#E9B44C", "empty": "#EAF0F4"
        }
        self.root.configure(bg=self.colors["background"])
        self.chart_mode = None
        self.chart_data = None

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TCombobox", padding=6, fieldbackground=self.colors["white"])
        style.configure("Treeview", background=self.colors["white"], foreground=self.colors["text"],
                        fieldbackground=self.colors["white"], rowheight=30, borderwidth=0,
                        font=("Segoe UI", 10))
        style.configure("Treeview.Heading", background=self.colors["navy_light"],
                        foreground=self.colors["white"], font=("Segoe UI", 9, "bold"), padding=8)
        style.map("Treeview", background=[("selected", "#C9F3EE")],
                  foreground=[("selected", self.colors["navy"])])

        header = tk.Frame(root, bg=self.colors["navy"], padx=26, pady=19)
        header.pack(fill="x")
        tk.Label(header, text="PAGE REPLACEMENT LAB", bg=self.colors["navy"], fg="#8DE3D8",
                 font=("Segoe UI", 9, "bold")).pack(anchor="w")
        tk.Label(header, text="Algorithm Simulator", bg=self.colors["navy"], fg=self.colors["white"],
                 font=("Segoe UI", 22, "bold")).pack(anchor="w", pady=(3, 0))

        controls = tk.Frame(root, bg=self.colors["white"], padx=20, pady=14,
                            highlightbackground=self.colors["line"], highlightthickness=1)
        controls.pack(fill="x", padx=20, pady=(16, 10))
        tk.Label(controls, text="REFERENCE STRING", bg=self.colors["white"], fg=self.colors["muted"],
                 font=("Segoe UI", 8, "bold")).grid(row=0, column=0, sticky="w", padx=(0, 8))
        self.page_entry = tk.Entry(controls, width=40, relief="flat", bg="#F2F6F8", fg=self.colors["text"],
                                   insertbackground=self.colors["teal_dark"], font=("Segoe UI", 11))
        self.page_entry.grid(row=1, column=0, sticky="ew", padx=(0, 18), ipady=8)
        tk.Label(controls, text="FRAME COUNT", bg=self.colors["white"], fg=self.colors["muted"],
                 font=("Segoe UI", 8, "bold")).grid(row=0, column=1, sticky="w", padx=(0, 8))
        self.frame_entry = tk.Entry(controls, width=10, relief="flat", bg="#F2F6F8", fg=self.colors["text"],
                                    insertbackground=self.colors["teal_dark"], font=("Segoe UI", 11))
        self.frame_entry.grid(row=1, column=1, sticky="ew", padx=(0, 18), ipady=8)
        tk.Label(controls, text="ALGORITHM", bg=self.colors["white"], fg=self.colors["muted"],
                 font=("Segoe UI", 8, "bold")).grid(row=0, column=2, sticky="w", padx=(0, 8))
        self.algo_var = tk.StringVar(value="FIFO")
        self.algo_menu = ttk.Combobox(controls, textvariable=self.algo_var,
                                      values=["FIFO", "LRU", "Optimal"], state="readonly", width=13)
        self.algo_menu.grid(row=1, column=2, sticky="ew", padx=(0, 18), ipady=3)

        button_frame = tk.Frame(controls, bg=self.colors["white"])
        button_frame.grid(row=1, column=3, sticky="e")
        self._button(button_frame, "Simulate", self.simulate, self.colors["teal_dark"]).pack(side="left", padx=(0, 8))
        self._button(button_frame, "Compare All", self.compare_all, self.colors["navy_light"]).pack(side="left", padx=(0, 8))
        self._button(button_frame, "Clear", self.clear, "#EAF0F4", self.colors["text"]).pack(side="left")
        controls.columnconfigure(0, weight=4)
        controls.columnconfigure(1, weight=1)
        controls.columnconfigure(2, weight=1)

        self.metrics_frame = tk.Frame(root, bg=self.colors["background"])
        self.metrics_frame.pack(fill="x", padx=20, pady=(0, 12))
        self.metric_values = {}
        for column, (key, title, color) in enumerate((
                ("faults", "PAGE FAULTS", self.colors["fault"]),
                ("hits", "PAGE HITS", self.colors["teal_dark"]),
                ("ratio", "HIT RATIO", self.colors["blue"]),
                ("requests", "REFERENCES", self.colors["gold"]))):
            card = tk.Frame(self.metrics_frame, bg=self.colors["white"], padx=15, pady=10,
                            highlightbackground=self.colors["line"], highlightthickness=1)
            card.grid(row=0, column=column, sticky="ew", padx=(0 if column == 0 else 8, 0))
            tk.Label(card, text=title, bg=self.colors["white"], fg=self.colors["muted"],
                     font=("Segoe UI", 8, "bold")).pack(anchor="w")
            value = tk.Label(card, text="--", bg=self.colors["white"], fg=color,
                             font=("Segoe UI", 20, "bold"))
            value.pack(anchor="w", pady=(3, 0))
            self.metric_values[key] = value
            self.metrics_frame.columnconfigure(column, weight=1, uniform="metric")
        self.comparison_label = tk.Label(root, text="", bg=self.colors["background"],
                                         fg=self.colors["muted"], font=("Segoe UI", 9))
        self.comparison_label.pack(fill="x", padx=22, pady=(0, 8))

        content = tk.Frame(root, bg=self.colors["background"])
        content.pack(fill="both", expand=True, padx=20, pady=(0, 18))
        table_panel = tk.Frame(content, bg=self.colors["white"],
                               highlightbackground=self.colors["line"], highlightthickness=1)
        table_panel.pack(side="left", fill="both", expand=True, padx=(0, 10))
        tk.Label(table_panel, text="SIMULATION STEPS", bg=self.colors["white"], fg=self.colors["navy"],
                 font=("Segoe UI", 10, "bold"), padx=14, pady=12).pack(anchor="w")
        table_body = tk.Frame(table_panel, bg=self.colors["white"])
        table_body.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        columns = ("step", "page", "frames", "result")
        self.steps_table = ttk.Treeview(table_body, columns=columns, show="headings", height=12)
        for column, title, width in (("step", "STEP", 62), ("page", "PAGE", 65),
                                     ("frames", "FRAME CONTENT", 260), ("result", "STATUS", 86)):
            self.steps_table.heading(column, text=title)
            self.steps_table.column(column, width=width, anchor="center" if column != "frames" else "w",
                                    stretch=column == "frames")
        table_scroll = ttk.Scrollbar(table_body, orient="vertical", command=self.steps_table.yview)
        self.steps_table.configure(yscrollcommand=table_scroll.set)
        self.steps_table.pack(side="left", fill="both", expand=True)
        table_scroll.pack(side="right", fill="y")
        self.steps_table.tag_configure("Fault", foreground="#B94B34")
        self.steps_table.tag_configure("Hit", foreground=self.colors["teal_dark"])

        charts_panel = tk.Frame(content, bg=self.colors["white"], width=370,
                                highlightbackground=self.colors["line"], highlightthickness=1)
        charts_panel.pack(side="right", fill="both", padx=(0, 0))
        charts_panel.pack_propagate(False)
        tk.Label(charts_panel, text="VISUAL ANALYSIS", bg=self.colors["white"], fg=self.colors["navy"],
                 font=("Segoe UI", 10, "bold"), padx=14, pady=12).pack(anchor="w")
        self.chart_canvas = tk.Canvas(charts_panel, height=300, bg=self.colors["white"],
                                      highlightthickness=0)
        self.chart_canvas.pack(fill="both", expand=True, padx=8)
        tk.Frame(charts_panel, bg=self.colors["line"], height=1).pack(fill="x", padx=14, pady=6)
        tk.Label(charts_panel, text="FINAL FRAME STATE", bg=self.colors["white"], fg=self.colors["muted"],
                 font=("Segoe UI", 8, "bold"), padx=14).pack(anchor="w")
        self.frames_canvas = tk.Canvas(charts_panel, height=160, bg=self.colors["white"],
                                       highlightthickness=0)
        self.frames_canvas.pack(fill="x", expand=True, padx=8, pady=(0, 8))
        self.chart_canvas.bind("<Configure>", self._redraw_charts)
        self.frames_canvas.bind("<Configure>", self._redraw_charts)
        self._draw_empty_charts()

    def _button(self, parent, text, command, background, foreground="white"):
        return tk.Button(parent, text=text, command=command, bg=background, fg=foreground,
                         activebackground=background, activeforeground=foreground,
                         relief="flat", borderwidth=0, padx=14, pady=9,
                         font=("Segoe UI", 9, "bold"), cursor="hand2")

    def _set_metrics(self, faults, requests):
        hits = requests - faults
        self.metric_values["faults"].config(text=str(faults))
        self.metric_values["hits"].config(text=str(hits))
        self.metric_values["ratio"].config(text=f"{hits / requests:.1%}")
        self.metric_values["requests"].config(text=str(requests))

    def _fill_steps(self, page_string, frames_history, steps):
        self.steps_table.delete(*self.steps_table.get_children())
        for index, (page, frames, step) in enumerate(zip(page_string, frames_history, steps), start=1):
            result = "Fault" if "Fault" in step else "Hit"
            frame_text = "  [  " + "  |  ".join("-" if value == -1 else str(value) for value in frames) + "  ]"
            self.steps_table.insert("", "end", values=(index, page, frame_text, result), tags=(result,))

    def _draw_empty_charts(self):
        self.chart_mode = None
        self.chart_data = None
        self._redraw_charts()

    def _redraw_charts(self, _event=None):
        if not hasattr(self, "chart_canvas"):
            return
        if self.chart_mode == "simulation":
            self._draw_simulation_chart(*self.chart_data)
        elif self.chart_mode == "comparison":
            self._draw_comparison_chart(*self.chart_data)
        else:
            self.chart_canvas.delete("all")
            self.chart_canvas.create_text(max(20, self.chart_canvas.winfo_width() / 2), 95,
                                          text="Run a simulation to see the fault timeline",
                                          fill=self.colors["muted"], font=("Segoe UI", 10))
            self.frames_canvas.delete("all")
            self.frames_canvas.create_text(max(20, self.frames_canvas.winfo_width() / 2), 55,
                                           text="Frame slots will appear here",
                                           fill=self.colors["muted"], font=("Segoe UI", 9))

    def _draw_simulation_chart(self, page_string, steps, algorithm, final_frames):
        canvas = self.chart_canvas
        canvas.delete("all")
        width = max(canvas.winfo_width(), 300)
        height = max(canvas.winfo_height(), 220)
        left, right, top, bottom = 40, width - 18, 42, height - 38
        faults = ["Fault" in step for step in steps]
        canvas.create_text(16, 13, anchor="w", text=f"{algorithm}  /  PAGE FAULT TIMELINE",
                           fill=self.colors["navy"], font=("Segoe UI", 9, "bold"))
        canvas.create_text(left - 10, top, anchor="e", text="Fault", fill=self.colors["muted"],
                           font=("Segoe UI", 8))
        canvas.create_text(left - 10, bottom, anchor="e", text="Hit", fill=self.colors["muted"],
                           font=("Segoe UI", 8))
        canvas.create_line(left, top, right, top, fill=self.colors["line"])
        canvas.create_line(left, bottom, right, bottom, fill=self.colors["line"])
        count = len(steps)
        for index, (page, fault) in enumerate(zip(page_string, faults)):
            x = left + (right - left) * (index / max(count - 1, 1))
            y = top + 12 if fault else bottom - 12
            color = self.colors["fault"] if fault else self.colors["hit"]
            canvas.create_line(x, top, x, bottom, fill="#EDF2F5")
            canvas.create_oval(x - 7, y - 7, x + 7, y + 7, fill=color, outline="")
            if count <= 30 or index in (0, count - 1):
                canvas.create_text(x, bottom + 16, text=str(index + 1), fill=self.colors["muted"],
                                   font=("Segoe UI", 7))
                canvas.create_text(x, top - 14, text=str(page), fill=self.colors["text"],
                                   font=("Segoe UI", 8, "bold"))
        self.frames_canvas.delete("all")
        self._draw_frame_slots(final_frames)

    def _draw_frame_slots(self, frames):
        canvas = self.frames_canvas
        canvas.delete("all")
        width = max(canvas.winfo_width(), 300)
        count = len(frames)
        gap, left = 6, 16
        slot_width = max(35, min(68, (width - 2 * left - gap * max(count - 1, 0)) / max(count, 1)))
        total = slot_width * count + gap * max(count - 1, 0)
        left = max(10, (width - total) / 2)
        for index, value in enumerate(frames):
            x = left + index * (slot_width + gap)
            canvas.create_text(x + slot_width / 2, 12, text=f"F{index + 1}", fill=self.colors["muted"],
                               font=("Segoe UI", 8, "bold"))
            fill = self.colors["empty"] if value == -1 else "#DDF7F3"
            text_color = self.colors["muted"] if value == -1 else self.colors["navy"]
            canvas.create_rectangle(x, 24, x + slot_width, 61, fill=fill,
                                   outline=self.colors["line"], width=1)
            canvas.create_text(x + slot_width / 2, 42, text="-" if value == -1 else str(value),
                               fill=text_color, font=("Segoe UI", 11, "bold"))

    def _draw_comparison_chart(self, names, fault_counts, fault_series):
        canvas = self.chart_canvas
        canvas.delete("all")
        width = max(canvas.winfo_width(), 300)
        height = max(canvas.winfo_height(), 220)
        canvas.create_text(16, 13, anchor="w", text="TOTAL PAGE FAULTS BY ALGORITHM",
                           fill=self.colors["navy"], font=("Segoe UI", 9, "bold"))
        colors = [self.colors["fault"], self.colors["blue"], self.colors["teal_dark"]]
        maximum = max(fault_counts) if fault_counts else 1
        base_y, top_y = min(height - 68, 146), 38
        slot = (width - 52) / max(len(names), 1)
        for index, (name, count) in enumerate(zip(names, fault_counts)):
            x = 36 + index * slot + slot * 0.2
            bar_width = slot * 0.48
            bar_height = (base_y - top_y) * count / max(maximum, 1)
            canvas.create_rectangle(x, base_y - bar_height, x + bar_width, base_y,
                                   fill=colors[index], outline="")
            canvas.create_text(x + bar_width / 2, base_y - bar_height - 12, text=str(count),
                               fill=self.colors["text"], font=("Segoe UI", 9, "bold"))
            canvas.create_text(x + bar_width / 2, base_y + 14, text=name,
                               fill=self.colors["muted"], font=("Segoe UI", 8))
        timeline_top = min(height - 35, 200)
        canvas.create_text(16, timeline_top + 12, anchor="w", text="Fault timeline",
                           fill=self.colors["muted"], font=("Segoe UI", 8, "bold"))
        plot_left, plot_right = 92, width - 16
        timeline_width = max(1, plot_right - plot_left)
        max_steps = max((len(series) for series in fault_series), default=1)
        for row, (name, series) in enumerate(zip(names, fault_series)):
            y = timeline_top + 31 + row * 20
            canvas.create_text(plot_left - 7, y, text=name, anchor="e", fill=self.colors["muted"],
                               font=("Segoe UI", 7))
            if len(series) == 1:
                xs = [plot_left]
            else:
                xs = [plot_left + timeline_width * i / (len(series) - 1) for i in range(len(series))]
            for x, is_fault in zip(xs, series):
                color = colors[row] if is_fault else "#D9E2EC"
                canvas.create_oval(x - 2, y - 2, x + 2, y + 2, fill=color, outline="")
        self.frames_canvas.delete("all")
        self.frames_canvas.create_text(max(20, self.frames_canvas.winfo_width() / 2), 50,
                                       text="Compare view shows fault counts and timelines",
                                       fill=self.colors["muted"], font=("Segoe UI", 9))

    def simulate(self):
        self.clear_output()
        try:
            page_string = [int(x) for x in self.page_entry.get().split()]
            frame_size = int(self.frame_entry.get())
            algorithm = self.algo_var.get()
            if frame_size <= 0 or not page_string:
                raise ValueError
        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid page string and frame size.")
            return

        if algorithm == "FIFO":
            faults, steps, frames_history = self.fifo(page_string, frame_size)
        elif algorithm == "LRU":
            faults, steps, frames_history = self.lru(page_string, frame_size)
        else:  # Optimal
            faults, steps, frames_history = self.optimal(page_string, frame_size)

        self._set_metrics(faults, len(page_string))
        self._fill_steps(page_string, frames_history, steps)
        self.plot_simulation(page_string, frames_history, steps, algorithm)

    def compare_all(self):
        self.clear_output()
        try:
            page_string = [int(x) for x in self.page_entry.get().split()]
            frame_size = int(self.frame_entry.get())
            if frame_size <= 0 or not page_string:
                raise ValueError
        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid page string and frame size.")
            return

        # Run all algorithms
        results = {
            "FIFO": self.fifo(page_string, frame_size),
            "LRU": self.lru(page_string, frame_size),
            "Optimal": self.optimal(page_string, frame_size)
        }
        names = list(results)
        fault_counts = [results[name][0] for name in names]
        fault_series = [["Fault" in step for step in results[name][1]] for name in names]
        selected = self.algo_var.get()
        selected_faults, selected_steps, selected_history = results[selected]
        self._set_metrics(selected_faults, len(page_string))
        self._fill_steps(page_string, selected_history, selected_steps)
        summaries = [
            f"{name}: {results[name][0]} faults, "
            f"Hit Ratio {(len(page_string) - results[name][0]) / len(page_string):.2%}"
            for name in names
        ]
        self.comparison_label.config(text="     |     ".join(summaries))
        self.chart_mode = "comparison"
        self.chart_data = (names, fault_counts, fault_series)
        self._redraw_charts()

    def plot_simulation(self, page_string, frames_history, steps, algorithm):
        self.chart_mode = "simulation"
        self.chart_data = (page_string, steps, algorithm, frames_history[-1])
        self._redraw_charts()

    def fifo(self, page_string, frame_size):
        frames = [-1] * frame_size
        queue = []
        faults = 0
        steps = []
        frames_history = []

        for i, page in enumerate(page_string):
            if page in frames:
                steps.append(f"{i+1:<4} | {page:<4} | {str(frames):<13} | Hit")
            else:
                faults += 1
                if len(queue) < frame_size:
                    frames[len(queue)] = page
                    queue.append(page)
                else:
                    old_page = queue.pop(0)
                    frames[frames.index(old_page)] = page
                    queue.append(page)
                steps.append(f"{i+1:<4} | {page:<4} | {str(frames):<13} | Fault")
            frames_history.append(frames.copy())
        return faults, steps, frames_history

    def lru(self, page_string, frame_size):
        frames = [-1] * frame_size
        recent = []
        faults = 0
        steps = []
        frames_history = []

        for i, page in enumerate(page_string):
            if page in frames:
                recent.remove(page)
                recent.append(page)
                steps.append(f"{i+1:<4} | {page:<4} | {str(frames):<13} | Hit")
            else:
                faults += 1
                if len(recent) < frame_size:
                    frames[len(recent)] = page
                else:
                    old_page = recent.pop(0)
                    frames[frames.index(old_page)] = page
                recent.append(page)
                steps.append(f"{i+1:<4} | {page:<4} | {str(frames):<13} | Fault")
            frames_history.append(frames.copy())
        return faults, steps, frames_history

    def optimal(self, page_string, frame_size):
        frames = [-1] * frame_size
        faults = 0
        steps = []
        frames_history = []

        for i, page in enumerate(page_string):
            if page in frames:
                steps.append(f"{i+1:<4} | {page:<4} | {str(frames):<13} | Hit")
            else:
                faults += 1
                if len([f for f in frames if f != -1]) < frame_size:
                    frames[frames.index(-1)] = page
                else:
                    future = page_string[i+1:]
                    replace_idx = 0
                    max_dist = -1
                    for j, frame in enumerate(frames):
                        dist = future.index(frame) if frame in future else len(future)
                        if dist > max_dist:
                            max_dist = dist
                            replace_idx = j
                    frames[replace_idx] = page
                steps.append(f"{i+1:<4} | {page:<4} | {str(frames):<13} | Fault")
            frames_history.append(frames.copy())
        return faults, steps, frames_history

    def clear_output(self):
        self.steps_table.delete(*self.steps_table.get_children())
        for value in self.metric_values.values():
            value.config(text="--")
        self.comparison_label.config(text="")
        self._draw_empty_charts()

    def clear(self):
        self.page_entry.delete(0, tk.END)
        self.frame_entry.delete(0, tk.END)
        self.clear_output()

if __name__ == "__main__":
    root = tk.Tk()
    app = PageReplacementSimulator(root)
    root.mainloop()
