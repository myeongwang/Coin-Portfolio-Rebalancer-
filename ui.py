import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import threading
import time

class RebalancerGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("SAM SD CHOI Coin Portfolio Rebalancer")
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        
        # 데이터 저장용
        self.coin_entries = []
        self.selected_coins = []
        self.target_ratios = {}
        self.scheduler_running = False
        
        # 로그 텍스트 초기화 (아직 UI 없을 때도 log() 호출 가능)
        self.log_text = None

        self.setup_ui()
        self.log("프로그램이 시작되었습니다.")
    
    def setup_ui(self):
        # 메인 헤더 추가
        self.create_header()
        
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        self.setup_coin_selection(main_container)
        self.setup_scheduling(main_container)
        self.setup_status_and_log(main_container)
    
    def create_header(self):
        """멋진 헤더 생성"""
        header_frame = tk.Frame(self.root, bg='#1a1a1a', height=60)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        header_frame.pack_propagate(False)
        
        # 메인 제목
        title_label = tk.Label(
            header_frame,
            text="SAM SD CHOI Coin Portfolio Rebalancer",
            font=('Arial Black', 16, 'bold'),
            fg='white',
            bg='#1a1a1a'
        )
        title_label.pack(pady=(2, 0))
        
        # 부제목 프레임
        subtitle_frame = tk.Frame(header_frame, bg='#1a1a1a')
        subtitle_frame.pack(pady=(2, 0))
        
        # 제작자 정보
        creator_label = tk.Label(
            subtitle_frame,
            text="Created by ",
            font=('Arial', 10),
            fg='#888888',
            bg='#1a1a1a'
        )
        creator_label.pack(side=tk.LEFT)
        
        myeongjin_label = tk.Label(
            subtitle_frame,
            text="MyeongJin LEE",
            font=('Arial', 10, 'bold'),
            fg='#FF4444',
            bg='#1a1a1a'
        )
        myeongjin_label.pack(side=tk.LEFT)
        
        # 버전 정보
        version_label = tk.Label(
            subtitle_frame,
            text=" • v1.0 • Crypto Trading Bot",
            font=('Arial', 9),
            fg='#666666',
            bg='#1a1a1a'
        )
        version_label.pack(side=tk.LEFT)
    
    def setup_coin_selection(self, parent):
        coin_frame = ttk.LabelFrame(parent, text="🪙 코인 선택 및 목표 비율 설정", padding=15)
        coin_frame.pack(fill=tk.X, pady=(0, 10))
        
        count_frame = ttk.Frame(coin_frame)
        count_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(count_frame, text="리밸런싱할 코인 개수:", font=('맑은 고딕', 10, 'bold')).pack(side=tk.LEFT)
        
        self.coin_count = tk.StringVar(value="3")
        coin_count_combo = ttk.Combobox(count_frame, textvariable=self.coin_count, 
                                        values=["2", "3", "4", "5", "6"], width=5, state="readonly")
        coin_count_combo.pack(side=tk.LEFT, padx=(10, 20))
        coin_count_combo.bind('<<ComboboxSelected>>', self.update_coin_inputs)
        
        ttk.Button(count_frame, text="코인 입력창 생성", command=self.update_coin_inputs).pack(side=tk.LEFT, padx=(10, 0))
        
        self.coin_input_frame = ttk.Frame(coin_frame)
        self.coin_input_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.update_coin_inputs()  # 초기 코인 입력창 생성
        
        button_frame = ttk.Frame(coin_frame)
        button_frame.pack(fill=tk.X, pady=(15, 0))
        
        ttk.Button(button_frame, text="목표 비율 적용", command=self.apply_target_ratios, style='Accent.TButton').pack(side=tk.LEFT)
        ttk.Button(button_frame, text="균등 분할", command=self.set_equal_ratios).pack(side=tk.LEFT, padx=(10,0))
        ttk.Button(button_frame, text="초기화", command=self.reset_ratios).pack(side=tk.LEFT, padx=(10,0))
    
    def setup_scheduling(self, parent):
        schedule_frame = ttk.LabelFrame(parent, text="⏰ 자동 리밸런싱 스케줄", padding=15)
        schedule_frame.pack(fill=tk.X, pady=(0, 10))
        
        schedule_grid = ttk.Frame(schedule_frame)
        schedule_grid.pack(fill=tk.X)
        
        ttk.Label(schedule_grid, text="실행 시간:", font=('맑은 고딕', 10)).grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        
        time_frame = ttk.Frame(schedule_grid)
        time_frame.grid(row=0, column=1, sticky=tk.W, padx=(0, 20))
        
        self.hour_var = tk.StringVar(value="09")
        self.minute_var = tk.StringVar(value="00")
        
        hour_combo = ttk.Combobox(time_frame, textvariable=self.hour_var, values=[f"{i:02d}" for i in range(24)], width=4, state="readonly")
        hour_combo.pack(side=tk.LEFT)
        ttk.Label(time_frame, text=" : ").pack(side=tk.LEFT)
        minute_combo = ttk.Combobox(time_frame, textvariable=self.minute_var, values=[f"{i:02d}" for i in range(0,60,5)], width=4, state="readonly")
        minute_combo.pack(side=tk.LEFT)
        
        ttk.Label(schedule_grid, text="반복 주기:", font=('맑은 고딕', 10)).grid(row=0, column=2, sticky=tk.W, padx=(20,10))
        
        self.repeat_var = tk.StringVar(value="매일")
        repeat_combo = ttk.Combobox(schedule_grid, textvariable=self.repeat_var, values=["매일","평일만","주말만","특정 요일","1회만"], width=10, state="readonly")
        repeat_combo.grid(row=0, column=3, sticky=tk.W, padx=(0,20))
        repeat_combo.bind('<<ComboboxSelected>>', self.on_repeat_change)
        
        # 세부 설정 프레임 (요일 선택용)
        self.detail_frame = ttk.Frame(schedule_frame)
        self.detail_frame.pack(fill=tk.X, pady=(10,0))
        
        # 요일 선택 체크박스들
        self.weekday_vars = {}
        weekdays = [("월", "monday"), ("화", "tuesday"), ("수", "wednesday"), 
                   ("목", "thursday"), ("금", "friday"), ("토", "saturday"), ("일", "sunday")]
        
        self.weekday_label = ttk.Label(self.detail_frame, text="실행 요일 선택:", font=('맑은 고딕', 10))
        
        self.weekday_checkboxes = {}
        for i, (day_kr, day_en) in enumerate(weekdays):
            var = tk.BooleanVar()
            self.weekday_vars[day_en] = var
            checkbox = ttk.Checkbutton(self.detail_frame, text=day_kr, variable=var)
            self.weekday_checkboxes[day_en] = checkbox
        
        # 초기에는 숨김
        self.hide_detail_settings()
        
        button_frame = ttk.Frame(schedule_frame)
        button_frame.pack(fill=tk.X, pady=(15,0))
        
        self.start_btn = ttk.Button(button_frame, text="🔄 스케줄 시작", command=self.start_scheduler)
        self.start_btn.pack(side=tk.LEFT)
        self.stop_btn = ttk.Button(button_frame, text="⏹️ 스케줄 중지", command=self.stop_scheduler, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=(10,0))
        self.manual_btn = ttk.Button(button_frame, text="▶️ 수동 실행", command=self.manual_rebalance)
        self.manual_btn.pack(side=tk.LEFT, padx=(10,0))
        
        self.schedule_status_var = tk.StringVar(value="스케줄 중지됨")
        status_label = ttk.Label(button_frame, textvariable=self.schedule_status_var, font=('맑은 고딕',10), foreground='red')
        status_label.pack(side=tk.RIGHT)
    
    def setup_status_and_log(self, parent):
        status_log_frame = ttk.Frame(parent)
        status_log_frame.pack(fill=tk.BOTH, expand=True)
        
        status_frame = ttk.LabelFrame(status_log_frame, text="📊 현재 설정 현황", padding=10)
        status_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0,5))
        
        status_columns = ('항목','설정값')
        self.status_tree = ttk.Treeview(status_frame, columns=status_columns, show='headings', height=12)
        for col in status_columns:
            self.status_tree.heading(col, text=col)
            self.status_tree.column(col, width=120, anchor='center')
        
        status_scroll = ttk.Scrollbar(status_frame, orient="vertical", command=self.status_tree.yview)
        self.status_tree.configure(yscrollcommand=status_scroll.set)
        
        self.status_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        status_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        log_frame = ttk.LabelFrame(status_log_frame, text="📝 실행 로그", padding=10)
        log_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5,0))
        
        log_container = ttk.Frame(log_frame)
        log_container.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = tk.Text(log_container, height=15, width=40, wrap=tk.WORD, font=('Consolas',9), bg='#f8f9fa', fg='#333333')
        log_scroll = ttk.Scrollbar(log_container, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scroll.set)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        log_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        log_btn_frame = ttk.Frame(log_frame)
        log_btn_frame.pack(fill=tk.X, pady=(10,0))
        
        ttk.Button(log_btn_frame, text="로그 지우기", command=self.clear_log).pack(side=tk.LEFT)
        ttk.Button(log_btn_frame, text="로그 저장", command=self.save_log).pack(side=tk.LEFT, padx=(10,0))
        
        self.update_status_display()
    
    def update_coin_inputs(self, event=None):
        for widget in getattr(self, 'coin_input_frame', []).winfo_children() if hasattr(self,'coin_input_frame') else []:
            widget.destroy()
        self.coin_entries = []
        try:
            coin_count = int(self.coin_count.get())
        except:
            coin_count = 3
        
        header_frame = ttk.Frame(self.coin_input_frame)
        header_frame.pack(fill=tk.X, pady=(0,10))
        ttk.Label(header_frame, text="코인 심볼", font=('맑은 고딕',10,'bold')).grid(row=0,column=0,padx=(0,50))
        ttk.Label(header_frame, text="목표 비율 (%)", font=('맑은 고딕',10,'bold')).grid(row=0,column=1,padx=(0,50))
        ttk.Label(header_frame, text="현재 비율 (%)", font=('맑은 고딕',10,'bold')).grid(row=0,column=2)
        
        popular_coins = ["BTC","ETH","XRP","ADA","DOT","LINK","SOL","AVAX","MATIC","UNI"]
        for i in range(coin_count):
            row_frame = ttk.Frame(self.coin_input_frame)
            row_frame.pack(fill=tk.X, pady=2)
            
            coin_var = tk.StringVar(value=popular_coins[i] if i<len(popular_coins) else "")
            coin_combo = ttk.Combobox(row_frame, textvariable=coin_var, values=popular_coins, width=8)
            coin_combo.grid(row=0,column=0,padx=(0,20))
            
            ratio_var = tk.StringVar(value="0")
            ratio_entry = ttk.Entry(row_frame, textvariable=ratio_var, width=8)
            ratio_entry.grid(row=0,column=1,padx=(0,20))
            
            current_ratio_label = ttk.Label(row_frame, text="0")
            current_ratio_label.grid(row=0,column=2)
            
            self.coin_entries.append({
                'coin': coin_var,
                'target_ratio': ratio_var,
                'current_ratio_label': current_ratio_label
            })
        
        if self.log_text:
            self.log(f"코인 입력창을 {coin_count}개로 업데이트했습니다.")
    
    def apply_target_ratios(self):
        self.log("목표 비율이 적용되었습니다.")
    
    def set_equal_ratios(self):
        if not self.coin_entries: return
        equal_ratio = 100 / len(self.coin_entries)
        for entry in self.coin_entries:
            entry['target_ratio'].set(str(round(equal_ratio,2)))
        self.log("모든 코인 목표 비율을 균등하게 설정했습니다.")
    
    def reset_ratios(self):
        for entry in self.coin_entries:
            entry['target_ratio'].set("0")
        self.log("목표 비율이 초기화되었습니다.")
    
    def on_repeat_change(self, event=None):
        """반복 주기 변경시 세부 설정 표시/숨김"""
        repeat_type = self.repeat_var.get()
        
        if repeat_type == "특정 요일":
            self.show_weekday_settings()
        else:
            self.hide_detail_settings()
    
    def show_weekday_settings(self):
        """요일 선택 설정 표시"""
        self.hide_detail_settings()
        
        self.weekday_label.grid(row=0, column=0, sticky=tk.W, padx=(0,10))
        
        col = 1
        for day_en, checkbox in self.weekday_checkboxes.items():
            checkbox.grid(row=0, column=col, padx=(0,5))
            col += 1
    
    def hide_detail_settings(self):
        """세부 설정 숨김"""
        # 모든 위젯 숨김
        self.weekday_label.grid_remove()
        for checkbox in self.weekday_checkboxes.values():
            checkbox.grid_remove()
    
    def start_scheduler(self):
        if self.scheduler_running:
            return

        # 특정 요일 선택시 validation
        if self.repeat_var.get() == "특정 요일":
            selected_days = [day for day, var in self.weekday_vars.items() if var.get()]
            if not selected_days:
                messagebox.showwarning("경고", "특정 요일을 선택했지만 요일이 선택되지 않았습니다.")
                return

        self.scheduler_running = True
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        
        # 시간 가져오기
        hour = int(self.hour_var.get())
        minute = int(self.minute_var.get())
        repeat = self.repeat_var.get()

        # 상태 메시지 생성
        status_msg = ""
        
        if repeat == "매일":
            status_msg = f"매일 {hour:02d}:{minute:02d} 실행 중"
            
        elif repeat == "평일만":
            status_msg = f"평일 {hour:02d}:{minute:02d} 실행 중"
            
        elif repeat == "주말만":
            status_msg = f"주말 {hour:02d}:{minute:02d} 실행 중"
            
        elif repeat == "특정 요일":
            selected_days = []
            day_names = {"monday": "월", "tuesday": "화", "wednesday": "수", 
                        "thursday": "목", "friday": "금", "saturday": "토", "sunday": "일"}
            
            for day_en, var in self.weekday_vars.items():
                if var.get():
                    selected_days.append(day_names[day_en])
            
            status_msg = f"매주 {'/'.join(selected_days)}요일 {hour:02d}:{minute:02d} 실행 중"
            
        elif repeat == "1회만":
            status_msg = f"1회만 {hour:02d}:{minute:02d} 실행 예정"

        self.schedule_status_var.set(status_msg)
        self.log(f"스케줄러 시작: {status_msg}")
        
        # 상태 업데이트
        self.update_status_display()
    
    def stop_scheduler(self):
        self.scheduler_running = False
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.schedule_status_var.set("스케줄 중지됨")
        self.log("스케줄러가 중지되었습니다.")
    
    def manual_rebalance(self):
        self.log("수동 리밸런싱이 실행되었습니다.")
    
    def update_status_display(self):
        # 상태 트리 업데이트
        self.status_tree.delete(*self.status_tree.get_children())
        
        # 코인별 목표 비율
        for entry in self.coin_entries:
            coin = entry['coin'].get()
            target = entry['target_ratio'].get()
            if coin and target != "0":
                self.status_tree.insert('', tk.END, values=(f"{coin} 목표", f"{target}%"))
        
        # 스케줄 정보
        if self.scheduler_running:
            repeat = self.repeat_var.get()
            time_str = f"{self.hour_var.get()}:{self.minute_var.get()}"
            
            if repeat == "특정 요일":
                selected_days = [day for day, var in self.weekday_vars.items() if var.get()]
                day_names = {"monday": "월", "tuesday": "화", "wednesday": "수", 
                            "thursday": "목", "friday": "금", "saturday": "토", "sunday": "일"}
                selected_kr = [day_names[day] for day in selected_days]
                schedule_info = f"{'/'.join(selected_kr)}요일 {time_str}"
            else:
                schedule_info = f"{repeat} {time_str}"
                
            self.status_tree.insert('', tk.END, values=("스케줄 상태", "실행중"))
            self.status_tree.insert('', tk.END, values=("스케줄 설정", schedule_info))
        else:
            self.status_tree.insert('', tk.END, values=("스케줄 상태", "중지됨"))
        
        # 마지막 업데이트 시간
        self.status_tree.insert('', tk.END, values=("마지막 업데이트", datetime.now().strftime('%H:%M:%S')))
    
    # 로그 관련
    def log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        if self.log_text:
            self.log_text.insert(tk.END, log_entry)
            self.log_text.see(tk.END)
        else:
            print(log_entry)
    
    def clear_log(self):
        if self.log_text:
            self.log_text.delete(1.0, tk.END)
    
    def save_log(self):
        if not self.log_text:
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files","*.txt")])
        if file_path:
            with open(file_path,"w",encoding="utf-8") as f:
                f.write(self.log_text.get(1.0, tk.END))
            self.log(f"로그를 {file_path}로 저장했습니다.")
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = RebalancerGUI()
    app.run()