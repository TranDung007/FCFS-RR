
import tkinter as tk
from tkinter import ttk, messagebox
import random
from collections import deque

class ProcessSchedulerGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Mô phỏng Thuật Toán Lập lịch CPU")
        
        # Tạo khung chính bên trái
        self.left_frame = ttk.Frame(master)
        self.left_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        
        # Tạo khung chính bên phải
        self.right_frame = ttk.Frame(master)
        self.right_frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        
        # Cấu hình grid để các khung co giãn đều
        master.grid_rowconfigure(0, weight=1)
        master.grid_columnconfigure(0, weight=1)
        master.grid_columnconfigure(1, weight=1)
        
        # Khung nhập thông số bên trái
        self.input_frame = ttk.LabelFrame(self.left_frame, text="Thông số đầu vào")
        self.input_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Nhập số lượng tiến trình
        ttk.Label(self.input_frame, text="Số lượng tiến trình:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.num_processes_entry = ttk.Entry(self.input_frame)
        self.num_processes_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.num_processes_entry.insert(0, "3")
        
        # Chọn cách nhập dữ liệu
        ttk.Label(self.input_frame, text="Phương thức nhập:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.input_method_combo = ttk.Combobox(self.input_frame, values=["Nhập tay", "Số ngẫu nhiên"])
        self.input_method_combo.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        self.input_method_combo.set("Nhập tay")
        
        # Chọn thuật toán
        ttk.Label(self.input_frame, text="Chọn thuật toán:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.algorithm_combo = ttk.Combobox(self.input_frame, values=["FCFS", "RR"])
        self.algorithm_combo.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        self.algorithm_combo.set("FCFS")
        
        # Time quantum cho RR
        self.quantum_label = ttk.Label(self.input_frame, text="Time Quantum (cho RR):")
        self.quantum_label.grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.quantum_entry = ttk.Entry(self.input_frame)
        self.quantum_entry.grid(row=3, column=1, padx=5, pady=5, sticky="ew")
        self.quantum_entry.insert(0, "2")
        
        # Nút mô phỏng
        self.simulate_button = ttk.Button(self.input_frame, text="Chạy mô phỏng", command=self.simulate)
        self.simulate_button.grid(row=4, column=0, columnspan=2, padx=5, pady=10, sticky="ew")
        
        # Khung thông tin tiến trình bên phải
        self.process_data_frame = ttk.LabelFrame(self.right_frame, text="Thông tin tiến trình")
        self.process_data_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Khung kết quả bên trái
        self.stats_frame = ttk.LabelFrame(self.left_frame, text="Kết quả thống kê")
        self.stats_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.avg_wait_label = ttk.Label(self.stats_frame, text="Waiting Time Trung Bình: -")
        self.avg_wait_label.pack(padx=5, pady=2, anchor="w")
        
        self.avg_tat_label = ttk.Label(self.stats_frame, text="Turnaround Time Trung Bình: -")
        self.avg_tat_label.pack(padx=5, pady=2, anchor="w")
        
        # Khung Gantt chart bên trái
        self.gantt_frame = ttk.LabelFrame(self.left_frame, text="Gantt Chart")
        self.gantt_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.gantt_label = ttk.Label(self.gantt_frame, text="Chưa có dữ liệu")
        self.gantt_label.pack(padx=5, pady=5, anchor="w")
        
        # Khung kết quả mô phỏng bên phải
        self.results_frame = ttk.LabelFrame(self.right_frame, text="Kết quả mô phỏng")
        self.results_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Tạo Treeview cho kết quả
        self.results_tree = ttk.Treeview(self.results_frame, columns=("ID", "Arrival", "Burst", "Start", "Finish", "Waiting", "TAT"), show="headings")
        self.results_tree.heading("ID", text="ID")
        self.results_tree.heading("Arrival", text="Arrival")
        self.results_tree.heading("Burst", text="Burst")
        self.results_tree.heading("Start", text="Start")
        self.results_tree.heading("Finish", text="Finish")
        self.results_tree.heading("Waiting", text="Waiting")
        self.results_tree.heading("TAT", text="TAT")
        
        # Căn đều các cột
        for col in self.results_tree["columns"]:
            self.results_tree.column(col, width=80, anchor="center")
        
        self.results_tree.pack(fill="both", expand=True)
        
        # Các biến trung gian
        self.process_inputs = []
        self.update_process_inputs()
        
        # Bind sự kiện
        self.num_processes_entry.bind("<Return>", self.update_process_inputs)
        self.input_method_combo.bind("<<ComboboxSelected>>", self.update_process_inputs)
        self.algorithm_combo.bind("<<ComboboxSelected>>", self.toggle_quantum_visibility)
        
        # Ẩn/hiện quantum ban đầu
        self.toggle_quantum_visibility()

    def toggle_quantum_visibility(self, event=None):
        if self.algorithm_combo.get() == "RR":
            self.quantum_label.grid()
            self.quantum_entry.grid()
        else:
            self.quantum_label.grid_remove()
            self.quantum_entry.grid_remove()

    def validate_input(self, value, is_burst=False):
        try:
            num = int(value)
            if is_burst:
                return num > 0
            return num >= 0
        except ValueError:
            return False

    def update_process_inputs(self, event=None):
        # Kiểm tra số lượng tiến trình
        try:
            num = int(self.num_processes_entry.get())
            if num <= 0:
                messagebox.showerror("Lỗi", "Số lượng tiến trình phải > 0")
                return
        except ValueError:
            messagebox.showerror("Lỗi", "Nhập số nguyên hợp lệ cho số lượng tiến trình")
            return

        # Xóa các widget cũ
        for widget in self.process_data_frame.winfo_children():
            widget.destroy()
        self.process_inputs.clear()

        if self.input_method_combo.get() == "Nhập tay":
            for i in range(num):
                ttk.Label(self.process_data_frame, text=f"P{i+1} Arrival:").grid(row=i, column=0, padx=5, pady=2, sticky="w")
                arrival = ttk.Entry(self.process_data_frame)
                arrival.grid(row=i, column=1, padx=5, pady=2, sticky="ew")
                arrival.insert(0, "0")

                ttk.Label(self.process_data_frame, text="Burst:").grid(row=i, column=2, padx=5, pady=2, sticky="w")
                burst = ttk.Entry(self.process_data_frame)
                burst.grid(row=i, column=3, padx=5, pady=2, sticky="ew")
                burst.insert(0, "3")

                self.process_inputs.append({'arrival': arrival, 'burst': burst})
                
        #Sinh ngẫu nhiên        
        else:
            processes = []
            for i in range(num):
                pid = f"P{i+1}"
                arrival = random.randint(0, 5)
                burst = random.randint(1, 10)
                processes.append({'id': pid, 'arrival': arrival, 'burst': burst})
            processes.sort(key=lambda x: x['arrival'])

            for i, p in enumerate(processes):
                ttk.Label(self.process_data_frame, text=f"{p['id']} Arrival:").grid(row=i, column=0, padx=5, pady=2, sticky="w")
                arrival = ttk.Entry(self.process_data_frame)
                arrival.grid(row=i, column=1, padx=5, pady=2, sticky="ew")
                arrival.insert(0, str(p['arrival']))

                ttk.Label(self.process_data_frame, text="Burst:").grid(row=i, column=2, padx=5, pady=2, sticky="w")
                burst = ttk.Entry(self.process_data_frame)
                burst.grid(row=i, column=3, padx=5, pady=2, sticky="ew")
                burst.insert(0, str(p['burst']))

                self.process_inputs.append({'id': p['id'],'arrival': arrival, 'burst': burst})

    def get_process_data(self):
        processes = []
        for i, inputs in enumerate(self.process_inputs):
            try:
                arrival = int(inputs['arrival'].get())
                burst = int(inputs['burst'].get())
                pid = inputs.get('id', f'P{i+1}')
                
                if not self.validate_input(arrival):
                    messagebox.showerror("Lỗi", f"Arrival time của {pid} phải ≥ 0")
                    return None
                if not self.validate_input(burst, is_burst=True):
                    messagebox.showerror("Lỗi", f"Burst time của {pid} phải > 0")
                    return None
                    
                processes.append({'id': pid, 'arrival': arrival, 'burst': burst})
            except ValueError:
                messagebox.showerror("Lỗi", f"Nhập số nguyên hợp lệ cho tiến trình")
                return None
        return sorted(processes, key=lambda x: x['arrival'])


    def simulate_fcfs(self, processes):
        
        processes.sort(key=lambda x: (x['arrival'], x['id']))
        current_time = 0
        gantt_chart = []
        results = []
        
        for p in processes:
            if current_time < p['arrival']:
                gantt_chart.append(('Idle', current_time, p['arrival']))
                current_time = p['arrival']
            
            start = current_time
            end = start + p['burst']
            gantt_chart.append((p['id'], start, end))
            
            results.append({
                'ID': p['id'], 'Arrival': p['arrival'], 'Burst': p['burst'],
                'Start': start, 'Finish': end,
                'Waiting': start - p['arrival'],
                'TAT': end - p['arrival']
            })
            current_time = end
        avg_tat = sum(r['TAT'] for r in results) / len(results)
        avg_wt = sum(r['Waiting'] for r in results) / len(results)

        return results, gantt_chart, avg_tat, avg_wt

    def simulate_rr(self, processes, quantum):
        processes.sort(key=lambda x: (x['arrival'], x['id']))
        ready_queue = deque()
        remaining = {p['id']: p['burst'] for p in processes}
        completion = {}
        gantt_chart = []
        start_times = {p['id']: None for p in processes}
        time = 0
        i = 0
        n = len(processes)
        
        while len(completion) < n:
            while i < n and processes[i]['arrival'] <= time:
                ready_queue.append(processes[i])
                i += 1
            if not ready_queue:
                if i < n:
                    next_arrival = processes[i]['arrival']
                    gantt_chart.append(('Idle', time, next_arrival))
                    time = next_arrival
                    continue
            
            proc = ready_queue.popleft()
            pid = proc['id']
            
            if start_times[pid] is None:
                start_times[pid] = time
            
            run_time = min(quantum, remaining[pid])
            gantt_chart.append((pid, time, time + run_time))
            time += run_time
            remaining[pid] -= run_time
            
            while i < n and processes[i]['arrival'] <= time:
                ready_queue.append(processes[i])
                i += 1
            
            if remaining[pid] == 0:
                completion[pid] = time
            else:
                ready_queue.append(proc)

        results = []
        for p in processes:
            comp = completion[p['id']]
            results.append({
                'ID': p['id'], 'Arrival': p['arrival'], 'Burst': p['burst'],
                'Start': start_times[p['id']], 'Finish': comp,
                'Waiting': comp - p['arrival'] - p['burst'],
                'TAT': comp - p['arrival']
            })

        avg_tat = sum(r['TAT'] for r in results) / len(results)
        avg_wt = sum(r['Waiting'] for r in results) / len(results)

        return results, gantt_chart, avg_tat, avg_wt

    def simulate(self):
        # Kiểm tra phương thức nhập ngay khi bắt đầu simulate
        selected_method = self.input_method_combo.get()
        if selected_method not in ["Nhập tay", "Sinh ngẫu nhiên"]:
            messagebox.showerror("Lỗi", f"Phương thức nhập '{selected_method}' không hợp lệ.")
            return
            
        # Xóa kết quả cũ
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        self.avg_wait_label.config(text="Waiting Time TB: -")
        self.avg_tat_label.config(text="Turnaround Time TB: -")
        self.gantt_label.config(text="Chưa có dữ liệu")

        processes = self.get_process_data()
        if not processes:
            return

        selected_algorithm = self.algorithm_combo.get()
        if selected_algorithm == "FCFS":
            results, gantt_chart, avg_tat, avg_wt = self.simulate_fcfs(processes)
        elif selected_algorithm == "RR":
            try:
                quantum = int(self.quantum_entry.get())
                if quantum <= 0:
                    messagebox.showerror("Lỗi", "Quantum phải > 0")
                    return
                results, gantt_chart, avg_tat, avg_wt = self.simulate_rr(processes, quantum)
            except ValueError:
                messagebox.showerror("Lỗi", "Nhập số nguyên hợp lệ cho Quantum")
                return
        else:
            if selected_algorithm not in ["FCFS", "RR"]:
                messagebox.showerror("Lỗi", f"Thuật toán '{selected_algorithm}' không được hỗ trợ.")
                return

        # Hiển thị kết quả
        for r in results:
            self.results_tree.insert("", "end", values=(
                r['ID'], r['Arrival'], r['Burst'], 
                r['Start'], r['Finish'], 
                r['Waiting'], r['TAT']
            ))

        self.avg_wait_label.config(text=f"Waiting Time TB: {avg_wt:.2f}")
        self.avg_tat_label.config(text=f"Turnaround Time TB: {avg_tat:.2f}")
        gantt_str = "Gantt Chart:\n"
        for i, (pid, start, end) in enumerate(gantt_chart):
            gantt_str += f"[{pid}]({start}→{end}) "
            if (i + 1) % 6 == 0:
                gantt_str += "\n"
        self.gantt_label.config(text=gantt_str.strip())
        
if __name__ == "__main__":
    root = tk.Tk()
    app = ProcessSchedulerGUI(root)
    root.mainloop()
    
 