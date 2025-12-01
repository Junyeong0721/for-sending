import tkinter as tk
from tkinter import messagebox, Toplevel
import json
import os

# 패턴 파일 이름
PATTERN_FILE = 'patterns.json'

class NonogramApp:
    def __init__(self, master):
        self.master = master
        master.title("파이썬 노노그램")

        self.grid_size = 0
        self.answer_grid = None
        self.player_grid = None
        self.row_clues = []
        self.col_clues = []
        self.cell_buttons = []
        self.current_pattern_name = ""
        self.current_filter_size = tk.IntVar(value=0)
        
        self.patterns = self._load_patterns()
        
        self.main_frame = tk.Frame(master)
        self.main_frame.pack(padx=10, pady=10)
        
        self.list_view = tk.Frame(self.main_frame)
        self.game_view = tk.Frame(self.main_frame)
        
        self._draw_main_menu()

    # -----------------------------------------------------------
    # 2-1. 데이터 파일 입출력 및 유틸리티
    # -----------------------------------------------------------
    
    def _load_patterns(self):
        """JSON 파일에서 패턴 데이터를 로드합니다."""
        if os.path.exists(PATTERN_FILE):
            try:
                with open(PATTERN_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                messagebox.showerror("오류", "패턴 파일이 손상되었습니다. 파일 삭제 후 다시 실행하세요.")
                return {}
        return {}

    def _save_patterns(self):
        """현재 패턴 데이터를 JSON 파일에 저장합니다."""
        try:
            with open(PATTERN_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.patterns, f, ensure_ascii=False, indent=4)
        except Exception as e:
            messagebox.showerror("오류", f"패턴 저장 중 오류 발생: {e}")

    # -----------------------------------------------------------
    # 2-2. 힌트 계산 로직
    # -----------------------------------------------------------

    def _calculate_row_clues(self, grid):
        """단일 행렬에 대한 가로 힌트를 계산합니다."""
        clues = []
        for row in grid:
            current_clue = []
            count = 0
            for cell in row:
                if cell == 1:
                    count += 1
                elif count > 0:
                    current_clue.append(count)
                    count = 0
            if count > 0:
                current_clue.append(count)
            if not current_clue:
                clues.append([0])
            else:
                clues.append(current_clue)
        return clues

    def _calculate_clues(self, answer_grid):
        """가로 및 세로 힌트를 모두 계산합니다."""
        transposed_grid = [list(col) for col in zip(*answer_grid)]
        row_clues = self._calculate_row_clues(answer_grid)
        col_clues = self._calculate_row_clues(transposed_grid)
        return row_clues, col_clues
    
    # -----------------------------------------------------------
    # 2-3. 메인 메뉴 및 뷰 전환
    # -----------------------------------------------------------

    def _show_view(self, view_name):
        """리스트 뷰와 게임 뷰를 전환합니다."""
        self.list_view.pack_forget()
        self.game_view.pack_forget()
        
        if view_name == "list":
            self.list_view.pack()
        elif view_name == "game":
            self.game_view.pack()

    def _draw_main_menu(self):
        """패턴 리스트 갤러리 화면을 그립니다."""
        
        for widget in self.list_view.winfo_children():
            widget.destroy()
            
        control_frame = tk.Frame(self.list_view)
        control_frame.pack(pady=10)
        
        tk.Label(control_frame, text="노노그램 패턴 갤러리", font=('Arial', 16, 'bold')).pack(side=tk.LEFT, padx=20)
        
        tk.Button(
            control_frame, 
            text="패턴 등록 (그리기)", 
            command=self._open_pattern_creator, 
            bg="#AFA", font=('Arial', 10)
        ).pack(side=tk.LEFT, padx=10)
        
        self.patterns = self._load_patterns()
        
        if not self.patterns:
            tk.Label(self.list_view, text="등록된 패턴이 없습니다. 새로운 패턴을 그려보세요!").pack(pady=50)
            self._show_view("list")
            return

        # --- 필터 컨트롤 ---
        filter_frame = tk.Frame(self.list_view)
        filter_frame.pack(pady=10)
        
        tk.Label(filter_frame, text="크기 필터:").pack(side=tk.LEFT, padx=5)

        filter_sizes = [0, 5, 10, 20]
        filter_names = ["전체", "5x5", "10x10", "20x20"]
        
        for size, name in zip(filter_sizes, filter_names):
            tk.Radiobutton(
                filter_frame, 
                text=name, 
                variable=self.current_filter_size, 
                value=size,
                command=self._draw_pattern_gallery
            ).pack(side=tk.LEFT, padx=5)

        self.gallery_frame = tk.Frame(self.list_view)
        self.gallery_frame.pack(padx=10)
        
        self.current_filter_size.set(0)
        self._draw_pattern_gallery()
        
        self._show_view("list")

    def _draw_pattern_gallery(self):
        """선택된 필터에 따라 패턴 갤러리를 새로 그립니다."""
        
        for widget in self.gallery_frame.winfo_children():
            widget.destroy()
            
        filter_size = self.current_filter_size.get()
        filtered_patterns = []
        
        for name, data in self.patterns.items():
            if filter_size == 0 or data['size'] == filter_size:
                filtered_patterns.append((name, data))

        if not filtered_patterns:
            tk.Label(self.gallery_frame, text="선택된 크기의 패턴이 없습니다.").pack(pady=20)
            return
            
        pattern_groups = {"5x5": [], "10x10": [], "20x20": []}
        for name, data in filtered_patterns:
            size_key = f"{data['size']}x{data['size']}"
            if size_key in pattern_groups:
                pattern_groups[size_key].append((name, data))
            
        for size_key, pattern_list in pattern_groups.items():
            if pattern_list:
                tk.Label(self.gallery_frame, text=f"--- {size_key} 퍼즐 ({len(pattern_list)}개) ---", 
                         font=('Arial', 11, 'bold')).pack(pady=5)
                
                group_frame = tk.Frame(self.gallery_frame)
                group_frame.pack(padx=10)
                
                for name, data in pattern_list:
                    self._draw_pattern_preview(group_frame, name, data)


    def _draw_pattern_preview(self, parent_frame, name, data):
        """단일 패턴의 작은 미리보기 타일을 그립니다."""
        
        preview_frame = tk.Frame(parent_frame, borderwidth=1, relief="solid", padx=5, pady=5)
        preview_frame.pack(side=tk.LEFT, padx=10, pady=5)
        
        size = data['size']
        pattern = data['pattern']
        cell_size = 80 // size
        
        canvas = tk.Canvas(preview_frame, width=80, height=80, bg='white')
        canvas.pack()
        
        for r in range(size):
            for c in range(size):
                color = "black" if pattern[r][c] == 1 else "white"
                x1 = c * cell_size
                y1 = r * cell_size
                x2 = (c + 1) * cell_size
                y2 = (r + 1) * cell_size
                
                outline_width = 1
                
                canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline='lightgray', width=outline_width)
                
        control_frame = tk.Frame(preview_frame)
        control_frame.pack(fill='x')
        
        tk.Label(control_frame, text=name, font=('Arial', 8)).pack(side=tk.LEFT, padx=2)
        
        tk.Button(
            control_frame, 
            text="삭제", 
            fg="red", 
            font=('Arial', 7),
            command=lambda n=name: self._delete_pattern(n)
        ).pack(side=tk.RIGHT, padx=2)

        canvas.bind("<Button-1>", lambda e: self.start_game(name))
        preview_frame.bind("<Button-1>", lambda e: self.start_game(name))

    def _delete_pattern(self, pattern_name):
        """선택한 패턴을 삭제합니다."""
        if messagebox.askyesno("삭제 확인", f"정말로 패턴 '{pattern_name}'을 삭제하시겠습니까?"):
            if pattern_name in self.patterns:
                del self.patterns[pattern_name]
                self._save_patterns()
                self._draw_main_menu()
                messagebox.showinfo("성공", f"패턴 '{pattern_name}'이 삭제되었습니다.")
            else:
                messagebox.showerror("오류", "해당 패턴을 찾을 수 없습니다.")


    def start_game(self, pattern_name):
        """선택된 패턴으로 게임을 시작하고 뷰를 전환합니다."""
        
        data = self.patterns.get(pattern_name)
        if not data:
            messagebox.showerror("오류", "선택된 패턴 데이터를 찾을 수 없습니다.")
            return

        self.current_pattern_name = pattern_name
        
        self.grid_size = data["size"]
        self.answer_grid = data["pattern"]
        self.player_grid = [[0] * self.grid_size for _ in range(self.grid_size)]
        
        self.row_clues, self.col_clues = self._calculate_clues(self.answer_grid)
        
        for widget in self.game_view.winfo_children():
            widget.destroy()
            
        self._draw_game_controls()
        self.game_board_frame = tk.Frame(self.game_view)
        self.game_board_frame.pack()
        
        self._draw_board(self.game_board_frame)
        self._show_view("game")


    def _draw_game_controls(self):
        """게임 중 사용할 컨트롤(뒤로가기)을 그립니다."""
        control_frame = tk.Frame(self.game_view)
        control_frame.pack(pady=10)
        
        tk.Button(
            control_frame, 
            text="< 목록으로 돌아가기", 
            command=self._go_to_main_menu, 
            bg="#FAA"
        ).pack(side=tk.LEFT, padx=10)
        
        tk.Label(control_frame, text=f"플레이 중: {self.current_pattern_name} ({self.grid_size}x{self.grid_size})", 
                 font=('Arial', 12, 'bold')).pack(side=tk.LEFT, padx=20)

    def _go_to_main_menu(self):
        """메인 메뉴로 돌아갑니다."""
        self._draw_main_menu()

    # -----------------------------------------------------------
    # 2-4. GUI 함수: 보드 생성 및 그리기 (게임 뷰)
    # -----------------------------------------------------------
    
    def _get_cell_dims(self, size):
        """난이도별 고정된 셀 크기(width, height)를 반환합니다."""
        if size == 5:
            return 5, 2  
        elif size == 10:
            return 3, 1 
        elif size == 20:
            return 2, 0 
        return 3, 1

    def _draw_board(self, parent_frame):
        """힌트 영역의 크기를 동적으로 계산하고, 고정된 크기의 게임 보드를 그립니다."""
        
        max_row_clue_len = max(len(c) for c in self.row_clues) if self.row_clues else 1
        max_col_clue_len = max(len(c) for c in self.col_clues) if self.col_clues else 1
        
        clue_col_span = max_row_clue_len 
        clue_row_span = max_col_clue_len
        
        cell_width, cell_height = self._get_cell_dims(self.grid_size)

        for c in range(self.grid_size):
            clue_text = "\n".join(map(str, self.col_clues[c]))
            
            label = tk.Label(
                parent_frame, text=clue_text, width=cell_width, height=clue_row_span,
                borderwidth=1, relief="solid", bg="#E0E0E0", font=('Arial', 8)
            )
            label.grid(row=0, column=c + clue_col_span, rowspan=clue_row_span, sticky="")

        for r in range(self.grid_size):
            clue_text = " ".join(map(str, self.row_clues[r]))
            
            label = tk.Label(
                parent_frame, text=clue_text, width=clue_col_span * 2, height=cell_height, 
                borderwidth=1, relief="solid", bg="#E0E0E0", font=('Arial', 8)
            )
            label.grid(row=r + clue_row_span, column=0, columnspan=clue_col_span, sticky="")

        self.cell_buttons = []
        for r in range(self.grid_size):
            row_buttons = []
            for c in range(self.grid_size):
                
                bd = 1
                
                button = tk.Button(
                    parent_frame, text="", 
                    width=cell_width, height=cell_height,
                    bg="white", 
                    relief="raised",
                    bd=bd, 
                    command=lambda r=r, c=c: self._cell_click(r, c) 
                )
                
                button.grid(row=r + clue_row_span, column=c + clue_col_span, sticky="")
                row_buttons.append(button)
            self.cell_buttons.append(row_buttons)

    # -----------------------------------------------------------
    # 2-5. 패턴 등록 기능 (클릭하여 그리기)
    # -----------------------------------------------------------

    def _open_pattern_creator(self):
        """패턴 등록 창을 엽니다. 클릭으로 패턴을 그릴 수 있습니다."""
        creator_window = Toplevel(self.master)
        creator_window.title("새 패턴 그리기 및 등록")
        
        self.creator_size = tk.IntVar(value=5)
        
        self.creator_size.trace_add('write', lambda *args: self._draw_creator_grid_auto_call(creator_window)) 
        
        self.creator_grid_state = []
        self.creator_buttons = []

        main_frame = tk.Frame(creator_window, padx=10, pady=10)
        main_frame.pack(fill="both", expand=True)
        
        control_frame = tk.Frame(main_frame)
        control_frame.pack(pady=10)
        
        tk.Label(control_frame, text="패턴 이름:").pack(side=tk.LEFT, padx=5)
        self.new_pattern_name = tk.StringVar()
        tk.Entry(control_frame, textvariable=self.new_pattern_name, width=15).pack(side=tk.LEFT, padx=5)

        tk.Label(control_frame, text="크기:").pack(side=tk.LEFT, padx=10)
        
        size_options = [5, 10, 20]
        tk.OptionMenu(control_frame, self.creator_size, *size_options).pack(side=tk.LEFT, padx=5)

        self.creator_grid_frame = tk.Frame(main_frame, borderwidth=2, relief="groove")
        self.creator_grid_frame.pack(pady=10, fill="both", expand=True)

        tk.Button(main_frame, text="등록 완료 및 저장", bg="lightblue", 
                  command=lambda: self._register_created_pattern(creator_window)).pack(pady=10)
        
        self._draw_creator_grid(main_frame)
    
    def _draw_creator_grid_auto_call(self, window):
        self._draw_creator_grid(window) 

    def _draw_creator_grid(self, parent_frame):
        """선택된 크기에 맞춰 격자 그리기 창을 업데이트합니다."""
        size = self.creator_size.get()
        
        if size not in [5, 10, 20]:
            return 
            
        for widget in self.creator_grid_frame.winfo_children():
            widget.destroy()
        
        self.creator_grid_state = [[0] * size for _ in range(size)]
        self.creator_buttons = []
        
        cell_width, cell_height = self._get_cell_dims(size)

        for r in range(size):
            row_buttons = []
            for c in range(size):
                
                bd = 1
                    
                btn = tk.Button(
                    self.creator_grid_frame,
                    bg="white", 
                    width=cell_width, height=cell_height,
                    bd=bd, 
                    relief="raised",
                    command=lambda r=r, c=c: self._creator_click(r, c)
                )
                
                btn.grid(row=r, column=c, sticky="")
                row_buttons.append(btn)
            self.creator_buttons.append(row_buttons)

    def _creator_click(self, r, c):
        """생성 격자 클릭 시 상태 토글 (0 -> 1 -> 0)."""
        current_state = self.creator_grid_state[r][c]
        
        if current_state == 0:
            self.creator_grid_state[r][c] = 1
            self.creator_buttons[r][c].config(bg="black")
        else:
            self.creator_grid_state[r][c] = 0
            self.creator_buttons[r][c].config(bg="white")
            
    def _register_created_pattern(self, window):
        """클릭하여 생성된 패턴을 저장합니다."""
        name = self.new_pattern_name.get().strip()
        size = self.creator_size.get()
        pattern = self.creator_grid_state

        if not name:
            messagebox.showerror("오류", "패턴 이름을 입력해야 합니다.")
            return
        if name in self.patterns:
            messagebox.showerror("오류", f"'{name}'은 이미 존재하는 패턴 이름입니다.")
            return

        self.patterns[name] = {"size": size, "pattern": pattern}
        self._save_patterns()
        
        self._draw_main_menu()
        
        messagebox.showinfo("성공", f"패턴 '{name}' ({size}x{size})가 성공적으로 등록되었습니다.")
        window.destroy()
        
    # -----------------------------------------------------------
    # 2-6. 이벤트 처리 및 판정
    # -----------------------------------------------------------
    
    def _cell_click(self, row, col):
        """셀 클릭 시 상태 토글 (0: 빈칸, 1: 채움(검정), 2: X표시)."""
        current_state = self.player_grid[row][col]
        next_state = (current_state + 1) % 3 
        self.player_grid[row][col] = next_state
        
        button = self.cell_buttons[row][col]
        
        if next_state == 0:
            button.config(text="", bg="white")
        elif next_state == 1:
            button.config(text="", bg="black")
        elif next_state == 2:
            button.config(text="X", bg="white", fg="gray", font=('Arial', 8, 'bold'))
            
        self._check_game_over()

    def _check_game_over(self):
        """현재 플레이어 보드와 정답 보드를 비교하여 승리 여부를 판정합니다."""
        
        for r in range(self.grid_size):
            for c in range(self.grid_size):
                if self.answer_grid[r][c] == 1 and self.player_grid[r][c] != 1:
                    return 
                if self.answer_grid[r][c] == 0 and self.player_grid[r][c] == 1:
                    return 

        messagebox.showinfo("승리!", f"축하합니다! {self.current_pattern_name} 퍼즐을 완성하셨습니다!")
        
        for r in range(self.grid_size):
            for c in range(self.grid_size):
                self.cell_buttons[r][c].config(state=tk.DISABLED)


# =================================================================
# 3. 애플리케이션 실행
# =================================================================
if __name__ == "__main__":
    root = tk.Tk()
    app = NonogramApp(root)
    root.protocol("WM_DELETE_WINDOW", lambda: [app._save_patterns(), root.destroy()])
    root.mainloop()